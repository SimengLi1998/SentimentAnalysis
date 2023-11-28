# from server import * 
import server
import translate
from fastapi import FastAPI
import uvicorn
import sys
import os
import logging


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

app = FastAPI()
app.include_router(server.serviceRouter,prefix='/service',tags=["service模块"])

if __name__  == '__main__':
    if sys.argv[1]: # 如果传递环境变量XXX,那么环境变量为XXX
        os.environ['dev_mode'] = sys.argv[1]
    else:           # 如果没有传递环境变量,那么环境变量为dev
        os.environ['dev_mode'] = 'dev'
    logging.info(f"dev_mode: {sys.argv[1]}")
    uvicorn.run('main:app',host='0.0.0.0',port=8800,reload=True, workers=4)
