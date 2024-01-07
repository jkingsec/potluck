#!/bin/python3

from flask_restful import Resource, Api

from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    request,
    abort
)

from datetime import datetime

from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)

from werkzeug.routing import BuildError

from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app,db,login_manager,bcrypt

from api import (
	clientIndex,
	clientDetail,
	taskIndex,
	taskDetail,
	taskBulletin,
	logIndex,
	logDetail,
	groupIndex,
	groupDetail,
	listenerIndex,
	listenerDetail,
	userIndex,
	userDetail,
	payloadDownload,
	basicTest
)

from forms import (
	user_login,
	user_register,
	user_generate_payload,
	user_command,
	user_configure_client,
	project_add_users,
	project_remove_users,
	project_add_manager,
	project_remove_clients,
	project_create_group,
	project_remove_groups,
	admin_remove_users,
	admin_change_users_password,
	admin_create_project,
	admin_remove_project,
	admin_remove_listeners,
	admin_clear_orphaned_clients
)

from ast import literal_eval

from models import _User, _Client, _Group, _Log, _Task, _Project, _Listener

from crypter import generate_payload
import os, json, uuid, re
import pandas, plotly, plotly.express

#Note: there's a bug with FlaskForms.SelectMultipleField and integers, so choices have to be strings
#change project_id to either a big random number or uuid so old assets don't get added to new projects

@login_manager.user_loader
def load_user(user_id):
    return _User.query.get(int(user_id))

app = create_app()

####API

api = Api(app)

api.add_resource(clientIndex,'/api/clients')
api.add_resource(clientDetail, '/api/clients/<string:client_id>')
api.add_resource(taskIndex,'/api/tasks')
api.add_resource(taskDetail,'/api/tasks/<string:task_id>')
api.add_resource(taskBulletin, '/api/tasks/client/<string:client_id>')
api.add_resource(logIndex, '/api/logs')
api.add_resource(logDetail,'/api/logs/<string:log_id>')
api.add_resource(groupIndex,'/api/groups')
api.add_resource(groupDetail,'/api/groups/<string:group_id>')
api.add_resource(listenerIndex,'/api/listeners')
api.add_resource(listenerDetail,'/api/listeners/<string:listener_id>')
api.add_resource(userIndex,'/api/users')
api.add_resource(userDetail,'/api/users/<string:user_id>')
api.add_resource(payloadDownload,'/api/download/<string:pl_file_name>')
#api.add_resource(projectIndex, '/api/projects')
#api.add_resource(projectDetail, '/api/projects/<string:project_id>')
#api.add_resource(serverSettings, '/api/settings')#changes made via parameters
api.add_resource(basicTest, '/api/test')

##Flask routes aka Forms
@app.route("/")
def blank():
	#if logged in
	return redirect('/index')

@app.route("/login", methods=['GET', 'POST'])
def login():
	ul_form = user_login()
	if request.method == "POST":
		try:
			if ul_form.ul_submit.data and ul_form.validate_on_submit():
				user = _User.query.filter_by(user_name=ul_form.ul_username.data).first()
				if check_password_hash(user.user_password, ul_form.ul_password.data):
					login_user(user)
					return redirect('/index')
				else:
					flash("Invalid Username or password!", "danger")
		except Exception as e:
			flash(e, "danger")
	return render_template("login.html",
		ul_form=ul_form
	)
	
@app.route("/register", methods=["GET", "POST"])
def register():
	ur_form = user_register()
	if request.method == "POST":
		try:
			if ur_form.ur_submit.data and ur_form.validate_on_submit():
				
				email = ur_form.ur_email.data
				password = ur_form.ur_password.data
				username = ur_form.ur_username.data
				
				newuser = _User(
					user_name=username,
					user_email=email,
					user_password=bcrypt.generate_password_hash(password),
				)

				db.session.add(newuser)
				db.session.commit()
				return redirect(url_for("login"))

		except InvalidRequestError:
			db.session.rollback()
			flash(f"Something went wrong!")
		except IntegrityError:
			db.session.rollback()
			flash(f"User already exists!.")
		except DataError:
			db.session.rollback()
			flash(f"Invalid Entry")
		except InterfaceError:
			db.session.rollback()
			flash(f"Error connecting to the database")
		except DatabaseError:
			db.session.rollback()
			flash(f"Error connecting to the database")
		except BuildError:
			db.session.rollback()
			flash(f"An error occured !")
	return render_template("register.html",
		ur_form=ur_form
	)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
	
