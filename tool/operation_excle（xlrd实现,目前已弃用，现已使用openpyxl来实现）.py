# xlrd，xlwt和xlutils是用Python处理Excel文档(*.xls)的高效率工具。其中，
# xlrd只能读取xls，xlwt只能新建xls（不可以修改），
# xlutils能将xlrd.Book转为xlwt.Workbook，从而得以在现有xls的基础上修改数据，
# 并创建一个新的xls，实现修改
import xlrd
from xlutils.copy import copy  # 导入xlutils模块实现对exlcle的修改
import os
from tool.MergeAllTestCase import OperationDataCase


class OperationExcle():
    def __init__(self, file_address=None, sheet_id=None):
        self.testCase=OperationDataCase()
        if file_address is not None:
            self.file_address=file_address
            self.sheet_id=sheet_id
        else:
            self.file_address='../dataCase/DataCase_ALL.xlsx'
            self.sheet_id=0

        self.data = self.get_data()
    # 获取sheets的内容
    def get_data(self):
        data = xlrd.open_workbook(self.file_address)
        tables = data.sheets()[self.sheet_id]
        return tables

    # 获取单元格的行数
    def get_lines(self):
        tables = self.data
        return tables.nrows

    # 获取某一个单元格的内容
    def get_cell_value(self, row, col):
        return self.data.cell_value(row, col)
        # print(row,col)
        # 根据行列返回表单内容

    # 写入数据
    def write_value(self, row, col, value):
        '''写入excle数据row，col，value'''
        read_data = xlrd.open_workbook(self.file_address)
        write_data = copy(read_data)
        sheet_data = write_data.get_sheet(0)
        sheet_data.write(row, col, value)
        write_data.save(self.file_address)

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
            if case_id == col_data:
                return num
            num = num + 1

    # 根据行号找到该行内容
    def get_row_values(self, row):
        tables = self.data
        row_data = tables.row_values(row)
        return row_data

    # 获取某一列的内容
    def get_cols_data(self, col_id: object = None) -> object:
        if col_id != None:
            cols = self.data.col_values(col_id)
        else:
            cols = self.data.col_values(0)
        return cols


if __name__ == '__main__':
    opers = OperationExcle()
    # print(opers.get_cell_value(1, 1))
    opers.get_row_num(3)
    # print(opers.get_cols_data())