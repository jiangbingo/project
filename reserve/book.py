#! -*- encoding=utf-8 -*-
#! /usr/bin/env python
"""
Purpose of the script:
    reservation or extension of a testline 
usage:
Example:
1. reserve a testline: python book.py
2. quick reserve or extend a testline by ID: python book.py [ID]
"""

import os,sys

current_dir = os.path.dirname(__file__)
pyLibFolder = os.path.abspath(os.path.join(current_dir,'3rdPyLib'))
cloudApiFolder = os.path.abspath(os.path.join(current_dir,"uteCloudApi"))
sys.path.append(pyLibFolder)
sys.path.append(cloudApiFolder)
from ute_cloud_manager_api.api import CloudManagerApi
from config import *
import datetime
from datetime import timedelta
from time import sleep
import requests,urllib3
import json

urllib3.disable_warnings()
sys.dont_write_bytecode= True

PROXY = "http://10.144.1.10:8080"
if 'http_proxy' not in os.environ:
    os.environ['http_proxy'] = PROXY
if 'https_proxy' not in os.environ:
    os.environ['https_proxy'] = PROXY

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)
fh = logging.FileHandler(filename="log.txt", mode="a")
log.addHandler(fh)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s ")
ch.setFormatter(formatter)
fh.setFormatter((formatter))


