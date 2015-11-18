#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
from dep import Dep
import json
import re

#this class is discarded,'cause indri will give a useful sentence
class Sentence:
	def __init__(self):
		pass

	#FOA, it will search the keywords
	#then,use a window(length) to get the sentence that is needed to be merged.
	#@order True if keyword1 and keyword2 must be in the order
	#@window the length 
	def _get_sentence_by_keywords(self,line,order,window,keyword1,keyword2):
		sentences=[]
		#import pdb
		#pdb.set_trace()
		if order:
			position1 = 0
			position2 = 0
			while True:
				position1 = line.find(keyword1,position1)
				position2 = line.find(keyword2,position2)
				if position1==-1 or position2==-1:
					break
				if position1>=position2:
					pass
				else:
					p = position1-window if position1-window > 0 else 0
					print line[p:position2+len(keyword2)+window]
					#sentences.append(line[position1:position2])
				position1 += len(keyword1)
				position2 += len(keyword2)
		else :
                        position1 = 0
                        position2 = 0
                        while True:
                                position1 = line.find(keyword1,position1)
                                position2 = line.find(keyword2,position2)
                                if position1==-1 or position2==-1:
                                        break
				if position1 == position2:
                                	position1 += len(keyword1)
                                	position2 += len(keyword2)
					continue
				elif position1 > position2:
					p = position2
					position2 = position1
					position1 = p
				p = position1-window if position1-window > 0 else 0
				print line[p:position2+len(keyword2)+window]
                                #sentences.append(line[position1:position2])
				position1 += len(keyword1)
				position2 += len(keyword2)

