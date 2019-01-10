#coding:utf-8
from bs4 import BeautifulSoup as bs4
from ftplib import FTP
import getpass, os.path
import requests
#import sys
import re
#import schedule
import xlrd
#import codecs
#import json
import time
import pandas as pd
import logging
import logging.handlers
from datetime import date, timedelta
import sys
sys.path.append("..")
from lib.pyDes import *
from lib.FTP_pydes import *
from lib.FTP_connection import *

logging.basicConfig(level=logging.INFO,
					format='[%(asctime)-4s] %(message)s',
					datefmt='%Y-%m-04 %H:%M:%S ',
					handlers = [logging.FileHandler('Log\Spiders'+'.log', 'a', 'utf-8'),]
					)


def get_xls(currency):
	if currency == "TWD":	
		URL = 'http://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond//'+time.strftime('%Y', time.localtime())+'/'+time.strftime('%Y%m', time.localtime())+'/COCurve.'+time.strftime('%Y%m%d', time.localtime())+'-c.xls'
	else:
		URL = 'http://www.tpex.org.tw/storage/bond_zone/tradeinfo/internationalbond//'+time.strftime('%Y', time.localtime())+'/'+time.strftime('%Y%m', time.localtime())+'/USDDIBCurve.'+time.strftime('%Y%m%d', time.localtime())+'.xls'
	r = requests.get(URL)
	soup = bs4(r.text, 'html.parser')
	try:
		a = soup.find(class_ = 'header_text01_over').text
		if currency == "TWD":
			print(time.strftime('%Y%m%d', time.localtime())+'台幣公司債還沒有提供檔案')
			logging.exception(time.strftime('%Y%m%d', time.localtime())+'台幣公司債還沒有提供檔案')
		else:
			print(time.strftime('%Y%m%d', time.localtime())+'美元國際債券還沒有提供檔案')
			logging.exception(time.strftime('%Y%m%d', time.localtime())+'美元國際債券還沒有提供檔案')
		CsvName = 'AddOnRate_' + currency + '_' + time.strftime('%Y%m%d', time.localtime())
		df = pd.DataFrame(data=[], columns=[])
		df.to_csv('data/csv/' + CsvName+'.csv', sep=',', encoding='utf-8', index=False)
	except:
		logging.info("Grab the " + currency + "_xls form web Success!")
		write_xls_Files(currency, r)

def write_xls_Files(curreny, xls_):
	if curreny == "TWD":
		fileName = 'COCurve' + time.strftime('%Y%m%d', time.localtime())
		output = open('data/xls/' + fileName + '.xls','wb')
		output.write(xls_.content)
		output.close()
		logging.info("Write and save " + fileName + ".xls Success!")
		get_TWD_xls_content(fileName)
	else:
		fileName = 'USDDIBCurve' + time.strftime('%Y%m%d', time.localtime())
		output = open('data/xls/' + fileName + '.xls','wb')
		output.write(xls_.content)
		output.close()
		logging.info("Write and save " + fileName + ".xls Success!")
		get_USD_xls_content(fileName)
		
def get_TWD_xls_content(fileName):
	try:
		data = xlrd.open_workbook('data/xls/' + fileName + '.xls')
		table = data.sheet_by_name(u'COCurve')
		rows = table.row_values(5)
		rows.insert(0,time.strftime('%Y%m%d', time.localtime()))
		csv_ = []
		csv_.append(rows)
		logging.info("Get data from " + fileName + ".xls Success!")
		write_TWD_csv(csv_)
	except:
		global times
		times += 1
		logging.exception("Get data from " + fileName + ".xls failed!The problem is :")
		ReRun(times,"TWD")
			
def get_USD_xls_content(fileName):
	try:
		data = xlrd.open_workbook('data/xls/' + fileName + '.xls')
		table = data.sheet_by_name(u'USDDIBCurve')
		rows = table.row_values(10)
		rows.insert(0,time.strftime('%Y%m%d', time.localtime()))
		csv_ = []
		csv_.append(rows)
		logging.info("Get data from " + fileName + ".xls Success!")
		write_USD_csv(csv_)	
	except:
		global times
		times += 1
		logging.exception("Get data from " + fileName + ".xls failed!The problem is :")
		ReRun(times,"USD")
		
def write_TWD_csv(Content):
	try:
		CsvName = 'AddOnRate_TWD_' + time.strftime('%Y%m%d', time.localtime())
		df = pd.DataFrame(data=Content, columns=['Date', 'Confident_Rank', '1M', '3M', '6M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y'])
		df.to_csv('data/csv/' + CsvName+'.csv', sep=',', encoding='utf-8', index=False)
		logging.info("Generate " + CsvName + ".csv Success!")
	except:
		logging.exception("Failed when Generate the " + CsvName + ".csv!The problem is :")

def write_USD_csv(Content):
	try:
		CsvName = 'AddOnRate_USD_' + time.strftime('%Y%m%d', time.localtime())
		df = pd.DataFrame(data=Content, columns=['Date', 'Confident_Rank', '6M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y', '11Y', '12Y', '13Y', '14Y', '15Y', '16Y', '17Y', '18Y','19Y','20Y','21Y','22Y','23Y','24Y','25Y','26Y','27Y','28Y','29Y','30Y'])
		df.to_csv('data/csv/' + CsvName+'.csv', sep=',', encoding='utf-8', index=False)
		logging.info("Generate " + CsvName + ".csv Success!")
	except:
		logging.exception("Failed when Generate the " + CsvName + ".csv!The problem is :")
		
