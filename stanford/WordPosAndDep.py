#coding:utf-8
import sys
import datetime

class WordPosAndDep:
    def __init__(self,dep=False):
	import re
	self.pattern = re.compile(u'[\u201c|\u300c|\u300a|\u3010]')
        self.pattern2 = re.compile(u'[\u201d|\u300b|\u300d|\u3011]')
	self.pattern3 = re.compile(u'[\uff1a|\u25aa|\u25b2|\.]')
	self.pattern4 = re.compile(u'\.\.\.')
        from pywrapper import CoreNLP
	import os
	if dep:
        	self.proc = CoreNLP(configdict={'ner.model':'edu/stanford/nlp/models/ner/chinese.misc.distsim.crf.ser.gz','pos.model': 'edu/stanford/nlp/models/pos-tagger/chinese-distsim/chinese-distsim.tagger','parse.model': 'edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz','annotators':'tokenize,ssplit,pos,lemma,ner,parse'},corenlp_jars=[os.path.split(os.path.realpath(__file__))[0]+"/stanford/stanford-corenlp-full-2015-04-20/*",os.path.split(os.path.realpath(__file__))[0]+"/stanford/stanford-chinese-corenlp-2015-04-20-models.jar"])
	else:
		self.proc_without_parser = CoreNLP(configdict={'ner.model':'edu/stanford/nlp/models/ner/chinese.misc.distsim.crf.ser.gz','pos.model': 'edu/stanford/nlp/models/pos-tagger/chinese-distsim/chinese-distsim.tagger','parse.model': 'edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz','tokenize.options':'untokenizable=noneDelete','annotators':'tokenize,ssplit,pos,lemma,ner'},corenlp_jars=[os.path.split(os.path.realpath(__file__))[0]+"/stanford/stanford-corenlp-full-2015-04-20/*",os.path.split(os.path.realpath(__file__))[0]+"/stanford/stanford-chinese-corenlp-2015-04-20-models.jar"])

    #this method input form stdin
    #it can be changed to get the depparser by stanford
    def PosAndDep(self):
        #import datetime
        #start = datetime.datetime.now()
        for line in sys.stdin:
           self._PosAndDep_line_without_parser(line.strip('\n'))
           #self._PosAndDep_line(line.strip('\n'))
        #end = datetime.datetime.now()
        #print end-start

    #this method will parse a line to get ner and pos
    #must return tuple 
    def PosAndNer_line(self,line):
        line = self.pattern.sub('(',line)
	line = self.pattern2.sub(')',line)
	line = self.pattern4.sub(':',line)
	line = self.pattern3.sub(':',line)
	try:
        	info =  self.proc_without_parser.parse_doc(line)
        	sentences = info['sentences']
		ner = ''
		pos = ''
        	for sentence in sentences :
                	pos += ','.join(sentence['pos'])
                	ner += ','.join(sentence['ner'])
			pos += ','
			ner += ','
		return (ner.strip(','),pos.strip(','))
	except:
		print '!! wrong:'+line.encode('utf-8')
		return ('','')

    #this method will parse a line to get ner dep and pos
    #must return tuple 
    def PosAndDep_line(self,line):
        line = self.pattern.sub('(',line)
	line = self.pattern2.sub(')',line)
	line = self.pattern4.sub(':',line)
	line = self.pattern3.sub(':',line)
        info =  self.proc.parse_doc(line)
        sentences = info['sentences']
	ner = ''
	pos = ''
	dep = ''
        for sentence in sentences :
		deps = sentence['deps_basic']
		basic = []
		for d in deps:
			basic.append('_'.join(str(x) for x in d))
		dep += ','.join(basic)
                pos += ','.join(sentence['pos'])
                ner += ','.join(sentence['ner'])
		pos += ','
		ner += ','
	return (ner.strip(','),pos.strip(','),dep.strip(','))

    #this method is for parse a line and get the pos and it just return a line of those info
    #current result:word pos\t
    #if it's needed, i could add the ner parser annotated by stanford
    def _PosAndDep_line_without_parser(self,line):
        start = datetime.datetime.now()
        info =  self.proc_without_parser.parse_doc(line)
	sentences = info['sentences']
	m_line=''
        for sentence in sentences :
                tokens = sentence['tokens']
                pos = sentence['pos']
                str = [[] for i in range(len(tokens)+1)]
                str[0].append(u'root')
                str[0].append(u'ROOT')
                #str[0].append(u'root+%d'% (deps[0][2]+1))
                for i in range(1,len(tokens)+1):
                    str[i].append(tokens[i-1])
                    str[i].append(pos[i-1])
                liststr = []
                for i in range(0,len(tokens)+1):
                        liststr.append((' '.join(str[i])).encode('utf-8'))
                m_line += '\t'.join(liststr) +'\n'
	return m_line
        #end = datetime.datetime.now()
        #print (end-start).total_seconds()

    #this method is for parse a line and get the pos dep and it just return a line of those info
    #current result:word pos deps(use ',' to split all result of parsing)\t
    #if it's needed, i could add the ner parser annotated by stanford
    def _PosAndDep_line(self,line):
        info =  self.proc.parse_doc(line)
        sentences = info['sentences']
        for sentence in sentences :
                tokens = sentence['tokens']
                pos = sentence['pos']
                deps = sentence['deps_basic']
                str = [[] for i in range(len(tokens)+1)]
                str[0].append(u'root')
                str[0].append(u'ROOT')
                str[0].append(u'root+%d'% (deps[0][2]+1))
                for i in range(1,len(tokens)+1):
                    str[i].append(tokens[i-1])
                    str[i].append(pos[i-1])
                deps_ = [[] for i in range(len(tokens)+1)]
                for i in range(1,len(deps)):
                    deps_[deps[i][1]+1].append('%s+%d'%(deps[i][0],deps[i][2]+1))
                for i in range(1,len(tokens)+1):
                    if len(deps_[i]) == 0 :
                        str[i].append(' ')
                    else:
                        str[i].append(','.join(deps_[i]))
                liststr = []
                for i in range(0,len(tokens)+1):
                        liststr.append((' '.join(str[i])).encode('utf-8'))
                return '\t'.join(liststr) +'\n'  

    #this method will read lines in a file and parse it
    #This method has been discarded
    def _PosAndDep(self,fileName):
        self.file = open(fileName,'r')
        import datetime
        start = datetime.datetime.now()
        while True:
	   line = self.file.readline()
	   if line:
                _PosAndDep_line(line.strip('\r\n'))
	   else:
		break
        end = datetime.datetime.now()
        print (end-start).total_seconds()

if __name__ == '__main__':
    s = WordPosAndDep()
    s.PosAndDep()
