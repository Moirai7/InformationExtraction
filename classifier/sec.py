#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
import copy
import re

month = u'(?:[0-9]+~)?[0-9]+月(?:[0-9]+日)?'
#time = u'(?:上午)?[0-9]+[:|：](?:下午)?[0-9]+'
time = u'(?:(?:pm)?[0-9]+[:|：][0-9]+(?:pm)?|天黑|天亮|日落|日出|(?:[0-9]+.)?[0-9]+(?:am|pm))'
rt_just_time=re.compile(time)
rt_all=re.compile(u'(?:不限|全天|全年|常年|24小时|免费|周一.{3}周日.{3}全天|周一.{3}周日.{2}全天)(开放)?')
rt_day=re.compile(u'[^周]*白天(开放)?')
rt_only_time = re.compile(u'('+time+u')[^0-9pm]{1,4}('+time+u')')
rt_week_time = re.compile(u'(?:周|星期)(.)(?:\s--\s|.|\s-\s)(?:周|星期)?(.)')
rt_month_time= re.compile(u'(?:('+month+u')[^0-9]*('+month+u')|('+month+'))')
rt_buy_time= re.compile(u'(?:('+time+u')(?:停止售票|止售|止售时间|停止发售|停售门船票))|(?:(?:[^0-9停止售]*(?:停止售票|止售时间|停止发售)[^0-9]*)('+time+u'))|(?:闭馆前([0-9]+)分钟停止售票)')
rt_enter_time=re.compile(u'(?:[^0-9停止]*(?:停止入场|停止检票|閉山|截止上岛|入场截止|停止入馆|入馆)[^0-9]*)('+time+')|(?:('+time+u')(?:停止入馆))')
rt_info_time=re.compile(u'(春、夏、秋|夏秋|冬春|冬季|冬|旺季|淡季|夏季|秋季|春季|非冬季|冬季|春.?夏|秋.?冬|单场|两场)')
number=re.compile(u'[0-9]+')

