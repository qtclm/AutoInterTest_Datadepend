import sys
sys.path.append("../")
from operation_data.get_data import GetData
from operation_data import data_config
from tool.OperationDatas import OperationYaml,OperationExcle
import demjson
#jsonpath_rw：接口自动化测试中，存在依赖情况：test_02的某个请求参数的值，需要依赖test_01返回结果中某个字段的数据，
# 所以就先需要拿到返回数据中特定字段的值

class DependentData(GetData):
    def __init__(self,case_id):
        super().__init__()
        # 实例依赖字段yaml文件
        self.yamlField=OperationYaml('dependFieldInfo.yaml')
        # 数据依赖字段实例
        self.dependFieldYaml=''
        self.case_id=case_id
        self.data=GetData()
        self.depend_key_dict = {}#存放依赖key数据
    
    #执行依赖测试，并返回结果
    def run_dependent(self):
        row_num=self.opera_excle.get_row_num(self.case_id)
        depend_response=self.data.request_info(row_num)
        self.log.info(self.mylog.out_varname(depend_response))
        return depend_response


    #根据依赖key去获取执行依赖测试case的响应，然后返回
    def get_data_for_key(self,row):
        self.depend_data_dict={}#执行前清空dict
        yamlDepentKey=self.data.get_depent_key(row)
        # print(yamlDepentKey)
        depend_Field_dict={}#数据依赖字段
        # response_data为依赖测试的执行结果
        response_data = self.run_dependent()
        # print(response_data)
        try:
            # ''' 判断depend_data使用eval是否发生异常，如果异常当做单字符处理，
            # 如果没异常判断是否是list且是否为空，满足条件循环处理，否则不处理'''
            if isinstance(response_data,str):
                response_data=eval(response_data)
            if isinstance(yamlDepentKey, list) and yamlDepentKey:
                for i in yamlDepentKey:
                    # print(i)
                    # print(self.depend_key_dict)
                    self.depend_data_parse(i,response_data)
            else:
                return None
        except SyntaxError as syntaxerror:
            print(syntaxerror)
            self.log.error(self.mylog.out_varname(syntaxerror))
            self.depend_data_parse(yamlDepentKey,response_data)
        excleDepentKey=self.dependFiel_kw(row)
        depend_Field_dict[excleDepentKey]=self.depend_key_dict
        # print(self.depend_key_dict)
        return depend_Field_dict
        
    def depend_data_parse(self,depend_key,response_data):
        '''处理依赖'''
        if depend_key:
            # 定义要获取的key
            # 处理依赖时，只取响应中的第一个值
            __dict=self.data.requestDataDispose.depend_data_parse(depend_key,response_data,index='one')
            # 合并字典
            # 确保字典不能为空与类型必须时字典
            if __dict and isinstance(__dict,dict):
                self.depend_key_dict.update(__dict)
        
        
    # 返回数据依赖字段
    def dependFiel_kw(self, row):
        col = int(data_config.get_field_depend())
        depend_field = self.opera_excle.get_cell_value(row, col)
        self.dependFieldYaml = '{}{}'.format(self.yaml['dependField'],row)
        # print('self.data.writelist',self.data.writelist)
        if not depend_field:
            # 判断field关键字是否存在存实例中
            if self.dependFieldYaml in self.data.writelist:
                return self.dependFieldYaml
            else:
                return False
        else:
            return depend_field

    # 获取数据依赖字段
    def get_depend_field(self, row):
        self.write_dependField(row)
        depend_field = self.dependFiel_kw(row)
        depend_field_data = self.yamlField.readforKey_onetier(key=depend_field)
        # print(depend_field)
        # print(depend_field_data)
        if depend_field_data:
            return depend_field_data
        else:
            return False

    # 写入数据依赖字段信息至yaml
    def write_dependField(self,row):
        try:
            dependFieldYaml=self.get_data_for_key(row)
            if dependFieldYaml:
                # '''这句代码用于处理yaml写入失败（浮点对象异常的问题）
                value = eval(demjson.encode(dependFieldYaml))
                # print(value)
                self.yamlField.write_yaml(value)
                return True
            else:
                return False
        except BaseException as error:
            print(error)
            self.log.error(self.mylog.out_varname(error))
            return False
        
    # 将依赖处理完毕的请求数据写入excle
    def writeDependRequestDataToExcle(self,row):
        source_data=self.get_depend_field(row)
        print(self.mylog.out_varname(source_data))
        falg=None
        if source_data:
            falg=self.data.writeDependFiledToRequestData(row,source_data=source_data)
            if falg:
                return True
            else:
                return False
        else:
            return False
    
    
