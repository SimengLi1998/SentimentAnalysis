from typing import List, Dict, Union
from pydantic import BaseModel

# input define

class SentimentResponse(BaseModel):
    Sentiment: str
    Intention: List[int]
    Keywords: Dict[str, List[str]]
    Translation: str
    # Feedback: str


class ContactInformation(BaseModel):
    qq: str
    email: str
    phoneNum: str
    facebook: str

class KafkaData(BaseModel):
    feedbackId: int
    deviceId: str
    dbtId: str
    pkg: str
    lang: str
    ip: str 
    content: str
    createTime: str
    remark: str
    textGameWordTypeSelectedList: List[str]
    contactInformation: ContactInformation
    type: str
    prompt_list: List[str] = None

# class Prompt(BaseModel):
#     feedbackId: int

class ReviewData(BaseModel):
    content: str
    commentId: int


# output define
class ResultItem(BaseModel):
    sentiment: str
    intensity: str
    intention: List[int]
    keywords: Dict[str, List[str]]

class FeedbackResult(BaseModel):
    feedbackId: int
    country: str
    result: ResultItem
    status: int




# error define
class ExceedMaxRetryError(Exception):
    pass