rt_speci_time = re.compile(u'[0-9]?[^0-9旺淡季]*(旺季|淡季|夏季|秋季|春季|非冬季|冬季)?[^0-9]*('+month+u')[^0-9]*('+month+u')[^0-9周]*('+time+u')[^0-9]{1,4}('+time+u')(?:(?:[^0-9停止|止售]*(?:停止售票|停止发售|止售时间)[^0-9]*)('+time+u'))?(?:(?:[^0-9停止]*[停止入场|停止检票][^0-9]*)('+time+')?)?')
rt_speci_time2 = re.compile(u'(?:[0-9]+~)?[0-9]+\s?月')
rt_speci_time3=re.compile(u'景:00(.*)')
rt_speci_time5=re.compile(u'([^无]夜场(.*))|(索道(.*))|(夜游开放时间(.*))')
rt_speci_time4=re.compile(u'[^0-9开]*开闭?园时间[^0-9]*('+time+u')[^0-9]{1,4}('+time+u')[^0-9]*售票[^0-9]*('+time+u')[^0-9]{1,4}('+time+u')')
rt_speci_time6 = re.compile(u'(?:[0-9]+、){1,5}[0-9]+月')
rt_speci_time7 = re.compile(u'[0-9]+[^0-9平日]*(?:平日)[^0-9]*('+time+u')[^0-9]{1,4}('+time+u')[^0-9停止]*停止售票[^0-9]*('+time+u')')
rt_open_time = re.compile(u'开门时间[^0-9]*('+time+u')')
rt_close_time= re.compile(u'关门时间[^0-9]*('+time+u')')
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
		return '1'
 	if tt==u'二':
		return '2'
	if tt==u'三':
		return '3'
 	if tt==u'四':
		return '4'
	if tt==u'五':
		return '5'
 	if tt==u'六':
		return '6'
 	if tt==u'日' or tt==u'天' or tt==u'七' or tt==u'末':
		return '7' 
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
					tt1=['1','1']
					tt2=['12','31']
			except:
				tt1=['1','1']
				tt2=['12','31']
			try:
				info['month']['info']=info_time[i]
			except:
				pass
			info['month']['start']=Proc_Month(tt1) if tt1 else '0101'
			info['month']['end']=Proc_Month(tt2) if tt2 else '1231'
			all.append(info)
		return all

	speci_price = pt_speci_price.findall(line)
	if speci_price :
		for m in speci_price:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			tt = number.findall(m[1])
			info['month']['start']=Proc_Month(tt) if tt else '0101'
			tt = number.findall(m[2])
			info['month']['end']=Proc_Month(tt) if tt else '1231'
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
			info['month']['start']=Proc_Month([tt[0]]) if tt else '0101'
			info['month']['end']=Proc_Month([tt[1]]) if tt else '1231'
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
	only_times=rt_only_time.findall(line)
	#全天
	if (rt_all.match(line) or rt_day.match(line)) and (len(only_times)==1 or len(only_times)==0):
		info={}
		info['month']={}
		info['month']['start']='0101'
		info['month']['end']='1231'
		info['week']={}
		info['week']['start']='1'
		info['week']['end']='7'
		info['type']='open'
		info['hour']={}
		if len(only_times)==1:
			info['hour']['opentime']= only_times[0][0]
			info['hour']['closetime']= only_times[0][1]
		elif rt_day.match(line):
			info['hour']['opentime']='09:00'
			info['hour']['closetime']='17:00'
		else:
			info['hour']['opentime']='00:00'
			info['hour']['closetime']='24:00'
		all.append(info)
		return all
	#开闭园
	speci_time4=rt_speci_time4.findall(line)
	if speci_time4:
		for x in speci_time4:
			info={}
			info['month']={}
			info['month']['start']='0101'
			info['month']['end']='1231'
			info['week']={}
			info['week']['start']='1'
			info['week']['end']='7'
			info['type']='open'
			info['hour']={}
			info['hour']['opentime']=x[0]
			info['hour']['closetime']=x[1]
			info['hour']['buytime']=x[3]
			all.append(info)
		return all
	speci_time7 = rt_speci_time7.match(line)
	if speci_time7:
		info={}
		info['month']={}
		info['week']={}
		info['week']['start']='1'
		info['week']['end']='7'
		info['type']='open'
		info['hour']={}
		info['hour']['opentime']=speci_time7.group(1)
		info['hour']['closetime']=speci_time7.group(2)
		info['hour']['buytime']=speci_time7.group(3)
		all.append(info)
		return all
	week_times=rt_week_time.findall(line)
	month_times=rt_month_time.findall(line)
	buy_times=rt_buy_time.findall(line)
	enter_times=rt_enter_time.findall(line)
	info_time=rt_info_time.findall(line)
	#时间 | 月+时间 | 周+时间 | 时间 时间
	if len(only_times)==1 or (len(only_times)==len(month_times) and len(only_times)==2) or (len(week_times)==len(only_times) and len(only_times)==2) or (len(only_times)==2 and len(month_times)==0 and len(week_times)==0 and line.find(u'外山门')==-1):
	   for i in xrange(len(only_times)):
		only_time = only_times[i]
		if len(only_times)==2 and only_time[0]==u'00:00' and only_time[1]==u'24:00' and line.find(u'售票时间')!=-1:
			continue
		info={}
		info['hour']={}
		if only_time[0].find('pm')!=-1:
			if only_time[0].find('.')!=-1 :
				if int(only_time[0].split(u'.')[0].strip('pm'))<12:
					time=str(int(only_time[0].split(u'.')[0].strip('pm'))+12)+':'+only_time[0].split(u'.')[1].strip('pm')	
				else:
					time= only_time[0].strip('pm')
			else:
			   try:
				if int(only_time[0].split(u':')[0].strip('pm'))<12:
					time=str(int(only_time[0].split(u':')[0].strip('pm'))+12)+':'+only_time[0].split(u':')[1].strip('pm')
				else:
					time= only_time[0].strip('pm')
			   except:
				if int(only_time[0].split(u'pm')[0])<12:
					time=str(int(only_time[0].split(u'pm')[0])+12)+':00'
				else:
					time= only_time[0].strip('pm')+":00"
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
			if buy_times[0][2]!=u'':
				time = time.split(u':')
				early=int(buy_times[0][2])
				if int(time[1])<early:
					time=str(int(time[0])-1)+':'+str(int(time[1])+60-early)
				else:
					time=time[0]+':'+str(int(time[1])-early)
				info['hour']['buytime']=time
			else:
				buy_time=buy_times[i]
				if buy_time[0]==u'':
					buy_time=buy_time[1]
				else:
					buy_time=buy_time[0]
				info['hour']['buytime']=buy_time
		except:
			pass
		try:
			if enter_times[i][1]!=u'':
				enter_time=enter_times[i][1]
			else:
				enter_time=enter_times[i][0]
			info['hour']['entertime']=enter_time
		except:
			pass
		info['type']='open'
		info['week']={}
		try:
			week_time=week_times[i]
			info['week']['start']=Proc_Week(week_time[0])
			if Proc_Week(week_time[1])!=None :
				info['week']['end']=Proc_Week(week_time[1]) 
			else: 
				info['week']['end']=Proc_Week(week_time[0])
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
				tt1=['1','1']
				tt2=['12','31']
		except:
			tt1=['1','1']
			tt2=['12','31']
		try:
			info['month']['info']=info_time[i]
		except:
			pass
		info['month']['start']=Proc_Month(tt1) if tt1 else '0101'
		info['month']['end']=Proc_Month(tt2) if tt2 else '1231'
		all.append(info)
	   return all
	#月 周 时间 周 时间
	if (len(only_times)==len(week_times) and len(only_times)==4 and len(month_times)==2) or (len(only_times)==3 and len(week_times)==2 and len(month_times)==2) or (len(only_times)==len(week_times) and len(only_times)==4 and len(info_time)==2):
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
			enter_time=enter_times[0][i]
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
				tt1=['1','1']
				tt2=['12','31']
		except:
			tt1=['1','1']
			tt2=['12','31']
		try:
			info['month']['info']=info_time[i/2]
		except:
			pass
		info['month']['start']=Proc_Month(tt1) if tt1 else '0101'
		info['month']['end']=Proc_Month(tt2) if tt2 else '1231'
		all.append(info)
	   return all
	speci_time6 = rt_speci_time6.findall(line)
	if speci_time6:
		for i in xrange(len(only_times)):
			only_time=only_times[i]
			info={}
			info['hour']={}
			info['hour']['opentime']=only_time[0]
			info['hour']['closetime']=only_time[1]
			try:
				buy_time=buy_times[0]
				buy_time=buy_time[1]
				info['hour']['buytime']=buy_time
			except:
				pass
			info['type']='open'
			info['week']={}
			info['week']['start']='1'
			info['week']['end']='7'
			month_time=month_times[i]
			tt = number.findall(month_time[0])
			info['month']={}
			month_time=speci_time6[i]
			tt = number.findall(month_time)
			for t in tt:
				info['month']['start']=Proc_Month([t]) if t else '0101'
				info['month']['end']=Proc_Month([t]) if t else '1231'
				all.append(info)
				info = copy.deepcopy(info)
		return all
	#月 月 时间
	if len(only_times)==2 and len(month_times)==4:
		for i in xrange(len(month_times)):
			info={}
			info['month']={}
			month_time=month_times[i]
			tt = number.findall(month_time[0])
			info['month']['start']=Proc_Month(tt) if tt else '0101'
			tt = number.findall(month_time[1])
			info['month']['end']=Proc_Month(tt) if tt else '1231'
			info['week']={}
			info['week']['start']='1'
			info['week']['end']='7'
			info['type']='open'
			info['hour']={}
			info['hour']['opentime']= only_times[i/2][0]
			info['hour']['closetime']= only_times[i/2][1]
			all.append(info)
		return all
	#只是时间
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
	#只是月份
	if len(month_times)==1 and len(only_times)==0:
		info={}
		info['month']={}
		tt = number.findall(month_times[0][0])
		info['month']['start']=Proc_Month(tt) if tt else '0101'
		tt = number.findall(month_times[0][1])
		info['month']['end']=Proc_Month(tt) if tt else '1231'
		info['week']={}
		info['week']['start']='1'
		info['week']['end']='7'
		info['type']='open'
		info['hour']={}
		info['hour']['opentime']='00:00'
		info['hour']['closetime']='24:00'
		all.append(info)
		return all
	#特殊
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
		  info['month']['start']=Proc_Month(tt1) if tt1 else '0101'
		  info['month']['end']=Proc_Month(tt2) if tt2 else '1231'
		  all.append(info)
		  info = copy.deepcopy(info)
		  if len(only_times)==i+1:
			break
		  k+=1
	   return all
	#特殊
	speci_time3=rt_speci_time3.findall(line)
	if speci_time3:
	   open_time = rt_open_time.findall(speci_time3[0])
	   close_time = rt_close_time.findall(speci_time3[0])
	   buy_times2 = rt_buy_time.findall(speci_time3[0])
	   if len(open_time)!=0 and len(close_time)!=0:
		if len(open_time)<len(close_time):
			for i in xrange(len(close_time)):
				info={}	
				info['hour']={}
				info['hour']['opentime']=open_time[0]
				info['hour']['closetime']=close_time[i]
				try:
					buy_time=buy_times2[i]
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
						tt1=['1','1']
						tt2=['12','31']
				except:
					tt1=['1','1']
					tt2=['12','31']
				try:
					info['month']['info']=info_time[i]
				except:
					pass
				info['month']['start']=Proc_Month(tt1) if tt1 else '0101'
				info['month']['end']=Proc_Month(tt2) if tt2 else '1231'
				all.append(info)
		return all
	#特殊大
	month_time=rt_speci_time.findall(line)
	if month_time  :
		for m in month_time:
			info={}
			info['month']={}
			info['month']['info']=m[0]
			tt = number.findall(m[1])
			info['month']['start']=Proc_Month(tt) if tt else '0101'
			tt = number.findall(m[2])
			info['type']='open'
			info['month']['end']=Proc_Month(tt) if tt else '1231'
			info['week']={}
			try:
				week_time=week_times[i]
				info['week']['start']=Proc_Week(week_time[0])
				info['week']['end']=Proc_Week(week_time[1])
			except:
				info['week']['start']='1'
				info['week']['end']='7'
			info['hour']={}
			info['hour']['opentime']=m[3]
			info['hour']['closetime']=m[4]
			if m[5]!=u'':
				info['hour']['buytime']=m[5]
			if m[6]!=u'':
				info['hour']['entertime']=m[6]
			all.append(info)
		return all

	_time=rt_just_time.findall(line)
	if len(_time)==1:
		info={}
		info['hour']={}
		info['hour']['opentime']=_time[0]
		info['type']='open'
		info['week']={}
		info['week']['start']='1'
		info['week']['end']='7'
		info['month']={}
		info['month']['start']='0101'
		info['month']['start']='1231'
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
				tt1=['1','1']
				tt2=['12','31']
		except:
			tt1=['1','1']
			tt2=['12','31']
		try:
			info['month']['info']=info_time[i]
		except:
			pass
		info['month']['start']=Proc_Month(tt1) if tt1 else '0101'
		info['month']['end']=Proc_Month(tt2) if tt2 else '1231'
		all.append(info)
	   return all
	elif line!='' and len(only_times)!=0:
		enter=[]
		out=[]
		for x in only_times:
			if int(x[0].split(':')[0])<10 and x[0].split(':')[0][0]!='0':
				enter.append(u'1'+x[0])
			else:
				enter.append(x[0])
			if int(x[1].split(':')[0])<10 and x[1].split(':')[0][0]!=0:
				out.append(u'1'+x[1])
			else:
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
rt_holiday_time=re.compile(u'(?:春节|五一|国庆节|暑假|佛诞节日|特殊佛教节日|每周一|周一闭馆|节假日|周一\\().*')
rt_except_time=re.compile(u'(?:\\(([^0-9除外]*)除外\\))|(?:(法定节假日)周一照常开放)|(?:(国家法定节假日)(?:除外|周一开馆))')
rt_close_time=re.compile(u'周(.)闭馆')
rt_extensive_time=re.compile(u'闭馆时间延长(.)小时，闭馆前(.)小时停止售票')
holiday=[u'五一',u'十一',u'春节',u'国庆节',u'暑假',u'佛诞节日',u'朔望',u'农历初一',u'十五',u'二月十九',u'四月初八',u'六月十九',u'九月十九',u'节假日',u'周一',u'除夕',u'初一',u'初二',u'国家法定节假日']

