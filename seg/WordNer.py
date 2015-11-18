# coding=utf-8

import jieba
import sys
import re
import os
import time
import logging
import marshal
import tempfile
import threading

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))
_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))

#test : cat ner|python WordNer.py

class WordNer:
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
        self.jieba = jieba
        self.jieba.load_userdict(dict_path)

    def add_new_words(self,newwords):
	    if newwords is not None:
		    for (n,tag) in newwords:
			    self.jieba.add_word(n)

    #call this method to seg,input's code is utf-8
    def seg_single(self, line):
        line = unicode(line.strip('\n'), 'utf8')
	ret = self.seg_line(line)
        ret_s = ""
        for i in ret:
            if i.strip() == "":
                continue
            i = i + ' '
            ret_s = ret_s + i
	return ret_s.strip(' ')

    def seg(self,line):
           ret = self.seg_single(line)
           sys.stdout.write(ret.encode('utf-8')+'\n')

    def seg_line(self,line):
        res = self.pd.search(line)
        ret = []
        if res != None:
            sli_sentence = line.split(res.group())
            split_word = res.group()
            if self.date.match(split_word) != None:
                split_word = split_word
            elif self.time.match(split_word) != None:
                split_word = split_word
            elif self.age.match(split_word) != None:
                split_word = split_word
            elif self.height.match(split_word) != None:
                split_word = split_word
            elif self.weight.match(split_word) != None:
                split_word = split_word
            elif self.digit.match(split_word) != None:
                split_word = split_word
            elif self.eng_word.match(split_word) != None:
                split_word = split_word
            else:
                split_word = split_word
            if len(sli_sentence) == 2:
                ret1 = list(self.seg_line(sli_sentence[0]))
                ret2 = list(self.seg_line(sli_sentence[1]))
                ret = ret + ret1
                ret.append(split_word)
                ret = ret + ret2
            else:
                seged_sentence = self.jieba.cut(line)
                ret = list(seged_sentence)
        else:
            seged_sentence = self.jieba.cut(line)
            ret = list(seged_sentence)
        return ret
        
    def load_dict(self, dict_name):
        self.jieba.load_userdict(dict_name)

def main():
	for line in sys.stdin:
    		s = WordNer()
    		s.seg(line)
if __name__ == '__main__':
    main()
