from __future__ import print_function
import sys
import socket
import time
import pickle
from time import sleep
import sqlite3
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import random
import string

def rs(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def get_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    host, port = tcp.getsockname()
    tcp.close()
    return port

def get_hash(password):
	return hashlib.md5(password.encode("utf-8")).hexdigest()

SERVER_PORT = get_port()

def sqlite_conn():
	conn = sqlite3.connect('task_3.db')
	create_query = """
	CREATE TABLE IF NOT EXISTS user (
    user TEXT PRIMARY KEY,
    password TEXT NOT NULL
	)
	"""
	conn.cursor().execute(create_query)
	conn.commit()
	return conn

def create_user(user,password):
	password = get_hash(password)
	conn = sqlite_conn()
	conn.cursor().execute("INSERT INTO user VALUES(?,?)",(user,password))
	conn.commit()
	conn.close()
	return password

def get_table(user=None,hash=None):
	conn = sqlite_conn()
	op = "\n"
	op+="+-------------------------------+----------------------------------+\n"
	op+="| user                          | password                         |\n"
	op+="+-------------------------------+----------------------------------+\n"
	res = conn.cursor().execute('SELECT * FROM user where user.user = ? and user.password = ?',(user,hash)) if user else conn.cursor().execute('SELECT * FROM user')
	for row in res:
		op+="| %s\t\t\t| %s |\n"%row
	op+="+-------------------------------+----------------------------------+\n"
	conn.close()
	return op

def send_message(tag,s,d):
	msg = pickle.dumps(d)
	msg = bytes(f"{len(msg):<{10}}", 'utf-8')+msg
	s.send(msg)
	op,data = d
	print(tag,op,data)

def recv_message(s):
	msglen=0;
	while True:
		x = s.recv(10)
		if x == b'':
			continue
		msglen = int(x)
		break;
	return pickle.loads(s.recv(msglen))

def do_task(op,params):
	status = "SUCCESS"
	response = None
	try:
		if op == "REGISTER":
			user,password = params
			h = create_user(user,password)
			response = "User created with hash "+h
			
		elif op == "VERIFY":
			user,hash = params
			response = get_table(user,hash)
			if user not in response:
				response = "matching user hash pair does not exist"
				status = "NOT_FOUND"
		elif op == "TERMINATE":
			raise KeyboardInterrupt
	except Exception as e:
		if e.__class__ == KeyboardInterrupt:
			raise e
		status,response =  e.__class__.__name__,str(e)
	return status,response

def server(port):
	print("Server Thread Started")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostname(), port))
	s.listen(5)
	try:
		clientsocket, address = s.accept()
		print("Server : CONN => ",address)
		while True:
			request = recv_message(clientsocket)
			op,params = request
			status,response = do_task(op,params)
			send_message("Server :",clientsocket,(status,response))
	except KeyboardInterrupt: #used to close the server
		s.close()
		return "Server Terminated"
	except Exception as e:
		return e


def client(params):
	print("Client Thread Started")

	port,user,password,verify = params
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True:
		try:
			s.connect((socket.gethostname(), port))
			break
		except ConnectionRefusedError:
			sleep(1)

	send_message("Client :",s,("REGISTER",(user,password)))
	status,response = recv_message(s)
	send_message("Client :",s,("VERIFY",(user,verify)))
	status,response = recv_message(s)
	send_message("Client :",s,("VERIFY",(user,"random_str_so_no_user_should_exist")))
	status,response = recv_message(s)
	send_message("Client :",s,("TERMINATE",None))
	s.close()
	return "Client Terminated"

if __name__ == '__main__':
	executor = ThreadPoolExecutor(3)
	user = rs(6)
	password = rs(6)
	hash = get_hash(password)
	s,c = executor.submit(server, (SERVER_PORT)), executor.submit(client, (SERVER_PORT,user,password,hash))
	print("\n\n{}".format(c.result()))
	print(s.result())
	print("\n\nUsers Table:")
	print(get_table())