#coding:utf-8
import sys
import json
import os
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

def get_result(sourcePath, destPath):
    dest = open(destPath, "w")
    source = open(sourcePath, "r")
    for line in source:
        result = line.split()
        length= len(result)
        ret = ""
        for i in range(2,length):
            if result[i] is None:
                ret = None
                print result[0]
                continue
            else:
                if i%2 == 0 :#and i < length-2:
                    score = get_score(result[0], result[1], result[i])
                    ret +=  result[i] + " " + str(score).strip(" \t\s\n") + " " 
        ret = ret.strip(" \t\s\n")
	if len(result)>1:
        	dest.write("%s\t%s\t%s\n" %(result[0], result[1], ret)) 

def get_score(s, p, o):
    data = "S=" + s + "&P=" + p + "&O=" + o
    req = urllib2.Request("http://nj02-kgb-krr01.nj02.baidu.com:8123/predict.php", data)
    response = urllib2.urlopen(req)
    ret = response.read()
    return ret

if __name__ == "__main__":
    get_result(sys.argv[1], sys.argv[2])
