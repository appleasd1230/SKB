from datetime import date, timedelta
import math
import datetime
import time as t
import json
import re
import pyodbc
import pandas as pd
import logging
import logging.handlers

logging.basicConfig(level=logging.INFO,
					format='[%(asctime)-4s] %(message)s',
					datefmt='%Y-%m-%d %H:%M:%S ',
					handlers = [logging.FileHandler('PythonSrc/Boostrapping/Log/boostapping_main.log', 'a', 'utf-8'),]
					)
class FTP(object):

	def __init__(self):
		self.instruments = dict()  # Map each T to an instrument

	def add_instrument(self, SEQ_NO, market, TRM_DAYS, adj, zero_spot, DF_spot, DAY_DF, flag, DATA_DT, currency, TRM_DATE, DF_Today, Zero_Today):
		self.instruments[SEQ_NO] = (round(market,7), TRM_DAYS, round(adj,7), zero_spot, DF_spot, DAY_DF, flag, DATA_DT, currency, TRM_DATE, DF_Today, Zero_Today)
		
	def get_base_rates(self):
		"""  Calculate a list of available zero rates """
		self.interpolation()
		self.get_Zero_Spot()
		self.get_DF_Spot()
		self.bootstapping()
		self.get_DF_Spot_prev()
		self.get_DF_Today()
		self.get_Zero_Today()
		ContentList_data_dt = []
		ContentList_currency = []
		ContentList_trm_days = []
		ContentList_Zero_Today = []
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today) = self.instruments[SEQ_NO]
			ContentList_data_dt.append(data_dt)
			ContentList_currency.append(currency)
			ContentList_trm_days.append(trm_days)
			ContentList_Zero_Today.append(Zero_Today)
		writeFile(ContentList_data_dt,ContentList_currency,ContentList_trm_days,ContentList_Zero_Today)
		self.clear_dict()

	def clear_dict(self):
		i = 1
		for SEQ_NO in self.instruments.keys():
			if i < SEQ_NO:
				i += 1
		while i > 0:
			del self.instruments[i]
			i -= 1

	def get_DF_Spot(self):
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)  = self.instruments[SEQ_NO]
			d1 = datetime.datetime.strptime(trm_date, "%Y-%m-%d")
			d2 = datetime.datetime.strptime(self.instruments[2][9], "%Y-%m-%d")
			days_ = (d1-d2).days
			DF_spot = 1/(1+zero_spot/get_days(currency)/100*days_)
			self.instruments[SEQ_NO] = (market, trm_days, adj, zero_spot, round(DF_spot,12), day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today) 

	def get_Zero_Spot(self):
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)  = self.instruments[SEQ_NO]
			Zero_Spot = adj
			self.instruments[SEQ_NO] = (market, trm_days, adj, Zero_Spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)

	def interpolation(self):
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)  = self.instruments[SEQ_NO]
			if adj == 0:
				last_day = datetime.datetime.strptime(self.instruments[SEQ_NO-1][9], "%Y-%m-%d")
				today = datetime.datetime.strptime(self.instruments[SEQ_NO][9], "%Y-%m-%d")
				ADJ = self.instruments[SEQ_NO-1][2] + (self.get_next_adj(SEQ_NO)-self.instruments[SEQ_NO-1][2])/(self.get_next_days(SEQ_NO)-last_day).days*(today-last_day).days
				self.instruments[SEQ_NO] = (round(ADJ,12), trm_days, round(ADJ,12), zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)
			else:
				pass

	def get_DF_Spot_prev(self):
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)  = self.instruments[SEQ_NO]
			if SEQ_NO < 3:
				d1 = datetime.datetime.strptime(trm_date, "%Y-%m-%d")
				d2 = datetime.datetime.strptime(data_dt, "%Y-%m-%d")
				days = (d1-d2).days
				DF_spot = 1/(1+zero_spot/get_days(currency)/100*days)
				self.instruments[SEQ_NO] = (market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, round(DF_Today,12), Zero_Today)

	def get_next_adj(self, SEQ_NO):
		while self.instruments[SEQ_NO][2] == 0:
			SEQ_NO += 1
		return self.instruments[SEQ_NO][2]

	def get_next_days(self, SEQ_NO):
		while self.instruments[SEQ_NO][2] == 0:
			SEQ_NO += 1
		d1 = datetime.datetime.strptime(self.instruments[SEQ_NO][9], "%Y-%m-%d")
		return d1

	def bootstapping(self):
		i = 0
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)  = self.instruments[SEQ_NO]
			if flag == 1:
				i += 1
				if i == 1:
					last = SEQ_NO
				if i >= 2:
					Diff = self.get_diff(SEQ_NO)
					ADJ = adj
					while Diff >= 0.00005:					
						self.instruments[SEQ_NO] = (market, trm_days, ADJ, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today)
						x = SEQ_NO
						while last != x-1:
							self.instruments[x-1] = (0, self.instruments[x-1][1], 0, 0, 0, self.instruments[x-1][5], self.instruments[x-1][6], self.instruments[x-1][7], self.instruments[x-1][8], self.instruments[x-1][9], 0, 0)
							x -= 1
						self.interpolation()
						self.get_Zero_Spot()
						self.get_DF_Spot()				
						Diff = self.get_diff(SEQ_NO)
						if Diff >= 0.00005:
							ADJ += Diff/1000000
						elif Diff < -0.00005:
							ADJ -= ADJ - Diff/1000000
					last = SEQ_NO

	def get_diff(self, SEQ_NO):
		return (self.get_cf_pv(SEQ_NO)-(1-self.instruments[SEQ_NO][4]))*1000000

	def get_cf_pv(self, SEQ_NO):
		i = 1
		d1 = datetime.datetime.strptime(self.instruments[1][9], "%Y-%m-%d") 
		while (datetime.datetime.strptime(self.instruments[i][9], "%Y-%m-%d")-d1).days < 90:
			i += 1
		sumproduct = 0
		while i <= SEQ_NO:
			sumproduct += self.instruments[i][4]*self.instruments[i][5]
			i += 1
		return self.instruments[SEQ_NO][0] * sumproduct / get_days(self.instruments[SEQ_NO][8]) / 100

	def get_DF_Today(self):
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today) = self.instruments[SEQ_NO]
			if SEQ_NO < 3:
				DF_Today = self.instruments[SEQ_NO][4]
			else:
				DF_Today = self.instruments[SEQ_NO][4]*self.instruments[2][4]
			self.instruments[SEQ_NO] = (market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, round(DF_Today,12), Zero_Today)

	def get_Zero_Today(self):
		for SEQ_NO in self.instruments.keys():
			(market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, Zero_Today) = self.instruments[SEQ_NO]
			d1 = datetime.datetime.strptime(trm_date, "%Y-%m-%d")
			d2 = datetime.datetime.strptime(data_dt, "%Y-%m-%d")
			days = (d1-d2).days
			Zero_Today = (1/DF_Today-1)*get_days(currency)*100/days
			self.instruments[SEQ_NO] = (market, trm_days, adj, zero_spot, DF_spot, day_df, flag, data_dt, currency, trm_date, DF_Today, round(Zero_Today,12))