if __name__=='__main__':
    dd=DependentData(1)
    depend_key={'course_name_id': 86}
    v=dd.requestDataDispose.denpendKeyGenerate(depend_key, '$..')
    response= {'code': 200, 'msg': '成功', 'data': {'current_page': 1, 'last_page': 1, 'per_page': 20, 'total': 6, 'data': [{'course_name_id': 188, 'course_name_sn': 'ZB_01_04_01', 'course_name': '抢跑“开学季”——朗培F4导师开学21天陪练营”', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '1980.00', 'member_price': '1980.00', 'least_price': '1980.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 1, 'is_put': 1, 'is_auto_refund': 1, 'is_refund_audit': 0, 'current_daiding_course_id': 1615, 'create_time': '2020-03-17 09:51:43', 'update_time': '2020-03-20 18:30:19', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': '向鹏贤3755', 'update_admin_name': '艾照友0025', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1615?is_need_share=1', 'card': []}, {'course_name_id': 184, 'course_name_sn': 'ZA010101', 'course_name': '校长，别再那么累--招生赢天下，管理定江山test', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '2.00', 'member_price': '1.00', 'least_price': '1.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 13, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 1, 'is_auto_refund': 0, 'is_refund_audit': 0, 'current_daiding_course_id': 1568, 'create_time': '2019-12-21 09:46:54', 'update_time': '2020-03-07 15:04:12', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-民生银行高新支行', 'org_name': '终身', 'create_admin_name': '向鹏贤3755', 'update_admin_name': '秦敏0157', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1568?is_need_share=1', 'card': []}, {'course_name_id': 170, 'course_name_sn': 'ZA_01_01_02', 'course_name': '校长，别再那么累--招生赢天下，管理定江山', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '2000.00', 'member_price': '1000.00', 'least_price': '100.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 1, 'is_put': 1, 'is_auto_refund': 1, 'is_refund_audit': 0, 'current_daiding_course_id': 1562, 'create_time': '2019-08-06 17:50:00', 'update_time': '2020-01-14 16:14:30', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': '孟飞', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1562?is_need_share=1', 'card': [{'study_card_type_id': '3', 'study_card_name': '孵化营9800'}]}, {'course_name_id': 2, 'course_name_sn': 'ZA_01_01_01', 'course_name': '校长，别再那么累2.0-打赢营销战', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '280.00', 'member_price': '280.00', 'least_price': '180.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 1, 'is_auto_refund': 0, 'is_refund_audit': 0, 'current_daiding_course_id': 1560, 'create_time': '2019-03-01 10:30:21', 'update_time': '2019-12-11 13:41:11', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': 'admin', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1560?is_need_share=1', 'card': []}, {'course_name_id': 86, 'course_name_sn': 'ZA_01_03_01', 'course_name': '教培业盈利高增长运营模式3.0', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '2980.00', 'member_price': '2980.00', 'least_price': '980.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 1, 'is_auto_refund': 1, 'is_refund_audit': 0, 'current_daiding_course_id': 583, 'create_time': '2019-03-01 10:30:21', 'update_time': '2020-03-21 15:37:47', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': '秦敏0157', 'share_url': 'https://front.lpcollege.com/#/courseDetails/583?is_need_share=1', 'card': []}, {'course_name_id': 3, 'course_name_sn': 'ZA_01_02_01', 'course_name': '解放校长，管理不再累2.0', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '1980.00', 'member_price': '1980.00', 'least_price': '580.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 0, 'is_auto_refund': 0, 'is_refund_audit': 0, 'current_daiding_course_id': 21, 'create_time': '2019-03-01 10:30:21', 'update_time': '2019-12-05 11:23:55', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': '向鹏贤3755', 'share_url': 'https://front.lpcollege.com/#/courseDetails/21?is_need_share=1', 'card': []}]}}
    value=dd.data.requestDataDispose.depend_data_parse(v[0],response,index='all')
    print(value)
    # # key=dd.get_data_for_key(2)
    # print(dd.write_dependField(3))
    # print(key)
    # value=dd.write_dependData_to_dependField(5)
    # print(value)