#!/bin/python3

def deploy():
	"""Run deployment tasks."""
	from app import create_app,db, bcrypt
	from flask_migrate import upgrade,migrate,init,stamp
	from models import _User, _Client, _Group, _Log, _Task, _Listener, _Project

	app = create_app()
	app.app_context().push()
	db.create_all()

	# add default admin account
	if not _User.query.all():
		def_admin = _User(
			user_name='admin',
			user_password=bcrypt.generate_password_hash('potluck123'),
			admin=True,
		)
		db.session.add(def_admin)
		db.session.commit()
	# migrate database to latest revision
	init()
	stamp()
	migrate()
	upgrade()
	
deploy()
