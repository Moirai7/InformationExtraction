#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
import json
import re
def Proc_Json():
	lines=[]
	for line in sys.stdin:
		line=line.strip()
		js = json.loads(line)
		id = js['@id']
		name = js['name']
		if 'price' in js:
			price = js['price']
		else:
				price = 'None'
		if 'openingHours' in js:
			openingHours = js['openingHours']
		else:
			openingHours = 'None'
		print (id+'\t'+name+'\t'+openingHours+'\t'+price).encode('utf-8')
		#lines.append(id+'\t'+name+'\t'+price+'\t'+openingHours)
	return lines

Proc_Json()
