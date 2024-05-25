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
from werkzeug.security import generate_password_hash,check_password_hash
def lin(la:list,lb:list):
    for i in la:
        if not i in lb:
            return False
    return True
def tagf(html,themeid):
    if themeid == 0:
        theme = "primary"
    elif themeid == 1:
        theme = "danger"
    elif themeid == 2:
        theme = "warning"
    elif themeid == 3:
        theme = "success"
    return html.format(theme=theme)
def render_markdown(string):
    return markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
# def deltag(html):
#     return html.translate({ord(i):None for i in "abcdefghijklmnopqrstuvwxyz1234567890 !-\"'<>/%\{\}=#.:;_"})
def deltag(html):
    bs = bs4.BeautifulSoup(html,"html.parser")
    return bs.getText()
def getuser_up(username,password):
    pass
def getuser_id(uid):
    user = ExUser.query.filter(ExUser.name == str(uid)).first()
    if not user:
        try:
            user = User.query.filter(User.id == int(uid)).first()
        except:
            user = False
    return user
def save_file(img,allowed):
    fileext = img.filename.strip().split(".")[-1].lower()
    if fileext in allowed:
        uuid = uuid4().hex
        img.save(open(os.path.join(ABDIR,f"static/uploads/{uuid}.{fileext}"),"wb"))
        return f"/static/uploads/{uuid}.{fileext}"
    return None