from cryptography.fernet import Fernet

d = open("faishal_data").read()
d = d.split()
key = d[0].encode()
token = d[1].encode()
f = Fernet(key)
print("Key: ",key)
print("Token: ",token)
print("on Decryption:",f.decrypt(token))
