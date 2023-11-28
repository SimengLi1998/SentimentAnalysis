from dataclass import ReviewData, SentimentResponse, FeedbackResult, ExceedMaxRetryError
from fastapi import APIRouter, HTTPException
import json
import hashlib
import requests
import os
import logging
import configparser
import asyncio

# logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
serviceRouter = APIRouter()


# --------------Receive Data--------------
@serviceRouter.post("/review_analysis")
async def receive_data(Input: ReviewData):
    try:
        kafka_content = Input.content
        kafka_id = Input.commentId
        config = 'config_rev.conf'

        # 调用数据处理路由处理数据
        response = await review_sentiment_route(kafka_content, kafka_id, config)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------Data Process--------------
@serviceRouter.post("/process_data")
def check_output_format(output_str):
    try:
        output_json = json.loads(output_str)
        # 检查是否包含必要的键
        if not set(output_json.keys()) >= {"commentId", "result", "status"}:
            return """输出格式有误：没有包含必要的键"commentId", "result", "status"。请严格根据格式要求生成。"""
        result = output_json["result"]
        
        # 检查result中是否包含必要的键
        if not set(result.keys()) >= {"sentiment", "intensity", "intention", "keywords"}:
            return """输出格式有误：没有包含必要的键"sentiment", "intensity", "intention", "keywords"。请严格根据格式要求生成。"""
        
        # 检查sentiment和intensity是否符合格式要求
        sentiment = result["sentiment"]
        intensity = result["intensity"]
        if sentiment not in {"正面", "负面", "中性"}:
            return """输出格式有误："sentiment"不是"正面", "负面", "中性"之一。请严格根据格式要求生成。"""
        
        try:
            intensity_float = float(intensity)
            if not (-1 <= intensity_float <= 1):
                return """输出格式有误："intensity"不是在-1到1之间的小数。请严格根据格式要求生成。"""
        except ValueError:
            return """输出格式有误："intensity"值无法转换为浮点数。请严格根据格式要求生成。"""

        # 检查intention是否是一个列表
        intention = result["intention"]
        if not isinstance(intention, list):
            return """输出格式有误："intention"不是list格式。请严格根据格式要求生成。"""
        
        # 检查keywords是否是一个字典
        keywords = result["keywords"]
        if not isinstance(keywords, dict):
            return """输出格式有误："keywords"不是dict格式。请严格根据格式要求生成。"""

        # 检查intention和keywords的长度是否一致
        if len(intention) != len(keywords):
            return """输出格式有误："intention"列表中的值和"keywords"的键不是一一对应。请严格根据格式要求生成。"""

        # 检查keywords中的键是否为字符串，值是否为字符串列表
        for key, value in keywords.items():
            if not isinstance(key, str) or not isinstance(value, list):
                return """输出格式有误："keywords"中的键不是string,值不是list。请严格根据格式要求生成。"""
        return True
    except json.JSONDecodeError:
        return """输出格式有误,请严格根据格式要求生成。"""


