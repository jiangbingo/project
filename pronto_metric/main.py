#! /usr/bin/env python
# -*- coding: utf-8

import os,sys
# sys.path.insert(0,os.path.curdir)

lib = os.path.abspath(os.path.join(os.path.dirname(__file__),'lib'))
sys.path.append(lib)

from lib.view import View
from lib.html_parser import TableParser
from lib.pronto import Pronto
from lib.html_report import generate_html


def main(viewid):
    #view_obj = View(None,viewid)
    '''
    with open(r"D:\userdata\erjiang\Desktop\test.html",'w') as F:
        F.write(view_obj._html)
    F.close()
    '''
    with open(r"D:\userdata\erjiang\Desktop\test.html",'r') as F:
        txt = F.read()
    F.close()
    TP = TableParser()
    TP.feed(txt)
    TP.HandleAfterFeed()

    try:
        for i in TP._result:
            P = Pronto(i)
            P.AlgorithmHops()
            print '-'*50
    except:
        pass

if __name__ == "__main__":
    v = View()
    view_id=v.GenerateView()
    v.GetViewCase()

    t = TableParser()
    t.feed(v._html)
    t.HandleAfterFeed()
    rawdata = []

    for i in t._result:
        p = Pronto(i)
        p.AlgorithmHops()
        i['Transfer Hops'] = p._hops
        rawdata.append(i)
    generate_html(view_id,rawdata)
    v.DeleteView()


