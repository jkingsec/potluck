from app import db
from flask_login import UserMixin
from datetime import datetime
from uuid import uuid4

#clients
class _Client(db.Model):
	id = db.Column(db.String, unique=True, primary_key=True, nullable=False)
	client_name = db.Column(db.String, nullable=False)
	client_ip = db.Column(db.String, nullable=False)
	client_os = db.Column(db.String, nullable=False)
	client_ping = db.Column(db.Float)
	client_settings = db.Column(db.String)
	client_project_id = db.Column(db.Integer)
	create_time = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
	modify_time= db.Column(db.String)
#client groups
class _Group(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
	group_name = db.Column(db.String, nullable=False)
	group_members = db.Column(db.String)
	group_project_id = db.Column(db.Integer)
	create_time = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
	modify_time= db.Column(db.String)
#tasks
class _Task(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
	task_client_id = db.Column(db.String, db.ForeignKey(_Client.id), nullable=False)
	task_cmd_type = db.Column(db.String, nullable=False)
	task_cmd_input = db.Column(db.String)
	task_issue_date = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
#logs
class _Log(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
	log_client_id = db.Column(db.String, nullable=False)
	log_cmd_type = db.Column(db.String, nullable=False)
	log_cmd_input = db.Column(db.String)
	log_cmd_output = db.Column(db.String)
	log_issue_date = db.Column(db.String, nullable=False)
	exec_date = db.Column(db.String, nullable=False)
#users
class _User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
	user_name = db.Column(db.String, nullable=False)
	user_email = db.Column(db.String)
	user_password = db.Column(db.String, nullable=False)
	admin = db.Column(db.Boolean, nullable=False, default=False)
	user_settings = db.Column(db.String)
	create_time = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
	modify_time= db.Column(db.String)
#listeners
class _Listener(db.Model):
	id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
	listener_ip = db.Column(db.String, nullable=False)
	listener_settings = db.Column(db.String, nullable=False)
	listener_port = db.Column(db.Integer, nullable=False)
	create_time = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
	modify_time= db.Column(db.String)
#project groups
class _Project(db.Model):
	id = db.Column(db.String, unique=True, primary_key=True, nullable=False, default=str(uuid4()))
	project_name = db.Column(db.String, unique=True, nullable=False)
	project_slug = db.Column(db.String, unique=True, nullable=False)
	project_users = db.Column(db.String)
	project_managers = db.Column(db.String, default="[]")
	#project_clients = db.Column(db.String)
	project_listeners = db.Column(db.String)
	create_time = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
	modify_time= db.Column(db.String)
#server settings
#class _Setting(db.Model):
#stored payload
class _Payload(db.Model):
	id = db.Column(db.String, unique=True, primary_key=True, nullable=False)
	file_name = db.Column(db.String, unique=True, nullable=False)
	file_expire = db.Column(db.String, nullable=False)
	create_time = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
