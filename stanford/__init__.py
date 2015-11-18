#!/usr/bin/env python
import  WordPosAndDep         
import sys
import os
sys.path.append('./stanford')
class Stanford:
	def __init__(self,dep=False):
		self.dep = dep
		self.w = WordPosAndDep.WordPosAndDep(dep)

	#call this method to get the pos and ner,maybe include dep if self.dep is true
	#return:(ner,pos) or (ner,pos,dep)
	def get_ner_pos(self,seg):
		if self.dep:
			return self.w.PosAndDep_line(seg)
		else:
			return self.w.PosAndNer_line(seg)
	
	def get_in_line(self,seg):
		if self.dep:
			return self.w._PosAndDep_line(seg)
		else:
			return self.w._PosAndDep_line_without_parser(seg)
if __name__ == '__main__':
        m = Stanford(True)
	import sys
	for line in sys.stdin:
		print line
       		print m.get_in_line(line)
