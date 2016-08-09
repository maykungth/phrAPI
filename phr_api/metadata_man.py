__author__ = 'Maykungth'
#date 18/8/2558
# Gernerating, save, searching metadata
import os
import time, uuid, hashlib,sha3
import happybase
from phr_api import Master,MasterHbase, HDFSMainPath, largeSize, app
import timeit

def genMeta(path, formdata,filename):
    start = timeit.default_timer()

    size = os.path.getsize(path)
    #filename = os.path.basename(path)
    dataid = str(uuid.uuid4())
    checksum = hashlib.new("sha3_256")
    checksum = hashlib.sha3_256()
    with open(path, 'rb') as f:
        checksum.update(f.read())
        f.close()
    if 'timestamp' in formdata.keys():
        timestamp = formdata['timestamp']
    else:
        timestamp = str(int(time.time()))
    if 'often' in formdata.keys():
        often = 'true'
    else:
        often = 'false'
    if 'description' in formdata.keys():
        description = formdata['description']
    else:
        description = ''
    rowkey = formdata['sysid']+'-'+formdata['userid']+'-'+timestamp+'-'+dataid
    stop=timeit.default_timer()
    app.logger.debug('Time to genMeta is %f' % (stop-start))
    return {
        'sysid': formdata['sysid'],
        'userid': formdata['userid'],
        'timestamp': timestamp,
        'dataid': dataid,
        'filename': filename,
        'size': size,
        'checksum': checksum.hexdigest(),
        'rowkey': rowkey,
        'often': often,
        'description': description,
    }

def getMeta(data_id):
    start = timeit.default_timer()
    con = happybase.Connection(MasterHbase)

    con.open()
    meta_table = con.table('MetaTable')
    meta_row = meta_table.row(str(data_id))
    con.close()
    stop = timeit.default_timer()
    app.logger.debug('Time to getMeta %f'%(float(stop-start)))
    if meta_row == {}:
        return None
    return {'filename':meta_row['pp:name'],'checksum':meta_row['pp:checksum'],'size':meta_row['pp:size'],
            'description':meta_row['pp:des']}

def searchMeta(formdata):
    con = happybase.Connection(MasterHbase)
    con.open()
    meta_table = con.table('MetaTable')
    meta=[{'Total':0}]

    if 'starttime' in formdata and 'endtime' in formdata:
        print("startttttt end endddd")
        rowstart = str(formdata['sysid']) + '-' + str(formdata['userid'])+'-' + str(formdata['starttime']) + '-'
        rowend = str(formdata['sysid']) + '-' + str(formdata['userid'])+'-'+str(int(formdata['endtime'])+1) + '-'
        for key, data in meta_table.scan(row_start=rowstart,row_stop=rowend):
            meta[0]['Total'] += 1
            meta.append({key: data})

    elif 'starttime' in formdata:
        print "startttt"
        rowstart=str(formdata['sysid']) + '-' + str(formdata['userid'])+'-' +str(formdata['starttime']) + '-'
        rowend=str(formdata['sysid']) + '-' + str(formdata['userid'])+'-x'
        for key, data in meta_table.scan(row_start=rowstart, row_stop=rowend):
            meta[0]['Total'] += 1
            meta.append({key: data})

    elif 'endtime' in formdata:
        rowstart = str(formdata['sysid']) + '-' + str(formdata['userid'])+'-'
        rowend = str(formdata['sysid']) + '-' + str(formdata['userid'])+'-'+str(int(formdata['endtime'])+1) + '-'
        print "Enddddddd"
        for key, data in meta_table.scan(row_start=rowstart, row_stop=rowend):
            meta[0]['Total'] += 1
            meta.append({key: data})
    else:
        print("NOneeeee")
        for key,data in meta_table.scan(row_prefix=str(formdata['sysid']) + '-' + str(formdata['userid'])+'-'):
            meta[0]['Total'] += 1
            meta.append({key: data})
    con.close()

    return meta

def delMeta(data_id):
    con = happybase.Connection(MasterHbase)
    con.open()
    meta_table = con.table('MetaTable')
    meta_table.delete(str(data_id))
    con.close()
    return True

def updateMeta(data_id,formdata):
    # Can update only filename, description and timestamp
    con = happybase.Connection(MasterHbase)
    con.open()
    metaTable = con.table('MetaTable')

    if 'filename' in formdata.keys():
        metaTable.put(data_id,{'pp:name': str(formdata['filename'])})
    if 'description' in formdata.keys():
        metaTable.put(data_id,{'pp:des': str(formdata['description'])})

