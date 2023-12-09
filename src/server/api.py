#!/bin/python3
import uuid, json
from datetime import datetime
from flask import request
from flask_restful import Resource, Api
from app import db 
from models import (
	_Client,
	_Group,
	_Task,
	_Log,
	_User,
	_Listener
)
#import app
##API
# add filter that limits index results to 500 posts
# db.paginate(db.select().order_by())
#create resources for client if settings object too big
#add access control to logs and clients based on project membership
#user info is only accessable by admin requests made to the server


class clientIndex (Resource):
	def get(self): #read
		entries = list(db.session.execute(db.select(_Client)))
		index = {}
		for x in entries:
			entry = x[0].__dict__
			index[entry['id']] = {
				'client_name': entry['client_name'],
				'client_ip': entry['client_ip'],
				'client_os': entry['client_os'],
				'client_ping': entry['client_ping']
			}
		return index
		
class clientDetail (Resource):
	#create/update
	def post(self, client_id):
		client_data = json.loads(request.form['data'])
		print(request.form)
		entries = list(db.session.execute(db.select(_Client).order_by(_Client.id)).scalars())
		clients = [x.id for x in entries]
		ping_time = (datetime.utcnow() - datetime.strptime(client_data['send_time'], "%d-%m-%Y %H:%M:%S")).total_seconds()
		if client_id not in clients:
			client = _Client(
				id=client_id,
				client_name=client_data['client_name'],
				client_ip=client_data['origin_ip'],
				client_os=client_data['client_os'],
				client_ping=ping_time,
				client_project_id=client_data['project_id'],
				client_settings=str(client_data['client_settings'])
			)
			db.session.add(client)
		else:
			client = db.session.execute(db.select(_Client).filter_by(id=client_id)).scalar()
			client.client_name = client_data['client_name']
			client.client_ip = client_data['origin_ip']
			client.client_ping=ping_time
			client.settings=str(client_data['client_settings'])
			client.modify_time=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
		db.session.commit()			
	def get(self, client_id): #read
		entries = list(db.session.execute(db.select(_Client).filter_by(id=client_id)))
		detail = [x[0].__dict__ for x in entries][0]
		detail.pop('_sa_instance_state', None)
		return detail

class taskIndex(Resource):
	def get(self): #read
		entries = list(db.session.execute(db.select(_Task)))
		index = {}
		for x in entries:
			entry = x[0].__dict__
			index[entry['id']] = {
				'task_client_id': entry['task_client_id'],
				'task_cmd_type': entry['task_cmd_type'],
				'task_cmd_input':  entry['task_cmd_input'],
				'task_issue_date':  entry['task_issue_date']
			}
		return index
	def post(self): #create
		task_data = json.loads(request.form['data'])
		task = _Task(
			task_client_id=request.form['task_client_id'],
			task_cmd_type=request.form['task_cmd_type'],
			task_cmd_input=request.form['task_cmd_input'],
			task_issue_date=request.form['task_issue_date']
		)
		db.session.add(task)
		db.session.commit()

class taskDetail(Resource):
	def get(self, task_id): #read
		entries = list(db.session.execute(db.select(_Task).filter_by(id=task_id)))
		detail = [x[0].__dict__ for x in entries][0]
		detail.pop('_sa_instance_state', None)
		return detail
	def delete(self, task_id):
		task = db.session.execute(db.select(_Task).filter_by(id=task_id)).scalar()
		db.session.delete(task)
		db.session.commit()

class taskBulletin (Resource):
	def get (self, client_id):
		entries = list(db.session.execute(db.select(_Task).filter_by(task_client_id=client_id)))
		tasks = [x[0].__dict__ for x in entries]
		for y in tasks:
			y.pop('_sa_instance_state', None)
		return tasks

class logIndex (Resource):
	#read
	def get (self):
		entries = list(db.session.execute(db.select(_Log)))
		index = {}
		for x in entries:
			entry = x[0].__dict__
			_input = entry['log_cmd_input']
			_output = entry['log_cmd_output']
			if len(_input) > 200:
				_input = _input[:200]+'...'
			if len(_output) > 200:
				_output = _output[:200]+'...'
			index[entry['id']] = {
				'log_cmd_type': entry['log_cmd_type'],
				'log_cmd_input': _input,
				'log_cmd_output': _output,
				'log_issue_date': entry['log_issue_date'],
				'exec_date': entry['exec_date']
			}
		return index
	#create
	def post(self):
		log_data = json.loads(request.form["data"])
		print(log_data)
		log = _Log(
			log_client_id=log_data['log_client_id'],
			log_cmd_type=log_data['log_cmd_type'],
			log_cmd_input=log_data['log_cmd_input'],
			log_cmd_output=log_data['log_cmd_output'],
			log_issue_date=log_data['log_issue_date'],
			exec_date=log_data['exec_date']
			# ip address goes here
		)
		db.session.add(log)
		#delete task #MAKE SURE TASK EVEN EXISTS TO AVOID ERRORS
		task = db.session.execute(db.select(_Task).filter_by(id=log_data["task_id"])).scalar()
		db.session.delete(task)
		db.session.commit()