#this clsss is to merge the results of Seg and Stanford
class Merge:

	#@jieba True means it will use jieba to ner
	#'cause the result of ner using jieba is not good enough,so @jieba must be False till i got a new way to get a better result.that means self.s always is not None
	def __init__(self,jieba=False,stanford=True):
		if jieba:
			self.json = json
			from seg import AllInfo
			from stanford import Stanford
			self.w = AllInfo()  
			self.s = None
			if stanford:
				self.st = Stanford(False)
			else:
				self.dep = Dep() 
		else:
			self.p = re.compile(u'\u25aa')
			self.json = json
			self.dep = Dep()
			from seg import Seg
			from stanford import Stanford
			self.w = Seg()                 
			self.s = Stanford(False)

	#ner,pos must like nn,nr,vv,ww 
	#dep	 must like word_id@@word dep+head\t
	#the input is a str(result in line)
	def _merge_with_str(self,line_ner,line_pos,line_dep,line_seg):
		ner = line_ner.split(',')
		pos = line_pos.split(',')
		if line_dep is not None:
			deps = line_dep.split('\t')
			line = ''
			lens = len(ner)-1
			for dep in deps:
				info = dep.split('@@')
				id = int(info[0])
				if id>lens:
					continue
				line += info[1].decode('gbk')
				line += ' '+pos[id]+'\t'
				#line += ' '+ner[id]+' '+pos[id]+'\t'
			line = line.strip('\t')
			return line
		else:
			seg = line_seg.split(' ')
			line = ''
			if len(seg)!=len(pos):
				print line_seg.encode('utf-8')
				print line_pos
			for id in xrange(len(ner)):
				if ner[id] !='O':
					seg[id] = ner[id]
				#line += seg[id] + ' ' + ner[id]+' '+pos[id]+'\t'
				line += seg[id] + ' ' +pos[id]+'\t'
			line = line.strip('\t')
			return line

	#this method is  for processing the json 
	def _process(self,line_json):
		decoded = self.json.loads(line_json)	
		line_ner = decoded['ner']
		line_pos = decoded['pos']
		line_seg = decoded['seg']
		return (line_ner,line_pos,line_seg)

	#this method is for getting all info of a line,without merging them in a line(return tuple)
	def _process_line(self,line_json):
		(line_ner,line_pos,line_seg) = self._process(line_json)
		line_dep = self.dep.dep_from_line(line_seg.encode('gbk'))
		deps = line_dep.split('\t')
		line = ''
		for dep in deps:
			info = dep.split('@@')
			info = info[1].split(' ')
			line += info[1].decode('gbk')+' '
		line = line.strip(' ')
		return (line_ner,line_pos,line_seg,line)

	#this method will parse the line and merge all info
	#the method will be used when i just have the json(including seg ner and pos) form indri
	#it can get the dep from stanford can merge it into a line
	#so it should not be used right now
	def merge(self,line_json,dep=False):
		if dep :
			(line_ner,line_pos,line_seg) = self._process(line_json)
			line_seg = self.p.sub('.',line_seg)
			line_dep = self.dep.dep_from_line(line_seg.encode('gbk'))
			line = self._merge_with_str(line_ner,line_pos,line_dep,None)
			return line
		else:
			(line_ner,line_pos,line_seg) = self._process(line_json)
			line = self._merge_with_str(line_ner,line_pos,None,line_seg)
			return line

	def add_new_words(self,newwords):
		self.w.add_words(newwords)

	def ner_using_nlpc(self,line):
		(line_seg,pos,ner) = self.w.getInfo(line)
		line_ner = self.dep._dep_line(line_seg.encode('gbk','ignore'))
		sner = line_ner.split('\t')
		#(line_seg,line_pos,line_ner) = self.dep._dep_all(line.encode('gbk','ignore'))
		if len(ner)!=len(sner):
			return ('','','')
		for i in xrange(len(ner)):
			j = ner[i]
			if j != 'other':
				sner[i]=j
		return ('\t'.join(line_seg.split(' ')),'\t'.join(pos),'\t'.join(sner))
		#return (line_seg,line_pos,line_ner)

	#this method is for get a json of a line
	#now it's for testing
	#i need to get the json(including seg ner and pos) form indri,and then use stanford to get the dep
	#BTW,I don't have to use dep anymore,so the method won't return dep
	#so,if stanford(True),the method must change
	def _get_line_json(self,line):
		if self.s is not None:
			dict = {'seg':'','ner':'','pos':''}
			dict['seg'] = self.w.seg(line)
			(dict['ner'],dict['pos']) = self.s.get_ner_pos(dict['seg'])
			return self.json.dumps(dict)
		else:
			(line_seg,pos,ner) = self.w.getInfo(line)
			(line_ner,line_pos) = self.st.get_ner_pos(line_seg)
			sner = line_ner.split(',')
			if len(ner)!=len(sner):
				return ('','','')
			#print line_seg.encode('utf-8')
			#print ','.join(ner)
			#print line_ner
			for i in xrange(len(ner)):
				j = ner[i]
				if j != 'other':
					sner[i]=j
			#print ','.join(sner)
			return (line_seg,line_pos,','.join(sner))

	#@dep False means without dep
	def get_line_info(self,line_json,dep=False):
		if self.s is not None:
		    if dep:
			return self._process_line(line_json)
		    else:
			(line_ner,line_pos,line_seg) = self._process(line_json)
			return (line_ner,line_pos,line_seg,None)
		else:
			(line_seg,line_pos,line_ner) = self._get_line_json(line_json)
			print line_seg
			print line_pos
			return (','.join(line_ner),','.join(line_pos),' '.join(line_seg),None)

	#this method is for testing 
	#it will use the jieba and standford tool to get the ner and pos's results. Then, transform them into json and use the method 'merge' to test whether it print the correct pattern
	#correct pattern:word dep(use ',' to split all result of parsing) ner pos\tword dep  ner pos  
	def test(self):
		for line in sys.stdin:
			line = line.strip('\n')
			#print line
			line_json = self._get_line_json(line)
	                line = self.merge(line_json)
			print line.encode('utf-8')

	#this method is for testing
	def test2(self):
		for line in sys.stdin:
			line = line.strip('\n')
			if self.s is not None:
				line_json = self._get_line_json(line)
				(line_ner,line_pos,line_seg,line_dep) = self.get_line_info(line_json,False)
				print line_ner
				print line_pos
				print line_seg.encode('utf-8')
				#print line_dep.encode('utf-8')
			else :
				(line_ner,line_pos,line_seg,line_dep) = self.get_line_info(line,False)
				print line_seg.encode('utf-8')
				print line_ner
				print line_pos


if __name__ == '__main__':
	m = Merge(False)
	m.test2()
	#s = Sentence()
	#s.test()        