class Reservation(object):
    def __init__(self):
        self.name = person.keys()[0]
        self._bts_state = RESERVATION_INFO["bts_state"]
        self._testline_type = RESERVATION_INFO["cloud_type"]
        self._reservation_duration = 60
        self._reservation = CloudManagerApi(api_token=person[self.name])
        self._ute_build = RESERVATION_INFO['ute_build']
        self._share_with_list = []
        self._share_with_list.append(RESERVATION_INFO['share_with'])
        if not RESERVATION_INFO['share_with']:
            self._share_with = None
        else:
            self._share_with = isinstance(RESERVATION_INFO['share_with'],list) and RESERVATION_INFO['share_with'] or self._share_with_list
            log.info('share_with is：',self._share_with)
        if not RESERVATION_INFO["enb_build"]:
            log.warning("enb build is not set")
            raise RuntimeError("enb build is not set")
        self.reservation_id = None


    def get_reservation_list(self):
        reservation_list = []
        for status in ['Pending for testline','Testline assigned','Confirmed']:
            if self._reservation.list_my_reservations(status=status):
                reservation_list += self._reservation.list_my_reservations(status=status)
        return reservation_list

    def reservation_detail(self):
        reserve_detail = self._reservation.get_reservation_details(reservation_id=self.reservation_id)
        return reserve_detail

    def reservation_a_server(self):
        try:
            self._enb_build = getLatestENBBuild(RESERVATION_INFO["enb_build"])
            log.info("success to get latest enb build :{}".format(self._enb_build))
            self.reservation_id = self._reservation.create_reservation(testline_type=self._testline_type,enb_build=self._enb_build,duration=self._reservation_duration,state=self._bts_state,ute_build=self._ute_build,share_with=self._share_with)
            log.info("success to reserve testline,reservation id is:{},enb build is:{}".format(self.reservation_id,self._enb_build))
        except Exception as e:
            log.warning('reservation failed, cause: %s'%e)
            sys.exit()
            
    def available_time(self):
        start_date,end_date = self.reservation_detail()["start_date"],self.reservation_detail()["end_date"]
        end_date_new = datetime.datetime.strptime(end_date.encode('utf-8'),"%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=8)
        available_time = end_date_new - datetime.datetime.now()
        return available_time
            
    def get_timestamp(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def schedule(self,schedule_time=RESERVATION_INFO["default_schedule_time"]):
        if self.get_reservation_list():
            log.info('history reservation list is {}'.format(self.get_reservation_list()))
        if len(self.get_reservation_list()) <= 2:    # now allow max = 3 testlines
            if schedule_time.strip() and schedule_time.strip().lower()!= 'now':
                interval_time(schedule_time)
            self.reservation_a_server()
            self.auto_extend_reservation()
        else:
            log.warning("max reservation count exceed\nyou have reserved 3 testline aleady ,id list is {}".format(self.get_reservation_list()))
            sys.exit()

    def auto_extend_reservation(self):
        while True:
            try:
                get_reservation_status = self._reservation.get_reservation_status(self.reservation_id)
                if get_reservation_status in ["Pending for testline","Testline assigned"]:
                    log.info("{} is {}".format(self.reservation_id,get_reservation_status))
                    sleep(120)    # 120s= 10mins
                    continue
                elif get_reservation_status in ["Canceled","Finished"]:
                    log.warning('reservation {} has been {}'.format(self.reservation_id,get_reservation_status))
                    sys.exit()
                elif get_reservation_status == "Confirmed":
                    print("{} ====now it will auto extend this testline until it ends====".format(self.get_timestamp()))
                    sleep(120)    # 120s= 2mins
                    available_time = self.available_time()
                    log.info("available time {} , testline ID {}".format(available_time,self.reservation_id))
                    if available_time.total_seconds() > 0 and available_time.total_seconds() <= 60 * 60:  # time <60min
                        log.info("available time {} minutes,begin to extend testline {}".format(available_time,self.reservation_id))
                        self._reservation.extend_reservation(reservation_id=self.reservation_id, duration=60)
                        log.info("succeed to extend") 
                else:
                    continue
            except Exception as e:
                log.warning("warning: %s"%e)
                continue

    def quick_reserve(self,reservation_id):
        if self.reservation_id in [id['id'] for id in self._reservation.list_available_quick_reservations()]:
            log.info('begin to quick reserve {}'.format(self.reservation_id))
            result = self._reservation.reserve_quick_reservation(self.reservation_id)
            log.info('{}'.format(result))
        # already  reserved 
        elif 'user' in self.reservation_detail()['testline']:
            log.info('reservation id {} is reserved'.format(self.reservation_id))
            log.info('{}'.format(self.reservation_detail()))
        self.auto_extend_reservation()

# ----------------------------------------------------------------------------------------------------------------------
def getLatestENBBuild(tag):
    URL = "https://cloud.ute.nsn-rdnet.net/artifact/list/ajax/?format=json&limit=1000&offset=0&ordering=-add_date&name={}&type=1&status=1".format(
        tag)
    requestheader = {
                       'Authorization': 'Token 2c9f15c8f12d1847bf699e949687cbe19b3044e6' ,
                       'X-Requested-With':'XMLHttpRequest',
                       'Content-Type': 'application/json'
                    }
    requests.packages.urllib3.disable_warnings()
    ret = requests.get(URL, headers=requestheader)
    ret = ret.json()
    return ret["results"][0]["name"]

def interval_time(time):
    current_time = datetime.datetime.now()
    log.info("current time is {}".format(current_time))
    default_schedule_hour,default_schedule_minute = time.strip().split(":")
    schedule_time = current_time.replace(hour=int(default_schedule_hour),minute=int(default_schedule_minute),second=0,microsecond=0)
    if  schedule_time < current_time:
        schedule_time += timedelta(days=1)
    log.info("scheduled time is {}".format(schedule_time))
    wait_time = (schedule_time - current_time).total_seconds()
    m, s = divmod(wait_time, 60)
    h, m = divmod(m, 60)
    log.info("wait time  %02d:%02d:%02d , total seconds %s" %(h, m, s, wait_time))
    sleep(wait_time)

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    OBJ = Reservation()
    if not sys.argv[1:] and not RESERVATION_INFO["reservation_id"]:
        OBJ.schedule()
  
    elif sys.argv[1:]:
        try:
            if sys.argv[1].isdigit():
                OBJ.reservation_id = int(sys.argv[1])
                OBJ.quick_reserve(OBJ.reservation_id)
        except Exception:
            raise
        
    elif RESERVATION_INFO["reservation_id"]:
        try:
            OBJ.reservation_id = int(RESERVATION_INFO["reservation_id"])
            OBJ.quick_reserve(OBJ.reservation_id)
        except Exception:
            raise
    else:
        print __doc__
        sys.exit(0)

    