@app.route("/project/<string:project_slug>", methods=['GET', 'POST'])
@login_required
def project_dash(project_slug):
	project = db.session.execute(db.select(_Project).filter_by(project_slug=project_slug)).scalar_one()
	if (current_user.id in literal_eval(project.project_users)) or current_user.admin:
		
		clients = list(db.session.execute(db.select(_Client).filter_by(client_project_id=project.id).order_by(_Client.id)).scalars())
		groups = list(db.session.execute(db.select(_Group).filter_by(group_project_id=project.id).order_by(_Group.id)).scalars())
		listeners = list(db.session.execute(db.select(_Listener).order_by(_Listener.id)).scalars())
		all_logs = list(db.session.execute(db.select(_Log).order_by(_Log.id)).scalars())
		managers_list = literal_eval(project.project_managers)
		
		#phase this out with foreign keys in the model
		logs = []
		if clients:
			for x in all_logs:
				if x.log_client_id in [y.id for y in clients]:
					logs.append(x)
		
		#Activity Graph		
		plot_dict = {'Client': [], 'Time': [], 'Type': []}
		for z in logs:
			plot_dict['Client'].append(z.log_client_id[0:8])#improve this
			plot_dict['Time'].append(datetime.strptime(z.exec_date, '%d-%m-%Y %H:%M:%S'))
			plot_dict['Type'].append(z.log_cmd_type)
		df = pandas.DataFrame(plot_dict)
		fig = plotly.express.scatter(df, x='Time', y='Client', color='Client', symbol="Type")
		fig.update_traces(marker=dict(size=10, opacity=0.6, line=dict(color='Black', width=2)))
		fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
		graph_json = fig.to_json()
		
		#Forms
		uc_form = user_command()
		uc_form.target.choices = [x.id for x in clients]
		ugp_form = user_generate_payload()
		ugp_form.ugp_name.choices = {}
		for os_folder in next(os.walk("clients"))[1]:
			ugp_form.ugp_name.choices[os_folder] = [(client_folder, client_folder) for client_folder in next(os.walk(f"clients/{os_folder}"))[1]]
		ugp_form.ugp_listeners.choices = [x.id for x in listeners]
		ucc_form = user_configure_client()	
		
		if request.method == "POST":
			try:
				if uc_form.uc_submit.data and uc_form.validate():
					command = uc_form.command.data
					command_type = uc_form.command_type.data
					for x in uc_form.target.data:
						target = x
						new_task = _Task(task_cmd_type=command_type, task_cmd_input=command, task_client_id=target)
						db.session.add(new_task)
						db.session.commit()
				elif ugp_form.ugp_submit.data and ugp_form.validate():
					pl_dict = {
						"os":'linux',#test
						"name":ugp_form.ugp_name.data,
						"arch":ugp_form.ugp_arch.data,
						"type":ugp_form.ugp_type.data
					}
					settings_dict = {
						"listener_json": json.dumps([{"host": x.listener_ip,"port":str(x.listener_port)} for x in listeners]),
						"project_id":project.id,
						"expiration_date":ugp_form.ugp_expiration_date.data.strftime('%d-%m-%Y'),
						"PERSIST_ON":str(ugp_form.ugp_persist_on.data).lower(),
						"NO_VM":str(ugp_form.ugp_no_vm.data).lower(),
						"sleep_time":str(ugp_form.ugp_sleep_time.data)
					}
					print(pl_dict, settings_dict)
					return render_template('payload.html', text_payload=generate_payload(pl_dict, settings_dict), project_slug=project_slug)
				#elif ucc_form.uc_submit.data and ucc_form.validate():
			except Exception as e:
				print(e)
				return redirect(f"/project/{project_slug}")
			return redirect(f"/project/{project_slug}")
		return render_template('project.html', 
			uc_form=uc_form, 
			ugp_form=ugp_form, 
			clients=clients, 
			groups=groups, 
			logs=logs, 
			project_id=project.id,
			project=project,
			graph_json=graph_json,
			managers_list=managers_list
		)
	else:
		return abort(403)

@app.route("/index")
@login_required
def index():
	projects = db.session.execute(db.select(_Project).order_by(_Project.id)).scalars()
	projects_dict = sorted([{'id': x.id, "slug": x.project_slug,'name': x.project_name, 'users': literal_eval(x.project_users)} for x in projects], key=lambda d: d['name'])
	return render_template('index.html', projects_dict=projects_dict)
		