def SpecialTime(line,openhours):
	all=[]
	only_time=rt_only_time.match(line)
	if only_time and line.find(u'闭馆')==-1:
		return all
	l=rt_holiday_time.findall(line)
	try:
		only_times=rt_only_time.findall(l[0])
	except:
		only_times=None
	if only_times:
		buy_times=rt_buy_time.findall(l[0])
		info={}
		info['type']='open'
		info['hour']={}
		info['hour']['opentime']=only_times[0][0]
		info['hour']['closetime']=only_times[0][1]
		try:
			info['hour']['buytime']=buy_times[0][1]
		except:
			pass
		info['holiday']=[]
		for h in holiday:
			if l[0].find(h)!=-1:
				info['holiday'].append(h)
		all.append(info)
		return all
	try:
		openearly_time = rt_openearly_time.findall(l[0])
	except:
		openearly_time = None
	if openearly_time:
		for i in xrange(len(openhours)):
			info={}
			info['type']='open'
			o=openhours[i]
			early_time = int(openearly_time[i])
			time = o['hour']['opentime'].split(u':')
			if int(time[1])<early_time:
				time=str(int(time[0])-1)+':'+str(int(time[1])+60-early_time)
			else:
				time=time[0]+':'+str(int(time[1])-early_time)
			info['hour']={}
			info['hour']['opentime']=time
			info['holiday']=[]
			for h in holiday:
				if l[0].find(h)!=-1:
					info['holiday'].append(h)
			all.append(info)
		return all
	try:
		if l[0].find(u'闭馆')!=-1 and l[0].find(u'延长')==-1:
			except_time = rt_except_time.findall(l[0])
			info={}
			info['type']='close'
			info['holiday']=[]
			for h in holiday:
				if (l[0].find(h)!=-1) and (h not in except_time[0]):
					if u'法定节假日' in  except_time[0] or u'国家法定节假日' in  except_time[0]:
						if h!=u'节假日':
							info['holiday'].append(h)
					else:
						info['holiday'].append(h)
			all.append(info)
			info={}
			info['type']='open'
			if except_time[0][0]!=u'':
				info['holiday']=[except_time[0][0]]
			elif except_time[0][1]!=u'':
				info['holiday']=[except_time[0][1]]
			elif except_time[0][2]!=u'':
				info['holiday']=[except_time[0][2]]
			else:
				info['holiday']=[except_time[0][3]]
			all.append(info)
			return all
	except:
		pass
	close_time=rt_close_time.findall(line)
	if close_time:
		info={}
		info['type']='close'
		info['holiday']=u'周'+close_time[0][0]
		all.append(info)
	try:
		extensive_time=rt_extensive_time.findall(l[0])
	except:
		extensive_time=None
	if extensive_time:
		for i in xrange(len(openhours)):
			info={}
			info['type']='open'
			o=openhours[i]
			early_time = int(30 if extensive_time[0][0]==u'半' else 0)
			time = o['hour']['closetime'].split(u':')
			if int(time[1])+early_time>60:
				close_time=str(int(time[0])+1)+':'+str(int(time[1])-60+early_time)
				buy_time=time[0]+':'+str(int(time[1])-60+early_time)
			else:
				close_time=time[0]+':'+str(int(time[1])+early_time)
				buy_time=str(int(time[0])-1)+':'+str(int(time[1])+early_time)
			info['hour']={}
			info['hour']['closetime']=close_time
			info['hour']['buytime']=buy_time
			info['holiday']=[]
			for h in holiday:
				if l[0].find(h)!=-1:
					info['holiday'].append(h)
			all.append(info)
		return all
	return all

