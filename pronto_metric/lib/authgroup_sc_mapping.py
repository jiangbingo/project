#! /usr/bin/env python
# -*- coding: utf-8

import os,sys
import urllib,urllib2,json

# get the mapping relationship between AuthGroup & System Component
def GetAllSC(paraurl):
    try:
        authGroup_SC_DICT = {}
        uploadData = {}
        uploadData['groupName'] = 'all'
        # urllib.urlencode()  To transfer the dict format "key:value" to format "key=value";return value's type is str,use ";" connect element in dict
        # Acctually,this step callled parameters encapsulation
        uploadDataUrlEncode = urllib.urlencode(uploadData)
        # The parameeter "data" is which parameters are submitted,and their submit method
        #req = urllib2.Request(url=SC_MAPPING_URL,data=uploadDataUrlEncode,proxies='10.144.1.10:8080')
        req = urllib2.Request(url=paraurl,data=uploadDataUrlEncode)
        # urllib2.urlopen() could accept a request object as parameter
        resData=urllib2.urlopen(req)
        res=resData.read()
        # json.loads() transfer data from "str" to "dict"
        ret = json.loads(res)
        for item in ret:
            authGroup = (item['Group']).encode('utf-8')
            SC = item['TestingSC']
            SystemComponent = item['SystemComponent']
            if SC :
                SC = (SC).encode('utf-8')
            if SystemComponent:
                SystemComponent = (SystemComponent).encode('utf-8')
            authGroup = authGroup.upper()
            authGroup_SC_DICT[authGroup] = (SystemComponent,SC)
    except Exception,err:
        print "Get All Auth SC Mapping failed, as %s" %err
    return authGroup_SC_DICT      # authGroup_SC_DICT's element format is "Authoegroup:(SystemComponent,SC)"

if __name__ == "__main__":
    pass


