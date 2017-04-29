__author__ = 'Maykungth'
# Date 18/8/2558

from flask import request, send_from_directory, make_response
from flask_restful import Resource
from flask_security import auth_token_required, current_user
from werkzeug import secure_filename
from phr_api import apirest, encrypted_data_man, app, metadata_man
from phr_api import logFormatter,rootLogger, consoleHandler

from threading import Thread
import threading
import os, timeit,sys
import time

upload_queue = []
upload_tasks = []

class UploadMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.upload_task_size = 10
        #self.upload_tasks = []
        self.running = True
    def stop(self):
        self.running = False
    def run(self):
        while self.running:
            remove_tasks = []
            for dict_t in upload_tasks:
                if not dict_t['thr'].is_alive():
                    dict_t['thr'].join()
                    remove_tasks.append(dict_t)
            for dict_t in remove_tasks:
                upload_tasks.remove(dict_t)
            while len(upload_tasks) < self.upload_task_size and len(upload_queue) > 0:
                args = upload_queue.pop(0)
                t = Thread(target=saveThreading, args=(args['path'], args['metadata']))
                t.start()
                name = "{}-{}".format(args['metadata']['filename'],args['metadata']['dataid'])
                dict_t = dict(name=name,thr=t)
                upload_tasks.append(dict_t)
            time.sleep(0.05)

def saveThreading(path,metadata):
    numtry = 0
    while numtry <= 5:
        try :
            # start captured time here
            start = timeit.default_timer()
            encrypted_data_man.saveToStore(path,metadata)
            time_save_to_store = timeit.default_timer() - start
            # end captured time
            os.remove(path)
            # print time to upload to store.
            # filename, rowkey, time, size
            rootLogger.info("write,{},{},sec:{:.3f},size:{}".format(metadata['filename'],metadata['rowkey'],time_save_to_store,metadata['size']))
            break
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            rootLogger.error("e {} {} {} {}".format(path,exc_type, fname, exc_tb.tb_lineno))
        numtry += 1
def create_monitor_upload():
    # Create monitor thread
    up = UploadMonitor()
    up.start()
    return up

class Upload(Resource):
    #@auth_token_required
    def post(self):
        file = request.files['file']
        formdata = request.form
        filename = secure_filename(request.files['file'].filename )
        path = os.path.join(app.config['UPLOAD_FOLDER'], formdata['userid']+'-'+formdata['sysid']+'-'+filename)
        file.save(path)
        metadata = metadata_man.genMeta(path,formdata,filename)
        upload_queue_str = ""
        upload_queue.append(dict(path=path, metadata=metadata))
        # show queue
        for dict_t in upload_tasks:
            upload_queue_str += "{};".format(dict_t['name'])
        for x in upload_queue:
            upload_queue_str += "{}-{};".format(x['metadata']['filename'],x['metadata']['dataid'])
        # show queue 
        rootLogger.info("queue_up,queue:{},{}".format(len(upload_queue)+len(upload_tasks),upload_queue_str))

        return metadata


class Download(Resource):
    #@auth_token_required
    def get(self,data_id):
        startget = timeit.default_timer()
        meta= metadata_man.getMeta(data_id)
        if meta != None:
            start = timeit.default_timer()
            file = encrypted_data_man.getFromStore(meta,data_id)
            stop = timeit.default_timer()
            # app.logger.debug('Time to getEncryptedData %f'%(float(stop-start)))
            res = make_response(file)
            res.headers['Content-Type'] = 'application/octet-stream'
            res.headers['Content-Disposition'] = 'attachment; filename="%s"' % meta['filename']
        else:
            return {'Message':'File not found'}
        stopget = timeit.default_timer()
        # app.logger.debug('Time to Download data %f'%(float(stopget-startget)))
        return res


class Index(Resource):
    def get(self):
        return {'message':'It is Work by Maykungth'}


class Search(Resource):
    def post(self):
        if 'userid' and 'sysid' in request.form.keys():
            #app.logger.debug('You send : '+ str(request.form))
            return metadata_man.searchMeta(request.form)
        return {'Message': 'Please specify the userid and sysid' , 'You send': request.form.keys()}

class EncData(Resource):
    def get(self,data_id):
        # get metadata from data_id
        meta = metadata_man.getMeta(data_id)
        if meta != None:
            return meta
        else:
            return {'Message': 'File not found'}
    def post(self,data_id):
        # update encrypted data
        return {}

    def put(self,data_id):
        # update the metadata by data_id
        # Can update only filename, description
        meta = metadata_man.getMeta(data_id)
        if meta == None:
            return {'Message': 'File not found'}
        formdata = request.form
        metadata_man.updateMeta(data_id,formdata)
        return metadata_man.getMeta(data_id) # return current Metadata in HBase

    def delete(self,data_id):
        # delete the enc data and metadata
        meta = metadata_man.getMeta(data_id)
        if meta != None:
            encrypted_data_man.delFromStore(meta, data_id)
            metadata_man.delMeta(data_id)
        else:
            return {'Message': 'File not found'}
        return {'Message': 'File %s deleted'%(data_id)}

@app.route('/account', methods=['GET'])
@auth_token_required
def account():
    return current_user.email #return current user

def addroute():
    apirest.add_resource(Upload, '/upload')
    apirest.add_resource(Download, '/download/<string:data_id>')
    apirest.add_resource(Index,'/')
    apirest.add_resource(Search,'/search')
    apirest.add_resource(EncData,'/encdata/<string:data_id>')

