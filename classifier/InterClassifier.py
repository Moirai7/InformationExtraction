#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
import math
import collections
#from merge import Merge
#from dep import Dep
import json
import traceback

class InterClassifier:
	def __init__(self,genre='line',identify=[]):
		self.genre = genre
		self.newwords2 =identify
		print self.newwords2[0].encode('utf-8')
		import re
		self.de = re.compile(u"[\u4e00-\u9fa5]")
		self.relation = {u'fuqin':('PERSON','PERSON'),u'erzi':('PERSON','PERSON'),u'nver':('PERSON','PERSON'),u'nvyou':('PERSON','PERSON'),u'nanyou':('PERSON','PERSON'),u'muqin':('PERSON','PERSON'),u'emma':('PERSON','PERSON'),u'zhangfu':('PERSON','PERSON'),u'qizi':('PERSON','PERSON'),u'\u5973\u53cb':('PERSON','PERSON'),u'\u5973\u513f':('PERSON','PERSON'),u'\u59bb\u5b50':('PERSON','PERSON'),u'\u4e08\u592b':('PERSON','PERSON'),u'\u524d\u592b':('PERSON','PERSON'),u'\u7236\u4eb2':('PERSON','PERSON'),u'\u8eab\u9ad8':('PERSON','HEIGHT'),u'\u751f\u65e5':('PERSON','DATE'),u'\u64ad\u51fa\u65f6\u95f4':('FILM','TIME'),u'\u4e3b\u9898\u66f2':('FILM','MUSIC')}
		self.pos_tagger={'Dg':1,'Ng':2,'Tg':3,'Vg':4,'a':5,'ad':6,'an':7,'b':8,'c':9,'e':10,'f':11,'g':12,'h':13,'i':14,'j':15,'k':16,'l':17,'m':18,'n':19,'nr':20,'ns':21,'nt':22,'nx':23,'nz':24,'o':25,'p':26,'q':27,'r':28,'s':29,'t':30,'u':31,'v':32,'vd':33,'Ag':34,'vn':35,'w':36,'y':37,'z':38,'d':39,'Rg':40,'Mg':41,'Bg':42}
		file = open('stopwords.txt','rb')
		line = file.readline()
		self.stop=[]
		while line:
			self.stop.append(line.strip('\r\n').strip('\n'))
			line = file.readline()
		self.speci = ["、",",","，","&"]
		self.biaodian = [u"\u3001",",",u"\uff0c",".",u"\u3002","|",u"\uff1b","_",u"\uff1a",":",u"\u201d",u"\u201c"]
		#self.biaodian = ["、",",","，",".","。","|","；","_","：",":","”","“"]
		#import DataProc
		#self.d = DataProc.DataProc()
		#self.d = Dep()
		pass
	#this function get info from indri
	def _process_data_indri(self,lines_info,newwords,tags=None,htmls=None,union=False):
		s = []
		p = []
		_seg = []
		_ner = []
		_html =[]
		_deps=[]
		list = []
		list_sen = []
		for i in xrange(len(lines_info)):
			(line_seg,line_pos,line_ner,line_dep) = lines_info[i]
			if tags is not None:
				tag = tags[i]
				nw = newwords[i][0].decode('utf-8')
				k = line_ner.count((self.relation[tag.decode('utf-8')])[1])
				if k==0 :
					continue
				elif k==1:
					if (self.relation[tag.decode('utf-8')])[1] == (self.relation[tag.decode('utf-8')])[1]:
						continue
			else:
				return
			seg = line_seg.split('\t')
			pos = line_pos.split('\t')
			ner = line_ner.split('\t')
			dep = line_dep.split('\t')
			pnw = -1
			if nw in seg:
				pnw = seg.index(nw) 
			else:
				for ds in xrange(len(seg)):
					if seg[ds].find(nw):
						pnw=ds
			pt = -1
			for nn in self.newwords2:
				if nn in seg:
					pt = seg.index(nn)
					break
				else:
					for ds in xrange(len(seg)):
						if seg[ds].find(nn):
							pt = ds
			if pt==-1 or pnw==-1:
				print ' '.join(seg).encode('utf-8')
				continue
			list_sen.append(' '.join(seg))
			if self.genre=='n_dict' or self.genre=='dict':
				ddd = collections.OrderedDict()
			elif self.genre=='line' or self.genre=='n_tuple':
				ddd = []
			if self.genre=='n_tuple':
				ddd.append(('Nun',line_pos.count('n')))
				ddd.append(('Nud',line_pos.count('\tr\t')))
				ddd.append(('Nuv',line_pos.count('v')))
				if pnw<=pt:
					lan = ('Seq',1)
					ddd.append(lan)
					lan = ('Dis',line_seg.count('\t',pnw,pt))
					ddd.append(lan)
					ss = seg[pnw:pt]
					pp = '\t'.join(pos[pnw:pt])
					lan =('tag',len(set(ss).intersection(set(self.biaodian))))
					ddd.append(lan)
					lan = ('spd',pp.count('\tr\t'))
					ddd.append(lan)
					lan = ('spn',pp.count('n'))
					ddd.append(lan)
					lan = ('spv',pp.count('v'))
					ddd.append(lan)
					lan = ('spz',pp.count('\tu\t'))
					ddd.append(lan)
				else:
					lan = ('Seq',0)
					ddd.append(lan)
					lan = ('Dis',line_seg.count('\t',pt,pnw))
					ddd.append(lan)
					ss = seg[pt:pnw]
					pp = '\t'.join(pos[pnw:pt])
					lan =('tag',len(set(ss).intersection(set(self.biaodian))))
					ddd.append(lan)
					lan = ('spd',pp.count('\tr\t'))
					ddd.append(lan)
					lan = ('spn',pp.count('n'))
					ddd.append(lan)
					lan = ('spv',pp.count('v'))
					ddd.append(lan)
					lan = ('spz',pp.count('\tu\t'))
					ddd.append(lan)
			elif self.genre=='n_dict' or self.genre=='dict':
				ddd['Nun']=line_pos.count('n')
				ddd['Nud']=line_pos.count('\tr\t')
				ddd['Nuv']=line_pos.count('v')
				if pnw<=pt:
					ddd['Seq']=1
					ddd['Dis']=line_seg.count('\t',pnw,pt)
					ss = seg[pnw:pt]
					pp = '\t'.join(pos[pnw:pt])
					ddd['tag']=len(set(ss).intersection(set(self.biaodian)))
					ddd['spd']=pp.count('\tr\t')
					ddd['spn']=pp.count('n')
					ddd['spv']=pp.count('v')
					ddd['spz']=pp.count('\tu\t')
				else:
					ddd['Seq']=0
					ddd['Dis']=line_seg.count('\t',pt,pnw)
					ss = seg[pt:pnw]
					pp = '\t'.join(pos[pnw:pt])
					ddd['tag']=len(set(ss).intersection(set(self.biaodian)))
					ddd['spd']=pp.count('\tr\t')
					ddd['spn']=pp.count('n')
					ddd['spv']=pp.count('v')
					ddd['spz']=pp.count('\tu\t')
			countner = []
			for id in xrange(len(seg)):
				if (ner[id]!="NOR") or (dep[id]=='HED_0'):
					countner.append(str(id+1))
			for id in xrange(len(seg)):
				ddeepp = dep[id].split('_')[0]
				#if ner[id] == (self.relation[tag.decode('utf-8')])[1]:
				if ner[id] != "NOR":
					if self.genre=='dict':
						ddd['word'+str(id)]=(self.relation[tag.decode('utf-8')])[1]
						ddd['pos'+str(id)]=pos[id]
					elif self.genre=='n_dict':
						ddd[ner[id]+'_'+ddeepp]=self.pos_tagger[pos[id]]
					elif self.genre=='n_tuple':
						lan = (ner[id]+'_'+ddeepp,self.pos_tagger[pos[id]])
						#lan = (ner[id],self.pos_tagger[pos[id]])
						ddd.append(lan)
					elif self.genre=='line':
						lan = (ner[id]+'_pos'+pos[id]).encode('utf-8')
						ddd.append(lan)
				else:
					if (dep[id].split('_')[1] in countner) or (dep[id]=='HED_0'):
						if self.genre=='n_tuple':
							lan = (ddeepp,self.pos_tagger[pos[id]]) 
							ddd.append(lan)
						elif self.genre=='n_dict' or self.genre=='dict':
							ddd[ddeepp]=self.pos_tagger[pos[id]]
						continue
					#elif seg[id].encode('utf-8') in self.stop:
					#	continue
					#if self.genre=='dict':
					#	ddd['word'+str(id)]=seg[id]
					#	ddd['pos'+str(id)]=pos[id]
					#elif self.genre=='n_dict':
					#	ddd[seg[id].encode('utf-8')]=self.pos_tagger[pos[id]]
					#elif self.genre=='n_tuple':
					#	lan = (seg[id].encode('utf-8'),self.pos_tagger[pos[id]])
					#elif self.genre=='line':
					#	lan = (seg[id]+"_pos"+pos[id]).encode('utf-8')
				#if self.genre=='n_tuple' or self.genre=='line':
				#	ddd.append(lan)
			#print (' \t '.join(seg)+'\n'+'\t'.join(dep)+'\n'+' \t '.join(pos)+'\n'+' \t '.join(ner)+'\n'+json.dumps(ddd)).encode('utf-8')
			s.append(nw)
			p.append(tag)
			_seg.append(seg)
			_ner.append(ner)
			_deps.append(dep)
			if htmls!=None:
				_html.append(htmls[i])
			if self.genre=='line':
				list.append(' '.join(ddd))
			elif self.genre=='n_dict' or self.genre=='dict' or self.genre=='n_tuple':
				list.append(ddd)
		if union:
			list.append(list_sen)
		if htmls!=None:
			return (s,p,list,_seg,_ner,_html,_deps)
		return (s,p,list,_seg,_ner)

	#this function call loacl function to get info of a sentencd
	def _process_data(self,lines,newwords,tags=None):
		s = []
		p = []
		_seg = []
		_ner = []
		list = []
		for i in xrange(len(lines)):
			line = lines[i]
			(line_seg,line_pos,line_ner)=self.d._dep_line_nmg(line)
			if tags is not None:
				tag = tags[i]
				nw = newwords[i][0].decode('utf-8')
				k = line_ner.count((self.relation[tag.decode('utf-8')])[1])
				if k==0 :
					continue
				elif k==1:
					if (self.relation[tag.decode('utf-8')])[1] == (self.relation[tag.decode('utf-8')])[1]:
						continue
			else:
				return
			seg = line_seg.split('\t')
			pos = line_pos.split('\t')
			ner = line_ner.split('\t')
			if self.genre=='n_dict' or self.genre=='dict':
				ddd = collections.OrderedDict()
			elif self.genre=='line' or self.genre=='n_tuple':
				ddd = []
			if self.genre=='n_tuple':
				pnw = line_seg.find(nw) 
				for nn in self.newwords2:
					pt = line_seg.find(nn)
					if pt!=-1:
						break
				if pnw<=pt:
					lan = ('Seq',1)
					ddd.append(lan)
					lan = ('Dis',line_seg.count('\t',pnw,pt))
					ddd.append(lan)
					lan = ('tag',line_seg.count(u'\u201d',pnw,pt)+line_seg.count(u'\u201c',pnw,pt)+line_seg.count(u'_',pnw,pt)+line_seg.count(u'\uff1a',pnw,pt)+line_seg.count(u':',pnw,pt)+line_seg.count(u'|',pnw,pt)+line_seg.count(u'.',pnw,pt)+line_seg.count(u'\u3002',pnw,pt)+line_seg.count(u',',pnw,pt)+line_seg.count(u'\uff0c',pnw,pt)+line_seg.count(u'\u3001',pnw,pt))
				else:
					lan = ('Seq',0)
					ddd.append(lan)
					lan = ('Dis',line_seg.count('\t',pt,pnw))
					ddd.append(lan)
					lan = ('tag',line_seg.count(u'\u201d',pt,pnw)+line_seg.count(u'\u201c',pt,pnw)+line_seg.count(u'_',pt,pnw)+line_seg.count(u'\uff1a',pt,pnw)+line_seg.count(u':',pt,pnw)+line_seg.count(u'|',pt,pnw)+line_seg.count(u'.',pt,pnw)+line_seg.count(u'\u3002',pt,pnw)+line_seg.count(u',',pt,pnw)+line_seg.count(u'\uff0c',pt,pnw)+line_seg.count(u'\u3001',pt,pnw))
				ddd.append(lan)
			for id in xrange(len(seg)):
				#if ner[id] == (self.relation[tag.decode('utf-8')])[1]:
				if ner[id] != "NOR":
					if self.genre=='dict':
						ddd['word'+str(id)]=(self.relation[tag.decode('utf-8')])[1]
						ddd['pos'+str(id)]=pos[id]
					elif self.genre=='n_dict':
						ddd[ner[id]+str(id)]=self.pos_tagger[pos[id]]
					elif self.genre=='n_tuple':
						lan = (ner[id],self.pos_tagger[pos[id]])
					elif self.genre=='line':
						lan = (ner[id]+'_pos'+pos[id]).encode('utf-8')
				else:
					if seg[id].encode('utf-8') in self.stop:
						continue
					if self.genre=='dict':
						ddd['word'+str(id)]=seg[id]
						ddd['pos'+str(id)]=pos[id]
					elif self.genre=='n_dict':
						ddd[seg[id].encode('utf-8')]=self.pos_tagger[pos[id]]
					elif self.genre=='n_tuple':
						lan = (seg[id].encode('utf-8'),self.pos_tagger[pos[id]])
					elif self.genre=='line':
						lan = (seg[id]+"_pos"+pos[id]).encode('utf-8')
				if self.genre=='n_tuple' or self.genre=='line':
					ddd.append(lan)
			print (' \t '.join(seg)+'\n'+' \t '.join(ner)+'\n'+json.dumps(ddd)).encode('utf-8')
			s.append(nw)
			p.append(tag)
			_seg.append(seg)
			_ner.append(ner)
			if self.genre=='line':
				list.append(' '.join(ddd))
			elif self.genre=='n_dict' or self.genre=='dict' or self.genre=='n_tuple':
				list.append(ddd)
		return (s,p,list,_seg,_ner)

