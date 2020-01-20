import sys
from subprocess import call

def transform(plain_text,k='A'):
	transformed = ""
	for x in plain_text:
		transformed += chr(ord(x)^ord(k[0]))
	return transformed

if __name__ == "__main__":
	args = sys.argv[1:]

	f = open(args[0],'r')
	text = f.read()
	print(transform(text,args[1]))
	if len(args) >= 3:
		print("sending")
		ff = open("tmp",'w')
		ff.write(transform(text,args[1]))
		ff.close()
		fname = "cipher.txt"
		if len(args) >3:
			fname = args[3]
		cmd = "sshpass -p 'cclab@123' scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null tmp cclab@{}:~/{}".format(args[2],fname)
		print(cmd)
		print(call(cmd,shell=True))
