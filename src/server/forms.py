from wtforms import (
    StringField,
    SelectField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    SelectMultipleField,
    SubmitField
)

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional
import email_validator
from flask_login import current_user
from wtforms import ValidationError,validators
from models import _User


class user_login(FlaskForm):
	#login_email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
	ul_password = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
	ul_username = StringField()
		#validators=[Optional()]
	#)
	ul_submit = SubmitField(u'Login')

class user_register(FlaskForm):
	ur_username = StringField(
		validators=[
			InputRequired(),
			Length(3, 20, message="Please provide a valid name"),
			Regexp(
				"^[A-Za-z][A-Za-z0-9_.]*$",
				0,
				"Usernames must have only letters, " "numbers, dots or underscores",
			),
		]
	)
	ur_email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
	ur_password = PasswordField(validators=[InputRequired(), Length(8, 72)])
	ur_cpassword = PasswordField(
		validators=[
			InputRequired(),
			Length(8, 72),
			EqualTo("ur_password", message="Passwords must match !")
		]
	)
	ur_submit = SubmitField(u'Register')

	def validate_email(self, email):
		if _User.query.filter_by(user_email=ur_email.data).first():
			raise ValidationError("Email already registered!")

	def validate_uname(self, uname):
		if _User.query.filter_by(user_name=ur_username.data).first():
			raise ValidationError("Username already taken!")

##Project User Forms
class user_generate_payload(FlaskForm):
	ugp_name = SelectField()
	ugp_arch = SelectField(choices=[('amd64','AMD64'), ('i386','i386')])
	ugp_type = SelectField(choices=[('py_fileless','Python Fileless')])
	ugp_listeners = SelectMultipleField()
	ugp_persist_on = BooleanField()
	ugp_no_vm = BooleanField()
	ugp_sleep_time = IntegerField()
	ugp_expiration_date = DateField()#string?
	ugp_submit = SubmitField(u"Generate")
	
class user_command(FlaskForm):#user_create_task
	command = StringField()
	command_type = SelectField(choices=[
		('command','Command'),
		('ping','Ping'),
		('delete','Delete'),
		('shutdown', 'Shutdown'),
		('configure','Configure')
		])
	target = SelectMultipleField()
	uc_submit = SubmitField(u"Submit")

class user_configure_client(FlaskForm):
	target = SelectMultipleField()
	listeners = SelectField()
	persistence_setting = BooleanField()
	def_read_time = IntegerField()
	def_execute_time = IntegerField()
	def_log_time = IntegerField()
	def_ping_time = IntegerField()
	acc_submit = SubmitField(u"Submit")

class user_change_password(FlaskForm):
	ucp_old_password = PasswordField()
	ucp_new_password = PasswordField(validators=[InputRequired(), Length(8, 72)])
	ucp_new_cpassword = PasswordField(
		validators=[
			InputRequired(),
			Length(8, 72),
			EqualTo("ucp_new_password", message="Passwords must match !")
		]
	)
	ucp_submit = SubmitField(u"Change")

##Project Manager Forms
class project_add_users(FlaskForm):
	users = SelectMultipleField()
	pau_submit = SubmitField(u"Add")
class project_remove_users(FlaskForm):
	users = SelectMultipleField()
	pru_submit = SubmitField(u"Remove")
class project_add_manager(FlaskForm):
	users = SelectMultipleField()
	project_id = SelectField()
	pam_submit = SubmitField(u"Add")

class project_remove_clients(FlaskForm):
	clients = SelectMultipleField()
	#send_delete = BooleanField()
	prc_submit = SubmitField(u"Remove")

class project_create_group(FlaskForm):
	group_name = StringField()
	clients = SelectMultipleField()
	pcg_submit = SubmitField(u"Create")
#class project_edit_group(FlaskForm)
class project_remove_groups(FlaskForm):
	groups = SelectMultipleField()
	prg_submit = SubmitField(u"Remove")

	
##Admin Forms
class admin_remove_users(FlaskForm):
	users = SelectMultipleField()
	aru_submit = SubmitField(u"Remove")
class admin_change_users_password(FlaskForm):
	users = SelectField()
	pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
	cpwd = PasswordField(
		validators=[
			InputRequired(),
			Length(8, 72),
			EqualTo("pwd", message="Passwords must match !")
		]
	)
	acup_submit = SubmitField(u"Change")

class admin_create_project(FlaskForm):
	project_name = StringField(validators=[
			InputRequired(),
			Length(3, 40, message="Please provide a valid name"),
			Regexp(
				"^[A-Za-z0-9_\-\ ]*$",
				0,
				"Usernames must have only letters, " "numbers, spaces, hyphens or underscores",
			),
		])
	project_users = SelectMultipleField()
	#project_managers = SelectMultipleField()
	project_listeners = SelectMultipleField()
	acp_submit = SubmitField(u"Create")
#class admin_edit_project(FlaskForm):
class admin_remove_project(FlaskForm):
	project_id = SelectField()
	arp_submit = SubmitField(u"Remove")
#class admin_remove_manager(FlaskForm):
	
class admin_remove_listeners(FlaskForm):
	listeners = SelectMultipleField()
	arl_submit = SubmitField(u"Remove")
class admin_clear_orphaned_clients(FlaskForm):
	acoc_submit = SubmitField(u"Clear")
