from ftplib import FTP
try:
	from pyDes import *
except:
	import sys
	sys.path.append("..")
	from lib.pyDes import *
try:
	from FTP_pydes import *
except:
	import sys
	sys.path.append("..")
	from lib.FTP_pydes import *	
import os	

def ftp_connect(remotepath):
	content = open("../set/FTP_Server_ip.txt","r").read()
	y = generate_key()
	k = des(y, CBC, generate_vector(), pad=None, padmode=PAD_PKCS5)
	host = content
	first = k.decrypt(get_encrypt_code(0))
	first = first.decode('utf-8')
	second = k.decrypt(get_encrypt_code(1))
	second = second.decode('utf-8')
	
	#¶}±ÒFTPªº¸ô®|
	#remotepath="OpenData"
	f=FTP(host)
	f.login(first, second)  
	f.cwd(remotepath)	
	return f