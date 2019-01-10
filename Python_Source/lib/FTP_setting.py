try:
	from pyDes import *
except:
	from lib.pyDes import *
try:
	from FTP_pydes import *
except:
	from lib.FTP_pydes import *
import re 

def get_decrypt_code():
	k = des(generate_key(), CBC, generate_vector(), pad=None, padmode=PAD_PKCS5)
	content = open("../set/FTP_Server_key.txt","rb").read().split(b'\n')
	first = k.decrypt(content[0])
	first = first.decode('utf-8')
	second = k.decrypt(content[1])
	second = second.decode('utf-8')
	print("The FTP Server setting Now is : \nusername : %s\npassword : %s" % (first, second))

def FTP_server_setting(answer):
	if answer == "Y" or answer == "y":
		print("********** Don't use the  \"\\\" **********")
		ac = input("reset the FTP Server account : ")
		pd = input("reset the FTP Server password : ")
		writeDes(ac, pd)
		get_decrypt_code()
		final_check()
	elif answer == "N" or answer == "n":
		print("Keepping uses old FTP Server setting!")
	else:
		flag = input("Do you sure to reset the FTP Server setting?[Y/N] ")
		FTP_server_setting(flag)

def writeDes(ac, pd):
	with open("../set/FTP_Server_key.txt", "wb+")as w:
		w.write(stringTobytes(ac))
		w.write(b'\n')
		w.write(stringTobytes(pd))
		w.close()
	
def stringTobytes(by):
	k = des(generate_key(), CBC, generate_vector(), pad=None, padmode=PAD_PKCS5)
	by = k.encrypt(by)
	return by

def final_check():
	check = input("Do you sure to set the FTP Server setting above as your new setting?[Y/N] ")
	if check == "Y" or check == "y":
		print("Reset complete!")
	elif check == "N" or check == "n":
		resetting()
	else:
		final_check()
		
def resetting():
	k = des(generate_key(), CBC, generate_vector(), pad=None, padmode=PAD_PKCS5)
	print("********** Don't use the  \"\\\" **********")
	data = str(input("Enter the username : "))
	data_en = k.encrypt(data)
	datas = str(input("Enter the password : "))
	datas_en = k.encrypt(datas)
	with open("../set/FTP_Server_key.txt","wb+") as w:
		w.write(data_en)
		w.write(b'\n')
		w.write(datas_en)
		w.close()
	print("Reset complete!")
		
def get_encrypt_code(code):
	content = open("set/FTP_Server_key.txt","rb").read().split(b'\n')
	return content[code]
	
if __name__ == '__main__':
	print("******************************************************************")
	print("If any problem occur, just use the fixing.bat to solve it!")
	print("******************************************************************")
	get_decrypt_code()
	flag = input("Do you sure to reset the FTP Server setting?[Y/N] ")
	FTP_server_setting(flag)
		