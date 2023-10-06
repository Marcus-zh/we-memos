import requests
import json
import re
import logging
from model import *

VISIBILITY = ['PUBLIC', ' PROTECTED', 'PRIVATE']

def sendmemos(decrypt_data: dict, info: tuple):
    content = decrypt_data.get('Content', '')
    visibility = "PUBLIC" if content[0] == '@' else "PRIVATE"
    acstoken, api = info[3], info[4] if info[4] is not None else default_api

    try:
        matches = re.findall(r'<(.*?)>', content)
        content = re.sub(r'<(.*?)>', '', content)
        result = [[int(e) for e in match.split(',')] for match in matches]
        data = {
            'content': content,
            "visibility": visibility,
            'resourceIdList': result[0] if len(result) == 1 else result
        }
        headers = {
            'accept': 'application/json',
            'Referer': api,
            'Authorization': f'Bearer {acstoken}'
        }
        response = requests.post(api + "/api/v1/memo", headers=headers, json=data)
        id = json.loads(response.text)["id"]
        msg = f"发送成功!\nid: {id}\n"
        bot.send_text(content=f"<a href='{api}/m/{id}'>点击查看</a>", touser=[decrypt_data.get("FromUserName")])
        logging.info(msg)
    except Exception as e:
        msg = f"发送失败! 错误: {e}"
        logging.error(msg)
    return msg

def updateimg(decrypt_data: dict, info: tuple):
    acstoken, api = info[3], info[4] if info[4] is not None else default_api
    headers = {
        'accept': 'application/json',
        'Referer': api,
        'Authorization': f'Bearer {acstoken}',
    }

    try:
        image_url = decrypt_data.get('PicUrl', '')
        print(image_url)
        imgblob = requests.get(image_url)
        files = {'file': ("1.png", imgblob.content, 'image/jpeg')}
        response = requests.post(default_api + "/api/v1/resource/blob", headers=headers, files=files)
        with open('1.txt', 'wb') as file:
          headers_str = str(response.request.headers)
          file.write(headers_str.encode('utf-8'))
        id = json.loads(response.text)["id"]
        msg = f"上传成功,图片id为: {id}"
        bot.send_text(content=f"<a href='{api+'/o/r/'+str(id)}'>点击查看</a>", touser=[decrypt_data.get("FromUserName")])
        logging.info(msg)
    except Exception as e:
        msg = f"上传失败,错误: {e}"
        logging.error(msg)
    return msg


