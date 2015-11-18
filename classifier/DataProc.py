#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
import json
import commands
from time import clock
class DataProc:
	def __init__(self):
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

	def _seg_line(self,line):
		line = line.decode('utf-8','ignore').encode('gbk','ignore')
		#try:
		#	line = line.decode('utf8').encode('gbk')
		#except:
		#	print line
		#	return ""
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
		line = self._seg_line(line)
		if line =="":
			return ("","","")
		strs = 'echo `curl -XPOST nmg01-kgb-odin2.nmg01:8007/1 -d \'{"method":"local_depparser", "params":[{"sentence":"'+line+'","sentence_segmented":true}]}\'`'
		#strs = 'echo `curl -XPOST nmg01-kgb-odin2.nmg01:8007/1 -d \'{"method":"local_depparser", "params":[{"sentence":"'+line+'","sentence_segmented":false}]}\'`'
		strs=commands.getoutput(strs).split('\n')
		try:
			strs = strs[3].strip('\r\n').strip('\n')
			js = json.loads(strs)
		except:
			print strs
			return ("","","")
		lists = js['result']['_ret']
		#seg = line.split(' ')
		seg = []
		lines = []
		pos = []
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
		return ('\t'.join(seg),'\t'.join(pos),'\t'.join(lines))
