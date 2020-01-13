from cryptography.fernet import Fernet
key = Fernet.generate_key()
print("Key: ",key)
f = Fernet(key)
token = f.encrypt(b"Hello World")
print("Token: ",token)
print("on Decryption:",f.decrypt(token))
