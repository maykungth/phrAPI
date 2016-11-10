__author__ = 'Maykungth'
# Date 18/8/2558

from flask import request, send_from_directory, make_response
from flask_restful import Resource
from flask_security import auth_token_required, current_user
from werkzeug import secure_filename
from phr_api import apirest, encrypted_data_man, app, metadata_man
from threading import Thread
import os, timeit,sys
import time

upload_queue = []


class UploadMonitor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.upload_task_size = 10
        self.upload_tasks = []

        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            remove_tasks = []
            for t in self.upload_tasks:
                if not t.is_alive():
                    t.join()
                    remove_tasks.append(t)

            for t in remove_tasks:
                self.upload_tasks.remove(t)

            while len(self.upload_tasks) < self.upload_task_size and len(upload_queue) > 0:
                args = upload_queue.pop(0)
                t = Thread(target=saveThreading, args=(args['path'], args['metadata']))
                t.start()

                self.upload_tasks.append(t)

            time.sleep(0.1)



def saveThreading(path,metadata):
    numtry = 0
    while numtry <= 5:
        try :
            encrypted_data_man.saveToStore(path,metadata)
            os.remove(path)
            app.logger.debug("Write and Clear {}".format(metadata['rowkey']))
            break
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            app.logger.error("e {} {} {} {}".format(path,exc_type, fname, exc_tb.tb_lineno))
        numtry += 1

class Upload(Resource):
    @auth_token_required
    def post(self):
        file = request.files['file']
        formdata = request.form
        filename = secure_filename(request.files['file'].filename )
        path = os.path.join(app.config['UPLOAD_FOLDER'], formdata['userid']+'-'+filename)
        file.save(path)
        app.logger.debug('Caching  %s', path)

        metadata = metadata_man.genMeta(path,formdata,filename)

        # Move this part to threading
        # t= Thread(target=saveThreading, args=(path,metadata))
        # t.start()
        upload_queue.append(dict(path=path, metadata=metadata))
        # encrypted_data_man.saveToStore(path,metadata)
        # os.remove(path)
        # app.logger.debug('Cache is deleteed !')
        return metadata


class Download(Resource):
    @auth_token_required
    def get(self,data_id):
        app.logger.debug('Get Request for download %s'%(data_id))
        startget = timeit.default_timer()
        meta= metadata_man.getMeta(data_id)
        if meta != None:
            start = timeit.default_timer()
            file = encrypted_data_man.getFromStore(meta,data_id)
            stop = timeit.default_timer()
            app.logger.debug('Time to getEncryptedData %f'%(float(stop-start)))
            res = make_response(file)
            res.headers['Content-Type'] = 'application/octet-stream'
            res.headers['Content-Disposition'] = 'attachment; filename="%s"' % meta['filename']
        else:
            return {'Message':'File not found'}
        stopget = timeit.default_timer()
        app.logger.debug('Time to Download data %f'%(float(stopget-startget)))
        return res
        # return send_from_directory(app.config['UPLOAD_FOLDER'], meta['pp:name'],as_attachment=True)


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

