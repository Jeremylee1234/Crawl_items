#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import datetime
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/message'
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    upload_time = db.Column(db.TIMESTAMP, default=datetime.datetime.now, nullable=False)

@app.route('/',methods=['POST'])
def main():
    if request.method == 'POST':
        data = request.get_data()
        if data == None:
            return jsonify({"msg": "no content send!"})
        else:
            try:
                data = json.loads(data)
                message = Message(
                    title = data.get('title'),
                    content = data.get('content'),
                    phone = data.get('phone'),
                    upload_time = datetime.datetime.now()
                )
                db.session.add(message)
                db.session.commit()
                return jsonify({"msg": "succeed!"})
            except:
                db.session.rollback()
                return jsonify({"msg": "failed!"})

app.run(host='0.0.0.0', debug=False, port=11123)