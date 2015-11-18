#!/usr/bin/env python

#include two class,'Seg' is to seg,'AllInfo' is to get all info(ner,pos,seg) using jieba
#'AllInfo' is discarded ,'cause jieba cann't do well in ner.I keep the class is for in case,for example,we get a new way to get the info of ner

class Seg:
        def __init__(self):
		import WordNer
                self.w = WordNer.WordNer()
	#it would be more precise if we add keywords into the dict
	def add_words(self,newwords):
		self.w.add_new_words(newwords)
	#the method is to seg a line
        def seg(self,line):
                return self.w.seg_single(line)

class AllInfo:
	def  __init__(self):
		import nerAndPos
		self.n = nerAndPos.NerAndPos()

	def add_words(self,newwords):
		self.n.add_new_words(newwords)

	#the method is to get all info using jieba,and it will return a line
	#return word pos ner\tword pos ner
	def getInfo_line(self,line):
		return self.n.ner_single(line)
	
	#the method is to get all info using jieba,and it will return three dict
	#return (word,pos,ner)
	def getInfo(self,line):
		return self.n.nerAndPos(line)

if __name__ == '__main__':
    #s = Seg()
    #import sys
    #for line in sys.stdin:
    #	line = s.seg(line)
    #	print line
    s = AllInfo()
    import sys
    for line in sys.stdin:
    #file = open('ner','r')
    #while True:
      #line = file.readline()
      #if line:
    	(seg,pos,ner) =  s.getInfo(line)
    	print seg.encode('utf-8')
    	#print ' '.join(pos)
    	#print ' '.join(ner)
