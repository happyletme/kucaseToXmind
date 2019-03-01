from kucase import Kucase
from xmindJson import Xmind
#kucase到xmind
def generateXmind(startnode,starttitle):
    kucase = Kucase()
    loginresult = kucase.login()
    if loginresult == 1:
        # 各个节点下的目录数据
        topicsdatalist=kucase.kucaseToDict(startnode,starttitle,{})
        #print (topicsdatalist)
        # 清洗目录数据
        topicsdatadic=kucase.clear_data(topicsdatalist,startnode)
        # 如果这是个字典和数组就循环遍历，如果没有topics，就当成用例去遍历步骤
        kucase.assembly_casestep(topicsdatadic)
        data=[{'title': '生成的xmind', 'topic': {'title': startnode+'|'+starttitle}}]
        data[0]['topic']['topics']=topicsdatadic['topics']
        return (data)

#kucase到xmind入口
xmindjson=Xmind()
data=generateXmind("93761","08 导入测试目录")
#print (data)
xmindjson.dictToXmind(data[0]['topic']['topics'], data[0]['title'],data[0]['topic']['title'], path="./xmind")