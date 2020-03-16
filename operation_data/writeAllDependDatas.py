from operation_data.get_data import GetData
from operation_data.dependent import DependentData
# 执行用例先调用此方法完成所有的数据依赖处理
def write_dependField(row):
    Gd=GetData()
    depend_case_id = Gd.is_depend(row)
    if depend_case_id:
        depend = DependentData(depend_case_id)
        # 获取依赖key
        Gd.get_depent_key(row)
        # 将依赖数据写入请求数据
        flag=depend.writeDependRequestDataToExcle(row)
        return flag
    else:
        return False

def write_dependSql(row):
    Gd = GetData()
    falg=Gd.get_sqlExecuteResult(row)
    if falg:
        execute_result = Gd.write_sqlExecuteResultToRequestData(row)
        return execute_result
    else:
        return False

def write_excle():
    Gd = GetData()
    row=Gd.get_case_line()
    # for i in range(2,row+1):
    for i in range(16,16+1):
        caseid = Gd.get_caseId(i)
        if caseid:
            falg=write_dependField(i)
            # print(falg)
            if not falg:
                write_dependSql(i)
        

if __name__=='__main__':
    write_excle()