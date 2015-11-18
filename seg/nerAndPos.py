# coding=utf-8
import jieba.posseg
import sys
import re
import os
import time
import logging
import marshal
import tempfile
import threading

#test : cat ner|python nerAndPos.py

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))
_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))

class NerAndPos:
    def __init__(self):
        dict_path = os.path.split(os.path.realpath(__file__))[0]+"/people.dict"
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.pd = re.compile(u'(\d{4}(\-|\/|\.|年)\d{1,2}(\-|\/|\.|月)\d{1,2}日?|\d{4}(\-|\/|\.|年)\d{1,2}月?|\d{1,2}(\-|\/|\.|月)\d{1,2}日?|\d{1,4}年|\d{1,2}月|\d{1,2}日|\d{1,4}年代|\d{4}(0[1-9]|10|11|12)(([0-2][0-9])|30|31)|\d{1,2}点\d{1,2}分|\d{1,2}点|\d{1,2}分|\d{1,2}:\d{1,2}|\d{1,3}岁|\d{1}\.\d{1,2}(M|m|米)|\d{2,3}(CM|Cm|cm|厘米|公分)|\d{1,2}(kg|KG|Kg|千克|公斤)|[a-zA-Z]+)')
        self.time = re.compile(u'\d{1,2}点\d{1,2}分|\d{1,2}:\d{1,2}|\d{1,2}点|\d{1,2}分')
        self.date = re.compile(u'(\d{4}(\-|\/|\.|年)\d{1,2}(\-|\/|\.|月)\d{1,2}日?|\d{4}(\-|\/|\.|年)\d{1,2}月?|\d{1,2}(\-|\/|\.|月)\d{1,2}日?|\d{1,4}年|\d{1,2}月|\d{1,2}日|\d{1,4}年代|\d{4}(0[1-9]|10|11|12)(([0-2][0-9])|30|31))')
        self.digit = re.compile(u'\d+')
        self.eng_word = re.compile(u'[a-zA-Z]+')
        self.age = re.compile(u'\d{1,3}岁')
        self.height = re.compile(u'\d{1}\.\d{1,2}(M|m|米)|\d{2,3}(CM|Cm|cm|厘米|公分)')
        self.weight = re.compile(u'\d{1,2}(kg|KG|Kg|千克|公斤)')
        self.ner_mark = re.compile(u'__@@@\w+@@@__')
	self.ner1 = re.compile(u'__@@@')
	self.ner2 = re.compile(u'@@@__')
        self.pseg = jieba.posseg
        f = open(dict_path)
        self.ner_dict = {}
	import Person
	self.person = Person.Person()
        for line in f:
            data = line.split('\t')
            self.ner_dict[unicode(data[0].strip(),'utf8')] = data[1].strip()
	    self.pseg.add_word(data[0].strip())
        f.close()

    #the method is to get all info of a line,input's code is utf-8
    def ner_single(self, line):
	line = ''.join(line.split())
        line = unicode(line.strip('\n'), 'utf8')
        ret = self.ner_line(line)
        ret_s = ""
        for i in ret:
            if i.strip() == "":
                continue
            if self.ner_mark.search(i) == None:
                try:
                    i = i + '__@@@%s@@@__'%(self.ner_dict[i.split()[0].strip()])
                except:
                    i = i + '__@@@other@@@__'
            i = i + '\t'
            ret_s = ret_s + i
	ret_s = self.ner1.sub(' ',ret_s)
	ret_s = self.ner2.sub('',ret_s)
        return ret_s+'\n'

    def ner_line(self, line):
        res = self.pd.search(line)
        ret = []
        if res != None:
            sli_sentence = line.split(res.group())
            split_word = res.group()
            if self.date.match(split_word) != None:
                split_word = split_word + ' nr__@@@DATE@@@__'
            elif self.time.match(split_word) != None:
                split_word = split_word + ' nr__@@@TIME@@@__'
            elif self.age.match(split_word) != None:
                split_word = split_word + ' nr__@@@AGE@@@__'
            elif self.height.match(split_word) != None:
                split_word = split_word + ' nr__@@@HEIGHT@@@__'
            elif self.weight.match(split_word) != None:
                split_word = split_word + ' nr__@@@WEIGHT@@@__'
            elif self.digit.match(split_word) != None:
                split_word = split_word + ' nr__@@@NUMBER@@@__'
            elif self.eng_word.match(split_word) != None:
                #split_word = split_word + ' nr__@@@english_word@@@__'
                split_word = split_word + ' nr'
            else:
                split_word = split_word + ' nr__@@@None@@@__'
            if len(sli_sentence) == 2:
                ret1 = list(self.ner_line(sli_sentence[0]))
                ret2 = list(self.ner_line(sli_sentence[1]))
                ret = ret + ret1
                ret.append(split_word)
                ret = ret + ret2
            else:
                info = self.pseg.cut(line)
                seg = []
                for word,flag in info:
                    seg.append('%s %s' % (word, flag.lstrip('\t')))
		ret = list(seg)
        else:
            info = self.pseg.cut(line)
            seg = []
	    for word,flag in info:
		    seg.append('%s %s' % (word, flag.lstrip('\t')))
            ret = list(seg)
        return ret

    #the method will return three dict of a line
    #like this (word,pos,ner)
    def nerAndPos(self,line):
        line = self.ner_single(line)
	#print line.encode('utf-8')
	words = line.strip('\t\n').split('\t')
	seg = []
	pos = []
	ner = []
	for word in words:
		#print word.encode('utf-8')
		i = word.split(' ') 
		#print i
		seg.append(i[0])
		pos.append(i[1])
		ner.append(i[2])
	(line,pos,ner)=self.person.merge_name(' '.join(seg),pos,ner)
	return (line,pos,ner)

    #add new words with a tag(ner)
    def add_new_words(self,newwords):
	    if newwords is not None:
		    for (n,tag) in newwords:
			    self.ner_dict[n] = tag
			    self.pseg.add_word(n)
				
if __name__ == '__main__':
    s = NerAndPos()
    for line in sys.stdin:
           ret = s.nerAndPos(line)
           #sys.stdout.write(ret.encode('utf-8'))
