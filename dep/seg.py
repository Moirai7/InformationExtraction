# coding=utf-8

class Seg:
	def __init__(self):
		path="people.dict"
		import sys
		reload(sys)
		sys.setdefaultencoding('utf-8')
		import Person
		self.person = Person.Person()
		f=open(path)
		self.ner_dict = {}
		for line in f:
			data = line.split('\t')
			self.ner_dict[unicode(data[0].strip(),'utf8')] = data[1].strip()
		f.close()

	def _seg(self,line):
		pass
