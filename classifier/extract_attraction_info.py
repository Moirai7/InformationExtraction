#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
import re

month = u'(?:[0-9]+~)?[0-9]+月(?:[0-9]+日)?'
#time = u'(?:上午)?[0-9]+[:|：](?:下午)?[0-9]+'
time = u'(?:(?:pm)?[0-9]+[:|：][0-9]+(?:pm)?|天黑|天亮|日落|日出|(?:[0-9]+.)?[0-9]+(?:am|pm))'
rt_all=re.compile(u'(?:不限|全天|全年|常年|24小时|免费|周一.{3}周日.{3}全天|周一.{3}周日.{2}全天)(开放)?')
rt_day=re.compile(u'[^周]*白天(开放)?')
rt_only_time = re.compile(u'('+time+u')[^0-9pm]{1,4}('+time+u')')
rt_week_time = re.compile(u'(?:周|星期)(.)(?:\s--\s|.|\s-\s)(?:周|星期)?(.)')
rt_month_time= re.compile(u'(?:('+month+u')[^0-9]*('+month+u')|('+month+'))')
rt_buy_time= re.compile(u'(?:('+time+u')(?:停止售票|止售时间|停止发售))|(?:(?:[^0-9停止售]*(?:停止售票|止售时间|停止发售)[^0-9]*)('+time+u'))')
rt_enter_time=re.compile(u'(?:[^0-9停止]*(?:停止入场|停止检票|閉山|截止上岛|入场截止|入馆)[^0-9]*)('+time+')')
rt_info_time=re.compile(u'(春、夏、秋季|冬季|旺季|淡季|夏季|秋季|春季|非冬季|冬季|春.?夏|秋.?冬|单场|两场)')
number=re.compile(u'[0-9]+')

rt_speci_time = re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)?[^0-9]*('+month+u')[^0-9]*('+month+u')[^0-9周]*('+time+u')[^0-9]{1,4}('+time+u')(?:(?:[^0-9停止|止售]*(?:停止售票|停止发售|止售时间)[^0-9]*)('+time+u'))?(?:(?:[^0-9停止]*[停止入场|停止检票][^0-9]*)('+time+')?)?')
rt_speci_time2 = re.compile(u'(?:[0-9]+~)?[0-9]+\s?月')
rt_time = re.compile(u'开放时间.('+time+u')')


price=u'(?:门票.?|平时.?|成人(?:HK)?|.{5}成人.{12}|通票)?(?:(\$[0-9]+)|([0-9]+(?:.[0-9]+)?\s?元))'
pt_free=re.compile(u'(?:.{0,4}免费|免门票)')
pt_only_price=re.compile(price)
pt_price=re.compile(price+u'[^0-9]*')
pt_speci_price=re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)?[^0-9]*('+month+u')[^0-9]*('+month+u')[^0-9]*('+price+u')')
pt_speci_price3=re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)?[^0-9]*((?:[0-9]+~)?[0-9]+\s?月)[^0-9]*('+price+u')')
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
 	if tt==u'日' or tt==u'天' or tt==u'七' or tt==u'末':
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
		if only_price.group(1) is None:
			info['price']=only_price.group(2)
		else:
			info['price']=only_price.group(1)
		all.append(info)
		return all
	only_price = pt_only_price.findall(line)
	if len(only_price)==1:
		info={}
		info['price']=only_price[0][1]
		all.append(info)
		return all
	month_times=rt_month_time.findall(line)
	info_time=rt_info_time.findall(line)
	if len(only_price)==len(month_times) and len(only_price)==2:
		for i in xrange(len(only_price)):
			p = only_price[i][1]
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
		for m in speci_price2:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			info['price']=m[1]
			all.append(info)
		return all
	speci_price3=pt_speci_price3.findall(line)
	if speci_price3:
		for m in speci_price3:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			tt = number.findall(m[1])
			info['month']['start']=Proc_Month([tt[0]]) if tt else ''
			info['month']['end']=Proc_Month([tt[1]]) if tt else ''
			info['price']=m[2]
			all.append(info)
		return all
	info={}
	prices=[]
	for o in only_price:
		prices.append(float(o[1].strip(u'元')))
	prices.sort()
	info['price']=str(prices[0])+u'元起'
	all.append(info)
	return all

