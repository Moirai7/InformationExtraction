#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
import Classifier
import traceback  
import Levenshtein
import commands
import json
import re
#from dep import TextSim
class Process:
	def __init__(self):
		#self.t = TextSim()
		self.rels = {}
		self.rels["erzi"] = [u"\u513f\u5b50"]    
                self.rels["nver"] = [u"\u5973\u513f"]
                self.rels["nanyou"] = [u"\u7537\u670b\u53cb",u"\u7537\u53cb"]
                self.rels["nvyou"] = [u"\u5973\u670b\u53cb",u"\u5973\u53cb"]
                self.rels["muqin"] = [u"\u5988\u5988",u"\u6bcd\u4eb2"]
                self.rels["fuqin"] = [u"\u7238\u7238",u"\u7236\u4eb2"]
                self.rels["qizi"] = [u"\u8001\u5a46",u"\u592b\u4eba",u"\u59bb\u5b50",u"\u592b\u5987"]
                self.rels["zhangfu"] = [u"\u8001\u516c",u"\u4e08\u592b",u"\u592b\u5987"]
		self.q = re.compile(r'\\')
		self.p = re.compile('<[^>]+>') 
		self.b = re.compile('(http|ftp|https)?(:\/\/)?([\w\-_]+\.)+([\w\-:_]+/)([\w\-\.,@^=%&amp;:/~\+#]+)?')
		pass

	def _semi(self,lines):
		strs=[]
		for l in lines:
			check=True
			l = self.p.sub("", l)
			l = self.b.sub("", l)
			l = l.strip('\n')
			if len(l)>1000:
				continue
			for s in strs:
				point = self.t.sim(s,l)
				print s
				print l
				print point
				if point>3:
					check=False
					if len(s)>len(l):
						strs.remove(s)
						strs.append(l)
					break
				#if point<2:
					#print s
					#print l
					#print len(l)
					#print point
			if check:
				strs.append(l)
		return strs
	
	def _semi_without(self,lines,lines_info,htmls):
		strs=[]
		strs_info=[]
		strs_htmls=[]
		for i in xrange(len(lines)):
			l = lines[i]
			l = self.p.sub("", l)
			l = self.b.sub("", l)
			l = l.strip('\n').lstrip('”').lstrip('。').lstrip('.').lstrip('，').lstrip(',')
			if len(l)>400 or len(l)<5:
				continue
			strs.append(l)
			strs_info.append(lines_info[i])
			strs_htmls.append(htmls[i])
		return (strs,strs_info,strs_htmls)

	def _semi_Levenshtein(self,lines,lines_info):
		strs=[]
		strs_info=[]
		for id in xrange(len(lines)):
			l = lines[id]
			line = l.split('\t')
			l = line[3]
			check=True
                        #l = self.p.sub("", l)
                        #l = self.b.sub("", l)
			#l = l.strip('\n')
			#l = l.decode('utf-8').lstrip(u'\u201d').lstrip(u'\u3002').lstrip('.').lstrip(u'\uff0c').lstrip(',').encode('utf-8')
			#l = l.lstrip('”').lstrip('。').lstrip('.').lstrip('，').lstrip(',')
			#line[3] = l
			if len(l)>400 or len(l)<5:
                                continue
			for s in strs:
				ss = s.split('\t')
				s = ss[3]
				#print s
				#print l
				#distance = Levenshtein.distance(s,l)
				#print 'distance : '+str(distance) 
				ratio = Levenshtein.ratio(s,l)
				#print 'ratio : '+str(ratio) 
				#if distance<105 and ratio>0.6:
				if ratio>0.6:
					check=False
					break
			if check:
				strs_info.append(lines_info[id])
				strs.append('\t'.join(line))
		return (strs,strs_info)
	
	def _train_data(self,iden,res=None,res_info=None):
		if res==None:
			import cPickle as pickle
			strs = 'classifier/train_res_'+iden+'.txt'
			f=open(strs)
			strs = 'classifier/train_info_'+iden+'.txt'
			f2=open(strs)
			res=pickle.load(f)
			f.close()
			res_info=pickle.load(f2)
			f2.close()
		else:
			(res,res_info)=self._fanhua_extract(iden)
		#self.c = Classifier.Classifier(test=False,type='RandomForestClassifier',vec='featurehash',genre='n_dict',identify=iden)
		self.c = Classifier.Classifier(test=False,type='AdaBoostClassifier',vec='featurehash',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(test=False,type='gaussiannb',vec='union',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(test=False,vec='dictvec',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(type='svc',test=False,vec='featurehash',genre='n_dict',identify=iden)
		self.c.test_train_indri(res,res_info)

	def _proc_call_shell(self,iden):
		self.c = Classifier.Classifier(type='AdaBoostClassifier',vec='featurehash',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(vec='dictvec',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(type='svc',vec='featurehash',genre='n_dict',identify=iden)
		all=0
		current=0
		for line in sys.stdin:
			line = line.strip('\r\n').strip('\n').split('\t')
			try:
				line[0] = line[0].strip() 
				#line[1] ='nvyou'
				#line.append('emma')
				#if line[1]!='muqin':
				#	break
				if line[1] == 'qizi':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","妻子 夫妇 老婆 夫人"], 500, 40, 10]}\'`'
				elif line[1] == 'zhangfu':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","丈夫 老公 夫妇"], 500, 40, 10]}\'`'
				elif line[1] == 'erzi':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","儿子"], 500, 40, 10]}\'`'
				elif line[1] == 'nver':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","女儿"], 500, 40, 10]}\'`'
				elif line[1] == 'fuqin':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","父亲 爸爸"], 500, 40, 10]}\'`'
				elif line[1] == 'muqin':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","母亲 妈妈"], 500, 40, 10]}\'`'
				elif line[1] == 'nvyou':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","女友 女朋友"], 500, 40, 10]}\'`'
				elif line[1] == 'nanyou':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","男友 男朋友"], 500, 40, 10]}\'`'
				(llll,lines_info) = self._process_json(strs,line)
				if llll is None:
					continue
				list = self.c.test_test_indri(llll,lines_info)
				if len(list)==0:
					continue
				#if line[2] != 'emma':
				if True:
					asa = 0
					if len(list) != 0:
						all+=1
					for l in list:
						print 'result'+l.encode('utf-8')
						if l.split('\t')[2]==line[2].decode('utf-8'):
							asa=1
					if asa==1:
						current+=1
						print 'current : '+line[0]+'\t'+line[1]+'\t'+line[2]
					else:
						print 'wrong(241) : '+line[0]+'\t'+line[1]+'\t'+line[2]
					print 'all :'+str(all)
					print 'current :'+str(current)
				else:
					asa=0
					if len(list) != 0:
						all+=1
					else:
						continue
					print 'high score current : '+line[0]+'\t'+line[1]+'\t'+line[2]
					asa=0
					for l in list:
						tline = l.encode('utf-8').split('\t')
						if tline[2] == line[2]:
							current+=1
							asa=1
						strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+tline[0]+'","'+tline[2]+'"], 500, 40, 10]}\'`'
						(llll,lines_info) = self._process_json(strs,tline)
						if llll is None:
							continue	
						#print tline[0]+' '+tline[2]
						(score,lens) = self.c.test_verify_indri(llll,lines_info)
						print 'high score result( score '+str(score)+' length '+str(lens)+') : '+l.encode('utf-8')
					if asa==0:
						print 'still wrong!'
					print 'all :'+str(all)
					print 'current :'+str(current)
			except IndexError:
				print 'waiting...'
				print 'wrong(269) : '+line[0]+'\t'+line[1]+'\t'+line[2]
				traceback.print_exc()
				continue
			except Exception,e:
				print 'wrong(273) : '+line[0]+'\t'+line[1]+'\t'+line[2]
				traceback.print_exc()  
				continue
		print 'all :'+str(all)
		print 'current :'+str(current)

	def _fanhua_extract(self,iden):
		res =[]
		res_info = []
		for ll in sys.stdin:
			line = ll.strip('\r\n').strip('\n').split('\t')
			try:
				line[0] = line[0].strip()
				if line[1] == 'qizi':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","妻子 夫妇 老婆 夫人"], 500, 40, 10]}\'`'
				elif line[1] == 'zhangfu':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","丈夫 老公 夫妇"], 500, 40, 10]}\'`'
				elif line[1] == 'erzi':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","儿子"], 500, 40, 10]}\'`'
				elif line[1] == 'nver':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","女儿"], 500, 40, 10]}\'`'
				elif line[1] == 'fuqin':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","父亲 爸爸"], 500, 40, 10]}\'`'
				elif line[1] == 'muqin':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","母亲 妈妈"], 500, 40, 10]}\'`'
				elif line[1] == 'nvyou':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","女友 女朋友"], 500, 40, 10]}\'`'
				elif line[1] == 'nanyou':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","男友 男朋友"], 500, 40, 10]}\'`'
				#print 'Process indri start'
				strs=commands.getoutput(strs).split('\n')
				js = json.loads(strs[3].replace('\r\n', '').replace('\n',''), strict=False)
				lists = js['result']['_ret']
				#htmls = []
				lines =[]
				lines_info=[]
				cc=0
				for l in lists:
					#h = self.q.sub("",l['docno'])
					#htmls.append(self.q.sub("",l['docno']).encode('utf-8'))
					ls = l['passage'].encode('utf-8')
					if ls.find(line[2]) ==-1:
						if cc>200:
							continue
						cc+=1
						lines.append(line[0]+'\temma\t'+line[2]+'\t'+ls)
						lines_info.append(self._process(l['pass_analyze']))
					else:
						lines.append(line[0]+'\t'+line[1]+'\t'+line[2]+'\t'+ls)
						lines_info.append(self._process(l['pass_analyze']))
				if len(lines)<1:
					continue
				if line[1] == 'qizi':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","妻子 夫妇 老婆 夫人","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'zhangfu':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","丈夫 老公 夫妇","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'erzi':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","儿子","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'nver':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","女儿","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'fuqin':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","父亲 爸爸","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'muqin':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","母亲 妈妈","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'nvyou':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","女友 女朋友","'+line[2]+'"], 500, 40, 10]}\'`'
				elif line[1] == 'nanyou':
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","男友 男朋友","'+line[2]+'"], 500, 40, 10]}\'`'
				strs=commands.getoutput(strs).split('\n')
				js = json.loads(strs[3].replace('\r\n', '').replace('\n',''), strict=False)
				lists = js['result']['_ret']
				for l in lists:
					lines_info.append(self._process(l['pass_analyze']))
					l = l['passage'].encode('utf-8')
					lines.append(line[0]+'\t'+line[1]+'\t'+line[2]+'\t'+l)
				if len(lines)<1:
					continue
				(lines,lines_info) = self._semi_Levenshtein(lines,lines_info)
				for l in xrange(len(lines)):
					res.append(lines[l])
					res_info.append(lines_info[l])
					print lines[l]
				#continue
				#if len(lines)<1:
				#	continue
			except IndexError:
				continue
			except Exception,e:
                                traceback.print_exc()
				continue
		import cPickle as pickle
		strs = 'classifier/train_res_'+iden+'.txt'
		print strs
		f=open(strs,'wb')
		strs = 'classifier/train_info_'+iden+'.txt'
		print strs
		f2=open(strs,'wb')
		pickle.dump(res,f)
		f.close()
		pickle.dump(res_info,f2)
		f2.close()
		return (res,res_info)
		
	def _process_json(self,strs,line):
		strs=commands.getoutput(strs).split('\n')
		js = json.loads(strs[3].replace('\r\n', '').replace('\n',''), strict=False)
		lists = js['result']['_ret']
		lines_info = []
		lines = []
		htmls = []
		for l in lists:
			h = self.q.sub("",l['docno'])
			htmls.append(self.q.sub("",l['docno']).encode('utf-8'))
			lines_info.append(self._process(l['pass_analyze']))
			lines.append(l['passage'].encode('utf-8'))
		if len(lines)<1:
			print 'too small info from indri '+line[0]+'\t'+line[1]+'\t'+line[2]
			return (None,None)
		(lines,lines_info,htmls) = self._semi_without(lines,lines_info,htmls)
		if len(lines)<1:
			print 'too small info from indri '+line[0]+'\t'+line[1]+'\t'+line[2]
			return (None,None)
		llll=[]
		for idd in xrange(len(lines)):
			l = lines[idd]
			llll.append(line[0]+'\t'+line[1]+'\t'+line[2]+'\t'+l+'\t'+htmls[idd])
		return (llll,lines_info)

	def _process(self,lists):
		seg = []
		lines = []
		pos = []
		dep = []
		for i in xrange(len(lists)):
			l = lists[i]
			if l['word'].strip() == None:
				pass	
			else:
				seg.append(l['word'])
			if l['ner'].strip() == None:
				lines.append("_")
			elif l['ner']=='PER':
				lines.append('PERSON')
			else:
				lines.append(l['ner'])
			if l['postag'].strip() == None:
				pos.append("_")
			else:
				pos.append(l['postag'])
			if l['deprel'].strip() == None or l['head']== None:
                                dep.append('None_None')
			else:
				dep.append(l['deprel']+'_'+str(l['head']))
				#dep.append(l['deprel'])
		return ('\t'.join(seg),'\t'.join(pos),'\t'.join(lines),'\t'.join(dep))

if __name__ == '__main__':
	p=Process()
	if len(sys.argv)==3:
		test = sys.argv[1]
		identify = sys.argv[2]
	else:
		test = 'test'
		identify = 'muqin'
	import time
	start = time.clock()
	start2 = time.time()
	#p._p_fanhua()
	#p._process()
	if test == 'test':
		print test
		p._proc_call_shell(identify)
	elif test == 'train':
		print test
		#p._fanhua_extract(identify)
		#p._train_data(identify,res='emma')
		p._train_data(identify)
	end = time.clock()
	end2 = time.time()
	print end-start
	print end2-start2
	#p._proc_call_shell_high_pv()
