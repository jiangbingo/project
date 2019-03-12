# -*- encoding:utf-8 -*-
# /usr/bin/env python

"""
sftp upload plugin  to IMP server and parsed the convert-engine

"""
import os
import sys
import logging
import time
import shutil
from datetime import datetime
from functools import wraps

current_dir = os.path.dirname(__file__)
pyLibFolder = os.path.abspath(os.path.join(current_dir,'Libs'))
sys.path.append(pyLibFolder)


import re
import paramiko

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
log.addHandler(ch)
fh = logging.FileHandler(filename="log.txt", mode="a")
log.addHandler(fh)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s ")
ch.setFormatter(formatter)
fh.setFormatter((formatter))

def open_port_8080():
    cmd = 'iptables -A OUTPUT -p tcp --dport 8080 -j ACCEPT'
    subprocess.call(cmd,shell=True)
    cmd = 'iptables -A INPUT -p tcp --sport 8080 -j ACCEPT'
    subprocess.call(cmd,shell=True)
    cmd = 'iptables -A FORWARD -p tcp --sport 8080 -j ACCEPT'
    subprocess.call(cmd,shell=True)

def timethis(func):
    """
    time consumption
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        total_time = (end-start).total_seconds()
        log.info(" %s consumpted %s seconds"%(func.__name__, str(total_time)))
        return result
    return wrapper

class Sftp(object):
    """ sftp client
    """
    def __init__(self, host):
        self.host = host
        self.port = 22
        self.username = "toor4nsn"
        self.password = "oZPS0POrRieRtu"

        try:
            self.transport = paramiko.Transport((self.host, self.port))
            log.debug("transport is ok, host:'%s', port:'%s'" % (self.host, self.port))
        except Exception as error:
            raise Exception("sftp failed, host:'%s', port:'%s', reason:'%s'" %(self.host, self.port, error))
        try:
            self.transport.connect(username=self.username, password=self.password)
            #'str' object has no attribute 'get_name' if use username, password directly
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            log.info("sftp connect to '%s', username:'%s', password:'%s' is ok"% (self.host, self.username, self.password))
        except Exception as error:
            raise Exception("sftp connect to '%s' as'%s'/'%s' failed for '%s'."% (self.host, self.username, self.password, error))

    def upload_file(self, local_file, target_file):
        try:
            self.sftp.put(local_file, target_file, confirm=False)
            log.info("sftp upload from '%s' to '%s' is ok." %(local_file, target_file))
            self.get_size(target_file)
        except Exception as error:
            raise Exception("sftp upload from '%s' to '%s' is failed, reason:'%s'." %(local_file, target_file, error))

    def get_size(self, host_file_path):
        if self.is_file(host_file_path):
            size = self.sftp.lstat(host_file_path).st_size / 1000
            log.debug("sftp get file size '%s' is %sKB" %(host_file_path, size))
            return size
        else:
            log.debug("sftp get file size '%s' is wrong: not a file or not exist" %(host_file_path))
            return None

    def is_file(self, path='.'):
        log.info(path)
        ret = self.sftp.lstat(path)
        if str(ret.__str__()).startswith('-'):
            return True
        else:
            return False

class SSHClient(object):
    def __init__(self,ip,timeout=300):
        self._ip = str(ip)
        self._user = "toor4nsn"
        self._password = "oZPS0POrRieRtu"
        self._port = 22
        self._timeout = float(timeout)
        self._flag = False
        self._client = None
        self._channel = None
        try:
            sock = (self._ip,self._port)
            self._client = paramiko.Transport(sock)
            self._client.connect(username=self._user,password=self._password)
        except:
            log.warning("Exception: " + __file__ + " Line %d"%(sys._getframe().f_lineno))
            log.warning("SSH Client init: Connect to '%s' fail"%self._ip)
            return None
        try:
            self._channel = self._client.open_session()
            self._channel.settimeout(self._timeout)
            self._channel.get_pty()
            self._channel.invoke_shell()
        except:
            log.warning("Exception: " + __file__ + " Line %d"%(sys._getframe().f_lineno))
            log.warning("sshSession init: Open Channel to '%s' fail"%self._ip)
            return None
        self._flag = True
        return
    def __del__(self):
        if self._flag:
            self._channel.shutdown(2)
            self._client.close()
            self._flag = False

    def Recv(self):
        str = ''
        end = '@[^#>]*[#>]$'
        try:
            str = self._channel.recv(65535)
            if str == '':
                return (False, 'No Data recved')

            while not re.search(end,str.strip()):
                if re.search('Press space to continue',str) !=None:
                    self._channel.send(' \r')
                    temp = self._channel.recv(65535)
                    str = str + temp
                else:
                    break
        except:
            log.warning("Exception: " + __file__ + " Line %d"%(sys._getframe().f_lineno))
            log.warning("SSH Session recv: Sesssion to '%s' recv except"%self.ip)
            return (False,str)

        return (True,str)

    def Cmd(self,cmd,timeout):
        if not self._flag:
            log.warning("SSH Session to connect '%s' is not inited"%self._ip)
            return False,'SSH session is not inited'

        self._channel.send(cmd)
        self._channel.send('\r')
        time.sleep(timeout)  # seconds 
        ret = self.Recv()
        return ret[1]

    def Cmd_expect(self,cmd,expect,timeout):
        if not self._flag:
            log.warning("SSH Session to connect '%s' is not inited"%self._ip)
            return False,'SSH session is not inited'
        rtn = self.Cmd(cmd,timeout)
        rstObj = re.search(expect,rtn)
        log.debug("*"*100)
        log.debug("expect is %s",expect)
        log.debug("rtn is %s",rtn)
        log.debug("*"*100)
        if rstObj != None:
            return (True,rtn)
        else:
            return (False,rtn)

class sshSes(object):
    def __init__(self):
        self.dict = dict()

    def __del__(self):
        del self.dict

    def create(self,ip):
        if ip in self.dict:
            return (True,self.dict[ip])

        ses = SSHClient(ip)
        if not ses._flag:
            return (False,None)

        self.dict[ip] = ses
        return (True,ses)

    def disconnect(self,ip):
        if not (ip in self.dict):
            return (False,'No connection to ' + ip)
        ses = self.dict[ip]
        del self.dict[ip]
        del ses
        return (True,'Succeed to disconnect ' + ip)

    def reset_session(self,ip):  
        self.disconnect(ip)
        ret,pro = self.create(ip)
        if not ret:
            return (False,'Fail to reconnect to ' + ip)
        else:
            return (True,pro)

    def sendCmd(self,ip,cmd,expect,timeout):
        ret,ses = self.create(ip)
        if not ret:
            log.warning("send cmd '%s' to ne '%s' sesssion creat fail"%(cmd,ip))
            return (False,'Session create fail')
        try:
            (ret,rtn) = ses.Cmd_expect(cmd,expect,timeout)
        except:
            log.warning("Now Reconnect session to IP '%s'"%ip)
            ret,ses = self.reset_session(ip)
            if not ret:
                log.warning("send cmd '%s' to ne '%s' sesssion creat fail"%(cmd,ip))
                return (False,'Session create fail')

            try:
                (ret,rtn) = ses.Cmd_expect(cmd,expect,timeout)
            except:
                log.warning("Exception : " + __file__ + " Line %d"%(sys._getframe().f_lineno))
                log.warning("sshSession sendCmd: sendCmd to '%s' except"%ip)
                ret = False
                rtn = 'socket is close'
        return (ret,rtn)

sshSessions = sshSes()

@timethis
def ssh_Cmd(ip,cmd,expect,timeout=1):
    timeout = timeout
    cmd = cmd.strip('\r\n\t')
    if cmd.lower() == 'reset_ses':
        sshSessions.reset_session(ip)
        log.debug('reset session')
        return (True,'reset session')
    if cmd.lower() == 'disconnect':
        sshSessions.reset_session(ip)
        log.debug('disconnect')
        return (True,'disconnect')
    (ret,rtn) = sshSessions.sendCmd(ip,cmd,expect,timeout)
    if ret:
        log.info("success to %s"%cmd)
    else:
        log.error("fail to %s"%cmd)
        raise Exception("fail to %s with expect result is %s"%(cmd,expect))
    return rtn

def get_plugin_path(ip):
    # cmd = 'bcli.sh -s'
    # rtn=ssh_Cmd(ip,cmd,'',10)
    # plugins = re.search('/opt/imp/.+/data/plugins/',rtn)
    # if plugins:
    #     path = plugins.group()
    #     return path
    # else:
    #     raise Exception("no plugin found")

    IMP_PATH_INFO=r"/var/imp/.impLocation.conf"  # /opt/imp/18a.1.20181214141457.6893d6
    cmd = "cat %s"%IMP_PATH_INFO
    rtn = ssh_Cmd(ip,cmd,'')
    res = re.search('/opt/imp/[0-9a-z\.]+',rtn)
    if res:
        impLocation = res.group()
        log.info("imp path is %s"%impLocation)
        path = "/".join([impLocation,"data","plugins"])
        return path
    else:
        raise Exception("no plugin found in %s"%IMP_PATH_INFO)

def get_converterEngine(path,ip):
    cmd = 'pwd'
    rtn=ssh_Cmd(ip,cmd,'',1) 
    cmd = 'find %s -name ConverterEngine*.txz '%path
    rtn=ssh_Cmd(ip,cmd,'ConverterEngine',1)
    converterEngine_path = rtn.strip().split('\n')[-2].rsplit('/',1)
    log.info("converterEngine_path is %s"%converterEngine_path)
    converterEngine_dir,converterEngine_name = converterEngine_path[0].strip(),converterEngine_path[1].strip()
    log.info("converterEngine directory is %s,converterEngine name is %s"%(converterEngine_dir,converterEngine_name))
    return (converterEngine_dir,converterEngine_name)


def main(ip,file):
    zipfile = os.path.basename(file)
    ret = re.search("btsmed_[0-9a-zA-Z\_]+\.zip$",zipfile)
    if not ret:
        raise Exception("there is no btsmed_xxxx.zip")
    # btsmed_FL19_FSM4_9997_181219_000804.zip ==> FL19_FSM4_9997_181219_000804
    zipfile_name = os.path.splitext(os.path.basename(zipfile))[0].replace("btsmed_",'')

    # 获取 IMP plugin 目录： /opt/imp/19.2.20190226101746.f28275/data/plugins/ 
    plugin_path = get_plugin_path(ip)
    log.info("plugin path is %s"%plugin_path)
    sftp_obj = Sftp(ip)
    path ='/'.join([plugin_path,zipfile])
    # 上传目录 /opt/imp/19.2.20190226101746.f28275/data/plugins/btsmed_FL19_FSM4_9997_181219_000804.zip
    log.info("upload path is %s"%path)
    sftp_obj.upload_file(file,path)

    # 切换到 /opt/imp/19.2.20190226101746.f28275/data/plugins/
    cmd = "cd %s"%plugin_path
    rtn = ssh_Cmd(ip,cmd,'')
    #创建 FL19_FSM4_9997_181219_000804
    cmd = "mkdir -p %s"%zipfile_name
    rtn = ssh_Cmd(ip,cmd,'')
    cmd = "unzip -o %s -d %s"%(zipfile,zipfile_name)   # overwrite if exist same folder and files
    rtn = ssh_Cmd(ip,cmd,'',3)    # a little time to overwrite files
    # 删除上传的ZIP文件
    cmd = 'rm -rf %s'%zipfile
    rtn = ssh_Cmd(ip,cmd,'')
    # 切换到 /opt/imp/19.2.20190226101746.f28275/data/plugins/FL19_FSM4_9997_181219_000804/
    cmd = "cd %s"%(zipfile_name)
    rtn = ssh_Cmd(ip,cmd,'')

    # 获取/opt/imp/19.2.20190226101746.f28275/data/plugins/FL19_FSM4_9997_181219_000804/所有路径下 ConverterEngine_S5107884.txz的目录和ConverterEngine_S5107884.txz
    path = '/'.join([plugin_path,zipfile_name])
    converterEngine_dir,converterEngine= get_converterEngine(path,ip)
    converterEngine_name = os.path.splitext(converterEngine)[0]
    # 切换到/opt/imp/19.3.20190311133607.b58c93/data/plugins/FL19_FSM4_9997_181219_000804/FCTM/
    cmd = "cd %s"%(converterEngine_dir)
    rtn = ssh_Cmd(ip,cmd,'')
    # 创建 /opt/imp/19.3.20190311133607.b58c93/data/plugins/FL19_ENB_0000_000010_000030/ConverterEngine_F7725906/
    jar_path = '/'.join([converterEngine_dir,converterEngine_name])
    log.info("jar path is %s"%jar_path)
    cmd = "mkdir -p %s"%jar_path
    rtn = ssh_Cmd(ip,cmd,'')
    # 解压缩 ConverterEngine_S5107884.txz 到 /opt/imp/19.3.20190311133607.b58c93/data/plugins/FL19_ENB_0000_000010_000030/ConverterEngine_F7725906/
    cmd = "tar xvf %s -C %s"%(converterEngine,jar_path)
    rtn = ssh_Cmd(ip,cmd,'')    
    # 用户组权限
    cmd = "chown -R btsmed:btsmedGroup %s"%plugin_path
    rtn = ssh_Cmd(ip,cmd,'')
    log.info("success to upload converterEngine ")



if __name__ == '__main__':
    main("10.108.152.14",r"D:\userdata\bijiang\Desktop\jiangbin\code\practice\IMP plugin\btsmed_SBTS18A_TDDENB_0000_000380_000000.zip")