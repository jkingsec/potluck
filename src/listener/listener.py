#!/bin/python3

import json
from uuid import uuid4
#from datetime import datetime
from flask import Flask, render_template, request, Response
#from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from requests import get, post
from requests import exceptions as req_exceptions
from sys import argv #for testing?

server_domain = "http://localhost"
server_port = "5000"
listener_port = 5150
listener_settings = {}

def ping():
	ping_data = json.dumps(
		{
			'listener_id': listener_settings['listener_id'],
			'listener_settings': listener_settings,
			'listener_port': listener_port
		}
	)
	try:
		post(f'{server_domain}:{server_port}/api/listeners/{listener_settings["listener_id"]}', data={'data':ping_data})
	except req_exceptions.ConnectionError or req_exceptions.TimeoutError:
		return False

app = Flask(__name__)

##SQLAlchemy

db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///listener.db' 

db.init_app(app)

class _Buffer(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
	req_path = db.Column(db.String)
	req_data = db.Column(db.String)

class _Settings(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
	listener_id = db.Column(db.String)
	ping_freq = db.Column(db.Integer)
	buffer_freq = db.Column(db.Integer)

with app.app_context():
	db.create_all()

def check_settings():
	with app.app_context():
		if not list(db.session.execute(db.select(_Settings))):
			init_settings = _Settings(
			listener_id=str(uuid4()),
			ping_freq=60,
			buffer_freq=15
			)
			db.session.add(init_settings)
			db.session.commit()
		setting_values = db.session.execute(db.select(_Settings).filter_by(id=1)).scalar()
		global listener_settings
		listener_settings = {
			'listener_id': setting_values.listener_id,
			'ping_freq': setting_values.ping_freq,
			'buffer_freq': setting_values.buffer_freq
		}

#curl -X POST -F 'data={"test": "proxy curl"}' http://localhost:5150/test
#post('http://localhost:5150/test', data={'data':'{"test":"python"}'})

@app.route('/')#, defaults={'path':''})
def index():
	return ""
@app.route('/<path:path>', methods=['GET','POST'])

def proxy(path):
	try:
		if request.method == "GET":
			try:
				results = get(f'{server_domain}:{server_port}/api/{path}')
				if results.content != b'null\n':
					return json.loads(results.content), 200
				else:
					return "200\n", 200
			except:
				return ""
		elif request.method == "POST":
			try:
				buffer_entry = _Buffer(#issue with the logic where GETs are throwing up exceptions
				req_path=path, 
				req_data=str(request.form['data'])
				) #save to buffer
				db.session.add(buffer_entry)
				db.session.commit()
				request_data = json.loads(request.form['data'])
				request_data['origin_ip'] = request.remote_addr
				results = post(f'{server_domain}:{server_port}/api/{path}', data={'data': json.dumps(request_data)})
				if results.status_code == 200:
					#delete buffer entry
					db.session.delete(buffer_entry)
					db.session.commit()
					if results.content != b'null\n':
						return json.loads(results.content), 200
					else:
						return "200\n", 200
				else:
					#delete buffer entry if invalid
					db.session.delete(buffer_entry)
					db.session.commit()
					return ""
			except:
				db.session.delete(buffer_entry) #something bad happening here
				db.session.commit()
				return ""
		
	except req_exceptions.ConnectionError or req_exceptions.TimeoutError as e:
		#only try buffer send if requests.exceptions.ConnectionError or TimeOut, not 400 or 600
		print(f"Connection Error: ({e})\nWaiting to resend...")
		return ""

#scheduler
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

@scheduler.task('interval', id='ping_job', minutes=60)#have this be a setting
def ping_job():
	ping()
	print('Server Pinged')
	
@scheduler.task('interval', id='buffer_job', minutes=15)#have this be a setting
def buffer_job():
	with app.app_context():
		buffer_list = list(db.session.execute(db.select(_Buffer)))
		if buffer_list:
				try:
					for x in buffer_list:
						buffer_dict = x[0].__dict__
						results = post(f'{server_domain}:{server_port}/api/{buffer_dict["req_path"]}', 
						data={'data': json.dumps(buffer_dict["req_data"])})
						if results.status_code == 200:
							db.session.delete(db.session.execute(db.select(_Buffer).filter_by(id=buffer_dict['id'])).scalar())
							db.session.commit()
							buffer_list.remove(x)
							print('Buffer request sent!')
				except:
					print('Error when trying to send buffer jobs...')
				
		else:
			pass

#boot stuff
check_settings()
ping()

if len(argv) == 2:
	listener_port = argv[1]

if __name__ == '__main__':
	scheduler.start()
	app.run(debug=True, port=listener_port)# use_reloader=False if the double pings are too annoying
