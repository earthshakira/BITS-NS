import sys
import string
from xor_cipher import transform
import enchant

d = enchant.Dict("en_US")

def check_substr(st):
	if " " in st:
		return True
	ans = False
	for i in st:
		if i not in  string.ascii_letters:
			return False
	return True

args = sys.argv[1:]
f = open(args[0],'r')
text = f.read()
for i in string.ascii_letters:
	cipher = transform(text,i)
	if check_substr(cipher):
		print(i,cipher)

