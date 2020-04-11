#服务号后台获取token
import requests
import re
import sys
sys.path.append("../")
from tool.get_token import Crm_token

class fwh_admin_token(Crm_token):
    def __init__(self,name='fwh_admin_token.data'):
        super().__init__(name=name)  # 最后继承Crm_token进一步处理
        self.url_login_in=self.config['url_login_in']
        self.return_url="{}/?return_url={}".format(self.config['crm_login_server'],self.config['fwhadmin_front_addr'])
        
    def get_token(self, username=18888888888, password='admin123456'):
        headers_check_login = self.config['headers_form_urlencoded']
        url_check_login = self.config['crm_test_api'] + '/Auth/checkLogin'
        check_login_data = 'username=%d&password=%s' % (username, password)
        request_check_login = requests.post(url=url_check_login, headers=headers_check_login, data=check_login_data)
        response_login_message = request_check_login.json()
        if response_login_message['msg'] == '成功' and response_login_message['code'] == 200:
            self.log.info('begin---login---')
            try:
                headers_text = self.config['headers_text']
                ruequest_get_login_server = requests.get(url=self.return_url, headers=headers_text, data=None)
                response_get_login_server = ruequest_get_login_server.text
                login_server = re.search('{}(.+\w)'.format(self.config['crm_login_server']),
                                         response_get_login_server).group()  # 正则匹配login_server
                with requests.Session() as session:  # 自动关闭会话
                    session = requests.Session()  # 建立session会话
                    headers_check_login.update({"Referer": self.return_url})
                    url_login_1 = self.url_login_in + '/CAS_server/login?action=getlt&service=%s&callback=jQuery33105752563290575323_1551706407492&_=1551706407493' % (
                        login_server)
                    request1 = session.request("GET", url=url_login_1, headers=headers_check_login, data=None)  # 登录前动态参数获取url
                    response1 = request1.text
                    get_shouquan_str1 = eval(re.search('{.*}', response1).group())  # 匹配出字典内的内容并用eval方法将str转换为dict
                    get_lt = get_shouquan_str1['lt']  # 提取授权参数1
                    get_execution = get_shouquan_str1['execution']  # 提取授权参数2
                    cookies_login_1 = request1.cookies.get_dict()  # 获取cookie：JSESSIONID
                    seesionId = cookies_login_1['JSESSIONID']
                    requestSeesionId = str('JSESSIONID=' + seesionId)  # 拼接为请求可用的cookie值
                    headers_check_login.update({"Cookie": requestSeesionId})
                    url_login_2 = self.url_login_in + '/CAS_server/login?service=%s' % (login_server)
                    # 请求信息头必须传cookie，否则会一直返回登录页面
                    login_data = 'lt=%s&execution=%s&_eventId=submit&username=%s&password=%s&submit=登录' % (
                    get_lt, get_execution, username, password)
                    # 登录body，将获取到对的两个动态参数也传进去
                    request2 = session.post(url=url_login_2, headers=headers_check_login, data=login_data.encode(),
                                            allow_redirects=False)
                    # allow_redirects=False,禁止请求重定向：为了获取重定向url，requests模块默认请求重定向:allow_redirects=True
                    responseHeaders2 = request2.headers  # 获取reponse header
                    url_chongdingxiang_st = responseHeaders2["Location"]  # 获取重定向url
                    requests3 = session.get(url=url_chongdingxiang_st, headers=headers_check_login, data=None,
                                            allow_redirects=False)
                    responseHeaders3 = requests3.headers
                    php_session_cookie = responseHeaders3['Set-Cookie']  # 获取php_session
                    php_session_id = re.search("(\w*\W*\w*)", php_session_cookie).group()  # 用正则匹配出所需要的php_session_id
                    url_chongdingxiang_get_ticket = responseHeaders3['Location']  # 获取重定向url
                    headers_text.update({ "Set-Cookie": php_session_id, "Referer": self.return_url})
                    requests4 = session.get(url=url_chongdingxiang_get_ticket, headers=headers_text, data=None,
                                            allow_redirects=False)
                    responseHeaders4 = requests4.headers
                    url_chongdingxiang_ticket = responseHeaders4['Location']  # 获取重定向url
                    cookies_fwh_admin = "%s" % (php_session_id)  # 写入cookie，用于headers调用
                    headers_text.update({"Cookie": cookies_fwh_admin})
                    requests5 = session.get(url=url_chongdingxiang_ticket, headers=headers_text, data=None,
                                            allow_redirects=False)
                    responseHeaders5 = requests5.headers
                    url_info_url = responseHeaders5['Location']
                    requests_getUserInfo = requests.get(url=url_info_url, headers=headers_text, data=None)
                    self.log.info('login---susscess---')
                    login_info='当前登陆手机号为:%s,sessionId为:\n%s' % (username, php_session_id)
                    self.log.info(self.mylog.out_varname(login_info))
                    headers_xml_fwh_admin = cookies_fwh_admin
                    return headers_xml_fwh_admin
            except BaseException as error:
                self.log.error(self.mylog.out_varname(error))
                print('登录错误，token获取失败，\n错误信息：%s' % (error))
        else:
            self.log.info(self.mylog.out_varname(response_login_message))

    def writeTokenToFile(self, username=18888888888, password='admin123456'):#将token写入文件
        token_list = []
        token = self.get_token(username, password)
        token_list.append(token)
        with open(self.file_name, 'w') as token_file:
            token_file.write(str(token_list))
        return token_list

    def loadTokenList(self, username=18888888888, password='admin123456'):#加载token
        try:
            with open(self.file_name,'r') as load:
                file_token_list=load.read()
                if not (file_token_list in(None,[],'','[None]')):
                    file_token_list=eval(file_token_list) #eval方法需要验证字符串是不是有效的
                    if len(file_token_list)==0:
                        file_token_list=self.writeTokenToFile(username,password)
                    self.config['headers_xml']['Cookie']=file_token_list[0]
                    token_test_url=self.config['fwh_admin_test_api']+'/system/news/index.html?page=1&limit=10&keywords=&startDate=&endDate=' #测试cookie是否有效
                    token_test_request=requests.get(url=token_test_url,headers=self.config['headers_xml'],data=None)
                    token_test_response=token_test_request.json()
                    # print(token_test_response)
                    if not token_test_response.get('msg') is None:
                        if token_test_response['code']==0 and token_test_response['msg']=='请登陆之后在操作':
                            file_token_list=self.writeTokenToFile(username,password)
                            # print(file_token_list['Cookie'])
                else:
                    file_token_list = self.writeTokenToFile(username,password)
            self.log.info(self.mylog.out_varname(file_token_list))
            return file_token_list
        except Exception as error: #当文件不存在时,对异常异常进行捕获
            self.log.error(self.mylog.out_varname(error))
            print('异常信息:%s'%(error))



if __name__=="__main__":
    tk=fwh_admin_token()
    tel=18883612485
    # for a in range(tel,tel+1):
    #   print(tk.get_token(a,'112233'))
    # tk.writeTokenToFile()
    print(tk.loadTokenList())

        