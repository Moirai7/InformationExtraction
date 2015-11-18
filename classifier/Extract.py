#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
import collections
from merge import Merge
from dep import TextSim
class Extract:
	def __init__(self,jieba=False):
		import re
		self.de = re.compile(u"[\u4e00-\u9fa5]")
		self.jieba = jieba
		self.relation = {u'fuqin':('PERSON','PERSON'),u'erzi':('PERSON','PERSON'),u'nver':('PERSON','PERSON'),u'nvyou':('PERSON','PERSON'),u'nanyou':('PERSON','PERSON'),u'muqin':('PERSON','PERSON'),u'emma':('PERSON','PERSON'),u'zhangfu':('PERSON','PERSON'),u'qizi':('PERSON','PERSON'),u'\u5973\u53cb':('PERSON','PERSON'),u'\u5973\u513f':('PERSON','PERSON'),u'\u59bb\u5b50':('PERSON','PERSON'),u'\u4e08\u592b':('PERSON','PERSON'),u'\u524d\u592b':('PERSON','PERSON'),u'\u7236\u4eb2':('PERSON','PERSON'),u'\u8eab\u9ad8':('PERSON','HEIGHT'),u'\u751f\u65e5':('PERSON','DATE'),u'\u64ad\u51fa\u65f6\u95f4':('FILM','TIME'),u'\u4e3b\u9898\u66f2':('FILM','MUSIC')}
		self.pos_tagger = {'a':0,'ad':1,'ag':2,'an':3,'b':4,'bg':5,'c':6,'d':7,'df':8,'dg':9,'e':10,'en':11,'f':12,'g':13,'h':14,'i':15,'in':16,'j':17,'jn':18,'k':19,'l':20,'ln':21,'m':22,'mg':23,'mq':24,'n':25,'ng':26,'nr':27,'nrfg':28,'nrt':29,'ns':30,'nt':31,'nz':32,'o':33,'p':34,'q':35,'qe':36,'qg':37,'r':38,'rg':39,'rr':40,'rz':41,'s':42,'t':43,'tg':44,'u':45,'ud':46,'ug':47,'uj':48,'ul':49,'uv':50,'uz':51,'v':52,'vd':53,'vg':54,'vi':55,'vn':56,'vq':57,'w':58,'x':59,'y':60,'yg':61,'z':62,'zg':63,'a':64,'ad':65,'ag':66,'an':67,'b':68,'bg':69,'c':70,'d':71,'df':72,'dg':73,'e':74,'en':75,'f':76,'g':77,'h':78,'i':79,'in':80,'j':81,'jn':82,'k':83,'l':84,'ln':85,'m':86,'mg':87,'mq':88,'n':89,'ng':90,'nr':91,'nrfg':92,'nrt':93,'ns':94,'nt':95,'nz':96,'o':97,'p':98,'q':99,'qe':100,'qg':101,'r':102,'rg':103,'rr':104,'rz':105,'s':106,'t':107,'tg':108,'u':109,'ud':110,'ug':111,'uj':112,'ul':113,'uv':114,'uz':115,'v':116,'vd':117,'vg':118,'vi':119,'vn':120,'vq':121,'w':122,'x':123,'y':124,'yg':125,'z':126,'zg':127,'a':128,'ad':129,'ag':130,'an':131,'b':132,'bg':133,'c':134,'d':135,'df':136,'dg':137,'e':138,'en':139,'f':140,'g':141,'h':142,'i':143,'in':144,'j':145,'jn':146,'k':147,'l':148,'ln':149,'m':150,'mg':151,'mq':152,'n':153,'ng':154,'nr':155,'nrfg':156,'nrt':157,'ns':158,'nt':159,'nz':160,'o':161,'p':162,'q':163,'qe':164,'qg':165,'r':166,'rg':167,'rr':168,'rz':169,'s':170,'t':171,'tg':172,'u':173,'ud':174,'ug':175,'uj':176,'ul':177,'uv':178,'uz':179,'v':180,'vd':181,'vg':182,'vi':183,'vn':184,'vq':185,'w':186,'x':187,'y':188,'yg':189,'z':190,'zg':191,'a':192,'ad':193,'ag':194,'an':195,'b':196,'bg':197,'c':198,'d':199,'df':200,'dg':201,'e':202,'en':203,'f':204,'g':205,'h':206,'i':207,'in':208,'j':209,'jn':210,'k':211,'l':212,'ln':213,'m':214,'mg':215,'mq':216,'n':217,'ng':218,'nr':219,'nrfg':220,'nrt':221,'ns':222,'nt':223,'nz':224,'o':225,'p':226,'q':227,'qe':228,'qg':229,'r':230,'rg':231,'rr':232,'rz':233,'s':234,'t':235,'tg':236,'u':237,'ud':238,'ug':239,'uj':240,'ul':241,'uv':242,'uz':243,'v':244,'vd':245,'vg':246,'vi':247,'vn':248,'vq':249,'w':250,'x':251,'y':252,'yg':253,'z':254,'zg':255,'eng':256}
		self.m = Merge(True,False)
		#self.m = Merge(True,True)
		pass

	#get the ner using merge and search the relation's Ner
	def _process_data(self,lines,newwords,n2,tags=None):
		s = []
		p = []
		_seg = []
		_ner = []
		self.m.add_new_words(newwords)
		if n2 is not None:
			self.m.add_new_words(n2)
		for i in xrange(len(lines)):
			line = lines[i]
			(line_seg,line_pos,line_ner)=self.m.ner_using_nlpc(line)
			#(line_ner,line_pos,line_seg,line_dep) = self.m.get_line_info(line,False)
			if tags is not None:
				tag = tags[i]
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
			s.append(newwords[i][0].decode('utf-8'))
			p.append(tag)
			_seg.append(seg)
			_ner.append(ner)
		return (s,p,_seg,_ner)

	def statistics(self,newwords,tags,segs,ners):
		s=[]
		p=[]
		answer=[]
		fromline=[]
		for i in xrange(len(tags)):
			tag = tags[i]
			seg = segs[i]
			ner = ners[i]
			_a = []
			print ' '.join(seg).encode('utf-8')
			for id in xrange(len(seg)):
				if tags is not None:
					if ner[id] == (self.relation[tag.decode('utf-8')])[1]:
						ll = len(self.de.findall(seg[id]))
						if ll==0:
							ll=len(seg[id])
						if (seg[id] != newwords[i]) and (seg[id] not in _a)  and (ll>1) and seg[id].isdigit()==False:
							print newwords[i].encode('utf-8')+','+tag.encode('utf-8')+','+seg[id].encode('utf-8')
							_a.append(seg[id])
							answer.append(seg[id])
							s.append(newwords[i])
							fromline.append(''.join(seg))
							p.append(tag)
		dict = collections.OrderedDict()
		for i in xrange(len(s)):
			s[i]=s[i].decode('utf-8')
			spo = s[i]+p[i]+answer[i]
			if spo in dict:
				dict[spo][2]+=1
			else:
				dict[spo]=[]
				dict[spo].append(s[i]+'\t'+p[i])
				dict[spo].append(answer[i])
				dict[spo].append(1)
				dict[spo].append(fromline[i])
		#result = {'sp':[[answer,count,line]]}
		result = collections.OrderedDict()
		for (k,v) in dict.items():
			sp = v[0]
			if sp in result:
				if v[2]>result[sp][0][1]:
					result[sp]=[]
					ddd = []
					ddd.append(v[1])
					ddd.append(v[2])
					ddd.append(v[3])
					result[sp].append(ddd)
				elif v[2]==result[sp][0][1]:
					ddd = []
					ddd.append(v[1])
					ddd.append(v[2])
					ddd.append(v[3])
					result[sp].append(ddd)
			else:
				result[sp]=[]
				ddd = []
				ddd.append(v[1])
				ddd.append(v[2])
				ddd.append(v[3])
				result[sp].append(ddd)
		list=[]
		for (k,v) in result.items():
			for i in xrange(len(v)):
				value = v[i]
				if value[1]==1:
					list.append(k+'\t'+value[0]+'\t'+'not sure'+'\t'+value[2])
				else:
					list.append(k+'\t'+value[0]+'\t'+str(value[1])+'\t'+value[2])
		return list

	def test3(self):
		lines =[]
		tags =[]
		newwords=[]
		newwords2=[]
		for line in sys.stdin:
		     try:
			line = line.split('\t')
			if len(line)<5:
				print 'read wrong:'+'\t'.join(line)
				continue
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			newwords2.append((line[2],(self.relation[line[1].decode('utf-8')])[0]))
			if line[4].strip()!='':
				lines.append(line[4].strip())
			else:
				print 'read wrong:'+'\t'.join(line)
		     except:
			     print 'read wrong:'+'\t'.join(line)
		(s,p,_seg,_ner) = self._process_data(lines,newwords,None,tags=tags)
		list = self.statistics(s,p,_seg,_ner)
		for l in list:
			print l.encode('utf-8')

	def test2(self):
		lines =[]
		tags =[]
		newwords=[]
		newwords2=[]
		for line in sys.stdin:
		     try:
			line = line.split('\t')
			if len(line)<6:
				print 'read wrong:'+'\t'.join(line)
				continue
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			newwords2.append((line[2],(self.relation[line[1].decode('utf-8')])[0]))
			if line[5].strip()!='':
				lines.append(line[5].strip())
			else:
				print 'read wrong:'+'\t'.join(line)
		     except:
			     print 'read wrong:'+'\t'.join(line)
		(s,p,_seg,_ner) = self._process_data(lines,newwords,newwords2,tags=tags)
		list = self.statistics(s,p,_seg,_ner)
		for l in list:
			print l.encode('utf-8')

	def test1(self):
		lines =[]
		tags =[]
		newwords=[]
		newwords2=[]
		ss = ''
		pstr = ''
		anstr = ''
		check=False
		wf = open('result_fanhua_1','ab')
		current=0
		all=0
		for line in sys.stdin:
			line = line.split('\t')
			if len(line)<5:
				print 'read wrong:'+'\t'.join(line)
				continue
			if ss != line[0] and check:
				(s,p,_seg,_ner) = self._process_data(lines,newwords,newwords2,tags=tags)
				list = self.statistics(s,p,_seg,_ner)
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
				newwords2=[]
			ss = line[0]
			pstr = line[1]
			anstr = line[2]
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			newwords2.append((line[2],(self.relation[line[1].decode('utf-8')])[0]))
			if line[4].strip()!='':
				check=True
				lines.append(line[4].strip())
			else:
				print 'read wrong:'+'\t'.join(line)
		wf.write('all'+str(all))
		wf.write('current'+str(current))
		wf.close()

	def test(self):
		lines =[]
		tags =[]
		newwords=[]
		for line in sys.stdin:
		     try:
			line = line.split(' \t')
			tags.append(line[0].split('\t')[1])
			newwords.append((line[0].split('\t')[0],(self.relation[line[0].split('\t')[1].decode('utf-8')])[0]))
			lines.append(line[1].strip())
		     except:
			     print line
			     quit()
		(s,p,answer) = self._process_data(lines,newwords,None,tags=tags)
		list = self.statistics(s,p,answer)
		for l in list:
			print l.encode('utf-8')
			
if __name__ == '__main__':
	c = Extract()
	c.test1()