@app.route("/project/<string:project_slug>/manage", methods=['GET', 'POST'])
@login_required
def project_manage(project_slug):
	project_managers_list = literal_eval(db.session.execute(db.select(_Project).filter_by(project_slug=project_slug)).scalar_one().project_managers)
	project_users_list = literal_eval(db.session.execute(db.select(_Project).filter_by(project_slug=project_slug)).scalar_one().project_users)
	if (current_user.id in project_users_list and current_user.id in project_managers_list) or current_user.admin:
		project = db.session.execute(db.select(_Project).filter_by(project_slug=project_slug)).scalar_one()
		
		all_users = list(db.session.execute(db.select(_User).order_by(_User.id)).scalars())
		project_users = []
		for x in all_users:
			if x.id in project_users_list:
				project_users.append(x)
		
		project_managers = []
		for x in all_users:
			if x.id in project_managers_list:
				project_managers.append(x)
		project_clients = list(db.session.execute(db.select(_Client).filter_by(client_project_id=project.id).order_by(_Client.id)).scalars())
		project_groups = list(db.session.execute(db.select(_Group).filter_by(group_project_id=project.id).order_by(_Group.id)).scalars())

		au_form = project_add_users()
		au_form.users.choices = [(str(x.id), x.user_name+f" ({x.id})") for x in all_users if x not in project_users]
		
		ru_form = project_remove_users()
		ru_form.users.choices = [(str(x.id), x.user_name+f" ({x.id})") for x in project_users if x not in project_managers] #same issue with foreign keys etc
		
		am_form = project_add_manager()
		am_form.users.choices = [(str(x.id), x.user_name+f" ({x.id})") for x in project_users if x not in project_managers]
		am_form.project_id.choices = [str(project.id)]
		am_form.project_id.data = str(project.id)
		
		rc_form = project_remove_clients()
		rc_form.clients.choices = [x.id for x in project_clients]
		
		cg_form = project_create_group()
		cg_form.clients.choices = [x.id for x in project_clients]
		
		rg_form = project_remove_groups()
		rg_form.groups.choices = [(str(x.id), x.group_name) for x in project_groups]

		if request.method == "POST":
			try:	
				if au_form.pau_submit.data and au_form.validate():
					project_entry = db.session.execute(db.select(_Project).filter_by(id=project.id)).scalar()
					for x in au_form.users.data:
						project_users_list.append(int(x))
					project_users_list = list(set(project_users_list)) #remove duplicates just to be safe
					project_entry.project_users = str(project_users_list)
					db.session.commit()
				elif ru_form.pru_submit.data and ru_form.validate():
					project_entry = db.session.execute(db.select(_Project).filter_by(id=project.id)).scalar()
					for x in ru_form.users.data:
						project_users_list.remove(int(x))
					project_entry.project_users = str(project_users_list)
					db.session.commit()
				elif am_form.pam_submit.data and am_form.validate():
					project_entry = db.session.execute(db.select(_Project).filter_by(id=project.id)).scalar()
					for x in am_form.users.data:
						project_managers_list.append(int(x))
					project_entry.project_managers = str(project_managers_list)
					db.session.commit()
				elif rc_form.prc_submit.data and rc_form.validate():
					for x in rc_form.clients.data:
						client_entry = db.session.execute(db.select(_Client).filter_by(id=x)).scalar()
						db.session.delete(client_entry)
					db.session.commit()
				elif cg_form.pcg_submit.data and cg_form.validate():
					print(5)
					new_group = _Group(
						group_name=cg_form.group_name.data,
						group_members=str(cg_form.clients.data),
						group_project_id=project.id
					)
					db.session.add(new_group)
					db.session.commit()
				elif rg_form.prg_submit.data and rg_form.validate():
					for x in rg_form.groups.data:
						group_entry = db.session.execute(db.select(_Group).filter_by(id=int(x))).scalar()
						db.session.delete(group_entry)
					db.session.commit()
			except Exception as e:
				print("Exception:",e)
				#add Flash here
				return redirect(f"/project/{project_slug}/manage")
			return redirect(f"/project/{project_slug}/manage")

		return render_template('manager.html', project_id=project.id, project_slug=project_slug, au_form=au_form,ru_form=ru_form,rc_form=rc_form,cg_form=cg_form,rg_form=rg_form,am_form=am_form)
	else:
		abort(403)

