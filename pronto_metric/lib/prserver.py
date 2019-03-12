#! /usr/bin/env python
# -*- coding: utf-8

import os,sys,urllib,urllib2,cookielib,socket
from variables import *
from log import *

logger = setup_logger()

class ProntoServer(object):
    def __init__(self):
        self._server_url = PR_SERVER
        self._user = PR_USER
        self._password = PR_PASS
        self._password_tmp = PR_PASS.replace(self._password,'*'*len(self._password))
        self._state = 'disconnected'
        self._socket_lock = None

        try:
            logger.info("Now try to connect HTTPS PR server '%s'.The login user is %s,password is %s)"%(self._server_url,self._user,self._password_tmp))
            ret = self.ConnectSerevr(self._server_url,self._user,self._password)
            if ret:
                self._state = 'connected'
                logger.info('Succeed to connect HTTPS PR serevr %s'%self._server_url)
        except Exception,e:
            if repr(e) == 'HTTPError()':
                logger.info('Fail to connect HTTPS PR serevr %s.'%PR_SERVER)

    def ConnectSerevr(self,verify_cert=False):
        if verify_cert:
            pass
        else:
            cookie_handler = urllib2.HTTPCookieProcessor()    # 处理HTTP Cookie
            https_handler = urllib2.HTTPSHandler()   # 通过处理HTTPS重定向
            opener = urllib2.build_opener(cookie_handler,https_handler)

            resp = opener.open(self._server_url + '/')
            ret = self.HandleAuth(self,opener,self._server_url,resp,self._user,self._password)  # request_url,opener,response对象,用户名,密码

            if ret:
                logger.info('Sueeccd to connect HTTPS PR serevr %s.'%PR_SERVER)
                ret = urllib2.install_opener(opener)     # 把这个opener作为后续这个程序里的默认opener
                '''没有上面这一句，每次Request都需要重新登录一下，不会使用cookie'''
                return ret
            else:
                logger.warning('Terrible !!! Fail to connect HTTPS PR serevr %s.'%PR_SERVER)
                return ret


    @staticmethod
    def HandleAuth(self,opener,server_url,resp,user,password):
        content_lines = resp.readlines()
        response_url = resp.url.split('/')[2]
        a_lines = []
        for line in content_lines:
            # 采用的验证方式是"Nokia Web Single Sign-On (SSO)" 单点登录  多系统应用群里登录一个系统后，整个群域里的其它所有系统就自动得到授权，无需再次登录
            # SSO里群域里的所有系统并没有自己的登录入口，只有一个单独的认证中心，所有的系统都只接收认证中心的间接授权
            if 'Single Sign-On (SSO)' in line.decode(PR_CHARSET):
                a_resp = self.SSOAuth(self,opener,server_url,user,password,response_url)
                # print a_resp.geturl()    # 登录成功后response url就是https://pronto.int.net.nokia.com/pronto/home.html
                if a_resp is False:
                    self.auth_failed_reason = 'HTTP error on authorization'
                    return False
                a_lines = a_resp.readlines()
                for a_line in a_lines:
                    decoded_a_line = a_line.decode(PR_CHARSET)
                    if '>Authentication Error</div>' in decoded_a_line:
                        logger.warning('SSO auth problem - user/password combination not accepted on ' + server_url)
                        self.auth_failed_reason = 'SSO error'
                        return False
        for a_line in a_lines:
            decoded_a_line = a_line.decode(PR_CHARSET)
            if '<h1>Pronto Home Page</h1>' in decoded_a_line:
                logger.info('Succeed to auth,and login to Pronto Home Page successfully')
                return True
        return False

    @staticmethod
    def CommonAuth(opener,server_url,redirect_url,post_data):
        try:
            a_resp = opener.open(redirect_url, timeout=PR_PROBE_TIMEOUT, data=post_data.encode())
        except Exception,e:
            logger.warning('Authorization failed with error: %s'%repr(e))
            return False
        return a_resp

    @staticmethod
    def SSOAuth(self,opener,server_url,user,password,sso_server):
        post_data = urllib.urlencode({
            'PASSWORD': password,
            'SMENC': 'ISO-8859-1',   # 编码格式
            'SMLOCALE': 'US-EN',
            'USER': user,
            'postpreservationdata': '',
            'smauthreason': '0',
            'target': server_url.replace('https', 'HTTPS') + '/',
            'x': '32',
            'y': '16',
        })
        redirect_url = 'https://' + sso_server + '/siteminderagent/forms/login.fcc'
        logger.info('Now we need to verify auth through SSO site:' + redirect_url)
        a_resp = self.CommonAuth(opener,server_url,redirect_url,post_data)
        return a_resp
    '''
    def GetSocketLock(self):
        self._socket_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket_lock.bind(('localhost', PR_SOCKET_LOCK_PORT))
        except socket.error:
            logger.error('Unable to bind to port ' + str(PR_SOCKET_LOCK_PORT))
        logger.info('Socket lock bind OK')
        return True

    def ReleaseSocketLock(self):
        if self._socket_lock is not None:
            self._socket_lock.close()
            self._socket_lock = None
            logger.info('Socket lock released')
    '''

    """
    get the html from the prserver tool for the given url through the http GET request,return a response instance
    """
    def HttpGet(self,url,referer=None,get_timeout=PR_GET_TIMEOUT):
        if not url.startswith('/'):
            url = '/' + url
        fullurl = self._server_url + url

        logger.info('Request GET from prserver tool: ' + fullurl)
        try:
            resp = urllib2.urlopen(urllib2.Request(fullurl))
            if resp.getcode() == 200:
                logger.debug('Request: OK')
                return resp
        except Exception,e:
            logger.error('repr(e)')


class PRTool(object):
    def __init__(self):
        pass

if __name__ == "__main__":
    pass