#!/usr/bin/env python
#_*_coding:utf8_*_
# vim: set expandtab ts=4 sw=4 sts=4 tw=100:

import sys
import json
import urllib
import urllib2
import argparse
import types
class BaseError(Exception):
    """Base Error
       All other exception in this module would inherit it. 
    """
    def __init__(self):
        pass


class ServerError(BaseError):
    """Server Error
       This exception will be raise when adaptor call restful api failed or the response is fail. 
    """
    def __init__(self, msg, url):
        self.mesg = msg
        self.url = url

    def __str__(self):
        return "ServerError err-detail: %s, url: %s" % (self.mesg, self.url)


class JsonStrToDictConverter(object):
    """JsonStrToDictConverter
    """
    def convert(self, string):
        try:
            dict = json.loads(string)
        except ValueError , err:
            raise Exception("json string is invalid")
        return self.encode(dict)
    
    def __toUTF8(self,obj):
        tp = type(obj)
        if tp is types.UnicodeType:
            return obj.encode('utf-8')
        if tp is types.ListType:
            return [ self.__toUTF8(val) for val in obj]
        if tp is types.DictType:
            newDict = {}
            for key in obj.keys():
                newDict[key.encode('utf-8')] = self.__toUTF8(obj[key])
            return newDict
        return obj
    
    def encode(self,dict):
        return self.__toUTF8(dict)


class HttpRequester(object):
    """Http Requester
    """
    def __init__(self):
        pass

    def post_request(self, url, timeout, paramsDict):
        """post requester
        """
        try:
            reqParams = urllib.urlencode(paramsDict)
            req = urllib2.Request(url, reqParams)
            res = urllib2.urlopen(req)
        except Exception , error:
            raise ServerError(str(error), url)
        return res.readlines()

    def get_request(self, url, timeout):
        """get requester
        """
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
        except Exception , error:
            raise ServerError(str(error), url)
        return res.readlines()

    def delete_request(self, url, timeout, paramsDict):
        """delete request
        """
        try:
            reqParams = urllib.urlencode(paramsDict)
            req = urllib2.Request(url, reqParams)
            req.get_method = lambda: "DELETE"
            res = urllib2.urlopen(req)
        except Exception , error:
            raise ServerError(str(error), url)
        return res.readlines()

    def request(self):
        """request
        """
        pass


class RawBaseUtil(object):
    def __init__(self, server, port):
        self.api = "http://%s:%s" % (server, str(port))
        self.requester = HttpRequester()
        self.jsonstr_converter = JsonStrToDictConverter()

    def create(self, rawbase_meta):
        """create a rawbase
        """
        params = {"param": rawbase_meta}
        url = "%s/rawbase" % (self.api)
        return self.__post_request(url, 5, params)        
    '''
    def delete_rawbase(self, rawbase_name):
        """delete rawbase specified by rawbase_name
           Attention: this delete is hard delete, could not recovery.
        """
        url = "%s/rawbase/absoluteDelete/%s" % (self.api, rawbase_name)
        params = {"params":'{"user":"", "host":"", "cred":""}'}
        return self.__delete_request(url, 5, params)
    '''

    def delete_rawbase(self, rawbase_name):
        """delete rawbase specified by rawbase_name
           Attention: this delete is hard delete, could not recovery.
        """
        url = "%s/rawbase/%s" % (self.api, rawbase_name)
        params = {"param":'{"user":"", "host":"", "cred":""}'}
        return self.__delete_request(url, 5, params)

    def rawbase_meta(self, rawbase_name):
        """get rawbase meta information based on rawbase name
        """
        url = "%s/rawbase/%s" % (self.api, rawbase_name)
        return self.__get_request(url, 5)

    def entity(self, rawbase_name, entity_id):
        """search the entity data via entity id when rawbase name is specified.
        """
        url = "%s/record/%s?id=%s" % (self.api, rawbase_name, entity_id)
        return self.__get_request(url, 5)

    def intervene(self, rawbase_name, entity_id, data):
        """intervene
        """
        url = "%s/rawbase/%s/intervene" % (self.api, rawbase_name)
        params = {"id": entity_id}
        params["param"] = '{"user":"","cred":"","host":""}'
        params["data"] = data
        return self.__post_request(url, 5, params)

    def sample(self, rawbase_name, count=10):
        """sample
           Args:
               rawbase_name: rawbase name.
               count: how many items to sample, must be an integer, default is 10.
           Returns: a list of entity data.
        """
        url = "%s/rawbase/%s/sample?count=%d" % (self.api, rawbase_name, count)
        return self.__get_request(url, 5)
         
    def __get_request(self, url, timeout):
        res = self.requester.get_request(url, 5)
        #sys.stderr.write("%s\n" % (res[0]))
        response = self.jsonstr_converter.convert(res[0])
        if response["code"] != "1" and response["code"] != 1:
            raise ServerError(url, response["msg"])
        return response["data"]

    def __post_request(self, url, timeout, params):
        res = self.requester.post_request(url, timeout, params)
        #sys.stderr.write("%s\n" % (res[0]))
        response = self.jsonstr_converter.convert(res[0])
        if response["code"] != "1" and response["code"] != 1:
            raise ServerError(url, response["msg"])
        return response["data"]

    def __delete_request(self, url, timeout, params):
        res = self.requester.delete_request(url, timeout, params)
        response = self.jsonstr_converter.convert(res[0])
        if response["code"] != "1" and response["code"] != 1:
            raise ServerError(url, response["msg"])
        return response["data"]
        

