import xlrd
from xlutils.copy import copy  # 导入xlutils模块实现对exlcle的修改
import os
import time

class OperationExcleBatch(object):
    def __init__(self, file_address=None, sheet_id=None,path='../dataCase'):
        self.dataCase_list = []
        if file_address is not None:
            self.file_address=file_address
            self.sheet_id=sheet_id
            self.dataCase_list.append(self.file_address)
        else:
            for test_list in os.listdir(path):
                file_address = path + '/' + test_list
                self.file_address = file_address
                self.sheet_id = sheet_id
                sheet_id = 0
                self.dataCase_list.append(self.file_address)
        self.data = self.get_dataBatch()

    # 获取所有sheets的内容
    def get_dataBatch(self):
        tables_list = []
        dataCase_list=self.dataCase_list
        if not dataCase_list in(None,[]):
            for dataCase in dataCase_list:
                data=xlrd.open_workbook(dataCase)
                tables=data.sheet_names()
                for table in tables:
                    table_data=data.sheet_by_name(table)
                    tables_list.append(table_data)
            return tables_list
        else:
            print("没有找到excle文件")
            return None

    #获取所有sheet的名称
    def get_sheets(self):
        sheet_list = []
        dataCase_list=self.dataCase_list
        if not dataCase_list in(None,[]):
            for dataCase in dataCase_list:
                data=xlrd.open_workbook(dataCase)
                tables=data.sheet_names()#返回的是一个列表
                for sheet in tables:#遍历
                    sheet_list.append(sheet)
            return sheet_list
        else:
            print("没有找到excle文件")
            return None
        
    # 获取单元格的行数
    def get_lines(self):
        tables = self.data
        lines_list=[]
        if not tables in([],None):
            for lines in tables:
                lines_list.append(lines.nrows)
            return lines_list
        else:
            print("没有找到excle文件")
            return None

    # 获取某一个单元格的内容
    def get_cell_valueBatch(self, row, col):
        cell_list=[]
        datas=self.data
        # print(datas)
        for cell in datas:
            try:
                cell_value=cell.cell_value(row, col)
                cell_list.append(cell_value)
            except IndexError as error: #判断是否超出索引范围
                pass
        return cell_list
    
    # 获取指定excle里所有的行与行数据
    def get_data(self, dataCase,row):
        data=xlrd.open_workbook(dataCase)
        tables=data.sheet_names()
        # print(tables)
        table_list=[]
        lines_list=[]
        row_data_list=[]
        for table in tables:
            table_data=data.sheet_by_name(table)
            table_list.append(table_data)
        # print(table_list)
        for lines,row_datas in zip(table_list,table_list):
            lines_list.append(lines.nrows)#获取一个excle里所有的页签行数
            try:
                row_data=row_datas.row_values(row)#获取excle里每一行的内容
                row_data_list.append(row_data)
            except IndexError as error:
                pass
        return lines_list,row_data_list#返回excle所有行，所有行数据
        # 根据行列返回表单内容

    # 写入数据
    def write_value(self, row, col, value):
        '''写入excle数据row，col，value'''
        dataCase_list=self.dataCase_list
        if not dataCase_list in([],None):
            for dataCase in dataCase_list:
                datas=self.get_data(dataCase,row)
                lines=datas[0]
                row_data=datas[1]
                method_list=[]
                for method in row_data:
                    if not method[4] in('',None):
                        method_list.append(method[4])
                    else:
                        method_list.append('')
                count=0#统计excle页签数
                read_data = xlrd.open_workbook(dataCase)#打开excle
                tables = read_data.sheet_names()#获取excle内所有页签
                write_data=copy(read_data)#复制原表数据
                #需在for循环外copy文件，不然会导致数据写入不完整，如果放在for循环里面执行，
                #会写入数据得时候之前得内容被替换掉，最终得结果就是仅保留了最后执行时写入得数据   
                for line in lines:              
                    if count>=len(tables):#判断如果count大于当前excle页签值，将count置为0
                        count=0
                    sheet_data = write_data.get_sheet(count)
                    count+=1
                    if (line-1)>=row and row!=0:  #如果当前页签行数大于等于传入的行数，才写入数据
                        #这里之所以要写line-1：因为获取的行数是页签的总行数，
                        #然后读取的时候是从第0行开始读取的,所以需要对其-1 
                        if not method_list in([],None):#如果当前行的数据不为空，开始获取method值，否则不写入数据
                            for method in method_list:
                                if not method in('',None):#当前行数行的method数据不为空，写入数据，否则不写入数据
                                    # print("写入数据%s"%(value))
                                    sheet_data.write(row,col,value)
                                else:  
                                    # print('请求方法数据为空，跳出写入数据')
                                    sheet_data.write(row,col,None)
                                write_data.save(dataCase)#注意保存文件
                        else:
                            pass
                            # print("单元格数据为空，跳出写入数据")
                    else:
                        pass
                        # print("当前页签小于写入行数获取写入数据行数为0,中止写入数据")
        else:
            print("当前路径没有可执行的excle")
            return None

    # 根据对应的caseid找到对应行的内容
    def get_row_data(self, case_id):
        row_num = self.get_row_num(case_id)
        rows_data = self.get_row_values(row_num)
        return rows_data

    # 根据对应的caseid找到相应的行号
    def get_row_num(self, case_id):
        num = 0
        cols_data = self.get_cols_data()
        for col_data in cols_data:
            if case_id in col_data:
                return num
            num = num + 1

    # 根据行号找到该行内容
    def get_row_values(self, row):
        tables = self.data
        row_list=[]
        if not tables in([],None):
            for table in tables:
                try:
                    row_data = table.row_values(row)
                    row_list.append(row_data)
                except IndexError as error:
                    pass
            return row_list
        else:
            print("当前路径没有可运行的excle文件")

    # 获取某一列的内容
    def get_cols_data(self, col_id = None):
        cols_list=[]
        datas=self.data
        if col_id != None:
            for col in datas:
                cols = col.col_value(col_id)
                cols_list.append(cols)
        else:
            for col in datas:
                cols = col.col_value(0)
                cols_list.append(cols)
        return cols_list

if __name__=="__main__":
    op=OperationExcleBatch()
    # print(op.get_data())
    # print(op.get_lines())
    # print(op.get_cell_value(3,1))
    # print(op.get_row_values(5))
    # print(op.get_data())
    print(op.write_value(0,11,'test5'))
    # print(op.get_cell_valueBatch(4,4))
    # print(op.get_sheet())
    # print(op.clear_data())