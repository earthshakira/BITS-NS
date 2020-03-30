from __future__ import print_function
"""
Name: Shubham Arawkar
Roll: 2019H1030502
"""

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

if __name__ == "__main__":
	print("""
--------------------------------------------------
	         Random Example                    
--------------------------------------------------
	""")

	p,q = 15,13
	rsa = RSA(p,q)
	print(rsa)
	rsa.set_keys(1)
	plain = 20
	c = RSA.encrypt(plain,rsa.pub_key)
	print("Encrypt ",plain," => ",c)
	print("Decrypt ",c," => ",rsa.decrypt(c))

	print("""
--------------------------------------------------
	         String Example                    
--------------------------------------------------
	""")

	rsa = RSA(13,11)
	print(rsa)
	plain = "plain"
	c = RSA.encrypt_str(plain,rsa.pub_key)
	print("Encrypt ",plain," => ",c)
	print("Decrypt ",c," => ",rsa.decrypt_str(c))