def get_days(currency):
	if currency == "TWD":
		return 365
	else:
		return 360

def turn_type(number):
	if number == 0:
		number = int(number)
	else:
		number = float(number)
	return number

def writeFile(ContentList_data_dt,ContentList_currency,ContentList_trm_days,ContentList_Zero_Today):
	for i in range(0,len(ContentList_data_dt)):
	#cursor.execute("delete from ADMIN.BASE_RATE_SG2 where DATA_DT='2017-09-01';")
		cursor2.execute("insert into ADMIN.BASE_RATE_SG2 values("+"'"+ContentList_data_dt[i]+"'"+","+"'"+ContentList_currency[i]+"'"+","+str(ContentList_trm_days[i])+","+str(ContentList_Zero_Today[i])+")")
	cnxn.commit()
	cnxn.close()
	
def delete_data():
	today = date.today().timetuple()
	yesterday = (date.today() - timedelta(1)).timetuple()
	cnxn = pyodbc.connect('DSN=NZ_BDW;Trusted_Connection=yes')
	cursor = cnxn.cursor()
	cursor.execute("delete from ADMIN.BASE_RATE_SG2 where DATA_DT='"+t.strftime('%Y-%m-%d', yesterday)+"';")
	cnxn.commit()
	cnxn.close()
	print("delete "+t.strftime('%Y-%m-%d', yesterday)+" Data success")
	
def clearLog():
	with open("PythonSrc/Boostrapping/Log/boostapping_main.log", "w") as file:
		file.truncate()

