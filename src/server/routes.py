#!/bin/python3

from flask_restful import Resource, Api

from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    request
)

from datetime import timedelta

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
	basicTest
)

from forms import (
	login_form,
	register_form,
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

#Note: there's a bug with FlaskForms.SelectMultipleField and integers, so choices have to be strings
#change project_id to either a big random number or uuid so old assets don't get added to new projects
#switch task_id to uuid?

##COPY PASTE##

@login_manager.user_loader
def load_user(user_id):
    return _User.query.get(int(user_id))

####

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
#api.add_resource(projectIndex, '/api/projects')
#api.add_resource(projectDetail, '/api/projects/<string:project_id>')
#api.add_resource(serverSettings, '/api/settings')#changes made via parameters
api.add_resource(basicTest, '/api/test')

####

##Flask routes aka Forms
@app.route("/")
def blank():
	return redirect('/index')
	
@app.route("/login", methods=['GET', 'POST'])
def login():
	#return render_template('login.html')
####
    form = login_form()

    if form.validate_on_submit():
        try:
            user = _User.query.filter_by(user_email=form.email.data).first()
            if check_password_hash(user.user_password, form.pwd.data):
                login_user(user)
                return redirect('/index')
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )
####
	
@app.route("/register", methods=["GET", "POST"])
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = _User(
                user_name=username,
                user_email=email,
                user_password=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

####

@app.route("/command", methods=['GET', 'POST'])#obselete
def command():
	client_entries = db.session.execute(db.select(_Client).order_by(_Client.id)).scalars() #works?
	group_entries = db.session.execute(db.select(_Group).order_by(_Group.id)).scalars()
	clients = [{
		'id':x.id,
		'name':x.client_name,
		'os':x.client_os,
		'ip':x.client_ip,
		'ping':x.client_ping
		} for x in client_entries]
	logs = db.session.execute(db.select(_Log).order_by(_Log.id)).scalars() #turn into json for consistency
	groups = [{
		'id':y.id,
		'name':y.group_name,
		'members':str([x[0:8]+'...' for x in eval(y.group_members)])[1:-1]
		} for y in group_entries]
	form_client_list = []
	if request.method == "POST":
		print(form_client_list)
		if "command-submit" in request.form:
			#validate form data here
			#discern types
			#if target not selected, give warning
			for w in request.form.getlist('client'):
				task = _Task(
					task_client_id=w,
					task_cmd_type=request.form['type'],
					task_cmd_input=request.form['command'],
					task_issue_date=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S') #changed to utc, have webapp convert to local
				)
				db.session.add(task)
			db.session.commit()
		elif "group-submit" in request.form:
			print(request.form)
			group = _Group(
				group_name=request.form['name'],
				group_members=str(request.form.getlist('client')),
			)
			db.session.add(group)
			db.session.commit()
	return render_template('command.html', clients=clients, logs=logs, groups=groups) #needs a refresh here

@app.route("/project/<string:project_id>", methods=['GET', 'POST'])
def project_dash(project_id):
	clients = list(db.session.execute(db.select(_Client).filter_by(client_project_id=project_id).order_by(_Client.id)).scalars())
	groups = list(db.session.execute(db.select(_Group).filter_by(group_project_id=project_id).order_by(_Group.id)).scalars())
	logs = list(db.session.execute(db.select(_Log).order_by(_Log.id)).scalars())
	#phase this out with foreign keys in the model
	for x in logs:
		if x.log_client_id not in [y.id for y in clients]:
			logs.remove(x)
	
	uc_form = user_command()
	uc_form.target.choices = [x.id for x in clients]
	ugp_form = user_generate_payload()
	ucc_form = user_configure_client()	
	
	# groups = [{
		# 'id':y.id,
		# 'name':y.group_name,
		# 'members':str([x[0:8]+'...' for x in eval(y.group_members)])[1:-1] ####
		# } for y in group_entries]
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
			#elif ugp_form.ugp_submit.data and ugp_form.validate():
			#elif ucc_form.uc_submit.data and ucc_form.validate():
		except Exception as e:
			print(e)
			return redirect(f"/project/{project_id}")
		return redirect(f"/project/{project_id}")
	return render_template('project.html', uc_form=uc_form, clients=clients, groups=groups, logs=logs, project_id=project_id)

@app.route("/index")
def index():
	projects = db.session.execute(db.select(_Project).order_by(_Project.id)).scalars()
	return render_template('index.html', projects=projects)
		
@app.route("/project/<int:project_id>/manage", methods=['GET', 'POST'])
def project_manage(project_id):
	all_users = list(db.session.execute(db.select(_User).order_by(_User.id)).scalars())
	project_users_list = literal_eval(db.session.execute(db.select(_Project).filter_by(id=project_id)).scalar_one().project_users)
	project_users = []
	for x in all_users:
		if x.id in project_users_list:
			project_users.append(x)
	project_managers_list = literal_eval(db.session.execute(db.select(_Project).filter_by(id=project_id)).scalar_one().project_managers)
	project_managers = []
	for x in all_users:
		if x.id in project_managers_list:
			project_managers.append(x)
	project_clients = list(db.session.execute(db.select(_Client).filter_by(client_project_id=project_id).order_by(_Client.id)).scalars())
	project_groups = list(db.session.execute(db.select(_Group).filter_by(group_project_id=project_id).order_by(_Group.id)).scalars())

	au_form = project_add_users()
	au_form.users.choices = [(str(x.id), x.user_name+f" ({x.id})") for x in all_users if x not in project_users]
	
	ru_form = project_remove_users()
	ru_form.users.choices = [(str(x.id), x.user_name+f" ({x.id})") for x in project_users if x not in project_managers] #same issue with foreign keys etc
	
	am_form = project_add_manager()
	am_form.users.choices = [(str(x.id), x.user_name+f" ({x.id})") for x in project_users if x not in project_managers]
	am_form.project_id.choices = [str(project_id)]
	am_form.project_id.data = str(project_id)
	
	rc_form = project_remove_clients()
	rc_form.clients.choices = [x.id for x in project_clients]
	
	cg_form = project_create_group()
	cg_form.clients.choices = [x.id for x in project_clients]
	
	rg_form = project_remove_groups()
	rg_form.groups.choices = [(str(x.id), x.group_name) for x in project_groups]

	if request.method == "POST":
		try:	
			if au_form.pau_submit.data and au_form.validate():
				project_entry = db.session.execute(db.select(_Project).filter_by(id=project_id)).scalar()
				for x in au_form.users.data:
					project_users_list.append(int(x))
				project_users_list = list(set(project_users_list)) #remove duplicates just to be safe
				project_entry.project_users = str(project_users_list)
				db.session.commit()
			elif ru_form.pru_submit.data and ru_form.validate():
				project_entry = db.session.execute(db.select(_Project).filter_by(id=project_id)).scalar()
				for x in ru_form.users.data:
					project_users_list.remove(int(x))
				project_entry.project_users = str(project_users_list)
				db.session.commit()
			elif am_form.pam_submit.data and am_form.validate():
				project_entry = db.session.execute(db.select(_Project).filter_by(id=project_id)).scalar()
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
					group_project_id=project_id
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
			return redirect(f"/project/{project_id}/manage")
		return redirect(f"/project/{project_id}/manage")

	return render_template('manager.html', project_id=project_id, au_form=au_form,ru_form=ru_form,rc_form=rc_form,cg_form=cg_form,rg_form=rg_form,am_form=am_form)

@app.route("/user", methods=['GET', 'POST'])
def user_panel():
	return render_template('user.html')

@app.route("/admin", methods=['GET', 'POST'])
def admin_panel():
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
				new_project = _Project(
					project_name=acp_form.project_name.data,
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
