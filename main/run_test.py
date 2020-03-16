import sys
sys.path.append('../')
from operation_data.get_data import GetData
from operation_data.writeAllDependDatas import write_excle
from tool.WriteTestReportToExcel import Write_testReport_excle

class RunTest(GetData):
    # 实例化前完成所有的请求数据依赖处理
    options=input('是否需要执行用例依赖数据写入操作,确认执行请输入yes,不执行请输入其他任意字符:\n')
    if options=='yes':
        write_excle()
        print('依赖数据写入完成')
    else:
        print("跳过写入依赖数据，开始执行测试")
    def __init__(self):
        super().__init__()
        self.data=GetData()
        self.op_testReport = Write_testReport_excle()
        # '''读取失败重试配置'''
        self.Config_Try_Num=self.yaml.readDataForKey('Config_Try_Num')
      
    # 程序执行
    def go_on_run(self):
        global pass_count, fail_count
        response = None
        pass_count = []
        fail_count = []
        rows_count = self.data.get_case_line()
        self.log.info(self.mylog.out_varname(rows_count))
        for i in range(2,rows_count+1):
        # for i in range(rows_count,rows_count+1):
            is_run = self.data.get_is_run(i)
            if is_run is True:
                # ''' 处理请求'''
                response=self.request_info(i)
                expect = self.data.expectData(i)  # 断言，也就i是预期结果
                # '''处理断言'''
                # response默认是dict类型，这里断言是字符串所以需要把dict转换为str
                self.assert_control(i,expect,str(response))
                self.log.info(self.mylog.out_varname(expect))
                self.log.info(self.mylog.out_varname(response))
                # print(expect in str(response))
                # print(str(response))
                
            # else:
            #     contine_info='当前用例为第{}条，跳过,is_run={}'.format(i-1,is_run)
            #     self.log.info(self.mylog.out_varname(contine_info))
   
    # 处理请求
    def request_info(self,row):
        request_name=self.get_request_name(row)
        self.log.info(self.mylog.out_varname(request_name))
        url = self.data.get_url(row)
        # print(row,url)
        self.log.info(self.mylog.out_varname(url))
        method = self.data.get_request_method(row)
        # print(method)
        self.log.info(self.mylog.out_varname(method))
        request_data = self.data.requestData(row)
        # print(request_data)
        self.log.info(self.mylog.out_varname(request_data))
        header = self.data.headerData(row)
        # print(header)
        self.log.info(self.mylog.out_varname(header))
        # try:
        if method!='get' and self.yaml.readDataForKey('config')['fwh_admin_test_api'] in url:
            response = self.run_method.run_main(method=method, url=url, data=request_data,headers=header, res_format='text')
        else:
            response = self.run_method.run_main(method=method, url=url, data=request_data,headers=header, res_format='json')
        # print(response)
        self.log.info(self.mylog.out_varname(response))
        return response

    
    #处理断言
    def assert_control(self,row,expect,response):
        errorNum = 0
        # 判断失败次数是否小于等于配置失败重试次数
        while errorNum <= self.Config_Try_Num:
            if self.com_util.is_contain(expect, response):
                self.data.write_result(row, 'pass')
                self.log.info('测试通过')
                pass_count.append(row)
                self.log.info(self.mylog.out_varname(pass_count))
                errorNum = 0
                break
            else:
                self.data.write_result(row, 'Filed')
                if errorNum < self.Config_Try_Num:
                    errorNum += 1
                    errorInfo = "测试失败，重试中,当前重试次数为第%s次" % (errorNum)
                    self.log.info(self.mylog.out_varname(errorInfo))
                else:
                    self.log.info("重试次数已用完,测试失败")
                    fail_count.append(row)
                    self.log.info(self.mylog.out_varname(fail_count))
                    break
            
    
                
    # 发送邮件、生成测试报告
    def create_test_report(self):
        self.op_testReport.write_TestReport(pass_count, fail_count)  # 生成excel表格测试报告
        self.op_testReport.excle_to_html()  # 将测试报告转换为html输出
        self.send_mail.send_main(pass_count, fail_count)  # 发送测试报告邮件


if __name__ == '__main__':
    run = RunTest()
    run.go_on_run()
    run.create_test_report()

