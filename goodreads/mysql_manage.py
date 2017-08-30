import numbers
import json
import goodreads.spiders.config as config
from  sqlalchemy.sql.expression import func, select
from sqlalchemy import or_
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.mysql_connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.sa_track_mods

db = SQLAlchemy(app)