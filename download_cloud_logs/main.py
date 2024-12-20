# -*- encoding=utf-8 -*-
#! /usr/bin/env python
import os,sys
import requests
import subprocess
import shutil
import platform
import zipfile
import logging
import datetime,time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)
fh = logging.FileHandler(filename="log.txt", mode="a")
log.addHandler(fh)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s ")
ch.setFormatter(formatter)
fh.setFormatter((formatter))

cur_dir = os.path.dirname(__file__)

# 有用logs类型扩展名
DATA_EXTS = [
        '.html',
        '.log',
        '.zip',
        ".xz"    # 不支持.xz 下载
        ]

EXCLUDE_FILES=[
'index.html',
'report.html',
'debug.log'
]

EXCLUDE_FOLDERS=[
'preparation_logs',
'reporting_portal_report'
]

# if 7z_dll error, download  https://fix4dll.com/7z_dll 
WGET_PATH = os.path.abspath(os.path.join(cur_dir,'./lib','wget.exe'))
UNZIP_PATH = os.path.abspath(os.path.join(cur_dir,'./lib/','7z.exe'))
sys.path.append(WGET_PATH)
sys.path.append(UNZIP_PATH)

PROXY = "http://10.144.1.10:8080"
if 'http_proxy' not in os.environ:
    os.environ['http_proxy'] = PROXY
if 'https_proxy' not in os.environ:
    os.environ['https_proxy'] = PROXY

def open_unzip_log_windows(path):
	if path and os.path.exists(path):
	    if os.path.isfile(path):
	        import win32process
	        try:   # 打开外部可执行程序
	            win32process.CreateProcess(path, '',None , None , 0 ,win32process. CREATE_NO_WINDOW , None , None ,win32process.STARTUPINFO())
	        except Exception, e:
	            log.error(e)
	    else:
	        os.startfile(str(path))  # 打开目录
	else:  
	    log.warning('{} folder does not exists'.format(path))

class handle(object):
    def __init__(self,url):
        self.url = url
        self.system = "windows" if  platform.system().lower()== "windows" else "linux"
        self.zip_name = None
        self.log_dir = None
        if os.path.isdir(dst_logs_dir):
            self.raw_logs = os.path.join(dst_logs_dir,'%s'%(time.strftime("%Y%m%d_%H.%M.%S",time.localtime(time.time()))))
        else:
            log.warning("%s is not a valid folder"%dst_logs_dir)
            self.raw_logs = os.path.abspath(os.path.join(cur_dir,'%s'%(time.strftime("%Y%m%d_%H.%M.%S",time.localtime(time.time())))))

    def download_files(self,REP_url):
        os.makedirs(self.raw_logs, 0777)
        log.info("begin to download files from:{}".format(self.url))
        log.info("download to {}".format(self.raw_logs))
        """
        # todo:https://stackoverflow.com/questions/3430810/wget-download-with-multiple-simultaneous-connections
        wget options:
        -nc : "no clobber" - it causes wget to ignore aready downloaded (even partially) files. 
        """
        options = '--tries=5 --accept {} --reject-regex preparation_logs --execute robots=off -c -r -nc -np -L -P'.format(','.join(DATA_EXTS))
        if self.system == "windows":
            cmd = r"%s %s %s %s"%(WGET_PATH,options,self.raw_logs,self.url)
        else:
            cmd = 'wget %s %s %s'%(options,self.raw_logs,self.url)   
        subprocess.call(cmd,shell=True)

    def get_files(self):
        all_files = []
        for root, dirname, files in os.walk(self.raw_logs):
            for d in dirname:
                if d in EXCLUDE_FOLDERS:
                    if os.path.exists(os.path.join(root,d)):
                        shutil.rmtree(os.path.join(root,d))
                        log.info("remove file: %s"%f)
                        continue
            for f in files:
                if f in EXCLUDE_FILES:
                    os.remove(os.path.join(root,f))
                    log.info("remove file: %s"%f)
                    continue
                if os.path.splitext(f)[-1] in DATA_EXTS:
                    all_files.append(os.path.join(root,f))
                    log.info("append file: %s"%f)
                if os.path.splitext(f)[-1].lower() =='.zip':
                    self.unzip(os.path.join(root,f),self.raw_logs)
                    self.zip_name = os.path.splitext(f)[0]
                    print self.zip_name
                    shutil.rmtree(os.path.dirname(os.path.join(root,f)),ignore_errors=True)
                if f == "log.html":
                    shutil.move(os.path.join(root,f),self.raw_logs)
        log.info("files are : {}".format(all_files))

    def adjust_dir(self,path):
        if os.path.isdir(path):
            for d in os.listdir(path):
                self.adjust_dir(os.path.join(path, d))
            if not os.listdir(path):
              os.rmdir(path)
        log.info("delete gap directory: {}".format(path))

    def change_name(self,path,name):
        if os.path.exists(path):
            newname = "{}_{}".format(os.path.basename(path),name)
            newpath = os.path.join(os.path.dirname(path),newname)
            os.rename(path,newpath)
            log.info("change folder name {} to {}".format(os.path.basename(path),newname))
            self.log_dir = newpath

    def unzip(self,zippath,dest_dir):
        if self.system == "windows":
            log.info("log dir is {}".format(dest_dir))
            options = "x -y -o{}".format(dest_dir)
            cmd = r"%s %s %s"%(UNZIP_PATH,options,zippath)
        else:
            options = "x -y -o{}".format(dest_dir)
            cmd = 'unzip %s %s'%(options,zippath)   
        subprocess.call(cmd,shell=True)

    def handle_logs(self):
        try:
            self.download_files(self.url)
            self.get_files()
            self.adjust_dir(self.raw_logs)
            if self.zip_name:
                self.change_name(self.raw_logs,self.zip_name)
            else:
                self.log_dir = self.raw_logs
        except Exception as err:
            log.error(err)
        finally:
            open_unzip_log_windows(self.log_dir)

if __name__ == "__main__":
    #默认log解压缩目录
    dst_logs_dir = r'D:/tmp'
    REP_url = "http://logs.ute.nsn-rdnet.net/cloud/execution/4208356/"
    obj = handle(REP_url)
    obj.handle_logs()
