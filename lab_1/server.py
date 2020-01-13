from cryptography.fernet import Fernet
key = Fernet.generate_key()
print("Key: ",key)
f = Fernet(key)
token = f.encrypt(b"shubham's data")
with open("key","w") as f:
	f.write(key.decode("utf-8"))
	f.close()

with open("data","w") as f:
	f.write(token.decode("utf-8"))
	f.close()

print("Token: ",token)
