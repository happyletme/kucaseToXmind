import base64
kucase_password="123456" #原始密码
print (str(base64.b64encode(kucase_password.encode('utf-8')))) #加密后密码

#example
'''
kucase_password="123456"
output:b'MTIzNDU2'
将MTIzNDU2填入Config文件的ConfigParameter类的kucase_password
'''