__author__ = 'Maykungth'
from flask import Flask
from flask_cors import CORS
from flask_restful import Resource,Api
from os import path, makedirs


app = Flask(__name__)
CORS(app)
apirest = Api(app)

workdir='/home/hduser/workspace/'  # set working dir

UPLOAD_DIR = path.join(workdir,'uploads')
if not path.exists(UPLOAD_DIR):
    makedirs(UPLOAD_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

MasterHbase = 'Master2'  # set HBase Master
Master = 'Master'          # Set HDFS Namenode
largeSize = 10000000 #10MB
HDFSMainPath ='/DSePHR/'

SSL_DIR = path.join(workdir,'sslcert')
if not path.exists(SSL_DIR):
    makedirs(SSL_DIR)

SQL_lite_DIR = path.join(workdir,'authen')
if not path.exists(SQL_lite_DIR):
    makedirs(SQL_lite_DIR)


app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+SQL_lite_DIR+'/authen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'something_super_secret_change_in_production'
app.config['WTF_CSRF_ENABLED'] = False