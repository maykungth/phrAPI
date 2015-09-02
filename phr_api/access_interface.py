__author__ = 'Maykungth'
# Date 18/8/2558

from flask import request, send_from_directory, make_response
from flask_restful import Resource
from werkzeug import secure_filename
from phr_api import apirest, encrypted_data_man, app,metadata_man
import os, timeit

class Upload(Resource):
    def post(self):
        file = request.files['file']
        formdata = request.form
        filename = secure_filename(request.files['file'].filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        # app.logger.debug('>>>>>> ',type(request.files['file']))
        # with open(path,'wb') as file:
        #     file.write(request.files['file'])
        app.logger.debug('Caching  %s', filename)

        metadata = metadata_man.genMeta(path,formdata)
        encrypted_data_man.saveToStore(path,metadata)

        os.remove(path)
        app.logger.debug('Cache is deleteed !')

        return metadata

class Download(Resource):
    def get(self,data_id):
        app.logger.debug('Get Request for download %s'%(data_id))
        startget = timeit.default_timer()
        start = timeit.default_timer()
        meta= metadata_man.getMeta(data_id)
        stop = timeit.default_timer()
        app.logger.debug('Time to getMeta %f'%(float(stop-start)))
        if meta != None:
            start = timeit.default_timer()
            file = encrypted_data_man.getFromStore(meta,data_id)
            stop = timeit.default_timer()
            app.logger.debug('Time to getEncryptedData %f'%(float(stop-start)))
            res = make_response(file)
            res.headers['Content-Type'] = 'application/octet-stream'
            res.headers['Content-Disposition'] = 'attachment; filename="%s"' % meta['pp:name']

            # f=open(os.path.join(app.config['UPLOAD_FOLDER'], meta['pp:name']), 'wb')
            # f.write(file)
            # f.close()
        else:
            return {'Message':'File not found'}
        stopget = timeit.default_timer()
        app.logger.debug('Time to Download data %f'%(float(stopget-startget)))
        return res
        # return send_from_directory(app.config['UPLOAD_FOLDER'], meta['pp:name'],as_attachment=True)
class Index(Resource):
    def get(self):
        return {'message':'It is Work by Maykungth'}
def addroute():
    apirest.add_resource(Upload, '/upload')
    apirest.add_resource(Download, '/download/<string:data_id>')
    apirest.add_resource(Index,'/')