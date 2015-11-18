#!/usr/bin/env python
from sys import *
path.append("./config")
#import os
#path.append(os.path.split(os.path.realpath(__file__))[0])
#path.append(os.path.split(os.path.realpath(__file__))[0]+"/config")
import json
import commands
class TextSim:
	def __init__(self):
		import Sim
		self.s = Sim.Sim()

	def sim(self,p1,p2):
		return self.s._sim(p1,p2)		

class Dep:
	def __init__(self):
		#f = open('people.dict')
		self.ner_dict = {}
		#for line in f:
		#	data = line.split('\t')
		#	self.ner_dict[unicode(data[0].strip(),'utf8')] = data[1].strip()
		#f.close()
		import sofa
		self.sofa = sofa
		import os
		cp = os.path.split(os.path.realpath(__file__))[0]+'/config/drpc_client.xml'
       		#seg
		self.sofa.use('drpc.ver_1_0_0', 'S')
		self.sofa.use('nlpc.ver_1_0_0', 'wordseg')
		conf = self.sofa.Config()
		conf.load(cp)
		self.wordseg_agent = S.ClientAgent(conf['sofa.service.nlpc_wordseg_3016'])

		#dep
		#self.sofa.use('drpc.ver_1_0_0', 'S')
		#self.sofa.use('nlpc.ver_1_0_0', 'nlpc')
		#conf = self.sofa.Config()
		#conf.load(cp)
		#conf.load('./config/drpc_client.xml')
		#self.query_agent = S.ClientAgent(conf['sofa.service.nlpc_depparser_uni_web_107']) #depparser_query
		#self.query_agent = S.ClientAgent(conf['sofa.service.nlpc_depparser_web_107']) #depparser_web
		pass
	
	#this method just return the result of parsing
	def _dep_line_without_ner(self,line):
                line = line.strip('\n')
                m_input = nlpc.parse_prep_input()
                m_input.sentence = str(line)
                m_input.grain_size = 1
                m_input.sentence_segmented = True
                input_data = self.sofa.serialize(m_input)
                for i in range(5) :
                        try:
                                ret, output_data = self.query_agent.call_method(input_data)
                                break
                        except Exception as e:
                                continue
                if len(output_data) == 0:
                        stdout.write('No result' + '\n')
                        return
                m_output = nlpc.depparser_output()
                m_output = self.sofa.deserialize(output_data, type(m_output))
                tokens = m_output.items
                list_size = len(tokens)
		m_line = ''
                for i in range(list_size):
                        if tokens[i].deprel.strip() == None:
                                tokens[i].deprel = 'None'
                        if tokens[i].word.strip() == None:
                                tokens[i].word = 'None'
                        m_line +=  str(i) + '@@' + tokens[i].word + ' '  + tokens[i].deprel+ '+' + str(tokens[i].head)  + '\t'
		return m_line.strip('\t')

	def _seg_line(self,line):
		line = line.decode('utf-8').encode('gbk')
		m_input = wordseg.wordseg_input()
		m_input.query = str(line)
		m_input.lang_id = int(0)
		m_input.lang_para = int(0)	
		input_data = self.sofa.serialize(m_input)
		for i in range(5) :
			try: 
				ret, output_data = self.wordseg_agent.call_method(input_data)
				break
			except Exception as e:
				output_data = []
				continue
		if len(output_data) == 0:
			print 'wrong'
			return ""
		m_output = wordseg.wordseg_output()
		m_output = self.sofa.deserialize(output_data, type(m_output))
		m_output = m_output.scw_out
		word = []
		for i in range(m_output.wpbtermcount):
			poslen = ((m_output.wpbtermpos[i]) >> 24)
			posidx = ((m_output.wpbtermpos[i]) & 0x00FFFFFF)
			word.append(m_output.wpcompbuf[posidx : posidx + poslen])
		return ' '.join(word).decode('gbk').encode('utf-8')

	def _dep_line_nmg(self,line):
		line = line.strip('\n')
		#print  self._seg_line(line)
		line = self._seg_line(line)
		print line
		strs = 'echo `curl -XPOST nmg01-kgb-odin2.nmg01:8007/1 -d \'{"method":"local_depparser", "params":[{"sentence":"'+line+'","sentence_segmented":true}]}\'`'
		#strs = 'echo `curl -XPOST nmg01-kgb-odin2.nmg01:8007/1 -d \'{"method":"local_depparser", "params":[{"sentence":"'+line+'","sentence_segmented":false}]}\'`'
		strs=commands.getoutput(strs).split('\n')
		js = json.loads(strs[3].strip('\r\n').strip('\n'))
		lists = js['result']['_ret']
		#seg = line.split(' ')
		seg = []
		lines = []
		pos = []
		m_line=''
		for i in xrange(len(lists)):
			l = lists[i]
			if l['word'].strip() == None:
				seg.append('_')
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
                        if l['deprel'].strip() == None:
                                tokens[i].deprel = 'None'
                        m_line +=  l['word']+' '+l['postag'] + ' '+l['ner']+' '  + l['deprel']+ '_' + str(l['head'])  + '/'
                        #m_line +=  l['word']+' ' + l['deprel']+ '_' + str(l['head'])  + '/'
		print m_line.encode('utf-8')
		return ('\t'.join(seg),'\t'.join(pos),'\t'.join(lines))

	#'cause nlpc parser will just return ner
	def _dep_line(self,line):
		#line = line.strip('\n').decode('utf-8').encode('gbk')
		in_sentences=[]
		in_sentences.append(str(line))
        	#m_input = nlpc.parse_prep_input()
		m_input = nlpc.depparser_uni_input()
        	m_input.sentences = in_sentences
       		m_input.grain_size = 1
        	m_input.sentence_segmented = False
        	input_data = self.sofa.serialize(m_input)
		for i in range(5) :
            		try:
                		ret, output_data = self.query_agent.call_method(input_data)
                		break
            		except Exception as e:
                		continue
        	if len(output_data) == 0:
            		stdout.write('No result' + '\n')
            		return
        	m_output = nlpc.depparser_uni_output()
        	m_output = self.sofa.deserialize(output_data, type(m_output))
        	dep_sentences = m_output.dep_sentences
        	list_size = len(dep_sentences)
		m_line = []
		#m_word = [] 
		#m_pos = [] 
        	for j in range(list_size):
		    tokens = dep_sentences[i].dep_terms
		    dep_terms = len(tokens)
		    for i in range(dep_terms):
            		if tokens[i].lemma.strip() == None:
                		tokens[i].lemma = '_'
            		if tokens[i].cpostag.strip() == None:
                		tokens[i].cpostag = '_'
            		if tokens[i].postag.strip() == None:
                		tokens[i].postag = '_'
            		if tokens[i].ner.strip() == None:
                		tokens[i].ner = '_'
			elif tokens[i].ner.strip() == 'PER':
				tokens[i].ner = 'PERSON'
            		if tokens[i].feat.strip() == None:
                		tokens[i].feat = '_'
            		if tokens[i].deprel.strip() == None:
                		tokens[i].deprel = '_'
			#m_pos.append(tokens[i].postag)
			#m_word.append(tokens[i].word)
			m_line.append(tokens[i].ner)
		return '\t'.join(m_line)

	#'cause nlpc parser will return all info
	def _dep_all(self,line):
		line = line.strip('\n')
        	m_input = nlpc.parse_prep_input()
        	m_input.sentence = str(line)
       		m_input.grain_size = 1
        	m_input.sentence_segmented = True
        	input_data = self.sofa.serialize(m_input)
		for i in range(5) :
            		try:
                		ret, output_data = self.query_agent.call_method(input_data)
                		break
            		except Exception as e:
				print 'wrong :' +line
                		continue
        	if len(output_data) == 0:
            		stdout.write('No result' + '\n')
            		return
        	m_output = nlpc.depparser_output()
        	m_output = self.sofa.deserialize(output_data, type(m_output))
        	tokens = m_output.items
        	list_size = len(tokens)
		m_ner = []
		m_word = []
		m_postag = []
        	for i in range(list_size):
            		if tokens[i].lemma.strip() == None:
                		tokens[i].lemma = '_'
            		if tokens[i].cpostag.strip() == None:
                		tokens[i].cpostag = '_'
            		if tokens[i].postag.strip() == None:
                		tokens[i].postag = '_'
            		if tokens[i].ner.strip() == None:
                		tokens[i].ner = '_'
			elif tokens[i].ner.strip() == 'PER':
				tokens[i].ner = 'PERSON'
            		if tokens[i].feat.strip() == None:
                		tokens[i].feat = '_'
            		if tokens[i].deprel.strip() == None:
                		tokens[i].deprel = '_'
			m_ner.append(tokens[i].ner)
			m_word.append(tokens[i].word)
			m_postag.append(tokens[i].postag)
		return ('\t'.join(m_word),'\t'.join(m_postag),'\t'.join(m_ner))
	
	#the method get lines form stdin
	def dep_from_stdin(self):
		import sys
		for line in sys.stdin:
			self._dep_line_nmg(line)
			#(seg,pos,ner) = self._dep_line_nmg(line)
			#print seg.encode('utf-8')
			#print pos
			#print ner
			#self._dep_line(line)

	#the method get line by input parameters
	def dep_from_line(self,line):
		line = self._dep_line_without_ner(line)
		return line

if __name__ == '__main__':
	d = Dep()
	d.dep_from_stdin()
