#! /usr/bin/env python
# -*- coding: utf-8

"""
URL里的?，意思是用GET方式访问"?"前的网址，"?"后跟的是"key=value"格式的传递的值，用"&"隔开

prserver root url:     https://pronto.int.net.nokia.com/pronto
SSO 登录验证URL:       https://wam.inside.nsn.com/siteminderagent/forms/login.fcc
home page首页：        https://pronto.int.net.nokia.com/pronto/home.html  登陆成功后会自动返回跳转到这一页
pr lin                 https://pronto.int.net.nokia.com/pronto/problemReport.html?prid=PR332613
get closed prs through view:  https://pronto.int.net.nokia.com/pronto/fetchAPIReports.html?viewsOrStatisticsId=VIEW0000639136NGIT&viewState=CLOSED   # 这里只关注close的case
"""

import time
from authgroup_sc_mapping import GetAllSC


PR_USER = 'bijiang' #'erjiang'
PR_PASS = 'J1angbi^' #'Jh456789'
VIEW_DATE = ('2018.3.1','2018.3.31')
PR_NOKIA_NAME = 'Jiang, Bingo (NSB - CN/Hangzhou)'

#===============================================================================================================================
PR_SERVER = 'https://pronto.int.net.nokia.com/pronto'
PR_PROBE_TIMEOUT = 60
PR_GET_TIMEOUT = 301
PR_CHARSET = 'utf-8'
LINE_BREAK_TAG = "<BR>"
PR_SOCKET_LOCK_PORT = 31410

PR_STATISTIC='https://pronto.inside.nsn.com/pronto/viewStatistics.html?statid='  #VIEW643997
PR_LINK='https://pronto.inside.nsn.com/pronto/problemReportSearch.html?freeTextdropDownID=prId&searchTopText='  #PR327767

SC_MAPPING_URL = 'http://ltemetrics.nsn-net.net/OpenAPI/GroupMapping'
AG_SC_MAPPING = GetAllSC(SC_MAPPING_URL)

#====================================================================================================================================================================#
VIEW_AG = 'LTE_DEVHZ5_CHZ_FV'

VIEW_NAME = 'PR_METRIC_%s'%(time.strftime("%Y%m%d_%H-%M-%S",time.localtime(time.time())))     # 名字不能太长，不然无法删除
VIEW_CREATE_POST_URL = "https://pronto.int.net.nokia.com/pronto/saveStatistics.html"
VIEW_DELETE_POST_URL = "https://pronto.int.net.nokia.com/pronto/deleteAllStatistics.html"


if __name__ == "__main__":
   pass





