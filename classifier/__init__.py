#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
import Classifier

if __name__ == '__main__':
	c = Classifier.Classifier()
	c.test_train()
