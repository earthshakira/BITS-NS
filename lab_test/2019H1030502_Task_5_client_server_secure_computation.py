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
from bisect import bisect_left
from time import sleep
from random import uniform

class RSA:
	@classmethod
	def gcd(cls,a,b):
		if (a%b):
			return cls.gcd(b,a%b)
		return b

	@classmethod
	def mod_inv(cls,a,m):
		for i in range(2,m):
			if (a*i)%m == 1:
				return i
		return None
	
	@classmethod
	def generate(cls,phi):
		pairs = []
		for pub in range(2,phi):
			if (cls.gcd(pub,phi) == 1):
				pair = (pub,cls.mod_inv(pub,phi))
				if pair[1]:
					pairs.append(pair)
		return pairs
	
	def __init__(self,p,q):
		self.n = p*q
		self.phi = (p-1) * (q-1)
		self.key_pairs = RSA.generate(self.phi)
		self.set_keys(2)

	def set_keys(self,i):
		assert i < len(self.key_pairs)
		self.keys = self.key_pairs[i]
		self.pub_key = (self.keys[0],self.n)
		self.priv_key = (self.keys[1],self.n)

	@classmethod
	def encrypt(cls,m,pub_key):
		e,n = pub_key
		assert m < n
		return pow(m,e,n)

	@classmethod
	def encrypt_str(cls,m,pub_key):
		cipher_text = ""
		nums = []
		for i in m:
			nums.append(cls.encrypt(ord(i),pub_key))
			cipher_text += chr(cls.encrypt(ord(i),pub_key))
		return cipher_text

	def decrypt(self,c):
		return RSA.encrypt(c,self.priv_key)
	
	def decrypt_str(self,c):
		return RSA.encrypt_str(c,self.priv_key)
	def __str__(self):
		return "RSA{{ public_key={}, private_key={}, n={}}}".format(self.keys[0],self.keys[1],self.n)



def get_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    host, port = tcp.getsockname()
    tcp.close()
    return port

SERVER_PORT = get_port()

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


def make_primes(pr):
	N = 10000
	lp = [0] * (N+1)
	for i in range(2,N+1):
	    if (lp[i] == 0):
	        lp[i] = i;
	        pr.append(i)
	    j = 0
	    while  j< len(pr) and pr[j]<=lp[i] and i*pr[j]<=N :
	        lp[i * pr[j]] = pr[j];
	        j+=1



def get_random_prime(N,primes=[]):
	if not primes:
		make_primes(primes)
	t = primes[:bisect_left(primes,N)]
	return t[int(uniform(0,len(t)))]


def server(port):
	print("Server Thread Started")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostname(), port))
	s.listen(5)
	alice = None
	bob = None
	try:
		while not (alice and bob):
			clientsocket, address = s.accept()
			print("Server           : CONN => ",address)
			request = recv_message(clientsocket)
			op,params = request
			if op == 'REGISTER':
				if params[0] == 'alice':
					alice = (clientsocket,params[1])
				else:
					bob = (clientsocket,params[1])
		send_message("Server -> Alice  :",alice[0],("SUCCESS",bob[1]))
		status,message = recv_message(alice[0])
		send_message("Server -> Bob    :",bob[0],(status,message))
		status,message = recv_message(bob[0])
		send_message("Server -> Alice  :",alice[0],(status,message))
		status,message = recv_message(alice[0])
		send_message("Server -> Bob    :",bob[0],(status,message))
		status,message = recv_message(bob[0])
		s.close()
		return "Server Terminated"
	except Exception as e:
		print(e)
		return e


def alice_thread(params):
	try:
		print("Alice Thread Started")
		port,rsa,x,mx,M1 = params
		print("{:17s}:".format("Alice"),"x =",x,"\n")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		while True:
			try:
				s.connect((socket.gethostname(), port))
				sleep(1)
				break
			except ConnectionRefusedError:
				sleep(1)
		
		send_message("Alice  -> Server :",s,("REGISTER",('alice',rsa.pub_key)))
		status,response = recv_message(s)
		bob_pub_key = response
		pad = 0 if M1 else int(uniform(1,M1/2))
		while not M1 or M1 == 2:
			M1 = get_random_prime(rsa.n);

		C = RSA.encrypt(M1,bob_pub_key)
		C1 = (C - x)%rsa.n
		print("{:17s}:".format("Alice"),"M1 =",M1,"C =",C,"C1 =",C1,"\n")
		send_message("Alice  -> Server :",s,("C1,Mlim",(C1,M1 - pad)))
		status,response = recv_message(s)
		Zd = response
		res = not Zd[x-1]%P == M1%P
		print("{:17s}:".format("Alice"),"checking congruence, ",Zd[x-1],"==" if not res else "=/=",M1,"( mod",P,")")
		send_message("Alice  -> Server :",s,("x > y",(res)))
		s.close()
	except Exception as e:
		print('Alice:',e)
	return "Alice Thread Terminated"

def bob_thread(params):
	print("Bob Thread Started")
	try:
		port,rsa,y,mx,P = params
		print("{:17s}:".format("Bob"),"y =",y,"\n")
		print("{:17s}:".format("Bob"),rsa,"\n")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		while True:
			try:
				s.connect((socket.gethostname(), port))
				sleep(1)
				break
			except ConnectionRefusedError:
				sleep(1)
		
		send_message("Bob    -> Server :",s,("REGISTER",('bob',rsa.pub_key)))
		status,response = recv_message(s)
		C1,Mlim = response
		M2 = [rsa.decrypt((C1+i)%rsa.n) for i in range(1,mx+1)]
		print("{:17s}:".format("Bob"),"M2 =",M2,"\n")
		print("{:17s}:".format("Bob"),rsa,"\n")
		Z= []
		valid = False
		seen = set()
		while not valid:
			while not P or P in seen:
				P = get_random_prime(M1)
			seen.add(P)
			print("{:17s}".format(""),"checking P = ",P)
			Z= [m2%P for m2 in M2]
			valid = True
			for i,a in enumerate(Z):
				if a == 0 or a >= P-1:
						continue;
				for j,b in enumerate(Z):
					if i == j or b == 0 or b >= P-1:
						continue;
					valid = valid and abs(a-b) >= 2
			print("{:17s}".format(""),"valid = ",valid)
			if not valid:
				P=None
		print("{:17s}:".format("Bob"),"Z =",Z,"\n")
		Zd = [z + 1 if i >= y else z for i,z in enumerate(Z)]
		send_message("Bob    -> Server :",s,("Zd",Zd))
		status,response = recv_message(s)
		send_message("Bob    -> Server :",s,("TERMINATE",None))
	except Exception as e:
		print('Bob :',e)
	return "Bob Thread Terminated"

if __name__ == '__main__':
	executor = ThreadPoolExecutor(5)
	b_rsa = RSA(11,5)
	b_rsa.set_keys(1)
	a_rsa = RSA(11,13)
	a_rsa.set_keys(1)
	x = 4
	y = 2
	mx = 4
	M1 = 39
	P = 31
	s = executor.submit(server, (SERVER_PORT))
	a = executor.submit(alice_thread, (SERVER_PORT,a_rsa,x,mx,M1))
	b = executor.submit(bob_thread, (SERVER_PORT,b_rsa,y,mx,P))
	print(s.result())
	print(a.result())
	print(b.result())