outlist=[u'提取',u'节',u'延长',u'其他时间',u'假日',u'休馆',u'闭',u'不开放',u'除',u'&',u'休息',u'不',u'具体时间']
def Proc():
	res = []
	file=open(sys.argv[2],'rb')
	namelist=[]
	l=file.readline()
	while l:
		namelist.append(l.strip().decode('utf-8'))
		l=file.readline()
	file.close()
	file=open(sys.argv[1],'rb')
	while True:
		line=file.readline()
		if line:
			line=line.strip()
			line = line.split('\t')
			info = {}
			info['id']=line[0]
			info['name']=line[1].decode('utf-8')
			if info['name'] not in namelist:
				continue
			print ('\t'.join(line))
			check = True
			info['detail_time']=line[2].decode('utf-8')
			line[2]=line[2].lower().decode('utf-8').replace(u'\uff1a',u':').replace(u'国定假日',u'国家法定节假日').replace(u'国定节假日',u'国家法定节假日').replace(u'每周七天开放','').replace(u'下午',u'pm').replace(u'点',u':00').replace(u'am to ',u'').replace(u'正午',u'12:00 ').replace(u'无休息日',u'').replace(u'全天开放',u'00:00-24:00').replace(u' - ',u'-')
			if line[2].find(u'平日')!=-1 and line[2].find(u'周六')!=-1 and line[2].find(u'周日')!=-1:
				line[2]=line[2].replace(u'平日',u'周一到周五')
			if line[2].find(u'平时')!=-1 and line[2].find(u'周末')!=-1:
				line[2]=line[2].replace(u'平时',u'周一到周六')
			for o in outlist:
				if line[2].find(o) != -1:
					check = False
					break
			l=rt_speci_time5.sub(u'',line[2])
			l=l.replace(u'节假日:06:00~20:00',u'').replace(u'墓室:09:00~18:00','')
			info['openingHours']=Time(l)
			if check is False:
				st =SpecialTime(line[2],info['openingHours'])
				if len(st)!=0:
					info['specialHours']=st
				#print line[2].encode('utf-8')
				#print info['openingHours']
				#print info['specialHours']
			#print info['openingHours']
			#print ''
			try:
				info['price']=Price(line[3].decode('utf-8'))
				info['detail_price']=line[3].decode('utf-8')
			except:
				info['price']=[{'price': '0'}]
				info['detail_price']='None'
			print info
		else:
			break
Proc()
