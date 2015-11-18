#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
from sklearn import metrics
from sklearn.feature_extraction import DictVectorizer, FeatureHasher
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
from sklearn.ensemble import BaggingClassifier,ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier,GradientBoostingClassifier,VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.decomposition import PCA
import numpy
import math
import collections
#from merge import Merge
#from dep import Dep
import json
import traceback
#should not use the class right now,i need to change the method _process_data to let the test data can get answer accurately
class Classifier:
	#genre:dict n_tuple n_dict line
	#vec:hashingvec featurehash dictvec
	#type:gaussiannb lr
	def __init__(self,test=True,genre='line',vec='hashingvec',type='lr',identify='muqin'):
		self.genre = genre
		self.vec = vec
		self.type = type
		self.identify=identify
		if identify == 'muqin':
			self.newwords2=[u"\u5988\u5988",u"\u6bcd\u4eb2"]#muqin
		elif identify == 'fuqin':
			self.newwords2=[u"\u7238\u7238",u"\u7236\u4eb2"]#fuqin
		elif identify == 'erzi':
			self.newwords2=[u"\u513f\u5b50"]#erzi
		elif identify == 'nver':
			self.newwords2=[u"\u5973\u513f"]#nver
		elif identify == 'nvyou':
			self.newwords2=[u"\u5973\u670b\u53cb",u"\u5973\u53cb"]#nvyou
		elif identify == 'nanyou':
			self.newwords2=[u"\u7537\u670b\u53cb",u"\u7537\u53cb"]#nanyou
		elif identify == 'zhangfu':
			self.newwords2=[u"\u8001\u516c",u"\u4e08\u592b",u"\u592b\u5987"]#zhangfu
		elif identify == 'qizi':
			self.newwords2=[u"\u8001\u5a46",u"\u592b\u4eba",u"\u59bb\u5b50",u"\u592b\u5987"]#qizi
		print self.newwords2[0].encode('utf-8')
		import re
		self.de = re.compile(u"[\u4e00-\u9fa5]")
		self.relation = {u'fuqin':('PERSON','PERSON'),u'erzi':('PERSON','PERSON'),u'nver':('PERSON','PERSON'),u'nvyou':('PERSON','PERSON'),u'nanyou':('PERSON','PERSON'),u'muqin':('PERSON','PERSON'),u'emma':('PERSON','PERSON'),u'zhangfu':('PERSON','PERSON'),u'qizi':('PERSON','PERSON'),u'\u5973\u53cb':('PERSON','PERSON'),u'\u5973\u513f':('PERSON','PERSON'),u'\u59bb\u5b50':('PERSON','PERSON'),u'\u4e08\u592b':('PERSON','PERSON'),u'\u524d\u592b':('PERSON','PERSON'),u'\u7236\u4eb2':('PERSON','PERSON'),u'\u8eab\u9ad8':('PERSON','HEIGHT'),u'\u751f\u65e5':('PERSON','DATE'),u'\u64ad\u51fa\u65f6\u95f4':('FILM','TIME'),u'\u4e3b\u9898\u66f2':('FILM','MUSIC')}
		self.pos_tagger={'Dg':1,'Ng':2,'Tg':3,'Vg':4,'a':5,'ad':6,'an':7,'b':8,'c':9,'e':10,'f':11,'g':12,'h':13,'i':14,'j':15,'k':16,'l':17,'m':18,'n':19,'nr':20,'ns':21,'nt':22,'nx':23,'nz':24,'o':25,'p':26,'q':27,'r':28,'s':29,'t':30,'u':31,'v':32,'vd':33,'Ag':34,'vn':35,'w':36,'y':37,'z':38,'d':39,'Rg':40,'Mg':41,'Bg':42}
		#import DataProc
		#self.d = DataProc.DataProc()
		#self.d = Dep()
		if test:
			import cPickle as pickle
			from sklearn.externals import joblib
			if self.identify == 'muqin':
				self.normalizer=pickle.load(open('classifier/train_data/muqin_norm.txt', 'rb'))
				#self.normalizer=pickle.load(open('classifier/test/train_norm.txt', 'rb'))
                	        #self.clf = joblib.load('classifier/test/fanhua_logic_position.train')
                	        self.clf = joblib.load('classifier/train_data/muqin_logic_dep.train')
               	 	elif self.identify == 'fuqin':
				self.normalizer=pickle.load(open('classifier/train_data/fuqin_norm.txt', 'rb'))
                 	        self.clf = joblib.load('classifier/train_data/fuqin_logic_dep.train')
              		elif self.identify == 'erzi':
				self.normalizer=pickle.load(open('classifier/train_data/erzi_norm.txt', 'rb'))
                        	self.clf = joblib.load('classifier/train_data/erzi_logic_dep.train')
                	elif self.identify == 'nver':
				self.normalizer=pickle.load(open('classifier/train_data/nver_norm.txt', 'rb'))
                	        self.clf = joblib.load('classifier/train_data/nver_logic_dep.train')
                	elif self.identify == 'nvyou':
				self.normalizer=pickle.load(open('classifier/train_data/nvyou_norm.txt', 'rb'))
                        	self.clf = joblib.load('classifier/train_data/nvyou_logic_dep.train')
                	elif self.identify == 'nanyou':
				self.normalizer=pickle.load(open('classifier/train_data/nanyou_norm.txt', 'rb'))
                        	self.clf = joblib.load('classifier/train_data/nanyou_logic_dep.train')
                	elif self.identify == 'zhangfu':
				self.normalizer=pickle.load(open('classifier/train_data/zhangfu_norm.txt', 'rb'))
                        	self.clf = joblib.load('classifier/train_data/zhangfu_logic_dep.train')
                	elif self.identify == 'qizi':
				self.normalizer=pickle.load(open('classifier/train_data/qizi_norm.txt', 'rb'))
                       	 	self.clf = joblib.load('classifier/train_data/qizi_logic_dep.train')
			#self.clf = joblib.load('classifier/train_data/nanyou.train')
			#self.wf = open('result_fanhua_change','ab')
			print self.clf
		file = open('stopwords.txt','rb')
		line = file.readline()
		self.stop=[]
		while line:
			self.stop.append(line.strip('\r\n').strip('\n'))
			line = file.readline()
		self.speci = ["、",",","，","&"]
		self.biaodian = [u"\u3001",",",u"\uff0c",".",u"\u3002","|",u"\uff1b","_",u"\uff1a",":",u"\u201d",u"\u201c"]
		#self.biaodian = ["、",",","，",".","。","|","；","_","：",":","”","“"]
		pass

	#this function get info from indri
	def _process_data_indri(self,lines_info,newwords,tags=None,htmls=None):
		s = []
		p = []
		_seg = []
		_ner = []
		_html =[]
		_deps=[]
		list = []
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
			if self.genre=='n_dict' or self.genre=='dict':
				ddd = collections.OrderedDict()
			elif self.genre=='line' or self.genre=='n_tuple':
				ddd = []
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

	def _vectorize_HashingVectorizer(self,words):
		vec = HashingVectorizer(n_features=2**20)
		vectorized = vec.transform(words)
		return vectorized

	def _vectorize_hash(self,words):
		if self.genre == 'n_tuple':
			vec = FeatureHasher(n_features=2**10,input_type='pair')
		elif self.genre == 'n_dict':
			vec = FeatureHasher(n_features=2**10)
		vectorized = vec.transform(words)
		#vectorized = preprocessing.scale(vectorized)
		#vectorized = preprocessing.normalize(vectorized)
		return vectorized
	
	#the train data and test data must be in the same dimension 
	def _vectorize_dict(self,words):
		vec =  DictVectorizer()
		pos_vectorized = vec.fit_transform(words)
		return pos_vectorized

	def _vectorize_union(self,words):
		pca = PCA(n_components=2)
		selection = SelectKBest(k=1)
		combined_features = FeatureUnion([("pca", pca), ("univ_select", selection)])
		pos_vectorized = combined_features.fit(X, y).transform(X)

	def _train_clf(self,vec,tag):
		if self.type =='gaussiannb':
			clf = GaussianNB()
		elif self.type =='lr':
			#clf = LogisticRegression(multi_class='multinomial',solver='lbfgs')
			clf = LogisticRegression(solver='lbfgs')
		elif self.type =='svc':
			clf = SVC(probability=True)#default with 'rbf'  
		elif self.type == 'BaggingClassifier':
			clf = BaggingClassifier(KNeighborsClassifier())
		elif self.type =='KNeighborsClassifier':
			clf = KNeighborsClassifier()
		elif self.type =='RandomForestClassifier':
			clf =RandomForestClassifier()
		elif self.type=='AdaBoostClassifier':
			clf = AdaBoostClassifier()
		elif self.type=='DecisionTreeClassifier':
			clf = DecisionTreeClassifier()
		elif self.type=='ExtraTreesClassifier':
			clf = ExtraTreesClassifier()
		elif self.type=='GradientBoostingClassifier':
			clf = GradientBoostingClassifier()
		elif self.type=='VotingClassifier':
			clf1 = DecisionTreeClassifier()
			clf2 = RandomForestClassifier()
			clf3 = LogisticRegression(solver='lbfgs')
			clf4 = GradientBoostingClassifier()
			clf5 = AdaBoostClassifier()
			#clf3 = GaussianNB()
			#clf = VotingClassifier(estimators=[('dt', clf1), ('rf', clf2), ('gnb', clf3)], voting='soft',weights=[3,3,1])
			clf = VotingClassifier(estimators=[('dt', clf1), ('rf', clf2),('lr',clf3),('gb',clf4),('ac',clf5)], voting='soft',weights=[2,2,3,3,3])
		print 'calu'
		if self.type =='gaussiannb' or self.type=='GradientBoostingClassifier':
			clf.fit(vec.toarray(), numpy.asarray(tag))
		else:
			clf.fit(vec, numpy.asarray(tag))
		#clf.fit(vec.toarray(), numpy.asarray(tag))
		print 'calu end'
		return clf

	def train_using_process(self,p,words):
		if self.vec =='hashingvec':
			vec = self._vectorize_HashingVectorizer(words)
		elif self.vec =='featurehash':
			vec = self._vectorize_hash(words)
		elif self.vec =='dictvec':
			vec = self._vectorize_dict(words)
		elif self.vec =='union':
			vec = self._vectorize_union(words)
		normalizer = preprocessing.Normalizer().fit(vec)
                import cPickle as pickle
                if self.identify == 'muqin':
                                pickle.dump(normalizer,open('classifier/train_data/muqin_norm.txt', 'wb'))
                elif self.identify == 'fuqin':
                                pickle.dump(normalizer,open('classifier/train_data/fuqin_norm.txt', 'wb'))
                elif self.identify == 'erzi':
                                pickle.dump(normalizer,open('classifier/train_data/erzi_norm.txt', 'wb'))
                elif self.identify == 'nver': 
                                pickle.dump(normalizer,open('classifier/train_data/nver_norm.txt', 'wb'))
                elif self.identify == 'nvyou':
                                pickle.dump(normalizer,open('classifier/train_data/nvyou_norm.txt', 'wb'))
                elif self.identify == 'nanyou':
                                pickle.dump(normalizer,open('classifier/train_data/nanyou_norm.txt', 'wb'))
                elif self.identify == 'zhangfu':
                                pickle.dump(normalizer,open('classifier/train_data/zhangfu_norm.txt', 'wb'))
                elif self.identify == 'qizi':
                                pickle.dump(normalizer,open('classifier/train_data/qizi_norm.txt', 'wb'))
		#pickle.dump(normalizer,open('test/train_norm.txt', 'wb'))
		vec = normalizer.transform(vec)
		print len(words)
		print len(p)
		return self._train_clf(vec,p)

	def classifier_using_process(self,s,p,words,_seg,_ner,clf,htmls,an,deps):
		if self.vec =='hashingvec':
			vec = self._vectorize_HashingVectorizer(words)
		elif self.vec =='featurehash':
			vec = self._vectorize_hash(words)
		elif self.vec =='dictvec':
			vec = self._vectorize_dict(words)
		vec = self.normalizer.transform(vec)   
		pred = clf.predict(vec.toarray())
		dec = clf.predict_proba(vec.toarray())
		#dec = clf.decision_function(vec.toarray())
		m_s=[]
		m_p=[]
		m_seg=[]
		m_ner=[]
		m_dep=[]
		for i in xrange(len(p)):
			if dec[i][1]<0.5:
				print 'test info : '+s[i].encode('utf-8')+' '+an+' emma '+htmls[i]+' '+''.join(_seg[i]).encode('utf-8')
			else:
				print 'test info : '+s[i].encode('utf-8')+' '+an+' '+pred[i]+' '+htmls[i]+' '+''.join(_seg[i]).encode('utf-8')
			print dec[i]
			#if p[i] == pred[i] and dec[i]>25.0:
			#if p[i] == pred[i] and dec[i][1]>0.5:
			if p[i]==pred[i]:
				#print s[i].encode('utf-8')+' '+str(i+1)+' '+pred[i]+' '+''.join(_seg[i]).encode('utf-8')
				m_s.append(s[i])
				m_p.append(p[i])
				m_seg.append(_seg[i])
				m_ner.append(_ner[i])
				m_dep.append(deps[i])
			else:
				pass
		return (m_s,m_p,m_seg,m_ner,m_dep)
		
	def classifier_get_score(self,s,p,words,_seg,clf):
		if self.vec =='hashingvec':
			vec = self._vectorize_HashingVectorizer(words)
		elif self.vec =='featurehash':
			vec = self._vectorize_hash(words)
		elif self.vec =='dictvec':
			vec = self._vectorize_dict(words)
		vec = self.normalizer.transform(vec)
		pred = clf.predict(vec.toarray())
		score = accuracy_score(p, pred)
		#for i in xrange(len(p)):
		#	print s[i].encode('utf-8')+' '+str(i+1)+' '+pred[i]+' '+''.join(_seg[i]).encode('utf-8')
		return (score,len(pred))

	#count the answer of a relation
	def statistics(self,newwords,tags,segs,ners,deps):
		s=newwords[0]
		p=tags[0]
		answer=[]
		fromline=[]
		dict = collections.OrderedDict()
		for i in xrange(len(tags)):
			tag = tags[i]
			seg = segs[i]
			ner = ners[i]
			#dep = deps[i]
			index_p=-1
			for nn in self.newwords2:
				if nn in seg:
					index_p = seg.index(nn)
					break
				else:
					for ds in xrange(len(seg)):
						if seg[ds].find(nn):
							index_p = ds
						else:
							index_p=-1
			if index_p == -1:
				print 'None P '
			if newwords[i] in seg:
				index_s = seg.index(newwords[i])
			else:
				for ds in xrange(len(seg)):
					if seg[ds].find(newwords[i]):
						index_s = ds
					else:
						index_s = -1
				if index_s == -1:
					print 'None S'
			print ' '.join(seg).encode('utf-8')+str(index_p)+','+str(index_s)
			#print ' '.join(dep).encode('utf-8')
			_a = []
			lianxu = 0
			dict_dis = collections.OrderedDict()
			fromline.append(''.join(seg))
			for id in xrange(len(seg)):
				if tags is not None:
					if ner[id] == (self.relation[tag.decode('utf-8')])[1]:
						ll = len(self.de.findall(seg[id]))
						if ll==0:
							ll=len(seg[id])
						if (seg[id] != newwords[i]) and (seg[id] not in _a)  and (ll>1) and seg[id].isdigit()==False:
							try:
								distance = 0.1/(math.fabs(id-index_p)+math.fabs(id-index_s))
								if id-index_p==1 and id-index_s==2:
									distance+=2
								elif id-index_p==1 and ner[id-2] != (self.relation[tag.decode('utf-8')])[1]:
									distance+=1
								if id>index_p:
									pnw=id
									pt=index_p
								else:
									pnw=index_p
									pt=id
								ss = seg[pt:pnw]
								if len(ss)!=0 and len(set(ss).intersection(set(self.biaodian)))==0:
									distance+=0.1
								#if dep[id].split('_')[1]==index_p+1:
								#	print 'dep info'
								#	distance+=1
								#elif dep[id].split('_')[1]==index_s+1:
								#	print 'dep info'
								#	distance+=0.5
							except :
								traceback.print_exc()
								print 'math error'+newwords[i].encode('utf-8')+','+tag.encode('utf-8')+','+seg[id].encode('utf-8')+str(math.fabs(id-index_p))+' '+str(math.fabs(id-index_s))
								continue
							print newwords[i].encode('utf-8')+','+tag.encode('utf-8')+','+seg[id].encode('utf-8')+','+str(distance+0.15)
							if seg[id] in answer:
								dict[seg[id]]+=distance+0.15
							else:
								dict[seg[id]]=distance+0.15
							dict_dis[seg[id]]=distance+0.15
							lianxu += 1
							_a.append(seg[id])
							answer.append(seg[id])
					else:
						if seg[id].encode('utf-8') in self.speci:
							continue
						if lianxu>=3:
							while lianxu>0:
								asa = answer.pop()
								dict[asa]-=dict_dis[asa]
								lianxu -= 1
						lianxu = 0
		dict= sorted(dict.iteritems(), key=lambda d:d[1], reverse = True)
		list=[]
		try :
			max = dict[0][1]
			if max<=0:
				return []
		except:
			return []
		top=3
		for v in dict:
			if top>0:
				if v[1] != max :
					top-=1
					max = top
				strs = s+'\t'+p+'\t'+v[0]+'\t'+str(v[1])
				for line in fromline:
					if line.find(v[0]) != -1:
						strs += '\t'+line
				list.append(strs)
		return list

	def test_train_indri(self,l,lines_info):
		lines =[]
		tags =[]
		newwords=[]
		for line in l:
			try:
				line = line.split('\t')
				tags.append(line[1])
				newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
				lines.append(line[3].strip())
			except Exception,e:
				traceback.print_exc()
		(s,p,word,_seg,_ner) = self._process_data_indri(lines_info,newwords,tags=tags)
		import cPickle as pickle
		if self.identify == 'muqin':
 			f = open('classifier/train_tag_muqin_dep.txt', 'wb')             
 			f2 = open('classifier/train_hash_muqin_dep.txt', 'wb')             
			#pass
                elif self.identify == 'fuqin':
            		f = open('classifier/train_tag_fuqin_dep.txt', 'wb')
            		f2 = open('classifier/train_hash_fuqin_dep.txt', 'wb')
                elif self.identify == 'erzi':
          		f = open('classifier/train_tag_erzi_dep.txt', 'wb')
          		f2 = open('classifier/train_hash_erzi_dep.txt', 'wb')
                elif self.identify == 'nver':
        		f = open('classifier/train_tag_nver_dep.txt', 'wb')
        		f2 = open('classifier/train_hash_nver_dep.txt', 'wb')
                elif self.identify == 'nvyou':
			f = open('classifier/train_tag_nvyou_dep.txt', 'wb')
			f2 = open('classifier/train_hash_nvyou_dep.txt', 'wb')
                elif self.identify == 'nanyou':
    			f = open('classifier/train_tag_nanyou_dep.txt', 'wb')
    			f2 = open('classifier/train_hash_nanyou_dep.txt', 'wb')
                elif self.identify == 'zhangfu':
  			f = open('classifier/train_tag_zhangfu_dep.txt', 'wb')
  			f2 = open('classifier/train_hash_zhangfu_dep.txt', 'wb')
                elif self.identify == 'qizi':
			f = open('classifier/train_tag_qizi_dep.txt', 'wb')
			f2 = open('classifier/train_hash_qizi_dep.txt', 'wb')
		pickle.dump(word,f2)
		f2.close()
		pickle.dump(p,f)
		f.close()
		#quit(0)
		clf = self.train_using_process(p,word)
		from sklearn.externals import joblib
                if self.identify == 'muqin':
			joblib.dump(clf,'classifier/train_data/muqin_logic_dep.train')
                elif self.identify == 'fuqin':
			joblib.dump(clf,'classifier/train_data/fuqin_logic_dep.train')
                elif self.identify == 'erzi':
			joblib.dump(clf,'classifier/train_data/erzi_logic_dep.train')
                elif self.identify == 'nver':
			joblib.dump(clf,'classifier/train_data/nver_logic_dep.train')
                elif self.identify == 'nvyou':
			joblib.dump(clf,'classifier/train_data/nvyou_logic_dep.train')
                elif self.identify == 'nanyou':
			joblib.dump(clf,'classifier/train_data/nanyou_logic_dep.train')
                elif self.identify == 'zhangfu':
			joblib.dump(clf,'classifier/train_data/zhangfu_logic_dep.train')
                elif self.identify == 'qizi':
			joblib.dump(clf,'classifier/train_data/qizi_logic_dep.train')
		print clf

	def test_test_indri(self,_lines,lines_info):
		lines=[]
		tags=[]
		newwords=[]
		htmls=[]
		an = '' 
		for line in _lines:
		     try:
			line = line.split('\t')
			if len(line)<4:
				#print 'read wrong ('+str(len(line))+'):'+'\t'.join(line)
				continue
			tags.append(line[1])
			an = line[2]
			htmls.append(line[4].strip())
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			if line[3].strip()!='':
				lines.append(line[3].strip())
		     except :
			     info=sys.exc_info() 
			     print info[0],":",info[1]
		      	     print 'read wrong (except):'+'\t'.join(line)
		#print 'Process Data start'
		(s,p,words,_seg,_ner,htmls,deps) = self._process_data_indri(lines_info,newwords,tags=tags,htmls=htmls)
		if len(words)<2:
			print ' words <2 too small'
			return []
		#print 'Classifier start'
		(s,p,_seg,_ner,deps) = self.classifier_using_process(s,p,words,_seg,_ner,self.clf,htmls,an,deps)
		if len(p)<2:
			print 'classifier <2 too small'
			return []
		list=self.statistics(s,p,_seg,_ner,deps)
		if len(list)==0:
			print 'len list ==0'
			return []
		return list

	def test_verify_indri(self,_lines,lines_info):
		#just count
		#using classifier
		tags=[]
		newwords=[]
		for line in _lines:
		     try:
			line = line.split('\t')
			if len(line)<4:
				#print 'read wrong ('+str(len(line))+'):'+'\t'.join(line)
				continue
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
		     except:
			info=sys.exc_info()
		#print 'Process Data start'
		(s,p,words,_seg,_ner) = self._process_data_indri_test(lines_info,newwords,tags=tags)
		if len(words)<2:
			return (0,0)
		#print 'Classifier start'
		return self.classifier_get_score(s,p,words,_seg,self.clf)
		

	def test_indri(self,_lines):
		lines=[]
		tags=[]
		newwords=[]
		ss = ''
		pstr = ''
		current=-1
		for line in _lines:
		     try:
			line = line.split('\t')
			if len(line)<4:
				#print 'read wrong ('+str(len(line))+'):'+'\t'.join(line)
				continue
			ss = line[0]
			pstr = line[1]
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			if line[3].strip()!='':
				lines.append(line[3].strip())
		     except :
			     info=sys.exc_info() 
			     print info[0],":",info[1]
		      	     print 'read wrong (except):'+'\t'.join(line)
		print 'Process Data start'
		(s,p,words,_seg,_ner) = self._process_data(lines,newwords,tags=tags)
		if len(words)<2:
			print ' words <2 too small'
			return []
		print 'Classifier start'
		(s,p,_seg,_ner) = self.classifier_using_process(s,p,words,_seg,_ner,self.clf)
		if len(p)<2:
			print 'classifier <2 too small'
			return []
		list=self.statistics(s,p,_seg,_ner)
		if len(list)==0:
			print 'len list ==0'
			return []
		return list

	def test_train(self):
		lines =[]
		tags =[]
		newwords=[]
		newwords2=[u"\u5988\u5988",u"\u6bcd\u4eb2"]
		for line in sys.stdin:
		     try:
			line = line.split('\t')
			if len(line)<4:
				print 'read wrong('+str(len(line))+'):'+'\t'.join(line)
				continue
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			#newwords2.append((line[2],(self.relation[line[1].decode('utf-8')])[0]))
			if line[3].strip()!='':
				lines.append(line[3].strip())
		     except Exception,e:
				traceback.print_exc()
			 	print 'read wrong (except):'+'\t'.join(line)
		(s,p,word,_seg,_ner) = self._process_data(lines,newwords,tags=tags)
		import cPickle as pickle
		f = open('classifier/train_hash.txt', 'wb')
		pickle.dump(word,f)
		f.close()
		f = open('classifier/train_tag.txt', 'wb')
		pickle.dump(p,f)
		f.close()
		#quit(0)
		del s
		del _seg
		del _ner
		clf = self.train_using_process(p,word)
		from sklearn.externals import joblib
		joblib.dump(clf,'classifier/train_data/fanhua_logic_position.train')

	def test_test(self):
		file = open('high_pv_person','rb')
		ren =[]
		while True:
			line = file.readline()
			if line:
				ren.append(line.strip('\r\n').strip('\n').split('\t')[0])
			else:
				break
		file.close()
		lines=[]
		tags=[]
		newwords=[]
		ss = ''
		pstr = ''
		anstr = ''
		check=False
		from sklearn.externals import joblib
		clf = joblib.load('classifier/train_data/fanhua_logic.train')
		wf = open('result_fanhua_logic','wb')
		current=0
		all=0
		for line in sys.stdin:
		     try:
			line = line.split('\t')
			if len(line)<5:
				print 'read wrong ('+str(len(line))+'):'+'\t'.join(line)
				continue
			if line[0] not in ren:
				print 'not in high pv : '+'\t'.join(line)
				continue
			#if line[1] != 'qizi':
				#continue
			if ss != line[0] and check:
				(s,p,words,_seg,_ner) = self._process_data(lines,newwords,None,tags=tags)
				if len(words)<2:
					#print 'too small'
					ss = line[0]
					continue
				(s,p,_seg,_ner) = self.classifier_using_process(s,p,words,_seg,_ner,clf)
				list=self.statistics(s,p,_seg,_ner)
				wf.write(ss+'\t'+pstr+'\t'+anstr+'\n')
				all+=1
				for l in list:
					print 'result'+l
					wf.write(l+"\n\n")
					if l.split('\t')[2]==anstr:
						current+=1
				print current
				lines=[]
				tags=[]
				newwords=[]
			ss = line[0]
			pstr = line[1]
			anstr = line[2]
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			#newwords2.append((line[2],(self.relation[line[1].decode('utf-8')])[0]))
			if line[4].strip()!='':
				check=True
				lines.append(line[4].strip())
			else:
				print 'read wrong ('+line[4]+'):'+'\t'.join(line)
		     except :
			     info=sys.exc_info() 
			     print info[0],":",info[1]
		      	     print 'read wrong (except):'+'\t'.join(line)
		#(s,p,_seg,_ner) = self.classifier(lines,tags,newwords,clf)
		#(s,p,words,_seg,_ner) = self._process_data(lines,newwords,None,tags=tags)
		#(s,p,_seg,_ner) = self.classifier_using_process(s,p,words,_seg,_ner)
		#list = self.statistics(s,p,_seg,_ner)
		#print '\nstart\n'
		#for l in list:
		#	print l.encode('utf-8')
		wf.write('all'+str(all))
		wf.write('current'+str(current))
		wf.close()

	def test(self):
		lines=[]
		for line in sys.stdin:
			lines.append(line.strip('\n'))
		clf = self.test_indri(lines)

	def test4(self):
		(s,p,answer,word) = self._process_data_file("qizi_for_train")
		list = self.statistics(s,p,answer)
		for l in list:
			print l.encode('utf-8')
		clf = self.train_using_process(s,p,answer,word)
		joblib.dump(clf, 'qizi.train')
		
if __name__ == '__main__':
	c = Classifier(test=False,genre='n_tuple')
	c.test_train()
	#c.test()
