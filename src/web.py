#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi import Response, Request, BackgroundTasks
from xml.etree.ElementTree import fromstring
import uvicorn
import logging
from memos import sendmemos, updateimg
from model import *
app = FastAPI()
logging.basicConfig(format='%(asctime)s [%(levelname)s]  (%(filename)s:%(lineno)d): %(message)s',
                    level=logging.DEBUG)


@app.get("/")
async def verify(msg_signature: str, timestamp: str, nonce: str, echostr: str):
    '''
    验证配置是否成功，处理get请求
    :param msg_signature:
    # :param timestamp:
    :param nonce:
    :param echostr:
    :return:
    '''
    ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
    if ret == 0:
        return Response(content=sEchoStr.decode('utf-8'))
    else:
        print(sEchoStr)


@app.post("/")
async def recv(msg_signature: str, timestamp: str, nonce: str, request: Request, background_tasks: BackgroundTasks):
    '''
    接收用户消息，可进行被动响应
    :param msg_signature:
    :param timestamp:
    :param nonce:
    :param request:
    :return:
    '''
    body = await request.body()
    ret, sMsg = wxcpt.DecryptMsg(body.decode(
        'utf-8'), msg_signature, timestamp, nonce)
    decrypt_data = {}
    for node in list(fromstring(sMsg.decode('utf-8'))):
        decrypt_data[node.tag] = node.text
    message = decrypt_data.get('Content', '')
    username = decrypt_data.get("FromUserName")
    type = decrypt_data.get('MsgType', '')
    logging.info(decrypt_data)
    # 解析后得到的decrypt_data: {"ToUserName":"企业号", "FromUserName":"发送者用户名", "CreateTime":"发送时间", "Content":"用户发送的内容", "MsgId":"唯一id，需要针对此id做出响应", "AagentID": "应用id"}
    sql.cursor_execute(
        f'select * from users where username="{username}";')
    result = sql.cursor_fetchone()
    print(result)

    # 进行判断
    if result == None:
        sql.cursor_execute_commit(
            'insert into users(username,type) values ("{0}", "{1}");'.format(username, 0))
        return Response(content=gmessage(f"请使用'/acstoken'配置从\n{default_api}/setting\n获取的Accesstoken", decrypt_data, nonce))
    api = result[4] if result[4] is not None else default_api

    # 获取信息
    usertype = result[2]
    acstoken = result[3]

    # 进行判断
    # 当发送文字时
    if type == "text":
        logging.info("发送文字")
        if "/acstoken" in message:
            logging.info("设置acstoken")
            update_query = f'UPDATE users SET accesstoken="{message.split("/acstoken ")[1]}" WHERE username="{username}";'
            sql.cursor_execute_commit(update_query)
            return Response(content=gmessage("设置成功", decrypt_data, nonce))
        elif acstoken == None:
          return Response(content=gmessage(f"请使用'/acstoken'配置从\n{api}/setting\n获取的Accesstoken", decrypt_data, nonce))
        elif "/api" in message:
            logging.info("设置api")
            update_query = f'UPDATE users SET api="{message.split("/api ")[1]}" WHERE username="{username}";'
            sql.cursor_execute_commit(update_query)
            return Response(content=gmessage("设置成功", decrypt_data, nonce))
        elif "/admin" in message:
            logging.info("admin查询")
            if usertype == 1:
                update_query = f'select * from users;'
                allinfo = sql.cursor_fetchall()
                return Response(content=gmessage(str(allinfo), decrypt_data, nonce))
            else:
                return Response(content=gmessage("你没有权限", decrypt_data, nonce))
        else:
            logging.info("发送memos")
            return Response(content=gmessage(sendmemos(decrypt_data, result), decrypt_data, nonce))
    # 当发送图片时
    elif type == "image":
        logging.info("发送图片")
        return Response(content=gmessage(updateimg(decrypt_data, result), decrypt_data, nonce))


if __name__ == "__main__":
    uvicorn.run("web:app", port=8000, host='0.0.0.0', reload=False)
