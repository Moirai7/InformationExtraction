#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
import re

month = u'(?:[0-9]+~)?[0-9]+月(?:[0-9]+日)?'
#time = u'(?:上午)?[0-9]+[:|：](?:下午)?[0-9]+'
time = u'[0-9]+[:|：][0-9]+'
rt_all=re.compile(u'[^周]*全天(开放)?')
rt_only_time = re.compile(u'('+time+u')[^0-9]{1,3}('+time+u')')
rt_week_time = re.compile(u'周(.).周?(.)')
rt_month_time= re.compile(u'(?:('+month+u')[^0-9]*('+month+u')|('+month+'))')
rt_buy_time= re.compile(u'(?:('+time+u')(?:停止售票|止售时间))|(?:(?:[^0-9停止售]*(?:停止售票|止售时间)[^0-9]*)('+time+u'))')
rt_enter_time=re.compile(u'(?:[^0-9停止]*(?:停止入场|停止检票|截止上岛)[^0-9]*)('+time+')')
rt_info_time=re.compile(u'(旺季|淡季|夏季|秋季|春季|非冬季|冬季)')
number=re.compile(u'[0-9]+')

rt_speci_time = re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)?[^0-9]*('+month+u')[^0-9]*('+month+u')[^0-9周]*('+time+u')[^0-9]{1,2}('+time+u')(?:(?:[^0-9停止|止售]*(?:停止售票|止售时间)[^0-9]*)('+time+u'))?(?:(?:[^0-9停止]*[停止入场|停止检票][^0-9]*)('+time+')?)?')
rt_speci_time2 = re.compile(u'(?:[0-9]+~)?[0-9]+\s?月')
rt_time = re.compile(u'开放时间.('+time+u')')

price=u'(?:门票.?|平时.?|成人|通票)?([0-9]+(?:.[0-9]+)?\s?元)'
pt_free=re.compile(u'(?:.{0,4}免费|免门票)')
pt_only_price=re.compile(price)
pt_price=re.compile(price+u'[^0-9]*')
pt_speci_price=re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)?[^0-9]*('+month+u')[^0-9]*('+month+u')[^0-9]*('+price+u')')
pt_speci_price2=re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)[^0-9]*('+price+u')')
def Proc_Month(tt):
	t=tt[0]
	if int(t)<10:
		t='0'+t
	if len(tt)>1:
		t2=tt[1]
		if int(t2)<10:
			t=t+'0'+t2
		else:
			t=t+t2
	return t
def Proc_Week(tt):
	if tt==u'一':
		return 1
 	if tt==u'二':
		return 2
	if tt==u'三':
		return 3
 	if tt==u'四':
		return 4
	if tt==u'五':
		return 5
 	if tt==u'六':
		return 6
 	if tt==u'日' or tt==u'天' or tt==u'七':
		return 7 
def Price(line):
	all=[]
	if pt_free.match(line):
		info={}
		info['price']='0'
		all.append(info)
		return all
	only_price = pt_only_price.match(line)
	if only_price:
		info={}
		info['price']=only_price.group(1)
		all.append(info)
		return all
	only_price = pt_only_price.findall(line)
	if len(only_price)==1:
		info={}
		info['price']=only_price[0]
		all.append(info)
		return all
	month_times=rt_month_time.findall(line)
	info_time=rt_info_time.findall(line)
	if len(only_price)==len(month_times) and len(only_price)==2:
		for i in xrange(len(only_price)):
			p = only_price[i]
			info={}
			info['price']=p
			info['month']={}
			try:
				month_time=month_times[i]
				if month_time[0]==u'' and month_time[2]!=u'':
					tt = number.findall(month_time[2])
					tt1 = [tt[0]]
					tt2 = [tt[1]]		
				elif month_time[0]!=u'':
					tt1 = number.findall(month_time[0])
					tt2 = number.findall(month_time[1])
				else:
					tt1=''
					tt2=''
			except:
				tt1=''
				tt2=''
			try:
				info['month']['info']=info_time[i]
			except:
				pass
			info['month']['start']=Proc_Month(tt1) if tt1 else ''
			info['month']['end']=Proc_Month(tt2) if tt2 else ''
			all.append(info)
		return all

	speci_price = pt_speci_price.findall(line)
	if speci_price :
		for m in speci_price:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			tt = number.findall(m[1])
			info['month']['start']=Proc_Month(tt) if tt else ''
			tt = number.findall(m[2])
			info['month']['end']=Proc_Month(tt) if tt else ''
			info['price']=m[3]
			all.append(info)
		return all
	speci_price2 = pt_speci_price2.findall(line)
	if speci_price2 :
		#print line.encode('utf-8')
		for m in speci_price2:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			info['price']=m[1]
			all.append(info)
		return all
	info={}
	info['price']=line
	all.append(info)
	return all
