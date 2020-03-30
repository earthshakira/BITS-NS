from __future__ import print_function
from _2019H1030502_Task_1_rsa import RSA
from bisect import bisect_left 
from random import uniform
"""
Name: Shubham Arawkar
Roll: 2019H1030502
"""

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

def simulate_secure_multiparty_computation(rsa,x,y,mx=100,M1=None,P=None):
	print("1 <= x,y <=",mx,"\n")
	print("Alice : x =",x)
	print("Bob   : y =",y,"\n")
	print("Bob   :",rsa.__str__())

	while not M1 or M1 == 2:
		M1 = get_random_prime(rsa.n);
	C = RSA.encrypt(M1,rsa.pub_key)
	C1 = (C - x)%rsa.n
	print("\nAlice : M1 =",M1,"C =",C,"C1 =",C1)
	M2 = [rsa.decrypt((C1+i)%rsa.n) for i in range(1,mx+1)]
	print("\nBob   : M2 =",M2)
	Z= []
	valid = False
	seen = set()
	while not valid:
		while not P or P in seen:
			P = get_random_prime(M1)
		seen.add(P)
		print("            checking P = ",P)
		Z= [m2%P for m2 in M2]
		valid = True

		for i,a in enumerate(Z):
			if a == 0 or a >= P-1:
					continue;
			for j,b in enumerate(Z):
				if i == j or b == 0 or b >= P-1:
					continue;
				valid = valid and abs(a-b) >= 2
		print("                 valid = ",valid)
		if not valid:
			P=None
	Zd = [z + 1 if i >= y else z for i,z in enumerate(Z)]
	print("        Z =",Z)
	print("        sending sequence =",Zd," P =",P)
	res = not Zd[x-1]%P == M1%P

	print("\nAlice : checking congruence, ",Zd[x-1],"==" if not res else "=/=",M1,"(mod",P,")")
	print("        result x>y =",res)
	print("\nBob   : x>y =",res)

rsa = RSA(11,5)
rsa.set_keys(1)

print("""
--------------------------------------------------
    Given Example in PDF:x=4, y=3, M1=39, P=31
--------------------------------------------------
""")

simulate_secure_multiparty_computation(rsa,x=4,y=3,mx=4,M1=39,P=31)

print("""
--------------------------------------------------
	         	Random Example                    
--------------------------------------------------
""")

rsa = RSA(89,97)
simulate_secure_multiparty_computation(rsa,x=1,y=5,mx=10)