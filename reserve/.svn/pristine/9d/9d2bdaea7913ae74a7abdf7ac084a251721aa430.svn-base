#! -*- encoding=utf-8 -*-
#! /usr/bin/env python


import sys;sys.dont_write_bytecode= True

person={
    "bingo":"8919cd356f5672b89ab8bfebe4cea5c90658969b",     # user info, token from cloud : https://cloud.ute.nsn-rdnet.net/user/settings/api
}

RESERVATION_INFO = {
    'enb_build': "TL00_FSM4",      		# string, fuzzy matching like "TL00_FSM4" or special ENB build 
    'cloud_type': 'CLOUD_R4P',          # string, Testline types eg. CLOUD_F. By default high-priority.
    "default_schedule_time":"now",      # string,'now' or blank for instant reservation,today or tomorrow time: "00:00~23:59"
    "ute_build":None,                   # None or string,None for default latest build  or special UTE build like "1818.01.00" 
    "share_with":None,                  # None or str or list of str, each str is User`s username,pls check username in UTE cloud
 	"bts_state":"configured",			# (string) – eNB state which should be achieved eg. configured, commissioned. By default configured.
 	"reservation_id": None				# integer or string,  quick reserve or extend a testline
}
