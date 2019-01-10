from pyDes import *
from FTP_pydes import generate_key
from FTP_pydes import generate_vector
	
#reset password for use
def fixing():
	k = des(generate_key(), CBC, generate_vector(), pad=None, padmode=PAD_PKCS5)
	data = "username"
	data_en = k.encrypt(data)
	datas = "password"
	datas_en = k.encrypt(datas)
	with open("../set/FTP_Server_key.txt","wb+") as w:
		w.write(data_en)
		w.write(b'\n')
		w.write(datas_en)
		w.close()
	print("Done!")
	
if __name__ == '__main__':
	fixing()