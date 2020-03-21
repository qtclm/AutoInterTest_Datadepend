import json
import requests
from tool.operation_logging import MyLog,logs

class RunMethod(object):
    def __init__(self):
        self.mylog=MyLog.get_log()
        self.log = self.mylog.get_logger()
    
    def post_main(self, url, data, headers):  # 封装post请求
        if headers:
            try:
                res = requests.post(url=url, data=data, headers=headers)
                return res
            except BaseException as e:
                return None
        else:
            try:
                res = requests.post(url=url, data=data)
                return res
            except BaseException as e:
                return None
    
    def put_main(self, url, data, headers):  # 封装put请求
        if headers:
            try:
                res = requests.put(url=url, data=data, headers=headers)
                return res
            except BaseException as e:
                return None
        else:
            try:
                res = requests.put(url=url, data=data)
                return res
            except BaseException as e:
                return None
    
    def get_main(self, url, data, headers):  # 封装get请求
        if headers:
            # verify:验证——（可选）要么是布尔型，在这种情况下，它控制我们是否验证服务器的TLS证书或字符串，在这种情况下，它必须是通往CA捆绑包的路径。默认值为True
            # res=requests.get(url=url,params=data,headers=headers,verify=false)
            # get请求请求参数尽量不要编码，防止会有一些错误，这里手动处理一下错误
            try:
                res = requests.get(url=url, params=data.decode(), headers=headers)
                return res
            except BaseException as e:
                return None
            
        else:
            # res=requests.get(url=url,params=data,verify=false)
            try:
                res = requests.get(url=url, params=data)
                return res
            except BaseException as e:
                return None

    def run_main(self, method, url, data=None, headers=None, res_format='json'):  # 封装主请求
        '''参数1：请求方式，参数2：请求data，参数3：请求信息头，参数4：返回的数据格式'''
        res = None
        if data is None or headers is None:
            data=None
            headers=None
        else:
            data=data
            headers=headers
        if method.lower() == 'post' or method.upper() == 'POST':
            res = self.post_main(url=url, data=data, headers=headers)
        elif method.lower() == 'put' or method.upper() == 'PUT':
            res = self.put_main(url=url, data=data, headers=headers)
        elif method.lower() == 'get' or method.upper() == 'GET':
            res = self.get_main(url=url, data=data, headers=headers)
            # print(res)
        else:
            # res=self.get_main(url,data,headers,verify=false)
            self.log.info("暂不支持的请求方式")
            raise Exception("暂不支持的请求方式")
            # dumps方法:
            # sort_keys是告诉编码器按照字典排序(a到z)输出,indent参数根据数据格式缩进显示，读起来更加清晰:
            # separators参数的作用是去掉,,:后面的空格,skipkeys可以跳过那些非string对象当作key的处理,
            # 输出真正的中文需要指定ensure_ascii=False
        if res:
            try:
                if res_format.lower() == 'json' or res_format.upper() == 'JSON':  # 以json格式返回数据
                    '''ensure_ascii:处理json编码问题（中文乱码），separators：消除json中的所有空格'''
                    response=res.json()
                    return response
                elif res_format.lower() == 'text' or res_format.upper() == 'TEXT':  # 以文本格式返回数据
                    response = res.text
                    return response
                elif res_format.lower() == 'str' or res_format.upper() == 'STR':  # 以文本格式返回数据
                    response = res.text
                    return response
                elif res_format.lower() == 'content' or res_format.upper() == 'CONTENT':  # 以二进制形式返回响应数据
                    response = res.content
                    return response
                else:  # 以json格式返回数据
                    response=res.json()
                    return response
            except BaseException as e:
                self.log.error('error:{}'.format(e))
                # print(e)
                # print(res.text)
        else:
            return None


if __name__ == '__main__':
    r = RunMethod()
    url='https://fwh.lpcollege.com/admin.php/system/feedback/index.html'
    # data='page=1&limit=10&keywords=秦敏&startDate=&endDate='
    data=b'page=1&limit=10&keywords=\xe7\xa7\xa6\xe6\x95\x8f&startDate=&endDate='
    header={'x-requested-with': 'XMLHttpRequest', 'Cookie': 'PHPSESSID=437649699becad37fe1587064163e990b9e0e5b1ff81506b681069dbcdd3a035'}
    # print(r.run_main('get', url, data=data, headers=header, res_format='json'))
    print(r.get_main(url=url, data=data, headers=header))