def main():
    parent_parser = argparse.ArgumentParser()
    subparsers = parent_parser.add_subparsers(help="sub-command help", dest="subparser_name")
    create_subparser = subparsers.add_parser("create") 
    create_subparser.add_argument("-i", "--input", dest="rb_meta", required=True)
    delete_subparser = subparsers.add_parser("delete")
    delete_subparser.add_argument("-n", "--rawbase-name", dest="rb_name", required=True) 
    rawbase_subparser = subparsers.add_parser("rawbase")
    rawbase_subparser.add_argument("-n", "--rawbase-name", dest="rb_name", required=True) 
    entity_subparser = subparsers.add_parser("entity")
    entity_subparser.add_argument("-n", "--rawbase-name", dest="rb_name", required=True) 
    entity_subparser.add_argument("-i", "--id", dest="entity_id", required=True) 
    entity_subparser = subparsers.add_parser("sample")
    entity_subparser.add_argument("-n", "--rawbase-name", dest="rb_name", required=True) 
    entity_subparser.add_argument("-c", "--count", dest="count", required=False, default=10) 
    args = parent_parser.parse_args()
    #util = RawBaseUtil("nj02-kb-slave3.nj02.baidu.com", 8094)
    #util = RawBaseUtil("kgservice-sandbox.baidu.com", 80)
    #util = RawBaseUtil("nj02-kg-mario3-dy.nj02.baidu.com", 8094)
    util = RawBaseUtil("imario.baidu.com", 80)
    #util = RawBaseUtil("nj02-kb-slave3.nj02.baidu.com", 8094)
    if args.subparser_name == "create":
        #with open(args.rb_meta, "r") as fd:
        fd = open(args.rb_meta, "r")
        try:
            rawbase_meta_info = fd.read()
        except:
            pass
        print json.dumps(util.create(rawbase_meta_info), ensure_ascii=False)
    elif args.subparser_name == "delete":
        print json.dumps(util.delete_rawbase(args.rb_name), ensure_ascii=False)
    elif args.subparser_name == "entity":
        entity_str = util.entity(args.rb_name, args.entity_id)
        if entity_str == "":
            print "the entity not exists"
        else:
            print entity_str
    elif args.subparser_name == "rawbase":
        print json.dumps(util.rawbase_meta(args.rb_name), ensure_ascii=False)
    elif args.subparser_name == "sample":
        items = util.sample(args.rb_name, int(args.count))
        for item in items:
            print item
    else:
        sys.stderr.write("please input correct command\n")


if __name__ == "__main__":
    main()
