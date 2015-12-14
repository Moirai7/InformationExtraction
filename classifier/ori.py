#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
import json
import time
import datetime
def Proc_Week(tt):
        if tt==0:
                return u'周一'
        if tt==1:
                return u'周二'
        if tt==2:
                return u'周三'
        if tt==3:
                return u'周四'
        if tt==4:
                return u'周五'
        if tt==5:
                return u'周六'
        if tt==6:
                return u'周日'
r=[]
ls=[]
file=open(sys.argv[1],'rb')
line=file.readline()
while line:
	line=line.strip()
	ls.append(line.strip())
	result=file.readline()
	result=eval(result.strip())
	r.append(result)
	line=file.readline()
today = datetime.datetime.now() 
all=[]
while today.day <=25:
	week=Proc_Week(today.weekday())
	for result in r:
		for m in result["price"]:
			if 'month' in m and 'start' in m['month']:
				if m['month']['end']<m['month']['start']:
					m['month']['end']='1231'
				if str(today.month)+str(today.day) >=m['month']['start'] and str(today.month)+str(today.day) <=m['month']['end']:
					price= m['price']
					break
			else:
				price= m['price']
				pass
		for m in result["openingHours"]:
			if today.weekday()>=int(m['week']['start'])-1 and today.weekday()<=int(m['week']['end'])-1:
				if m['month']['end']<m['month']['start']:
					m['month']['end']='1231'
				if str(today.month)+str(today.day) >=m['month']['start'] and str(today.month)+str(today.day) <=m['month']['end']:
					opentime= m['hour']['opentime']
					closetime=m['hour']['closetime']
					if 'buytime' in m['hour']:
						buytime= m['hour']['buytime']
					if 'entertime' in m['hour']:
						entertime= m['hour']['entertime']
					break
		if 'specialHours' in result:
			for m in result['specialHours']:
				if m['type']=='open':
					if week in m['holiday']:
						if 'hour' in m and 'opentime' in m['hour']:
							opentime= m['hour']['opentime']
						if 'hour' in m and 'closetime' in m['hour']:
							closetime=m['hour']['closetime']
						if 'hour' in m and 'buytime' in m['hour']:
							buytime= m['hour']['buytime']
						if 'hour' in m and 'entertime' in m['hour']:
							entertime= m['hour']['entertime']
					else:
						pass
				else:
					if week in m['holiday']:
						opentime = 'close'
						closetime = 'close'
		info = {}
		info['id']=result['id']					
		info['detail_time']=result['detail_time']			
		info['detail_price']=result['detail_price']
		info['price']=price
		info['opentime']=opentime
		info['closetime']=closetime
		all.append(info)
	print all
	today= today+datetime.timedelta(days = 1)
