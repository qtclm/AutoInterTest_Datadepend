import sys
sys.path.append('../')
from tool.OperationDatas import OperationExcle
import xlsxwriter
import pandas
import codecs
import time
import os

class Write_testReport_excle(object):
    global workbook,worksheet,sheet_chart,testFiled_chart,chart,formatter,title_formatter,ave_formatter,now,filename
    now = time.strftime("%Y-%m-%d %H-%M-%S")
    workbook_path="../report/excle_report"
    if not os.path.exists(workbook_path):
        os.makedirs(workbook_path)
        '''makedirs:创建多级目录（也可以创建单层目录），mkdir：只能创建单层目录'''
    filename=workbook_path +'/'+now + '_test_report.xls'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("测试报告")#创建测试报告模板
    sheet_chart=workbook.add_worksheet("图形报告")#创建图形报告模板
    testFiled_chart=workbook.add_worksheet("测试失败接口明细")#创建图形报告模板
    # 创建一个图表对象,column:柱形图
    chart = workbook.add_chart({'type': 'column'})
    def __init__(self):
        self.Ope=OperationExcle()

    def create_TestReport(self):#创建测试报告模板
        worksheet.set_column("A:ZZ",20)
        # bold = workbook.add_format({"bold": True})
        # 定义标题栏格式对象：边框加粗1像素，背景色为灰色，单元格内容居中、加粗，自动换行
        formatter = workbook.add_format()
        formatter.set_border(1)
        formatter.set_text_wrap()
        title_formatter = workbook.add_format()
        title_formatter.set_border(1)
        title_formatter.set_bg_color('#cccccc')
        title_formatter.set_align('center')
        title_formatter.set_bold()
        title_formatter.set_text_wrap()
        title = ['系统名称', '全部接口个数', '通过接口数', '失败接口数', '测试通过率', '测试失败率']#定义报告列名称
        buname = ['CRM系统', '服务号微信端', '服务号后台']#定义报告行名称
        worksheet.write_row("A1",title,title_formatter)
        worksheet.write_column("A2", buname, formatter)

    def write_TestReport(self,pass_list,fail_list):
        pass_num=float(len(pass_list))
        fail_num=float(len(fail_list))
        all_num=pass_num+fail_num
        pass_result = "%.2f%%" % (pass_num / all_num * 100)
        fail_result = "%.2f%%" % (fail_num / all_num * 100)
        data = [[all_num, pass_num, fail_num, pass_result, fail_result],
                [all_num, pass_num, fail_num, pass_result, fail_result],
                [all_num, pass_num, fail_num, pass_result, fail_result]
                ]
        #添加柱形图
        list1=('B','C','D')
        start_line=2#定义数据起始行
        end_line=4#定义数据结束行:len(buname)+1
        for row_num in list1:
            chart.add_series({
            "name":"=测试报告!${}$1".format(row_num,row_num),
            "categories":"=测试报告!$A${}:$A${}".format(start_line,end_line),
            "values":"=测试报告!${}${}:${}${}".format(row_num,start_line,row_num,end_line)
            })
        # 添加柱状图标题
        chart.set_title({"name": "各个系统接口测试报告"})
        # Y轴名称
        chart.set_y_axis({"name": "接口数量明细"})
        # X轴名称
        chart.set_x_axis({"name": "系统名称"})
        # 图表样式
        chart.set_style(10)
        #设置图表大小
        chart.set_size({'width': 600, 'height': 400})
        # 插入图表带偏移
        sheet_chart.insert_chart('A2', chart, {'x_offset': 25, 'y_offset': 10})
        # 定义标题栏格式对象：边框加粗1像素，背景色为灰色，单元格内容居中、加粗,自动换行
        formatter = workbook.add_format()
        formatter.set_border(1)
        formatter.set_text_wrap()
        # 写入第2到第6行的数据，并将第2~6行数据加入图表系列
        for i in range(start_line,end_line+1):#循环写入数据
            try:
                worksheet.write_row('B{}'.format(i), data[i-start_line],formatter)
            except IndexError as error:
                print("数据写入超出列表索引范围")
        self.create_TestReport()
        self.write_faild_to_excle(fail_list)  # 将失败的用例回写到文件
        workbook.close()  # 关闭excel对象
        

    def write_faild_to_excle(self,fail_list):
        #定义标题栏格式对象：边框加粗1像素，背景色为灰色，单元格内容居中、加粗,自动换行
        formatter = workbook.add_format()
        formatter.set_border(1)
        formatter.set_font_color('red')
        formatter.set_text_wrap()
        first_line=self.Ope.get_row_values(1)
        testFiled_chart.write_row('A{}'.format(1),first_line,formatter)
        for i in fail_list:
            datas=self.Ope.get_row_values(i)
            #将失败的用例写入测试报告中
            testFiled_chart.write_row('A{}'.format(i),datas,formatter)


    def excle_to_html(self):
        # 注意这里不能直接使用workbook,因为直接引用workbook返回的对象不是一个文件路径，而是:<class 'xlsxwriter.workbook.Workbook'>
        fp=pandas.ExcelFile(filename)
        df=fp.parse()
        html_report_path='../report/html_report/'
        if not os.path.exists(html_report_path):
            os.makedirs(html_report_path)
        with codecs.open(html_report_path+now+'_test_report.html', 'w', 'utf-8') as html_file:
            html_file.write(df.to_html(header=True, index=False))


if __name__=="__main__":
    wte=Write_testReport_excle()
    wte.write_TestReport([1,2,3],[2,3,4,5])
    # wte.excle_to_html()
    # wte.write_faild_to_excle()
