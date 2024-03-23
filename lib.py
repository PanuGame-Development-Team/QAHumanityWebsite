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
def lin(la:list,lb:list):
    for i in la:
        if not i in lb:
            return False
    return True