# --------------Sentiment Analysis--------------
@serviceRouter.post("/review_sentiment")
async def review_sentiment_route(review: str, kafka_id:int, config:str):
    # 获取当前文件的绝对路径
    folder_dir = os.path.dirname(os.path.realpath('__file__'))
    conf = configparser.ConfigParser()
    conf.read(f'{folder_dir}/'+config)
    dev_mode = os.environ['dev_mode']
    config = conf[dev_mode]

    role = "你扮演一个高级评论分析人员,你需要分析用户的评论,提取出用户有价值的信息,你只能输出中文,如果有小语种,请翻译成中文后输出."

    # 同步请求chatgpt的方法
    def req_gpt(review, kafka_id):
        retry_count = int(config['retry']) 

        # 第二版prompt(翻译原文为中文)
        prompt = f"""从评论文本中识别以下5个项目,用中文回复:
                    - 情绪识别
                        正面/负面/中性
                    - 情感强度
                        返回-1到1之间的folat小数(精确到小数点后三位),越靠近1代表越正面,越靠近-1代表越负面,越靠近0代表越中性
                    - 评论的意图是什么？可以有多个意图标签(尽可能识别多个意图,区分细一点),列表仅返回意图代号,比如[1,2,4],格式为list[int],不能为空，实在不知道可以回传[5]
                        0:广告频次反馈(比如,广告太多了,广告频繁的抱怨)
                        1:广告BUG反馈(比如,广告打不开,广告不能正常播放等只与广告有关的bug)
                        2:游戏BUG反馈(比如,游戏关卡有问题,登录页有问题等只与游戏有关的bug) 
                        3:游戏优化建议(比如,用户的一些建议,包括但不限于建议增加或减少某些功能等)
                        4:退款请求(比如，用户有退款、退钱这类的意图)
                        5:情感表达,无其他意图
                        6:其他(不包含以上意图的其他问题)
                    - 关键词提炼,用中文回复,分别总结提炼不同意图的文本内容,要求全面覆盖用户的不同意图,重点关注你做为开发人员看到这个评论会在意的部分,请句意完整的表述用户的诉求。列表返回(请以意图标签代号作为键),比如 "1":["广告打不开","广告不能正常播放"]。不能为空，实在不知道可以回传"6":["未识别"].

                    评论用三个反引号分隔。将您的响应格式化为 JSON 对象,严格按照 “sentiment”、“intensity”、“intention”、“keywords”作为键,有且仅有这四个键，不要添加任何多余的内容。
                    仅分析评论文本```之间的信息,上述指令中例子为参考,并非真实用户评论的一部分。
                    让你的回应尽可能简短。

                    评论文本: ```{review}```
                    """

        # 情感分析
        headers = {'Content-Type': 'application/json', 'charset':'utf-8', "X-Request-req-accessKeyId": config['cp_accessKeyId'], 'X-Request-Req-Accesskeysecret': config['cp_accessKeySecret']}
        data = {'issue': prompt, 'systemContent': role,'maxPromptToken': int(config['max_token'])}

        while retry_count > 0:
            try:
                response = requests.post(f"{config['url']}/AIGCChatOpenServ/saas/{config['model']}/text", headers=headers, data=json.dumps(data))
                result_ = json.loads(response.text)

                answer_data_str = result_['data']['answer']
                start_index = answer_data_str.find('{')
                end_index = answer_data_str.rfind('}')
                cleaned_answer_data_str = answer_data_str[start_index:end_index+1]
                sentiment = json.loads(cleaned_answer_data_str)

                if response.status_code == 200:
                    output_data = {
                        "commentId": kafka_id,
                        "result": sentiment,
                        "status": 1
                    }
                    # output_data = {
                    #         "commentId": 1,
                    #         "result": {
                    #             "sentiment": "中性",
                    #             "intensity": "-0.333",
                    #             "intention": [],
                    #             "keywords": {}
                    #         },
                    #         "status": 1
                    #     }
                

                # 在每次尝试后进行检查

                if not output_data["result"].get("intention"):
                    output_data["result"]["intention"] = [6]
                if not output_data["result"].get("keywords"):
                    output_data["result"]["keywords"] = {"6": ["未识别"]}
                        
                check_result = check_output_format(json.dumps(output_data))
                if check_result == True:
                    break  # 如果 check_output_format 为 True，直接退出循环
                else:
                    logging.info('错误信息: %s', check_result)  # 更详细地打印check_result的值
                    prompt = prompt + check_result  # 根据错误信息更新prompt

                retry_count -= 1
            except:
                status = 0
                output_data = {
                    "commentId": kafka_id,
                    "result": response.status_code,
                    "status": status
                }
                logging.info('请求时发生异常！')
                break  # 当有异常时，直接退出循环

        if retry_count == 0:
            status = 0
            output_data = {
                "commentId": kafka_id,
                "result": response.status_code,
                "status": status
            }
            logging.info('超出最大重试请求数!')

        return output_data

    return req_gpt(review,kafka_id)
