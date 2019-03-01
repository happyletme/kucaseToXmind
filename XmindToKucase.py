from kucase import Kucase
from xmindJson import Xmind
#xmind到kucase
def generateKucase(outdata):
    kucase = Kucase()
    loginresult = kucase.login()
    if loginresult == 1:
        kucase.insert_nodetype(outdata[0]['topic'])
        #print (outdata)
        kucase.carry_Kucasedata(outdata[0]['topic'])


#xmind到kucase入口
xmindjson=Xmind()
outdata=xmindjson.xmindToDict("生成的xmind")
generateKucase(outdata)