def Time(line):
	all =[]
	if rt_all.match(line):
		#print line.encode('utf-8')
		info={}
		info['month']={}
		info['month']['start']='0101'
		info['month']['end']='1231'
		info['week']={}
		info['week']['start']=1
		info['week']['end']=7
		info['type']='open'
		info['hour']={}
		info['hour']['opentime']='00:00'
		info['hour']['closetime']='24:00'
                info['hour']['entertime']='24:00'
                info['hour']['buytime']='24:00'
		all.append(info)
		return all
	only_times=rt_only_time.findall(line)
	week_times=rt_week_time.findall(line)
	month_times=rt_month_time.findall(line)
	buy_times=rt_buy_time.findall(line)
	enter_times=rt_enter_time.findall(line)
	info_time=rt_info_time.findall(line)
	if len(only_times)==1 or (len(only_times)==len(month_times) and len(only_times)==2) or (len(week_times)==len(only_times) and len(only_times)==2) or (len(only_times)==2 and len(month_times)==0 and len(week_times)==0):
	   #print line.encode('utf-8')
	   #print buy_times
	   #print enter_times
	   #print only_times
	   #print week_times
	   for i in xrange(len(only_times)):
		only_time = only_times[i]
		info={}
		info['hour']={}
		info['hour']['opentime']=only_time[0]
		info['hour']['closetime']=only_time[1]
		try:
			buy_time=buy_times[i]
			if buy_time[0]==u'':
				buy_time=buy_time[1]
			else:
				buy_time=buy_time[0]
			info['hour']['buytime']=buy_time
		except:
			pass
		try:
			enter_time=enter_times[i]
			info['hour']['entertime']=enter_time
		except:
			pass
		info['type']='open'
		info['week']={}
		try:
			week_time=week_times[i]
			info['week']['start']=Proc_Week(week_time[0])
			info['week']['end']=Proc_Week(week_time[1])
		except:
			info['week']['start']=''
			info['week']['end']=''
		#a=Proc_Week(week_time[0])
		#b=Proc_Week(week_time[1])
		#s=''
		#while a<=b:
		#	s+=str(a)
		#	a+=1
		#info['week']=s
		info['month']={}
		try:
			month_time=month_times[i]
			if month_time[0]==u'' and month_time[2]!=u'':
				tt = number.findall(month_time[2])
				tt1 = [tt[0]]
				tt2 = [tt[1]]		
			elif month_time[0]!=u'':
				tt1 = number.findall(month_time[0])
				tt2 = number.findall(month_time[1])
			else:
				tt1=''
				tt2=''
		except:
			tt1=''
			tt2=''
		try:
			info['month']['info']=info_time[i]
		except:
			pass
		info['month']['start']=Proc_Month(tt1) if tt1 else ''
		info['month']['end']=Proc_Month(tt2) if tt2 else ''
		#print info
		all.append(info)
	   return all

	if (len(only_times)==len(week_times) and len(only_times)==4 and len(month_times)==2) or (len(only_times)==3 and len(week_times)==2 and len(month_times)==2):
	   for i in xrange(len(only_times)):
		only_time = only_times[i]
		info={}
		info['hour']={}
		info['hour']['opentime']=only_time[0]
		info['hour']['closetime']=only_time[1]
		try:
			buy_time=buy_times[i]
			if buy_time[0]==u'':
				buy_time=buy_time[1]
			else:
				buy_time=buy_time[0]
			info['hour']['buytime']=buy_time
		except:
			pass
		try:
			enter_time=enter_times[i]
			info['hour']['entertime']=enter_time
		except:
			pass
		info['type']='open'
		info['week']={}
		try:
			week_time=week_times[i]
			info['week']['start']=Proc_Week(week_time[0])
			info['week']['end']=Proc_Week(week_time[1])
		except:
			info['week']['start']=''
			info['week']['end']=''
		#a=Proc_Week(week_time[0])
		#b=Proc_Week(week_time[1])
		#s=''
		#while a<=b:
		#	s+=str(a)
		#	a+=1
		#info['week']=s
		info['month']={}
		try:
			month_time=month_times[i/2]
			if month_time[0]==u'' and month_time[2]!=u'':
				tt = number.findall(month_time[2])
				tt1 = [tt[0]]
				tt2 = [tt[1]]		
			elif month_time[0]!=u'':
				tt1 = number.findall(month_time[0])
				tt2 = number.findall(month_time[1])
			else:
				tt1=''
				tt2=''
		except:
			tt1=''
			tt2=''
		try:
			info['month']['info']=info_time[i]
		except:
			pass
		info['month']['start']=Proc_Month(tt1) if tt1 else ''
		info['month']['end']=Proc_Month(tt2) if tt2 else ''
		#print info
		all.append(info)
	   return all
	
	only_time=rt_only_time.match(line)
	if only_time:
		#print line.encode('utf-8')
		info={}
		info['month']={}
		info['month']['start']='0101'
		info['month']['end']='1231'
		info['week']={}
		info['week']['start']=1
		info['week']['end']=7
		info['type']='open'
		info['hour']={}
		info['hour']['opentime']=only_time.group(1)
		info['hour']['closetime']=only_time.group(2)
		all.append(info)
		return all

	speci_time=rt_speci_time2.findall(line)
	if speci_time and len(only_times)==3 and len(speci_time)==5 and len(buy_times)==3:
	   #print line.encode('utf-8')
	   for i in xrange(len(only_times)):
		only_time = only_times[i]
		info={}
		info['hour']={}
		info['hour']['opentime']=only_time[0]
		info['hour']['closetime']=only_time[1]
		try:
			buy_time=buy_times[i]
			if buy_time[0]==u'':
				buy_time=buy_time[1]
			else:
				buy_time=buy_time[0]
			info['hour']['buytime']=buy_time
		except:
			pass
		info['type']='open'
		info['week']={}
		info['week']['start']=1
		info['week']['end']=7
		info['month']={}
		k=i
		while k<2+i:
		  try:
			month_time=speci_time[i+k]
			tt = number.findall(month_time)
			tt1 = [tt[0]]
			tt2 = [tt[1]]		
		  except:
			tt2=[tt[0]] 
		  info['month']['start']=Proc_Month(tt1) if tt1 else ''
		  info['month']['end']=Proc_Month(tt2) if tt2 else ''
		  all.append(info)
		  if len(only_times)==i+1:
			break
		  k+=1
	   return all

	month_time=rt_speci_time.findall(line)
	if month_time  :
		#print line.encode('utf-8')
		for m in month_time:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			tt = number.findall(m[1])
			info['month']['start']=Proc_Month(tt) if tt else ''
			tt = number.findall(m[2])
			info['month']['end']=Proc_Month(tt) if tt else ''
			info['week']={}
			try:
				week_time=week_times[i]
				info['week']['start']=Proc_Week(week_time[0])
				info['week']['end']=Proc_Week(week_time[1])
			except:
				info['week']['start']=''
				info['week']['end']=''
			info['hour']={}
			info['hour']['openime']=m[3]
			info['hour']['closetime']=m[4]
			info['hour']['buytime']=m[5]
			info['hour']['entertime']=m[6]
			#print info
			all.append(info)
		#print month_time
		#print all
		#print ''
		return all

	_time=rt_time.findall(line)
	if len(_time)==5:
	   for i in xrange(len(_time)):
		only_time = _time[i]
		info={}
		info['hour']={}
		info['hour']['opentime']=only_time[0]
		try:
			buy_time=buy_times[i]
			if buy_time[0]==u'':
				buy_time=buy_time[1]
			else:
				buy_time=buy_time[0]
			info['hour']['buytime']=buy_time
		except:
			pass
		info['type']='open'
		info['month']={}
		try:
			month_time=month_times[i]
			if month_time[0]==u'' and month_time[2]!=u'':
				tt = number.findall(month_time[2])
				tt1 = [tt[0]]
				tt2 = [tt[1]]		
			elif month_time[0]!=u'':
				tt1 = number.findall(month_time[0])
				tt2 = number.findall(month_time[1])
			else:
				tt1=''
				tt2=''
		except:
			tt1=''
			tt2=''
		try:
			info['month']['info']=info_time[i]
		except:
			pass
		info['month']['start']=Proc_Month(tt1) if tt1 else ''
		info['month']['end']=Proc_Month(tt2) if tt2 else ''
		#print info
		all.append(info)
	   return all
	else:
		pass
		print line.encode('utf-8')
	return

def Proc():
	res = []
	#for line in sys.stdin:
	file=open(sys.argv[1],'rb')
	line=file.readline()
	while line:
		line=line.strip()
		print line
		info = {}
		line = line.split('\t')
		info['id']=line[0]
		info['name']=line[1]
		info['openingHours']=Time(line[2].decode('utf-8'))
		try:
			info['price']=Price(line[3].decode('utf-8'))
		except:
			info['price']='None'
		print info
		print ''
		line=file.readline()

Proc()
		
