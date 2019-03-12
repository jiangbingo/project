#! /usr/bin/env python
# -*- coding: utf-8

"""
    View的state有3种：OPEN  CLOSED  ALL
    当viewState=OPEN时是把所有符合这个view的，并且是open状态的pr都列出显示在页面上
      viewState=CLOSED,pr状态是"Closed"或者"Correction Not Needed"
      viewState=ALL,就是两者都有
"""
import re
from prserver import *
from variables import *

class View(object):
    def __init__(self,prserver=None):
        #list.__init__(self)
        if prserver == None:
            self._prserver = ProntoServer()
        else:
            self._prserver = prserver
        self._prserver.ConnectSerevr()

        self._id = ''
        self._state = 'CLOSED'
        self._week_mapping = {
                                '1':'Jan',
                                '2':'Feb',
                                '3':'Mar',
                                '4':'Apr',
                                '5':'May',
                                '6':'Jun',
                                '7':'Jul',
                                '8':'Aug',
                                '9':'Sep',
                                '0':'Oct',
                                '11':'Nov',
                                '12':'Dec'
                             }

        self._start_date = '%s %s %s'%(VIEW_DATE[0].split('.')[2],self._week_mapping[VIEW_DATE[0].split('.')[1]],VIEW_DATE[0].split('.')[0])
        self._end_date = '%s %s %s'%(VIEW_DATE[1].split('.')[2],self._week_mapping[VIEW_DATE[1].split('.')[1]],VIEW_DATE[1].split('.')[0])

    def GetViewCase(self,view_id=None,state='CLOSED'):
        if view_id is not None:
            self._id = view_id
            self._state = state

        params = {
            'viewsOrStatisticsId': self._id,         # view的ID
            'viewState': self._state,                # view的state
        }

        self._url = 'fetchAPIReports.html?%s'%urllib.urlencode(params)
        resp = self._prserver.HttpGet(self._url)
        if resp.geturl() == self._prserver._server_url + '/' + self._url:
        #if resp.geturl() == self._prserver._server_url + '/' + self._url + "&HomeFlag=true":
            self._html = resp.read()
            logger.info('Succeed to get content of the view %s'%self._id)
    '''
    POST create a view,return the url ,eg:https://pronto.int.net.nokia.com/pronto/saveNewStatistics.html?statid=VIEW639414
    '''
    def GenerateView(self):
        postdata = {
                         "criteria": {
                                        "ViewOrStatistics":[
                                                                 {
                                                                      "doc":"ProblemReport",
                                                                      "field":"GroupName",
                                                                      "values":{"%s^^^^^"%VIEW_AG:"%s^^^^^"%VIEW_AG},
                                                                      "mCriteria":"Is Exactly",
                                                                      "lCriteria":"AND"
                                                                 },
                                                                 {
                                                                      "doc":"ProblemReport",
                                                                      "field":"PRDCreated",
                                                                      "values":{
                                                                                  "from":"%s"%self._start_date,
                                                                                  "to":"%s"%self._end_date,
                                                                                  "from_date":"%s"%self._start_date,
                                                                                  "to_date":"%s"%self._end_date,
                                                                                  "from_today":"",
                                                                                  "to_today":""
                                                                                },
                                                                      "mCriteria":"","lCriteria":""
                                                                 }
                                        ]
                         },
                         "displayColumnJSON": {
                                                 "DisplayColumns":[
                                                                      {
                                                                           "doc":"ProblemReport",
                                                                           "field":"PRID",
                                                                           "sortBy":1,
                                                                           "sequence":0
                                                                      },
                                                                      {
                                                                           "doc":"ProblemReport",
                                                                           "field":"Author",
                                                                           "sortBy":0,
                                                                           "sequence":1
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"GroupName",
                                                                            "sortBy":0,
                                                                            "sequence":2
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"PRDCreated",
                                                                            "sortBy":0,
                                                                            "sequence":3
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"PRState",
                                                                            "sortBy":0,
                                                                            "sequence":4
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"ClosedEnter",
                                                                            "sortBy":0,
                                                                            "sequence":5
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"ANNEnter",
                                                                            "sortBy":0,
                                                                            "sequence":6
                                                                      },
                                                                      {
                                                                            "doc":"Correction",
                                                                            "field":"CNNCategory",
                                                                            "sortBy":0,
                                                                            "sequence":7
                                                                      },
                                                                      {
                                                                            "doc":"Correction",
                                                                            "field":"MCImpGroup",
                                                                            "sortBy":0,
                                                                            "sequence":8
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"AttachedPRID",
                                                                            "sortBy":0,
                                                                            "sequence":9
                                                                      },
                                                                      {
                                                                            "doc":"ProblemReport",
                                                                            "field":"RevisionHistory",
                                                                            "sortBy":0,
                                                                            "sequence":10
                                                                      }
                                                 ]
                         },
                        "title": "%s"%VIEW_NAME,
                        "schedule": "Instant",
                        "days":'',
                        "deleteDays": 30,
                        "to": "%s"%PR_NOKIA_NAME,
                        "CC":'',
                        "source": 0,
                        "format": "Excel",
                        "separator": "Comma",
                        "gfType": 0,
                        "vsCriteriaList[0].documentName": "ProblemReport",
                        "vsCriteriaList[0].documentField": "GroupName",
                        "vsCriteriaList[0].matchingCriteria": "Is Exactly",
                        "vsCriteriaList[0].value": "%s"%VIEW_AG,
                        "vsCriteriaList[0].logicalCriteria": "AND",
                        "vsCriteriaList[1].documentName": "ProblemReport",
                        "vsCriteriaList[1].documentField": "PRDCreated",
                        "vsCriteriaList[1].fromLabel": "From",
                        "vsCriteriaList[1].dateFrom": "%s"%self._start_date,
                        "vsCriteriaList[1].dateTo": "%s"%self._end_date,
                        "vsCriteriaList[1].dynamicDateFrom":'',
                        "vsCriteriaList[1].dynamicDateTo":'',
                        "TargetFieldsTX": "ProblemReport:PRID",
                        "TargetFieldsTX": "ProblemReport:Author",
                        "TargetFieldsTX": "ProblemReport:GroupName",
                        "TargetFieldsTX": "ProblemReport:PRDCreated",
                        "TargetFieldsTX": "ProblemReport:PRState",
                        "TargetFieldsTX": "ProblemReport:ClosedEnter",
                        "TargetFieldsTX": "ProblemReport:ANNEnter",
                        "TargetFieldsTX": "Correction:CNNCategory",
                        "TargetFieldsTX": "Correction:MCImpGroup",
                        "TargetFieldsTX": "ProblemReport:AttachedPRID",
                        "TargetFieldsTX": "ProblemReport:RevisionHistory",
                        "Column": "ProblemReport:PRID"
            }
        para = urllib.urlencode(postdata).replace('%27','%22')   #  提交的表单数据一定要用%22(双引号)，不能用%27(单引号)
        request = urllib2.Request(VIEW_CREATE_POST_URL)
        response = urllib2.urlopen(request,para)
        ret = re.search('statid=(\w+)',response.geturl())
        if ret is not None:
            self._id = ret.group().split('=')[-1]
        return self._id

    def DeleteView(self,view_id=None):
        if view_id == None:
            paraid = self._id
        else:
            paraid = view_id

        data = {
                  "source":0,
                  "pageStarts":1,
                  "itemPg":1,
                  "viewState":"Open",
                  "viewType":"",
                  "sortByDoc":"",
                  "sortByCol":"",
                  "sortOrder":"",
                  "statistics":"%s"%paraid,
                  "pageStarts":1,
                  "itemPg":1,
                  "viewState":"Open",
                  "viewType":"",
                  "sortByDoc":"",
                  "sortByCol":"",
                  "sortOrder":""
               }

        request = urllib2.Request(VIEW_DELETE_POST_URL)
        para = urllib.urlencode(data)
        response = urllib2.urlopen(request,para)
        return True


if __name__ == "__main__":
    # pass
    v = View()
    view_id=v.GenerateView()
    v.DeleteView(view_id)






