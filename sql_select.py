#coding:utf-8
import sqlite3
import os
import requests
import matplotlib.pyplot as plt

path= os.path.abspath(os.path.dirname(__file__)) 
conn = sqlite3.connect(path+"/db.sqlite3")
cur = conn.cursor()

plt.rcParams.update({'font.size':20})
plt.axis('equal')
color=("red", "blue")
label = ["Positiv", "Negativ"]

xingApi="https://lr.capio.jp/iminos/webapis/synana_k/1_1/"
xingAccessKey="RGeTMEHcXPp8wjyz"

class sql_time:
	def __init__(self,data):
		self.date=data
		self.yea=""
		self.mon=""
		self.da=""
		self.hou=""
		self.minu=""
		self.sec=""

	def year(self):
		for i in range(0,4):self.yea+=self.date[i]
		return int(self.yea)
	def month(self):
		for i in range(5,7):self.mon+=self.date[i]
		return int(self.mon)
	def day(self):
		for i in range(8,11):self.da+=self.date[i]
		return int(self.da)
	def hour(self):
		for i in range(11,13):self.hou+=self.date[i]
		return int(self.hou)
	def minutu(self):
		for i in range(14,16):self.minu+=self.date[i]
		return int(self.minu)
	def second(self):
		for i in range(17,26):self.sec+=self.date[i]
		return float(self.sec)

if __name__ == "__main__":
	"""
	sent="めっちゃムカつく"
	#sent="果物が甘い"
	sent="料理は美味しくない"
	#sent="美味しくない"
	sent="お前ブスだな"
	#sent="マジウケる"
	#sent="www"
	"""

	cur.execute( "select * from socks_message;" )
	count=0
	positiv=0
	negativ=0
	other=0
	for row in cur:
		sent= row[2]
		time=sql_time(row[3])
		#print time.year(),time.month(),time.day(),time.hour(),time.minutu(),time.second()
		query=xingApi+"?acckey=" + xingAccessKey + "&sent=" + sent
		r=requests.get(query).json()
		#print r["results"][0]["phrases"][0]["pairpn"]
		for m in r["results"]:
			for n in m["phrases"]:
				num=int(n["pairpn"])
				if num == 1:positiv+=1
				elif num == 2:negativ+=1#count-=1
				else:other+=1#count+=0.5
				#print count
	"""
	if count<0: print "negativ"
	elif count>0:print "positiv"
	else: print "nothing"
	"""
	print positiv,negativ,other
	data=[positiv,negativ]

	plt.pie(data, 
		autopct='%1.1f%%',	# グラフ中に割合を表示
		pctdistance=0.6,	# 割合の位置を指定 0が中心, 1が外周
		startangle=90,		# グラフの開始位置を12時の位置に変更
		labels=label,
		labeldistance=1.1,	# ラベルの位置を指定
		colors=color
	)
	lgnd=plt.legend(bbox_to_anchor=(1.0, 0.25, 1.55, 1.5), loc="center left", borderaxespad=0.)
	plt.savefig("graph.png", bbox_extra_artists=(lgnd,), bbox_inches="tight")

	cur.close()
	conn.close()
