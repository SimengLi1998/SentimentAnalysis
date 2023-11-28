FROM python:3.9 as requirements-stage
ENV PIP_NO_CACHE_DIR=yes

#ARG DEV_MODE=dev
#ENV DEV_MODE=$DEV_MODE

#打包镜像工作路径
WORKDIR /app  

#拷贝相关文件
COPY requirements.txt .
COPY dataclass.py .
COPY config_rev.conf .
COPY server.py .
COPY main.py .


RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=pypi.aliyun.com/simple --upgrade pip

#无缓存安装
# RUN pip install -r requirements.txt 
RUN pip install -r sentiment120.txt 

RUN pip install langdetect


EXPOSE 7800


CMD ["python", "main.py", "pro"]
