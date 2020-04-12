import requests
import sys
sys.path.append("../")
from tool.get_token import Crm_token
from tool.OperationRequestData import operationRequestData

class fwh_token(Crm_token):
	def __init__(self,name='fwh_token.data'):
		super().__init__(name=name)
		self.fwh_test_api = self.config['fwh_test_api']
		self.data_to_str=operationRequestData()
		
	
	def get_token(self,tel=18888888888,code=9547):
		url_code_login=self.fwh_test_api+'/index/user/loginByCode'
		code_login_data='tel={}&code={}'.format(tel,code)
		request_code_login=requests.post(url=url_code_login,headers=self.config['headers_form_urlencoded'],data=code_login_data)
		response_login_message=request_code_login.json()
		if response_login_message['state']==True:
			fwh_system_token=response_login_message['data']['token']
			login_info='当前登陆手机号为:{},token为:\n{}'.format(tel,fwh_system_token)
			self.log.info(self.mylog.out_varname(login_info))
			return fwh_system_token
		else:
			self.log.info(self.mylog.out_varname(response_login_message))
			# print("登录失败：%s"%(response_login_message))

	def writeTokenToFile(self,tel=18888888888,code=9547):#将token写入文件
		token_list=[]
		token=self.get_token(tel,code)
		token_list.append(token)
		with open(self.file_name,'w') as token_file:
			token_file.write(str(token_list))
		return token_list

	def loadTokenList(self,tel=18888888888,code=9547):#加载token
		try:
			with open(self.file_name,'r') as load:
				file_token_list=load.read() #此处读取类型应为list,使用eval方法进行转换
				if not (file_token_list is None or file_token_list==''):
					file_token_list=eval(file_token_list) #eval方法需要验证字符串是不是有效的
					if len(file_token_list)==0  :
						file_token_list=self.writeTokenToFile(tel,code)
					self.config['headers_form_urlencoded']['token']=file_token_list[0]
					token_test_url=self.config['fwh_test_api']+'/index/user/info' #测试token是否有效
					token_test_data=self.data_to_str.fwh_request_sha1('''timestamp:1566009861580
					sign:d7c2d1b453f206e2f075c9fb9add34eb88735649''')
					# print(self.mylog.out_varname(token_test_url))
					# print(self.mylog.out_varname(token_test_data))
					# print(self.config['headers_form_urlencoded'])
					token_test_request=requests.post(url=token_test_url,headers=self.config['headers_form_urlencoded'],data=token_test_data)
					token_test_response=token_test_request.json()
					if token_test_response['state']!=True :
						# print(self.mylog.out_varname(token_test_response))
						file_token_list=self.writeTokenToFile(tel,code)
				else:
					file_token_list=self.writeTokenToFile(tel,code)
			self.log.info(self.mylog.out_varname(file_token_list))
			return file_token_list
		except Exception as error: #当文件不存在时,对异常异常进行捕获
			self.log.error(self.mylog.out_varname(error))
			print('异常信息:%s'%(error))


if __name__=="__main__":
	tk=fwh_token()
	tel_list=[18888888888,13550314521,15651079241,13330005359,15962883801,15850564627,18815530362,15827474399,15240248892,15996200807,15996348047,13476185839,15855105403,15895018953,18912963593,18895399631,13270898768,18856163660,18251885334,13921431841,17798521120,15261831529]
	# print(tk.get_token(18772937709))
	# tk.get_token()
	tk.loadTokenList()
	# tk.writeTokenToFile()
	# for a in tel_list :
	# 	print("token:",tk.get_token(a))

	