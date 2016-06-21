__author__ = 'Maykungth'
#26/8/2558
# This file is a test upload file to Hbase
import requests
import datetime
import glob
import time, os
from random import randint
from time import sleep
from requests.packages import urllib3
urllib3.disable_warnings()

user_pass={'user':'system1@example.com','pass':'system1'}
cert_path='/home/hduser/workspace/sslcert/ssl_DSePHR.crt'

r = requests.post('https://master:50000/login', data=json.dumps({'email':user_pass['user'],
'password':user_pass['pass']}), headers={'content-type': 'application/json'},verify=cert_path)
tokenkey = r.json()['response']['user']['authentication_token']

parent_dir = str(os.path.dirname(os.path.abspath(__file__)).rsplit('/',1)[0])
def printlog(strr):
    strr=str(strr)
    strr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': ' + strr
    print strr
    fpt=open(parent_dir + '/flush.log','a')
    fpt.write(strr+'\n')
    fpt.close()
#os.path.dirname(os.path.abspath(__file__))
path= parent_dir + '/enc_files/*.*'
#path = '../enc_files/*.*'

start_time = time.time()
listfile = glob.glob(path)
# don't forgive to divide 12,  456 for each client

for i in range(1,2):
    if i % 100 == 0:
        listfile.append(str(parent_dir + '/enc_files/big/12videobig.mp4'))
    if (i-1) % 100 ==0:
        listfile = glob.glob(path)
    for filepath in listfile:
    	sysid='s3'
    	userid=randint(1500,5000)
        userid= 'u'+ str(userid)
        payload = {'sysid':sysid,'userid':userid}
        f = open(filepath, 'rb')
        files = {'file': f}
        numtry = 0
        while numtry < 20:
            try:
                res = requests.post('https://master:50000/upload', headers={'Authentication-Token':tokenkey},
                                    files=files,data=payload, verify=cert_path)
                break
            except requests.exceptions.RequestException as e:
                print "ERROR: {}".format(e)
                printlog("ERROR: {}".format(e))
                numtry+=1
                sleep(5)
            except:
                print "ERROR: Unknown Error"
                printlog("ERROR: Unknown Error")
                numtry+=1
                sleep(5)
        f.close()
        log = dict(res.json())
        printlog('i=%d, file = %s'%(i,str(filepath.rsplit('/',1)[1])))
        printlog(log['rowkey'])
total_time = "Total runtime : " + str(time.time()-start_time) + " sec"
print total_time
printlog(total_time)

