import xmind,os
from xmindparser import xmind_to_dict

class Xmind:
    def dict_ite(self,dictslist, topic):
        for dicts in dictslist:
            subtopic = topic.addSubTopic()
        # Create a topic with key
            try:
                subtopic.setTitle(dicts['title'])
            except:
                pass
            try:
                subtopic.setPlainNotes(dicts['note'])
            except:
                pass
            if 'topics' in dicts:
                self.dict_ite(dicts['topics'], subtopic)
        return True

    def dictToXmind(self,dictslist, filename,startnodemessage, path):
        file_str = path + "/" +filename+".xmind"
        # 先删除文件
        if os.path.exists(file_str):
            os.remove(file_str)
        workbook = xmind.load(file_str) # load an existing file or create a new workbook if nothing is found

        sheet = workbook.getPrimarySheet() # get the first sheet
        sheet.setTitle(filename) # set its title
        rtopic_sheet = sheet.getRootTopic() # get the root topic of this sheet
        #中心
        rtopic_sheet.setTitle(startnodemessage) # set its title

        if self.dict_ite(dictslist, rtopic_sheet):
            xmind.save(workbook, file_str)
            pass
            return True
        else:
            return False

    def xmindToDict(self,filename):
        file_str = "./xmind/" + "/" + filename + ".xmind"
        if os.path.exists(file_str):
            out = xmind_to_dict(file_str)
        else:
            out=None
        return out

#xmindjson=Xmind()

'''
data=[{'title': '生成的xmind', 'topic': {'title': '93761|08 导入测试目录', 'topics': [{'title': '93762|0801 目录1', 'topics': [{'title': '93764|080101 二级目录', 'topics': [{'title': '93887|080101用例', 'topics': [{'title': '234', 'note': '234'}, {'title': '123', 'note': '567'}]}, {'title': '93891|080102 用例'}]}]}, {'title': '93763|0802 目录2'}]}, 'structure': 'org.xmind.ui.map.unbalanced'}]
xmindjson.dictToXmind(data[0]['topic']['topics'], data[0]['title'],data[0]['topic']['title'], path="./xmind")
'''
#[{'title': '生成的xmind', 'topic': {'title': '93761|08 导入测试目录', 'topics': [{'title': '93762|0801 目录1', 'topics': [{'title': '93764|080101 二级目录', 'topics': [{'title': '93887|080101用例', 'topics': [{'title': '234', 'note': '234'}, {'title': '123', 'note': '567'}]}, {'title': '93891|080102 用例'}]}]}, {'title': '93763|0802 目录2'}]}}]
'''
out=xmindjson.xmindToDict("生成的xmind")
print (out)
'''