class logDetail (Resource):
	def get(self, log_id): #read
		entries = list(db.session.execute(db.select(_Log).filter_by(id=log_id)))
		detail = [x[0].__dict__ for x in entries][0]
		detail.pop('_sa_instance_state', None)
		return detail

class groupIndex (Resource):
	def get(self): #read
		entries = list(db.session.execute(db.select(_Group)))
		index = {}
		for x in entries:
			entry = x[0].__dict__
			_members = literal_eval(entry['group_members'])
			for z in range(0, len(_members)):
				_members[z] = _members[z][:8]+'...'
			index[entry['id']] = {
				'group_name': entry['group_name'],
				'group_members': _members
				#creation date
			}
		return index 
	def post(self): #create
		group_data = json.loads(request.form['data'])
		group = _Group(
			group_name=request.form['group_name'],
			group_members=str(request.form['group_members'])
		)
		db.session.add(group)
		db.session.commit()

class groupDetail (Resource):
	def get(self, group_id): #read
		entries = list(db.session.execute(db.select(_Group).filter_by(id=group_id)))
		detail = [x[0].__dict__ for x in entries][0]
		detail['group_members'] = literal_eval(detail['group_members'])
		detail.pop('_sa_instance_state', None)
		return detail
	def post(self, group_id): #update
		entries = list(db.session.execute(db.select(_Group).filter_by(id=group_id)))
		if entries:
			group = db.session.execute(db.select(_Group).filter_by(id=group_id)).scalar()
			group.group_name = request.form['group_name']
			group.group_members = str(request.form['group_members'])
			group.modify_time=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
			db.session.commit()
			
	def delete(self, group_id):
		group = db.session.execute(db.select(_Group).filter_by(id=group_id)).scalar()
		db.session.delete(group)
		db.session.commit()

class listenerIndex (Resource):
	def get(self): #read
		entries = list(db.session.execute(db.select(_Listener)))
		index = {}
		for x in entries:
			entry = x[0].__dict__
			index[entry['id']] = {
				'listener_ip': entry['listener_ip'],
				'listener_settings': entry['listener_settings']
			}
		return index

class listenerDetail (Resource):
	def get(self, listener_id): #read
		entries = list(db.session.execute(db.select(_Listener).filter_by(id=listener_id)))
		detail = [x[0].__dict__ for x in entries][0]
		detail.pop('_sa_instance_state', None)
		return detail
	def post(self, listener_id):
		#check for listener record
		listener_data = json.loads(request.form['data'])
		entries = list(db.session.execute(db.select(_Listener).order_by(_Listener.id)).scalars())
		listeners = [x.id for x in entries]
		if listener_id not in listeners:
			#create
			listener = _Listener(
				id=listener_data['listener_id'],
				listener_ip=request.remote_addr,
				listener_settings=str(listener_data['listener_settings'])
			)
			db.session.add(listener)
		else:
			#update
			listener = db.session.execute(db.select(_Listener).filter_by(id=listener_id)).scalar()
			listener.listener_ip = request.remote_addr
			listener.listener_settings = str(listener_data['listener_settings'])
			listener.modify_time=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
		db.session.commit()
	def delete(self, listener_id):
		listener = db.session.execute(db.select(_Listener).filter_by(id=listener_id)).scalar()
		db.session.delete(listener)
		db.session.commit()

class userIndex (Resource):
	def get(self): #read
		entries = list(db.session.execute(db.select(_User)))
		index = {}
		for x in entries:
			entry = x[0].__dict__
			index[entry['id']] = {
				'user_name': entry['user_name'],
				'user_email': entry['user_email']
			}
		return index
	def post(self): #create
		user_data = json.loads(request.form['data'])
		user = _User(
			user_name=request.form['user_name'],
			user_email=request.form['user_email'],
			user_password=request.form['user_password']#hash before or after sending?
		)
		db.session.add(user)
		db.session.commit()

class userDetail (Resource):
	def get(self, user_id): #read
		entries = list(db.session.execute(db.select(_User).filter_by(id=user_id)))
		detail = [x[0].__dict__ for x in entries][0]
		detail.pop('_sa_instance_state', None)
		return detail
	def post(self, user_id): #update
		entries = list(db.session.execute(db.select(_User).filter_by(id=user_id)))
		if entries:
			user = db.session.execute(db.select(_User).filter_by(id=user_id)).scalar()
			user.user_name = request.form['user_name']
			user.user_email = request.form['user_email']
			user.user_password=request.form['user_password']
			user.client.modify_time=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
			db.session.commit()
			
	def delete(self, user_id):
		user = db.session.execute(db.select(_User).filter_by(id=user_id)).scalar()
		db.session.delete(user)
		db.session.commit()

class basicTest (Resource):
	# curl -X POST -F 'data={"test": "curl"}' http://localhost:5000/api/test
	def post(self):
		global test_data
		test_data = json.loads(request.form['data'])
		print(request.headers)
		print(request.cookies)
		print(request.data)
		print(request.args)
		print(request.form)
		print(request.endpoint)
		print(request.method)
		print(request.remote_addr)
	def get(self):
		return test_data
