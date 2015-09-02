__author__ = 'Maykungth'
#date 18/8/2558
# Gernerating, save, searching metadata
import os
import time, uuid, hashlib,sha3
import happybase
from phr_api import Master,MasterHbase, HDFSMainPath, largeSize, app
import timeit

def genMeta(path, formdata):
    start = timeit.default_timer()

    size = os.path.getsize(path)
    filename = os.path.basename(path)
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
    con = happybase.Connection(MasterHbase)
    con.open()
    meta_table = con.table('MetaTable')
    meta_row = meta_table.row(str(data_id))
    con.close()
    if meta_row == {}:
        return None
    return meta_row

def searchMeta(meta):
    pass
