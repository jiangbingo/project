#! /usr/bin/env python
# -*- coding: utf-8
import re
from variables import AG_SC_MAPPING

class Pronto(object):
    def __init__(self,paradict):
        # htmlparser解析出的dict的每一个value都是list格式
        self._pr_id = paradict['Problem ID'][0]
        self._reporter_author = paradict['Author'][0]
        self._reporter_ag = paradict['Author Group'][0]
        self._report_date = paradict['Reported Date'][0]

        self._pr_state = paradict['State'][0]
        self._close_date = paradict['State Changed to Closed'][0] if len(paradict['State Changed to Closed']) != 0 else None
        self._cnn_date = paradict['State Changed to Correction not needed'][0] if len(paradict['State Changed to Correction not needed']) !=0 else None
        self._cnn_reason = paradict['Reason Why Correction is Not Needed'][0] if len(paradict['Reason Why Correction is Not Needed']) !=0 else None

        self._implementation_group = paradict['Implementation Group'] # 可能是空list

        self._attached_prs = paradict['Attached PRs']  # 可能是空list
        self._revision_history = paradict['Revision History']    # list  每一行就是一个新日期开头的


        self._reporter_sc = ''
        self._trace_ag = []
        self._trace_sc = []
        self._hops = 0

    def AlgorithmHops(self):
        hops = []
        for i in self._revision_history[::-1]:
            ret = re.findall('The group in charge changed from ([\w]+ [tT]o [\w]+)',i)
            if ret != []:
                hops.append([ret[0].split(' ')[0],ret[0].split(' ')[-1]])
        self._trace_ag = []
        for i in range(len(hops)):
            if i == 0:
                ret = [self._trace_ag.append(x) for x in hops[i]]
            else:
                self._trace_ag.append(hops[i][-1])

        for i in self._trace_ag:
            self._trace_sc.append(AG_SC_MAPPING[i])    # 元素是一个tuple:('C-PLANE PKR', 'C-Plane')

        hopnumber = 0
        if len(self._trace_sc) != 0:
            if self._trace_sc[0] == self._trace_sc[-1]:   # An--->Bn---->Cn--->...--->An
                hopnumber = 0
            else:
                I = iter(self._trace_sc)    #list转为迭代器
                lastbefore = ''
                last = I.next()
                for i in range(1,len(self._trace_sc)):
                    sc = I.next()
                    if sc == last :
                        hopnumber = hopnumber + 0
                    elif sc == self._reporter_sc:
                        hopnumber = hopnumber + 0
                    elif last == self._reporter_sc and sc == lastbefore:
                        hopnumber = hopnumber + 0
                    else:
                        hopnumber = hopnumber + 1
                    lastbefore = last
                    last = sc
        else:
             if len(self._implementation_group) != 0:
                hopnumber = 0
             else:
                hopnumber = 0

        self._hops= hopnumber

if __name__ == "__main__":
    pass