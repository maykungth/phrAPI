__author__ = 'Maykungth'
# Date 18/8/2558

from flask import request, send_from_directory, make_response
from flask_restful import Resource
from werkzeug import secure_filename
from phr_api import apirest, encrypted_data_man, app,metadata_man
import os

class Upload(Resource):
    def post(self):
        file = request.files['file']
        formdata = request.form
        #from request sysid, userid, description
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        app.logger.debug('Caching  %s', filename)

        metadata = metadata_man.genMeta(path,formdata)
        encrypted_data_man.saveToStore(path,metadata)

        os.remove(path)
        app.logger.debug('Cache is deleteed !')

        return metadata

class Download(Resource):
    def get(self,data_id):
        meta= metadata_man.getMeta(data_id)
        if meta != None:
            file = encrypted_data_man.getFromStore(meta,data_id)
            res = make_response(file)
            res.headers['Content-Type'] = 'application/octet-stream'
            res.headers['Content-Disposition'] = 'attachment; filename="%s"' % meta['pp:name']

            # f=open(os.path.join(app.config['UPLOAD_FOLDER'], meta['pp:name']), 'wb')
            # f.write(file)
            # f.close()
        else:
            return {'Message':'File not found'}
        return res
        # return send_from_directory(app.config['UPLOAD_FOLDER'], meta['pp:name'],as_attachment=True)
class Index(Resource):
    def get(self):
        return {'message':'It is Work by Maykungth'}
def addroute():
    apirest.add_resource(Upload, '/upload')
    apirest.add_resource(Download, '/download/<string:data_id>')
    apirest.add_resource(Index,'/')