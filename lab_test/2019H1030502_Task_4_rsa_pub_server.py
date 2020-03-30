from __future__ import print_function
from _2019H1030502_Task_1_rsa import RSA
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

def get_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    host, port = tcp.getsockname()
    tcp.close()
    return port

SERVER_PORT = get_port()

def sqlite_conn():
	conn = sqlite3.connect('task_4.db')
	create_query = """
	CREATE TABLE IF NOT EXISTS user (
    user TEXT PRIMARY KEY,
    pub_key TEXT NOT NULL
	)
	"""
	conn.cursor().execute(create_query)
	conn.commit()
	return conn

def add_pub_key(user,pub_key):
	conn = sqlite_conn()
	conn.cursor().execute("INSERT or REPLACE INTO user VALUES(?,?)",(user,str(pub_key).replace('(','[').replace(')',']')))
	conn.commit()
	conn.close()

def query_pub_key(user):
	conn = sqlite_conn()
	res = conn.cursor().execute('SELECT * FROM user where user.user = ?',(user,))
	row = res.fetchone()
	return row

def get_table(user=None,hash=None):
	conn = sqlite_conn()
	op = ""
	op+="+----------------+-----------------+\n"
	op+="| user           | pub_key         |\n"
	op+="+----------------+-----------------+\n"
	res = conn.cursor().execute('SELECT * FROM user where user.user = ? and user.pub_key = ?',(user,hash)) if user else conn.cursor().execute('SELECT * FROM user')
	for row in res:
		op+="| {:15s}| {:15s} |\n".format(row[0],row[1])
	op+="+----------------+-----------------+\n"
	conn.close()
	return op

def send_message(tag,s,d):
	msg = pickle.dumps(d)
	msg = bytes(f"{len(msg):<{10}}", 'utf-8')+msg
	s.send(msg)
	op,data = d
	if not data:
		data = ""
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
			user,pub_key = params
			add_pub_key(user,pub_key)
			response = "added entry "+str((user,pub_key))
		elif op == "QUERY":
			user = params
			response = query_pub_key(user)
			if not response:
				response = "matching user does not exist"
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

	port,user,rsa,queries = params

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True:
		try:
			s.connect((socket.gethostname(), port))
			break
		except ConnectionRefusedError:
			sleep(1)

	send_message("Client :",s,("REGISTER",(user,rsa.pub_key)))
	status,response = recv_message(s)
	for q in queries:
		send_message("Client :",s,("QUERY",q))
		status,response = recv_message(s)
	send_message("Client :",s,("TERMINATE",None))
	s.close()
	return "Client Terminated"

if __name__ == '__main__':
	executor = ThreadPoolExecutor(3)
	queries = ["bob","cathy","nancy"]
	rsa = RSA(19,17)
	for i,user in enumerate(queries):
		add_pub_key(user,rsa.pub_key)
		rsa.set_keys(3*i)
	user = "alice"
	s,c = executor.submit(server, (SERVER_PORT)), executor.submit(client, (SERVER_PORT,user,rsa,queries))
	print("\n\n{}".format(c.result()))
	print(s.result())
	print("\n\nUsers Table:")
	print(get_table())