@app.route("/user", methods=['GET', 'POST'])
@login_required
def user_panel():
	return render_template('user.html')

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin_panel():
	if current_user.admin:
		all_users = list(db.session.execute(db.select(_User).order_by(_User.id)).scalars())
		all_projects = list(db.session.execute(db.select(_Project).order_by(_Project.id)).scalars())
		all_listeners = list(db.session.execute(db.select(_Listener).order_by(_Listener.id)).scalars())
		
		aru_form = admin_remove_users()
		aru_form.users.choices = [(str(x.id), x.user_name) for x in all_users if x.admin != True]
		
		acp_form = admin_create_project()
		acp_form.project_users.choices = [(str(x.id), x.user_name) for x in all_users]
		#acp_form.project_managers.choices = [(str(x.id), x.user_name) for x in all_users]
		acp_form.project_listeners.choices = [x.id for x in all_listeners]
		
		pam_form = project_add_manager()
		pam_form.project_id.choices = [(str(x.id), x.project_name) for x in all_projects]
		pam_form.users.choices = [(str(x.id), x.user_name) for x in all_users]
		
		arp_form = admin_remove_project()
		arp_form.project_id.choices = [(str(x.id), x.project_name) for x in all_projects]
		
		arl_form = admin_remove_listeners()
		arl_form.listeners.choices = [x.id for x in all_listeners]
		
		acoc_form = admin_clear_orphaned_clients()
		
		if request.method == "POST":
			try:	
				if aru_form.aru_submit.data and aru_form.validate():
					for x in aru_form.users.data:
						user_entry = db.session.execute(db.select(_User).filter_by(id=int(x))).scalar()
						db.session.delete(user_entry)
					db.session.commit()
				elif acp_form.acp_submit.data and acp_form.validate():
					#create slug
					new_slug = acp_form.project_name.data 
					new_slug = re.sub(r'\W+', ' ', new_slug)
					new_slug = re.sub(r'\s+', '-', new_slug)
					new_slug = new_slug.strip('-')
					new_slug = new_slug.lower() + '-' + str(uuid.uuid4())[:8]
					
					new_project = _Project(
						project_name=acp_form.project_name.data,
						project_slug=new_slug,
						project_users=str([int(x) for x in acp_form.project_users.data]),
						#project_managers=str([int(x) for x in acp_form.project_managers.data]),
						project_listeners=str(acp_form.project_listeners.data)
					)
					db.session.add(new_project)
					db.session.commit()
				elif pam_form.pam_submit.data and pam_form.validate():
					project_entry = db.session.execute(db.select(_Project).filter_by(id=pam_form.project_id.data)).scalar()
					project_users_list = literal_eval(project_entry.project_users)
					project_managers_list = literal_eval(project_entry.project_managers)
					for x in pam_form.users.data:
						if int(x) not in project_users_list:
							project_users_list.append(int(x))
						project_managers_list.append(int(x))
					project_entry.project_managers = str(project_managers_list)
					project_entry.project_users = str(project_users_list)
					db.session.commit()
				elif arp_form.arp_submit.data and arp_form.validate():
					project_entry = db.session.execute(db.select(_Project).filter_by(id=arp_form.project_id.data)).scalar()
					db.session.delete(project_entry)
					db.session.commit()
				elif arl_form.arl_submit.data and arl_form.validate():
					project_entry = db.session.execute(db.select(_Project).filter_by(id=arp_form.project_id.data)).scalar()
					db.session.delete(project_entry)
					db.session.commit()
				elif acoc_form.acoc_submit.data and acoc_form.validate():
					all_clients = list(db.session.execute(db.select(_Client).order_by(_Client.id)).scalars())
					for x in all_clients: 
						if x.client_project_id not in [y.id for y in all_projects]:
							client_entry = db.session.execute(db.select(_Client).filter_by(client_project_id=x.client_project_id)).scalar()
							db.session.delete(client_entry)
					db.session.commit()
			except Exception as e:
				print("Exception:",e)
				return redirect(f"/admin")
			return redirect(f"/admin")
		
		return render_template('admin.html', aru_form=aru_form,acp_form=acp_form,arp_form=arp_form,pam_form=pam_form,arl_form=arl_form,acoc_form=acoc_form)
	else:
		return abort(403)
