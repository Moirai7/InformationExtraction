#!/usr/bin/env python
import sys
sys.path.append("./config")
import sofa
class Sim:
	def __init__(self):
		self.sofa = sofa
		self.sofa.use('drpc.ver_1_0_0', 'S')
		self.sofa.use('nlpc.ver_1_0_0', 'textsim')
		conf = self.sofa.Config()
		conf.load('./config/drpc_client.xml')
		self.textsim_agent = S.ClientAgent(conf['sofa.service.nlpc_textsim_103']) #depparser_query
		
	def _sim(self,q1,q2):
		m_input = textsim.textsim_input()
		m_input.query1 = q1
		m_input.query2 = q2
		input_data = sofa.serialize(m_input)
		for i in range(5) :
			try:
				ret, output_data = self.textsim_agent.call_method(input_data)
				break
			except Exception as e:
				#print e
				output_data=''
				continue
		if len(output_data) == 0:
			pass
		else:
			m_output = textsim.textsim_output()
			m_output = sofa.deserialize(output_data, type(m_output))
			return m_output.textsim

if __name__ == '__main__':
	sim = Sim()
	lines = []
	for line in sys.stdin:
		line = line.strip('\n')
		lines.append(line)
	strs = []
	strs.append(lines[0])
	for l in lines:
		check=True
                for s in strs:
                        point = sim._sim(s,l)
			print s
			print l
			print point 
			print '\n'
                        if point>1:
                                check=False
                if check:
                        strs.append(l)