if __name__ == '__main__':
	#(   0  ,   1   ,     2   ,  3 ,     4    ,    5   ,   6   ,  7  ,    8   ,  9 ,    10   ,    11   ,     12    )
	#(SEQ_NO, market, TRM_DAYS, adj, zero_spot, df_spot, DAY_DF, flag, data_dt, ccy, TRM_DATE, df_today, zero_today)
	clearLog()
	ftp_rate = FTP()
	today = date.today().timetuple()
	yesterday = (date.today() - timedelta(1)).timetuple()
	try:
		delete_data()
		logging.info("delete "+t.strftime('%Y-%m-%d', yesterday)+" Data success!")
	except:
		logging.exception("Failed delete "+t.strftime('%Y-%m-%d', yesterday)+" Data, The problem is : ")
		print("Failed delete "+t.strftime('%Y-%m-%d', yesterday)+" Data!")	
	cnxn = pyodbc.connect('DSN=NZ_BDW;Trusted_Connection=yes')
	cursor = cnxn.cursor()
	cursor2 = cnxn.cursor()
	cursor.execute("select a.SEQ_NO,nvl(a.MARKET_RATE,0) as MARKET_RATE,nvl(a.TRM_DAYS,0) as TRM_DAYS,nvl(a.MARKET_RATE,0) as ADJ,nvl(a.DAY_DF,0) as DAY_DF,a.DATA_DT,a.CCY,a.TRM_DATE,case when a.SEQ_NO<10 then 0 when a.SEQ_NO=10 then 1 when a.MARKET_RATE is null then 0 when a.MARKET_RATE is not null then 1 end flag from ADMIN.base_rate_sg1 a where a.DATA_DT='"+t.strftime('%Y-%m-%d', yesterday)+"' and a.CCY='TWD' order by a.CCY asc,a.SEQ_NO asc;")
	rc = cursor.rowcount
	if rc == 0:
		logging.info(t.strftime('%Y-%m-%d', yesterday)+" TWD_Data not found!")
		print(t.strftime('%Y-%m-%d', yesterday)+" TWD_Data not found!")
		cnxn.close()
	else:
		for i in range(0, rc):
			record = cursor.fetchone()
			SEQ_NO = record[0]
			MARKET_RATE = record[1]
			TRM_DAYS = record[2]
			ADJ = record[3]
			Zero_Spot = 0
			Df_Spot = 0
			DAY_DF = record[4]
			Flag = record[8]
			Data_DT = record[5]
			CCY = record[6]
			TRM_DATE = record[7]
			Df_Today = 0
			Zero_Today = 0
			ftp_rate.add_instrument(int(SEQ_NO), turn_type(MARKET_RATE), int(TRM_DAYS), turn_type(ADJ), Zero_Spot, Df_Spot, int(DAY_DF), int(Flag), str(Data_DT), CCY, str(TRM_DATE), Df_Today, Zero_Today)
		try:
			ftp_rate.get_base_rates()
			logging.info("insert "+t.strftime('%Y-%m-%d', yesterday)+" TWD_Data success!")
			print("insert "+t.strftime('%Y-%m-%d', yesterday)+" TWD_Data success!")
		except:
			logging.exception("Failed insert "+t.strftime('%Y-%m-%d', yesterday)+" TWD_Data, The problem is : ")
			print("Failed insert "+t.strftime('%Y-%m-%d', yesterday)+" TWD_Data")
		
	cnxn = pyodbc.connect('DSN=NZ_BDW;Trusted_Connection=yes')
	cursor = cnxn.cursor()
	cursor2 = cnxn.cursor()
	cursor.execute("select a.SEQ_NO,nvl(a.MARKET_RATE,0) as MARKET_RATE,nvl(a.TRM_DAYS,0) as TRM_DAYS,nvl(a.MARKET_RATE,0) as ADJ,nvl(a.DAY_DF,0) as DAY_DF,a.DATA_DT,a.CCY,a.TRM_DATE,case when a.SEQ_NO<10 then 0 when a.SEQ_NO=10 then 1 when a.MARKET_RATE is null then 0 when a.MARKET_RATE is not null then 1 end flag from ADMIN.base_rate_sg1 a where a.DATA_DT='"+t.strftime('%Y-%m-%d', yesterday)+"' and a.CCY='USD' order by a.CCY asc,a.SEQ_NO asc;")
	rc = cursor.rowcount
	if rc == 0:
		logging.info(t.strftime('%Y-%m-%d', yesterday)+" USD_Data not found!")
		print(t.strftime('%Y-%m-%d', yesterday)+" USD_Data not found!")
		cnxn.close()
	else:	
		for i in range(0, rc):
			record = cursor.fetchone()
			SEQ_NO = record[0]
			MARKET_RATE = record[1]
			TRM_DAYS = record[2]
			ADJ = record[3]
			Zero_Spot = 0
			Df_Spot = 0
			DAY_DF = record[4]
			Flag = record[8]
			Data_DT = record[5]
			CCY = record[6]
			TRM_DATE = record[7]
			Df_Today = 0
			Zero_Today = 0
			ftp_rate.add_instrument(int(SEQ_NO), turn_type(MARKET_RATE), int(TRM_DAYS), turn_type(ADJ), Zero_Spot, Df_Spot, int(DAY_DF), int(Flag), str(Data_DT), CCY, str(TRM_DATE), Df_Today, Zero_Today)
		try:
			ftp_rate.get_base_rates()
			logging.info("insert "+t.strftime('%Y-%m-%d', yesterday)+" USD_Data success!")
			print("insert "+t.strftime('%Y-%m-%d', yesterday)+" USD_Data success!")
		except:
			logging.exception("Failed insert "+t.strftime('%Y-%m-%d', yesterday)+" USD_Data, The problem is : ")
			print("Failed insert "+t.strftime('%Y-%m-%d', yesterday)+" USD_Data")
