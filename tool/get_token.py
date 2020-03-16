import requests
import re
import sys
sys.path.append("../")
from tool.OperationDatas import OperationYaml
import os
from tool.operation_logging import MyLog,logs

# 配置基类
class Config(object):
    def __init__(self):
        Config = OperationYaml().read_data()
        self.config=Config['config']

class Crm_token(Config):
    def __init__(self,file_name_path='../tokenFiles',name='token.data'):
        super().__init__()
        self.url_login_in=self.config['url_login_in']
        self.return_url="{}/?return_url={}".format(self.config['crm_login_server'], self.config['crm_front_addr'])
        self.login_server='{}/CAS_server/login'.format(self.url_login_in)
        if not os.path.exists(file_name_path):#判断文件夹是否存在    
            print('文件夹不存在，开始创建文件夹:"%s"'%(file_name_path))
            os.mkdir(file_name_path) #创建文件夹
            print('文件夹"%s"已创建'%(file_name_path))
        self.file_name=file_name_path+'/'+name
        if not os.path.exists(self.file_name): #判断文件是否存在
            print('文件不存在，开始创建文件:"%s"'%(self.file_name))
            with open(self.file_name,'w') as file:#创建文件
                file.close() 
            print('文件"%s"已创建'%(name))
        self.mylog = MyLog.get_log()
        self.log = self.mylog.get_logger()
    
    def get_token(self,username=18883612485,password='112233'):
        url_check_login=self.config['crm_test_api']+'/Auth/checkLogin'
        check_login_data='username=%s&password=%s'%(str(username),password)
        request_check_login=requests.post(url=url_check_login,headers=self.config['headers_form_urlencoded'],data=check_login_data)
        response_login_message=request_check_login.json()
        # print(response_login_message)
        if response_login_message['msg'] == '成功' and response_login_message['code']==200:
            self.log.info('begin---login---')
            try:
                ruequest_get_login_server=requests.get(url=self.return_url,headers=self.config['headers_text'],data=None)
                response_get_login_server=ruequest_get_login_server.text
                login_server=re.search('{}(.+\w)'.format(self.config['crm_login_server']),response_get_login_server).group() #正则匹配login_server
                with requests.Session() as session: #自动关闭会话
                    session=requests.Session() #建立session会话
                    url_login_1=self.url_login_in+'''/CAS_server/login?action=getlt&service=%s&callback=jQuery33105752563290575323_1551706407492&
                    _=1551706407493'''%(login_server)
                    request1=session.request("GET",url=url_login_1,headers=self.config['headers_form_urlencoded'],data=None) #登录前动态参数获取url
                    response1=request1.text
                    get_shouquan_str1=eval(re.search('{.*}',response1).group()) #匹配出字典内的内容并用eval方法将str转换为dict
                    get_lt=get_shouquan_str1['lt'] #提取授权参数1
                    get_execution=get_shouquan_str1['execution'] #提取授权参数2
                    url_login_2=self.url_login_in+'/CAS_server/login?service=%s'%(login_server) 
                    login_data='lt=%s&execution=%s&_eventId=submit&username=%s&password=%s'%(get_lt,get_execution,username,password)
                    #登录body，将获取到对的两个动态参数也传进去
                    request2=session.post(url=url_login_2,headers=self.config['headers_form_urlencoded'],data=login_data.encode(),allow_redirects=True)
                    #allow_redirects=False,禁止请求重定向：为了获取重定向url，requests模块默认请求重定向
                    response2=request2.text
                    responseHeaders2=request2.headers #获取reponse header
                    ticket_url=request2.url #获取重定向url
                    ticket_data=re.search('(ticket=.*)',ticket_url).group()
                    url_get_token=self.config['crm_test_api']+'/Auth/login' #登录接口
                    requests_get_token=session.post(url=url_get_token,headers=self.config['headers_form_urlencoded'],data=ticket_data)
                    reponse6=requests_get_token.json()
                    crm_system_token=reponse6['data']['token']
                    self.log.info('login---susscess---')
                    login_info='当前登陆手机号为:%s,token为:\n%s'%(username,crm_system_token)
                    self.log.info(self.mylog.out_varname(login_info))
                    return crm_system_token
            except BaseException as error:
                self.log.error(self.mylog.out_varname(error))
                # print('登录错误，token获取失败，\n错误信息：%s'%(error))
        else:
            self.log.info(self.mylog.out_varname(response_login_message))
            # print(response_login_message)

    def writeTokenToFile(self,username=18883612485,password='112233'):#将token写入文件
        token=[]
        token_list=self.get_token(username,password)
        token.append(token_list)
        if len(token)==0:
            token_list=self.get_token(username,password)
            with open(self.file_name,'w') as token_file:
                token_file.write(str(token))
        else:
            with open(self.file_name,'w') as token_file:
                token_file.write(str(token))
        return token

    def loadTokenList(self,username=18883612485,password='112233'):#加载token
        try:
            with open(self.file_name,'r') as load:
                file_token_list=load.read() #此处读取类型应为list,使用eval方法进行转换
                if not (file_token_list is None or file_token_list==''):
                    file_token_list=eval(file_token_list) #eval方法需要验证字符串是不是有效的
                    if len(file_token_list)==0  :
                        file_token_list=self.writeTokenToFile(username,password)
                    self.config['headers_form_urlencoded']['token']=file_token_list[0]
                    token_test_url=self.config['crm_test_api']+'/message?time=1558758390454&current_page=1&per_page=4&message_type=1' #测试token是否有效
                    token_test_request=requests.get(url=token_test_url,headers=self.config['headers_form_urlencoded'],data=None)
                    token_test_response=token_test_request.json()
                    # print(token_test_response)
                    if token_test_response['code']!=200 :
                        file_token_list=self.writeTokenToFile(username,password)
                else:
                    file_token_list=self.writeTokenToFile(username,password)
            self.log.info(self.mylog.out_varname(file_token_list))
            return file_token_list
        except Exception as error: #当文件不存在时,对异常异常进行捕获
            self.log.error(self.mylog.out_varname(error))
            # print('异常信息:%s'%(error))


if __name__=="__main__":
    tk=Crm_token()
    tel=18883612485
    # print(tk.get_token(tel))
    # Crm_token.config()
    tel_list=['18888888889','15110162871','17610005663','18883612485','13693422350','15907556250','13678185000','13057603900','13522806201','18782132657','18108116138','18349304112','15902831531','18381334041']
    tk.get_token(15902831531,'1qaz2wsx')
    # for a in tel_list:
    #     tk.get_token(a,'112233')
    # a=tk.loadTokenList()
    # print(a)
    # tk.writeTokenToFile()


        