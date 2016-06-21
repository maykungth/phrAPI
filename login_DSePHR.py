#!/usr/bin/python
import requests
import json
from time import sleep
from requests.packages import urllib3
urllib3.disable_warnings()

# This files is to login to DSePHR and get token key for use in client.

user_pass={'user':'system1@example.com','pass':'system1'}
cert_path='/home/hduser/workspace/sslcert/ssl_DSePHR.crt'

r = requests.post('https://master:50000/login', data=json.dumps({'email':user_pass['user'],
'password':user_pass['pass']}), headers={'content-type': 'application/json'},verify=cert_path)

tokenkey = r.json()['response']['user']['authentication_token']
print 'user : %s \ntokenkey : %s'%(user_pass['user'],tokenkey)


payload = {'sysid':'s3','userid':'u1234'}
f = open('tmpfile.txt', 'rb')
files = {'file': f}
res = requests.post('https://master:50000/upload', headers={'Authentication-Token':tokenkey},
                                    files=files,data=payload, verify=cert_path)

# res = requests.post('http://master:50000/upload',files=files,data=payload)

# for i in range(1,20):
#     rg = requests.get('https://master:50000/account',headers={'Authentication-Token':tokenkey},verify=cert_path)
#     print rg.text

print res.json()


