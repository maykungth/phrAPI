__author__ = 'Maykungth'
# Date 18/8/2558
from pywebhdfs.webhdfs import PyWebHdfsClient
import happybase
from phr_api import Master,MasterHbase, HDFSMainPath, largeSize, app
import os

def saveToStore(path,meta):
    con=happybase.Connection(MasterHbase)
    con.open()
    metaTable= con.table('MetaTable')
    if meta['size'] < largeSize:
        # save to Hbase
        encTable = con.table('EncTable')
        with open(path,'rb') as f:
            encTable.put(meta['rowkey'],{'enc:data': f.read()})
        metaTable.put(str(meta['rowkey']),{
                'pp:name': str(meta['filename']),
                'pp:checksum': str(meta['checksum']),
                'pp:size': str(meta['size']),
                'pp:often': str(meta['often']),
                'pp:des': str(meta['description'])
                }
              )
        app.logger.debug('%s is saved to Hbase', meta['rowkey'])
    else:
        # save to HDFS
        hdfs = PyWebHdfsClient(host=Master,port='50070', timeout=None,user_name='hduser')
        with open(path, 'rb') as f:
            hdfs.create_file(HDFSMainPath+meta['rowkey'], f)
        metaTable.put(str(meta['rowkey']),{
                'pp:name': str(meta['filename']),
                'pp:checksum': str(meta['checksum']),
                'pp:size': str(meta['size']),
                'pp:HDFSpath': str(HDFSMainPath + meta['rowkey']),
                'pp:often': str(meta['often']),
                'pp:des': str(meta['description'])
                }
              )
        app.logger.debug('%s is saved to HDFS', meta['rowkey'])
    con.close()

def getFromStore(meta,rowkey):
    if 'pp:HDFSpath' in meta.keys():
        # retrieve from HDFS
        hdfs = PyWebHdfsClient(host=Master,port='50070', timeout=None,user_name='hduser')
        file = hdfs.read_file(meta['pp:HDFSpath'])
        app.logger.debug(">> READ from HDFS %s",type(file))
        return file
    else:
        #retrieve from Hbase
        con=happybase.Connection(MasterHbase)
        con.open()
        enc_table = con.table('EncTable')
        row_enc = enc_table.row(rowkey)
        con.close()
        app.logger.debug(">> READ from Hbase %s",type(row_enc['enc:data']))
        return row_enc['enc:data']

def delFromStore(meta,rowkey):
    if 'pp:HDFSpath' in meta.keys():
        # the data persist in HDFS
        hdfs = PyWebHdfsClient(host=Master,port='50070', timeout=None,user_name='hduser')
        hdfs.delete_file_dir(meta['pp:HDFSpath'])
        app.logger.debug(">> DELETE from HDFS %s",meta['pp:HDFSpath'])
        return True
    else:
        # the data persist in HBase
        con = happybase.Connection(MasterHbase)
        con.open()
        enc_table = con.table('EncTable')
        enc_table.delete(rowkey)
        con.close()
        app.logger.debug(">> DELETE from HBase %s",rowkey)
        return True



