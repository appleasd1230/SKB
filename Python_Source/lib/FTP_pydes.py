try:
	from pyDes import *
except:
	from lib.pyDes import *
import re 
import os

def get_encrypt_code(code):
	content = open("../set/FTP_Server_key.txt","rb").read().split(b'\n')
	return content[code]

#def encode(s):
#    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

def decode(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])
	
def generate_key():
	# path = os.getcwd()
	# path = os.path.join(path,"set","GK.txt")
	fp = open("../set/GK.txt","r")
	K = fp.read()
	K = decode(K)
	return K
	
def generate_vector():
	vec = b"\x22\x34\x35\x36\x18\x11\x11\x12"
	return vec

if __name__ == '__main__':
	generate_key()