def Generate_WatchFile():
	fileName = 'Readme_' + time.strftime('%Y%m%d', time.localtime())
	output = open('data/txt/' + fileName + '.txt','wb')
	output.close()
	
def Ftp_upload():
	try:
		remotepath="OpenData"
		f = ftp_connect(remotepath)
		#AddOnRate_USD_csv
		localfile='data/csv/' + 'AddOnRate_USD_' + time.strftime('%Y%m%d', time.localtime()) + '.csv'
		fd=open(localfile,'rb')
		print(os.path.basename(localfile))     
		f.storbinary('STOR %s ' % os.path.basename(localfile),fd)
		#AddOnRate_TWD_csv
		localfile='data/csv/' + 'AddOnRate_TWD_' + time.strftime('%Y%m%d', time.localtime()) + '.csv'  
		fd=open(localfile,'rb')
		print(os.path.basename(localfile))
		f.storbinary('STOR %s ' % os.path.basename(localfile),fd)
		#WatchFile
		Generate_WatchFile()
		localfile='data/txt/' + 'Readme_' + time.strftime('%Y%m%d', time.localtime()) + '.txt'
		fd=open(localfile,'rb')
		print(os.path.basename(localfile)) 
		f.storbinary('STOR %s ' % os.path.basename(localfile),fd)
		fd.close()   
		f.quit
		logging.info("Upload the files to FTP success!")
		print("Upload the files to FTP success!")
		time.sleep(3)
	except:
		logging.exception("Failed when Upload the files to FTP!The problem is :")
	
def clearLog():
	with open("Log/Spiders.log", "w") as file:
		file.truncate()

def ReRun(times,ccy):
	if times < 4:
		logging.info("Rerunning times : " + str(times))
		print("Rerunning times : " + str(times))
		get_xls(ccy)
		
if __name__ == '__main__':
	times = 0
	clearLog()
	get_xls("TWD")
	get_xls("USD")
	Ftp_upload()
	#schedule.every().day.at("17:00").do(get_xls)
	#schedule.every().day.at("23:00").do(get_xls)
	#print('Next Run: ' + time.strftime('%Y/%m/04 %H:%M:%S', schedule.next_run().timetuple()) + '\n')
	#while True:
		#schedule.run_pending()
		
#generate json
"""
def get_TWD_xls_content(fileName):
	data = xlrd.open_workbook('xls/' + fileName + '.xls')
	table = data.sheet_by_name(u'COCurve')
	rows = table.row_values(5)
	rows.insert(0,time.strftime('%Y%m%d', time.localtime()))
	reviewDict = {
		'Data_Date' : rows[0],
		'Rank' : rows[1],
		'one_month' : rows[2],
		'three_month' : rows[3],
		'six_month' : rows[4],
		'one_year' : rows[5],
		'two_year' : rows[6],
		'three_year' : rows[7],
		'four_year' : rows[8],
		'five_year' : rows[9],
		'six_year' : rows[10],
		'seven_year' : rows[11],
		'eight_year' : rows[12],
		'nine_year' : rows[13],
		'ten_year' : rows[14]
	}
	listjson = []
	listjson.append(reviewDict)
	with codecs.open('json/' + 'AddOnRate_TWD' + time.strftime('%Y%m%d', time.localtime()) + '.json', 'wb', encoding='utf-8') as outfile:
		json.dump(listjson, outfile, ensure_ascii=False)
	Adown_ = []
	Adown_.append(rows)
	write_TWD_Files(Adown_)

def get_USD_xls_content(fileName):
	data = xlrd.open_workbook('xls/' + fileName + '.xls')
	table = data.sheet_by_name(u'USDDIBCurve')
	rows = table.row_values(10)
	rows.insert(0,time.strftime('%Y%m%d', time.localtime()))
	reviewDict = {
		'Data_Date' : rows[0],
		'Rank' : rows[1],
		'six_month' : rows[2],
		'one_year' : rows[3],
		'two_year' : rows[4],
		'three_year' : rows[5],
		'four_year' : rows[6],
		'five_year' : rows[7],
		'six_year' : rows[8],
		'seven_year' : rows[9],
		'eight_year' : rows[10],
		'nine_year' : rows[11],
		'ten_year' : rows[12],
		'eleven_year' : rows[13],
		'twelve_year' : rows[14],
		'thirteen_year' : rows[15],
		'fourteen_year' : rows[16],
		'fifteen_year' : rows[17],
		'sixteen_year' : rows[18],
		'seventeen_year' : rows[19],
		'eighteen_year' : rows[20],
		'nineteen_year' : rows[21],
		'twenty_year' : rows[22],
		'twenty-one_year' : rows[23],
		'twenty-two_year' : rows[24],
		'twenty-three_year' : rows[25],
		'twenty-four_year' : rows[26],
		'twenty-five_year' : rows[27],
		'twenty-six_year' : rows[28],
		'twenty-seven_year' : rows[29],
		'twenty-eight_year' : rows[30],
		'twenty-nine_year' : rows[31],
		'thirty_year' : rows[32]
	}
	listjson = []
	listjson.append(reviewDict)
	with codecs.open('json/' + 'AddOnRate_USD_' + time.strftime('%Y%m%d', time.localtime()) + '.json', 'wb', encoding='utf-8') as outfile:
		json.dump(listjson, outfile, ensure_ascii=False)
	Adown_ = []
	Adown_.append(rows)
	write_USD_Files(Adown_)
"""