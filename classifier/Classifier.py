#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
from sklearn import metrics
from sklearn.feature_extraction import DictVectorizer, FeatureHasher
from sklearn.feature_extraction.text import HashingVectorizer,TfidfVectorizer
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
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.decomposition import PCA,TruncatedSVD
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
		from InterClassifier import InterClassifier
		self.ic = InterClassifier(genre,self.newwords2)
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
		self.speci = ["、",",","，","&"]
		self.biaodian = [u"\u3001",",",u"\uff0c",".",u"\u3002","|",u"\uff1b","_",u"\uff1a",":",u"\u201d",u"\u201c"]
		#self.biaodian = ["、",",","，",".","。","|","；","_","：",":","”","“"]
		pass

	def _process_data_indri(self,lines_info,newwords,tags=None,htmls=None,union=False):
		return self.ic._process_data_indri(lines_info,newwords,tags,htmls,union)

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
		pipeline = Pipeline([
			('SentenceDep', SentenceDepExtractor()),
			('union', FeatureUnion(
				transformer_list=[
					('line', Pipeline([
						('selector', ItemSelector(key='line')),
						('dict',  DictVectorizer()),
					])),
					('dep', Pipeline([
						('selector', ItemSelector(key='dep')),
						('tfidf', FeatureHasher(n_features=2**8,input_type='dict')),
					])),
					('sentence', Pipeline([
						('selector', ItemSelector(key='sentence')),
						('tfidf', TfidfVectorizer()),
						('best', TruncatedSVD(n_components=50)),
					])),
				],
				# weight components in FeatureUnion
				transformer_weights={
					'line' : 0.3,
					'sentence': 0.2,
					'dep': 0.5,
				},
			)),
		])
		return pipeline.fit(words).transform(words)

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
		elif self.vec == 'union':
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
		elif self.vec == 'union':
			vec = self._vectorize_union(words)
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
		elif self.vec == 'union':
			vec = self._vectorize_union(words)
		vec = self.normalizer.transform(vec)
		pred = clf.predict(vec.toarray())
		score = accuracy_score(p, pred)
		#for i in xrange(len(p)):
		#	print s[i].encode('utf-8')+' '+str(i+1)+' '+pred[i]+' '+''.join(_seg[i]).encode('utf-8')
		return (score,len(pred))

	def _train(self,lines_info,newwords,tags):
		if self.vec == 'union':
			(s,p,word,_seg,_ner) = self._process_data_indri(lines_info,newwords,tags=tags,union=True)
		else:
			(s,p,word,_seg,_ner) = self._process_data_indri(lines_info,newwords,tags=tags)
		import cPickle as pickle
		if self.identify == 'muqin':
			f = open('classifier/train_tag_muqin_dep.txt', 'wb')             
			f2 = open('classifier/train_hash_muqin_dep.txt', 'wb')             
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
		return self.train_using_process(p,word)

	def _test(self,lines_info,newwords,tags,htmls,an):
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
		clf = self._train(lines_info,newwords,tags=tags)
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
		return self._test(lines_info,newwords,tags=tags,htmls=htmls,an=an)

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
		(s,p,words,_seg,_ner) = self._process_data_indri(lines_info,newwords,tags=tags)
		if len(words)<2:
			return (0,0)
		#print 'Classifier start'
		return self.classifier_get_score(s,p,words,_seg,self.clf)

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

if __name__ == '__main__':
	c = Classifier(test=False,genre='n_tuple')
	c.test_train()
	#c.test()
from sklearn.base import BaseEstimator, TransformerMixin

class SentenceDepExtractor(BaseEstimator, TransformerMixin):
	def fit(self, x, y=None):
		return self
	def transform(self, posts):
		features = numpy.recarray(shape=(len(posts),),dtype=[('sentence', object), ('line',object),('dep', object)])
		for i,dep in enumerate(posts):
			features['dep'][i] = dep[0]
			features['line'][i] = dep[1]
			features['sentence'][i] = dep[2]
		print 'SentenceDepExtractor'
		return features

class ItemSelector(BaseEstimator, TransformerMixin):
	def __init__(self, key):
		self.key = key

	def fit(self, x, y=None):
		return self

	def transform(self, data_dict):
		print self.key
		return data_dict[self.key]

