from lib.WXBizMsgCrypt3 import WXBizMsgCrypt
import sqlite3
import yaml
from corpwechatbot.app import AppMsgSender

# 声明
with open("./data/config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
default_api = config["memos"]["memo_api"]
# 初始化bot
bot = AppMsgSender(
    corpid=config["wecom"]["corpid"],  # 你的企业id
    corpsecret=config["wecom"]["corpsecret"],  # 你的应用凭证密钥
    agentid=config["wecom"]["agentid"],  # 你的应用id
)
# 初始化wxcpt
wxcpt = WXBizMsgCrypt(config["wecom"]["token"],
                      config["wecom"]["aeskey"], config["wecom"]["corpid"])


def gmessage(content: str, decrypt_data: dict, nonce: str):
    sRespData = f"""
    <xml>
        <ToUserName>{decrypt_data['ToUserName']}</ToUserName>
        <FromUserName>{decrypt_data['FromUserName']}</FromUserName>
        <CreateTime>{decrypt_data['CreateTime']}</CreateTime>
        <MsgType>text</MsgType>
        <Content>{content}</Content>
    </xml>
    """
    ret, send_msg = wxcpt.EncryptMsg(sReplyMsg=sRespData, sNonce=nonce)
    return send_msg
import sqlite3

class Model():
    def __init__(self):
        try:
            self.db = sqlite3.connect('we-memos.db')
            self.create_cursor()
            self.cursor_execute("""CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        type INTEGER,
                        accesstoken TEXT,
                        api TEXT
                      );""")
        except sqlite3.Error as e:
            print("数据库连接错误:", e)

    def cursor_execute(self, sql):
        if not self.db or not self.cursor:
            print("还没连接数据库或创建游标！")
            return
        self.cursor.execute(sql)

    def cursor_execute_commit(self, sql):
        if not self.db or not self.cursor:
            print("还没连接数据库或创建游标！")
            return
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise

    def cursor_fetchone(self):
        return self.cursor.fetchone()

    def cursor_fetchall(self):
        return self.cursor.fetchall()

    def create_cursor(self):
        if not self.db:
            print("还没连接数据库！")
            return
        self.cursor = self.db.cursor()

    def close_connect(self):
        if not self.db:
            print("还没连接数据库！")
            return
        self.db.close()

    def get_table_line_count(self, tableName):
        self.cursor_execute('SELECT COUNT(*) FROM {0}'.format(tableName))
        result = self.cursor_fetchone()
        return result[0]


sql = Model()