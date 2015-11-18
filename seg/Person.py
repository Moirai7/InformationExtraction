import re
import sys

class Person:
	def __init__(self):
		reload(sys)
		sys.setdefaultencoding('utf-8')
		import os
		file = open(os.path.split(os.path.realpath(__file__))[0]+"/zh",'r')
		line = file.readline()
		file.close()
		self.prename = line.split('\t')
		self.t1 = re.compile(u'([0-9])')
		self.de = re.compile(u"[\u4e00-\u9fa5]")
	
	def merge_name(self,line,pos,ner):
		line = line.split(' ')
		for i in xrange(len(line)):
			try:
				x = line[i]
				m = line[i+1]
			except:
				return (' '.join(line),pos,ner)
			xing = self.de.findall(x)
			ming = self.de.findall(m)
			if x in self.prename or (len(xing)==2 and len(ming)==1 and xing[0] in self.prename) :
				   if (self.t1.search(m) is None) and (pos[i].find('n')!=-1) and (pos[i+1].find('n')!=-1):
					del pos[i+1]
					del ner[i+1]
				   	line[i]=x+m
				   	del line[i+1]
		return (' '.join(line),pos,ner)

if __name__ == '__main__':
	p = People()
	file=open('output','r')
	while True:
	   line = file.readline()
	   if line:
		print line
		print p.merge_name(line.strip('\r\n').decode('utf-8')).encode('utf-8')
	   else:
		   break