def Time(line):
	all =[]
	if rt_all.match(line) or rt_day.match(line):
		info={}
		info['month']={}
		info['month']['start']='0101'
		info['month']['end']='1231'
		info['week']={}
		info['week']['start']=1
		info['week']['end']=7
		info['type']='open'
		info['hour']={}
		if rt_day.match(line):
			info['hour']['opentime']='09:00'
			info['hour']['closetime']='17:00'
		else:
			info['hour']['opentime']='00:00'
			info['hour']['closetime']='24:00'
		all.append(info)
		return all
	only_times=rt_only_time.findall(line)
	week_times=rt_week_time.findall(line)
	month_times=rt_month_time.findall(line)
	buy_times=rt_buy_time.findall(line)
	enter_times=rt_enter_time.findall(line)
	info_time=rt_info_time.findall(line)
	if len(only_times)==1 or (len(only_times)==len(month_times) and len(only_times)==2) or (len(week_times)==len(only_times) and len(only_times)==2) or (len(only_times)==2 and len(month_times)==0 and len(week_times)==0):
	   for i in xrange(len(only_times)):
		only_time = only_times[i]
		info={}
		info['hour']={}
		if only_time[0].find('pm')!=-1:
			if only_time[0].find('.')!=-1:
				time=str(int(only_time[0].split(u'.')[0].strip('pm'))+12)+':'+only_time[0].split(u'.')[1].strip('pm')
			else:
			   try:
				time=str(int(only_time[0].split(u':')[0].strip('pm'))+12)+':'+only_time[0].split(u':')[1].strip('pm')
			   except:
				time=str(int(only_time[0].split(u'pm')[0])+12)+':00'
		else:
			time=only_time[0]
		info['hour']['opentime']=time
		if only_time[1].find('pm')!=-1:
			if only_time[1].find('.')!=-1:
				time=str(int(only_time[1].split(u'.')[0].strip('pm'))+12)+':'+only_time[1].split(u'.')[1].strip('pm')
			else:
			   try:
				time=str(int(only_time[1].split(u':')[0].strip('pm'))+12)+':'+only_time[1].split(u':')[1].strip('pm')
			   except:
				time=str(int(only_time[1].split(u'pm')[0])+12)+':00'
		else:
			time=only_time[1]
		info['hour']['closetime']=time
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
			info['week']['start']='1'
			info['week']['end']='7'
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
			info['week']['start']='1'
			info['week']['end']='7'
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
		all.append(info)
	   return all
	
	only_time=rt_only_time.match(line)
	if only_time:
		info={}
		info['month']={}
		info['month']['start']='0101'
		info['month']['end']='1231'
		info['week']={}
		info['week']['start']='1'
		info['week']['end']='7'
		info['type']='open'
		info['hour']={}
		info['hour']['opentime']=only_time.group(1)
		info['hour']['closetime']=only_time.group(2)
		all.append(info)
		return all

	speci_time=rt_speci_time2.findall(line)
	if speci_time and len(only_times)==3 and len(speci_time)==5 and len(buy_times)==3:
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
		info['week']['start']='1'
		info['week']['end']='7'
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
		for m in month_time:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			tt = number.findall(m[1])
			info['month']['start']=Proc_Month(tt) if tt else ''
			tt = number.findall(m[2])
			info['type']='open'
			info['month']['end']=Proc_Month(tt) if tt else ''
			info['week']={}
			try:
				week_time=week_times[i]
				info['week']['start']=Proc_Week(week_time[0])
				info['week']['end']=Proc_Week(week_time[1])
			except:
				info['week']['start']='1'
				info['week']['end']='7'
			info['hour']={}
			info['hour']['openime']=m[3]
			info['hour']['closetime']=m[4]
			if m[5]!=u'':
				info['hour']['buytime']=m[5]
			if m[6]!=u'':
				info['hour']['entertime']=m[6]
			all.append(info)
		return all

	_time=rt_time.findall(line)
	if len(_time)==5:
	   for i in xrange(len(_time)):
		only_time = _time[i]
		info={}
		info['hour']={}
		info['hour']['opentime']=only_time
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
		info['week']['start']='1'
		info['week']['end']='7'
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
	elif line!='':
		enter=[]
		out=[]
		for x in only_times:
			enter.append(x[0])
			out.append(x[1])
		enter.sort()
		out.sort(reverse = True)
		info={}
		info['hour']={}
		info['hour']['opentime']=enter[0]
		info['hour']['closetime']=out[0]
		info['type']='open'
		info['week']={}
		info['week']['start']='1'
		info['week']['end']='7'
		info['month']={}
		info['month']['start']='0101'
		info['month']['end']='1231'
		all.append(info)
	return all

rt_openearly_time=re.compile(u'提前([0-9]*)分钟开门')

def SpecialTime(line,openhours):
	openearly_time = rt_openearly_time.findall(line)
	all=[]
	if openearly_time:
		for i in xrange(len(openhours)):
			info={}
			info['type']='open'
			o=openhours[i]
			early_time = openearly_time[i]
			time = o['hour']['opentime'].split(u':')
			if int(time[1])<early_time:
				time[0]=str(int(time[0])-1)
			else:
				time[1]=str(int(time[1])-early_time)
			info['hour']={}
			info['hour']['opentime']=time[0]+':'+time[1]
			info['holiday']=line.split(u' ')[3].split(u'，')[0].split(u'、')
			all.append(info)
	return all

outlist=[u'提取',u'节',u'延长',u'其他时间',u'假日',u'休馆',u'闭',u'不开放',u'除',u'&',u'休息',u'不',u'具体时间']
def Proc(key,line):
	res = []
	info = {}
	line = line.split('\t')
	info['id']=line[0]
	info['name']=line[1].decode('utf-8')
	check = True
	line[2]=line[2].lower().decode('utf-8').replace(u'\uff1a',u':').replace(u'每周七天开放','').replace(u'下午',u'pm').replace(u'点',u':00').replace(u'am to ',u'').replace(u'正午',u'12:00 ').replace(u'无休息日',u'').replace(u'全天开放',u'00:00-24:00')
	for o in outlist:
		if line[2].find(o) != -1:
			print line[2].encode('utf-8')
			check = False
			break
	info['openingHours']=Time(line[2])
	if len(info['openingHours'])==0 and line[3].lower()!='none':
		print line[2].encode('utf-8')
		pass
		print info['openingHours']
	if check is False:
		info['specialHours']=SpecialTime(line[2],info['openingHours'])
		print info['openingHours']
		print info['specialHours']
	#print info['openingHours']
	#print ''
	try:
		info['price']=Price(line[3].decode('utf-8'))
	except:
		info['price']='None'
	return info


