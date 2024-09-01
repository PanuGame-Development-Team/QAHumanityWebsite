import requests

PARTNER = 'qdzx'
LOGIN_URL = 'https://bnds.yunxiao.com/accountApi/userLogin'
USER_INFO_URL = 'https://bnds.yunxiao.com/accountApi/school/userInfo'
CAPTCHA_URL = 'https://bnds.yunxiao.com/api/v1/verify/captchaCode'


def yx_login(username, password, captcha_code='', captcha_value=''):
    print(username, password, captcha_code, captcha_value)
    session = requests.Session()
    login_data = {
        'account': username,
        'password': password,
        'captchaCode': captcha_code,
        'captchaValue': captcha_value,
        'rememb': False,
    }
    try:
        result = session.post(LOGIN_URL,
                              data=login_data,
                              timeout=5,
                              headers={
                                  'Host': f'{PARTNER}.yunxiao.com',
                              }).json()
    except requests.Timeout:
        return {'status': 'timeout', 'msg': '请求超时', 'data': None}
    if result['code'] == '2':
        return {'status': 'error', 'msg': result['msg']}
    elif result['code'] == '3':
        return {
            'status': 'error',
            'msg': result['msg'],
            'captcha_code': result['data']['captchaCode']
        }
    elif result['code'] != '1':
        return {'status': 'error', 'msg': result['msg']}
    try:
        user_info = session.get(USER_INFO_URL,
                                timeout=5,
                                headers={
                                    'Host': f'{PARTNER}.yunxiao.com',
                                }).json()['userinfo']
    except requests.Timeout:
        return {'status': 'timeout', 'msg': '请求超时', 'data': None}
    if len(user_info['roles']) != 1:
        return {'status': 'error', 'msg': '该账号无身份信息或身份信息不唯一'}

    return {'status': 'success', 'data': user_info}

def get_captcha_code():
    session = requests.Session()
    try:
        result = session.get(CAPTCHA_URL, timeout=5)
    except requests.Timeout:
        return {'status': 'timeout', 'msg': '请求超时', 'data': None}
    result = result.json()
    return result['data']

#lib
from markdown import markdown
from settings import *
import bs4
from model import *
from uuid import uuid4
from base64 import b64encode,b64decode
from werkzeug.security import generate_password_hash,check_password_hash
def lin(la:list,lb:list):
    for i in la:
        if not i in lb:
            return False
    return True
def tagf(html:str,themeid:int):
    if themeid == 0:
        theme = "primary"
    elif themeid == 1:
        theme = "danger"
    elif themeid == 2:
        theme = "warning"
    elif themeid == 3:
        theme = "success"
    return html.replace("{theme}",theme)
def render_markdown(string:str):
    return markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
def deltag(html):
    bs = bs4.BeautifulSoup(html,"html.parser")
    return bs.getText()
def getuser_id(uid):
    user = ExUser.query.filter(ExUser.name == str(uid)).first()
    if not user:
        try:
            user = User.query.filter(User.id == int(uid)).first()
        except:
            user = None
    return user
def getuser_intid(uid:int):
    user = ExUser.query.filter(ExUser.id == uid).first()
    if not user:
        user = User.query.filter(User.id == uid).first()
    return user
def save_file(img,allowed):
    fileext = img.filename.strip().split(".")[-1].lower()
    if fileext in allowed:
        uuid = uuid4().hex
        img.save(open(os.path.join(ABDIR,f"static/uploads/{uuid}.{fileext}"),"wb"))
        return f"/static/uploads/{uuid}.{fileext}"
    return None
def safe_script(content:str):
    bs = bs4.BeautifulSoup(content,"html.parser")
    for script in bs.find_all("script"):
        script.decompose()
    for attr in DANGERARGS:
        for i in bs.find_all(attrs={attr:True}):
            del i[attr]
    return bs.__str__()
class MsgQueue:
    def __init__(self):
        import pickle
        self.pickle = pickle
        self.queue = pickle.load(open("msg.q","rb")) if os.path.isfile("msg.q") else []
    def push(self,msg):
        self.queue.append(msg)
        with open("msg.q","wb") as file:
            self.pickle.dump(self.queue,file)
    def pop(self):
        self.queue.pop(0)
        with open("msg.q","wb") as file:
            self.pickle.dump(self.queue,file)
msgqueue = MsgQueue()

def uidencode(uid:int|str):
    suid = str(uid).encode("UTF-8")
    return b64encode(suid,b"+=").hex().upper()
def uiddecode(encoded:str):
    return b64decode(bytes.fromhex(encoded.lower())).decode("UTF-8")