__author__ = 'Maykungth'
from flask import Flask
from flask.ext.cors import CORS
from flask_restful import Resource,Api

app = Flask(__name__)
CORS(app)
apirest = Api(app)

app.config['UPLOAD_FOLDER'] = '/home/hduser/uploads'

MasterHbase = '172.30.224.142'
Master = '172.30.224.137'
largeSize = 10000000 #10MB
HDFSMainPath ='/DSePHR/'

