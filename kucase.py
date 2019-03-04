import requests,json,base64,time,datetime,re,copy
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar
import xmindJson
from Config import ConfigParameter
#!/usr/bin/python
#-*- encoding:utf-8 -*-

class Kucase(ConfigParameter):
    def __init__(self):
        ConfigParameter.__init__(self)
        self.myself={"username":self.kucase_usname,"password":self.kucase_password}
        self.s = requests.session()
        self.s.cookies = CookieJar()
        #控制清洗步骤单次
        self.nodelist=[]
    def login(self):
        url = self.kucase_host+"/login.php"
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        params = {"user": self.myself['username'], "passwd": base64.b64decode(self.myself['password']).decode(), "testproject": 79, "project_group": 3,
                  "action": "switchProject", "reqURI": ""}
        self.loginresponse = self.s.post(url, data=params, headers=headers)
        soup = BeautifulSoup(self.loginresponse.text)
        if (BeautifulSoup(self.loginresponse.text).script.text=="location.href='"+self.kucase_host+"/kucase.php';"):
            code=1
            print ("登录成功")
        else:
            code = 0
            print("登录失败")
        return code
    def get_next_node(self,node):
        try:
            nextnode=[]
            url = self.kucase_host+'/lib/ajax/gettprojectnodes.php'
            params={"node": node}
            response = self.s.post(url, cookies=self.loginresponse.cookies,params=params)
            jsonobj=json.loads(response.text)
            for i in jsonobj:
                nextnodeone = {}
                nextnodeone['id']=i['id']
                nextnodeone['tlNodeType'] = i['tlNodeType']
                nextnodeone['position'] = i['position']
                nextnodeone['text']=re.compile(r'<[^>]+>', re.S).sub('', i['text'])
                nextnode.append(nextnodeone)

            return nextnode
        except:
            pass
            #print("获取下层数据失败")

    #各个节点下的目录数据
    def kucaseToDict(self,node,title,topicsdatalist):
        topicsdata={'topics':[]}
        nextnodedata=self.get_next_node(node)
        #print (nextnodedata)
        if nextnodedata:
            for dict in nextnodedata:
                title=dict['id']+'|'+dict['text']
                NodeType=dict['tlNodeType']
                if NodeType=="testcase" or NodeType == "testsuite":
                    topicsdata['topics'].append({'title':title,'labels':NodeType})
                if NodeType == "testsuite":
                    self.kucaseToDict(dict['id'],title,topicsdatalist)
            #newopicsdata= oldopicsdata['topics']
            #print (node)
            #print (topicsdata)
            #topicsdatalist.append(topicsdata)
            topicsdatalist[node]=topicsdata
            #print(topicsdatalist)
        return topicsdatalist

        #print (nextnodedata)

    #清洗目录数据
    def clear_data(self,topicsdatalist,startnode):
        for node in topicsdatalist.keys():
            #print (node)
            for othernode in topicsdatalist.keys():
                #去除自己的节点
                if node!=othernode:
                    for titleCount in range(len(topicsdatalist[othernode]['topics'])):
                        nodetitle=topicsdatalist[othernode]['topics'][titleCount]['title'].split('|')[0]
                        #当找到上级节点
                        if nodetitle==node and topicsdatalist[node]['topics']:
                            topicsdatalist[othernode]['topics'][titleCount]['topics']=topicsdatalist[node]['topics']

        return topicsdatalist[startnode]

    #解析html
    def solve_html(self,soup,Attributes):
        List=[]
        Soupobj = soup.find_all('td', attrs={"class": "clickable ui-widget-content",
                                                        "ondblclick": re.compile(Attributes)})
        for i in Soupobj:
            #print (i.find('div'))
            labellist = i.find('div').find_all('p')
            if labellist:
                for j in range(len(labellist)):
                    labellist[j] = labellist[j].text
                message = '\r\n'.join(labellist)
            elif i.find('div').find_all('br'):
                strhtml = str(i.find('div')).replace('<br/>','\r\n')
                message=BeautifulSoup(strhtml).text
                #message=i.find('div').text
            else:
                message=i.find('div').text
            #去除多余的换行
            message = re.sub(r'(\r\n)+', "\r\n", message)
            #去除尾部的换行
            if message[-2:] == "\r\n":
                message = message[0:-2]
            List.append(message)
        return List
    #得到单节点步骤数据
    def get_stepdata(self,testcaseid):
        actionsList=[]
        expected_resultsList=[]
        teststepdic={}
        teststeplist=[]
        url = self.kucase_host+'/lib/testcases/editTestCases.php'
        params = {"edit": "testcase","id":testcaseid}
        response = self.s.get(url, cookies=self.loginresponse.cookies, params=params)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text)
        #id列表
        ListTeststepId = []
        Soupobjlist = soup.find_all('td', attrs={"class": "clickable ui-widget-content",
                                             "ondblclick": re.compile('actions')})
        for Soupobj in Soupobjlist:
            ListTeststepId.append(Soupobj.attrs['ondblclick'].split('\'')[1])
        #步骤列表
        actionsList=self.solve_html(soup,'actions')
        #预期结果列表
        expected_resultsList=self.solve_html(soup,'expected_results')
        for i in range(len(actionsList)):
            teststepdic['title']=actionsList[i]
            teststepdic['note'] = expected_resultsList[i]
            teststepdic['TeststepId'] = ListTeststepId[i]
            teststeplist.append(copy.copy(teststepdic))
        return (teststeplist)

     #如果这是个字典和数组就循环遍历，如果没有topics，就当成用例去遍历步骤
    def assembly_casestep(self,topicsdata):
        if isinstance(topicsdata,dict):
            try:
                topicsdata=topicsdata['topics']
                self.assembly_casestep(topicsdata)
            except:
                if topicsdata['labels'] == "testcase":
                    teststeplist=self.get_stepdata(topicsdata['title'].split('|')[0])
                    if teststeplist:
                        topicsdata['topics']=teststeplist
                    else:
                        topicsdata['topics'] =[{"title":"","note":""}]
        elif isinstance(topicsdata,list):
            for i in topicsdata:
                self.assembly_casestep(i)

    #编辑目录或者用例
    def edit_kucaseSuiteCase(self,node,title,node_type):
        url = self.kucase_host+"/lib/ajax/ajaxChangeNodeName.php"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        params = {"node_id": node,
                  "node_name": title, "node_type": node_type}
        response = self.s.post(url, cookies=self.loginresponse.cookies, params=params)
        jsonobj = json.loads(response.text)
        if jsonobj['success']:
            print ("节点"+node+"内容变更为'"+title+"'")
        else:
            print("节点" + node+"修改失败")

    # 新增目录或者用例
    def add_kucaseSuiteCase(self, previousNode, title, node_type):
        url = self.kucase_host+"/lib/ajax/ajaxCreateNode.php"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        params = {"container_id": previousNode,
                  "node_name": title, "node_type": node_type}
        response = self.s.post(url, cookies=self.loginresponse.cookies, params=params)
        jsonobj = json.loads(response.text)
        if jsonobj['id']:
            print("节点" + jsonobj['id'] + "创建内容为'" + title + "'")
            return jsonobj['id']
        else:
            print("节点" + jsonobj['id'] + "创建失败")

    #新增步骤
    def add_kucaseTeststep(self,node,add_steps,expected_results):
        url = self.kucase_host+"/lib/ajax/testcases/ajaxAddTCaseStep.php"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        params = {"tcversion_id": node,"tcstep_number":-1,"add_steps":add_steps.replace('\n',"<br />")+"<br />","expected_results":expected_results.replace('\n',"<br />")}
        response = self.s.post(url, cookies=self.loginresponse.cookies, params=params)
        print ("用例节点"+node+"下新增步骤："+add_steps+";新增预期："+expected_results)

    #删除步骤
    def delete_kucaseTeststep(self,node):
        if node not in self.nodelist:
            self.nodelist.append(node)
            #查找用例下的所有步骤节点
            teststeplist=self.get_stepdata(node)
            #删除所有步骤节点
            for teststep in teststeplist:
                url = self.kucase_host+'/lib/ajax/testcases/ajaxDeleteTCaseStep.php'
                params = {"tc_step_id": teststep['TeststepId']}
                response = self.s.get(url, cookies=self.loginresponse.cookies, params=params)
            print("删除用例节点："+node+"下删除步骤数据")

    # 插入nodetype
    def insert_nodetype(self, topicsdata):
        if isinstance(topicsdata, dict):
            # 如果是teststep
            if 'note' in topicsdata:
                topicsdata['nodetype']="teststep"
            # 如果是testcase
            elif 'topics' in topicsdata:
                try:
                    # 先填testsuite
                    topicsdata['nodetype'] = "testsuite"
                    #然后遍历，如果遇到下个note节点，则改写nodetype为testcase
                    for topicsdic in topicsdata['topics']:
                        if '|' in topicsdata['title']:
                            topicsdic['previousId'] = topicsdata['title'].split('|')[0]
                        if 'note' in topicsdic:
                            topicsdata['nodetype']="testcase"
                except:
                    pass
            # 如果是testsuite
            else:
                topicsdata['nodetype'] = "testsuite"
            #递归
            try:
                topicsdata = topicsdata['topics']
                self.insert_nodetype(topicsdata)
            except:
                pass
        # 递归
        elif isinstance(topicsdata, list):
            for i in topicsdata:
                self.insert_nodetype(i)

    #生成kucase数据
    def carry_Kucasedata(self, topicsdata):
        if isinstance(topicsdata, dict):
            # 如果是teststep
            if topicsdata['nodetype'] == "teststep" and ("title" in topicsdata):
                node=topicsdata['previousId']
                #删除步骤
                self.delete_kucaseTeststep(node)
                #新增步骤
                self.add_kucaseTeststep(str(int(node)+1), topicsdata['title'],topicsdata['note'])
            #如果是testcase
            elif topicsdata['nodetype'] == "testcase":
                # 编辑节点
                if '|' in topicsdata['title']:
                    self.edit_kucaseSuiteCase(topicsdata['title'].split('|')[0], topicsdata['title'].split('|')[1],
                                              'testcase')
                # 新增节点
                else:
                    previousId = self.add_kucaseSuiteCase(topicsdata['previousId'], topicsdata['title'], 'testcase')
                    #回填下个节点的previousId
                    if 'topics' in topicsdata:
                        for topicsdic in topicsdata['topics']:
                            topicsdic['previousId']=previousId
            # 如果是testsuite
            elif topicsdata['nodetype'] == "testsuite":
                # 编辑节点
                if '|' in topicsdata['title']:
                    self.edit_kucaseSuiteCase(topicsdata['title'].split('|')[0],
                                              topicsdata['title'].split('|')[1],
                                              'testsuite')
                # 新增节点
                else:
                    previousId = self.add_kucaseSuiteCase(topicsdata['previousId'], topicsdata['title'],
                                                          'testsuite')
                    # 回填下个节点的previousId
                    if 'topics' in topicsdata:
                        for topicsdic in topicsdata['topics']:
                            topicsdic['previousId'] = previousId
            #递归
            try:
                topicsdata = topicsdata['topics']
                self.carry_Kucasedata(topicsdata)
            except:
                pass
        # 递归
        elif isinstance(topicsdata, list):
            for i in topicsdata:
                self.carry_Kucasedata(i)
