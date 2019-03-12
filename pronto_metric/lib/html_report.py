#! /usr/bin/env python
# -*- coding: utf-8

import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),'3rd_lib')))

import pyh
import pandas as pd

from email.mime.text import MIMEText
SENDER = 'I_EXT_MBB_GLOBAL_LTE_TDD_OM_CI@internal.nsn.com'
TO_RECEIVERS = ['']
CC_RECEIVERS = ['I_EXT_MBB_GLOBAL_LTE_TDD_OM_CI@internal.nsn.com']


from variables import VIEW_AG,VIEW_DATE,PR_STATISTIC,PR_LINK

from log import *
logger = setup_logger()

curdir = os.path.abspath(os.path.dirname(__file__))
report_html = os.path.abspath(os.path.join(curdir, '..', 'log', 'report.html')) 
raw_file = os.path.abspath(os.path.join(curdir, '..', 'rawData.txt'))


paradict = {}
def GenerateHTMLReport(paradict):
    # 初始化一个PyH对象,参数是page的名称
    curdir = os.path.abspath(os.path.dirname(__file__))
    report_html = os.path.abspath(os.path.join(curdir, '..', 'log', 'report.html'))
    page = PyH("Pronto transfer hops report")

    '''
    page<<  写入的都是<body>...</body>里的内容
    '''
    # h1~h6  标题标签   h1~h6字体逐渐变小
    page<<h2("Pronto transfer hops statistics(reported by Author Group '%s')"%VIEW_AG,cl = 'left')
    page<<h2("Start Date:%s"%VIEW_DATE[0],cl = 'left')
    page<<h2("End   Date:%s"%VIEW_DATE[1],cl = 'left')
    logger.info('Begin to Generate HTML Report')
    page.printOut(report_html)

class SentEmail(object):
    def __init__(self, log):
        self._mail_host = 'mailrelay.int.nokia.com'
        self._mail_user = 'tdd_lte_oam_ci'
        self._mail_password = ''
        self._msg = None
        self._log = log

    def run(self):
        self._generate_mail_text()
        self._sent_email()

    def _get_xml_content(self):
        with open(self._log, 'rb') as fp:
            content = fp.read()
        return content

    def _generate_mail_text(self):
        _msg = MIMEText('Hello\n\n%s\n%s' % (self._get_xml_content(),
                                             'Best Regards'), 'html', 'utf-8')
        _msg['From'] = SENDER
        _msg['To'] = ';'.join(set(TO_RECEIVERS))
        _msg['Cc'] = ';'.join(set(CC_RECEIVERS))
        _msg['Subject'] = '[%s]Here is Pronto metric from {0}-{1}'.format(VIEW_DATE[0],VIEW_DATE[1])
        self._msg = _msg

    def _sent_email(self):
        try:
            smtpobj = smtplib.SMTP()
            smtpobj.connect(self._mail_host, 25)
            try:
                smtpobj.login(self._mail_user, self._mail_password)
            except:
                pass
            smtpobj.sendmail(self._msg['From'], (self._msg['To'] + ';' + self._msg['Cc']).split(';'),
                             self._msg.as_string())
            smtpobj.quit()
            print "[%s]INFO: Sent email successfully!" % get_timestamp()
        except smtplib.SMTPException as e:
            raise RuntimeError("[%s]ERROR: Can not send email. Error is %s." % (get_timestamp(), str(e)))


def generate_html(view_id,rawdata):
    title = rawdata[0].keys()
    rows = [['' for i in range(len(rawdata))] for j in range(len(title))]
    for j in range(len(rawdata)):
        for i in range(len(title)):
            rows[i][j] = rawdata[j][title[i]]
    with open(report_html, 'wb') as fp:
        fp.write('<!DOCTYPE html><html><body> \
                          <h3>Pronto transfer hops statistics(reported by Author Group {group})<br> \
                          Pronto statistics:{pr_statistic}</a><br>\
                          Start Date:{start_date}<br>\
                          End   Date:{end_date}<br>\
                          Result Summary:<br><br>'
                 .format(group = VIEW_AG,pr_statistic=generate_hyperlink(PR_STATISTIC+view_id,PR_STATISTIC+view_id),start_date=VIEW_DATE[0],end_date=VIEW_DATE[1]))
        tableToHtml(fp,rows,title)
        fp.write('</body>\n</html>')


def generate_hyperlink(link,text):
    return '<a href={0} target="_blank" style="color:green">{1}</a>'.format(link,text)


def tableToHtml(fp,rows,title):
    #将数据转换为html的table
    #result是list[list1,list2]这样的结构
    #title是list结构；和result一一对应。titleList[0]对应resultList[0]这样的一条数据对应html表格中的一列
    d = {}
    index = 0
    for t in title:
        d[t]=rows[index]
        index = index+1
    df = pd.DataFrame(d)
    df = df[title]
    h = df.to_html(index=True)
    # print df.to_string()
    fp.write(h)

if __name__ == "__main__":
    # GenerateHTMLReport(paradict={})
    # generate_html('VIEW643997')
    # d1 = {'Transfer Hops': 1, 'Author': ['Ren, Lola (NSB - CN/Hangzhou)'], 'Problem ID': ['PR333057'], 'Revision History': ['2018-04-04 06:59 Cai, Shenyu (NSB - CN/Shanghai) State changed from Investigating to Correction Not Needed', '2018-04-03 07:45 Hu, Xiaofeng A. (NSB - CN/Shanghai) edited. Changed field(s): RD Information', '2018-04-02 08:31 Hu, Xiaofeng A. (NSB - CN/Shanghai) edited. Changed field(s): RD Information', '2018-04-02 06:07 Hu, Xiaofeng A. (NSB - CN/Shanghai) The group in charge changed from RABLTESWCELLC to EXT_LTE_ASB_CSH_CP. Reason for Transfer: SHA is checking', '2018-04-02 06:07 Hu, Xiaofeng A. (NSB - CN/Shanghai)  The state of the problem changed from New to Investigating.', '2018-04-01 07:06 Pronto, Auto (Nokia - Global) New Correction document Correction for TL00 TL00_ENB_9999_xxxxxx_yyyyyy has been created.', '2018-03-30 12:37 Ren, Lola (NSB - CN/Hangzhou) Problem Report created'], 'State': ['Correction Not Needed'], 'State Changed to Correction not needed': ['04 Apr 2018'], 'State Changed to Closed': [''], 'Reported Date': ['30 Mar 2018'], 'Attached PRs': [''], 'Implementation Group': [''], 'Author Group': ['LTE_DEVHZ5_CHZ_FV'], 'Reason Why Correction is Not Needed': ['Fault was not reproducible']}
    # d2 = {'Transfer Hops': 10, 'Author': ['Jiang, Huabao (NSB - CN/Hangzhou)'], 'Problem ID': ['PR326955'], 'Revision History': ['2018-03-20 08:45 Pang, Bo (NSB - CN/Beijing) The state of the problem changed from First Correction Complete to Closed', '2018-03-20 08:39 Shang, Jl (NSB - CN/Beijing) Additional Value is modified from PREINV WR MZAK, admin, TDDCPRI to PREINV WR MZAK, admin, TDDCPRI  bj_wmp12', '2018-03-20 04:46 Pang, Bo (NSB - CN/Beijing) edited. Changed field(s): RD Information', '2018-03-20 04:32 Yang, Zhantao (NSB - CN/Beijing) The fault id  FA379480 associated with this PR before attach has been deleted - data is restorable by Pronto Support', '2018-03-20 04:32 Yang, Zhantao (NSB - CN/Beijing) Problem attached to PR327499.', '2018-03-20 04:32 Yang, Zhantao (NSB - CN/Beijing) The group in charge changed from RABLTESWPWROAM To RABLTESWCBEOAM', '2018-03-20 04:32 Yang, Zhantao (NSB - CN/Beijing) The state of the problem changed from New to First Correction Complete', '2018-03-19 04:10 Yang, Zhantao (NSB - CN/Beijing) The group in charge changed from RABLTESWCBEOAM to RABLTESWPWROAM. Reason for Transfer: FZHJ is OBSAI radio, BBC to check', '2018-03-17 10:06 Zak, Mateusz (Nokia - PL/Wroclaw) edited. Changed field(s): RD Information', '2018-03-17 10:06 Zak, Mateusz (Nokia - PL/Wroclaw) Additional Value is modified from PREINV WR MZAK, admin to PREINV WR MZAK, admin, TDDCPRI', "2018-03-17 09:56 Zak, Mateusz (Nokia - PL/Wroclaw) The group in charge changed from NISSOAM to RABLTESWCBEOAM. Reason for Transfer: @I_MBB_BTS_LTE_TDDCPRI_GMS: please check HWAPI's comment from email\r\n\r\n\xe2\x80\x9cWith the provided logs and analysis, I cannot point out other root cause but wrong cpri link rate, which is requested by OAM.\r\nAnd if that\xe2\x80\x99s the case, then there\xe2\x80\x99s similar PR327499, which is at First Correction Ready For Testing state, by OAM fix.\r\n\xe2\x80\x9c", '2018-03-16 14:26 Kuki, Henri (EXT - FI/Oulu) The group in charge changed from NIOSHC to NISSOAM. Reason for Transfer: Please check mcuhwapi analysis: wrong cpri link rate etc.', '2018-03-16 14:26 Kuki, Henri (EXT - FI/Oulu) The state of the problem changed from Investigating to New', '2018-03-16 14:21 Kuki, Henri (EXT - FI/Oulu) edited. Changed field(s): RD Information', '2018-03-16 14:20 Kuki, Henri (EXT - FI/Oulu) Attachment MCUHWAPI_analysis_4.txt added.', '2018-03-16 10:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt added.', '2018-03-16 10:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-16 08:01 Kuki, Henri (EXT - FI/Oulu) edited. Changed field(s): RD Information', '2018-03-16 08:00 Kuki, Henri (EXT - FI/Oulu)  The state of the problem changed from New to Investigating.', '2018-03-15 18:39 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) The group in charge changed from RABLTESWPWROAM to NIOSHC. Reason for Transfer: @Nsn, Mcuhwapi-Prescreening (Nokia - Global) could you please check this case.\r\nIt looks like there are some problems with communication to platform services. \r\nAccording to OAM code:\r\ncase EFaultId_CommunicationFailureAl:\r\n        {\r\n            auto pCcu = getCcuByNode(adetLimProxy_, faultReq.faultyUnit);\r\n\r\n            if (not pCcu) break;\r\n\r\n            handleCcuFaultReq(adetLimProxy_,\r\n                lim::CCU_L::StateInfo::EReasoningStatus_NoCommunicationWithPlatformServices,\r\n                pCcu-getDistName(), faultReq.faultState);\r\n            break;\r\n        }\r\n\r\nFor sure there was reported EFaultId_CommunicationFailureAl (1806) fault on 0x10 but this prints were omitted in provided logs.', '2018-03-15 18:38 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:38 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:38 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:38 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:38 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:37 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:36 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt removed.', '2018-03-15 18:35 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) edited. Changed field(s): RD Information', '2018-03-15 18:33 Nowacki, Arkadiusz (Nokia - PL/Wroclaw) Attachment ADET analysis.txt added.', '2018-03-14 16:22 Moldovan, Loredana (Nokia - RO/Timisoara) The group in charge changed from NITSSOAM to RABLTESWPWROAM. Reason for Transfer: @ADET please check according to attached analysis', '2018-03-14 16:21 Moldovan, Loredana (Nokia - RO/Timisoara) New Correction document Correction for SBTS_TDD SBTS00_TDDFSM4_9999_xxxxxx_yyyyyy has been created.', '2018-03-14 16:21 Moldovan, Loredana (Nokia - RO/Timisoara) New Correction document Correction for SBTS_TDD SBTS00_TDDFSM3_9999_xxxxxx_yyyyyy has been created.', '2018-03-14 15:57 Codrean, Razvan (Nokia - RO/Timisoara) edited. Changed field(s): RD Information', '2018-03-14 15:57 Codrean, Razvan (Nokia - RO/Timisoara) Attachment FRI_analysis.txt added.', '2018-03-14 15:57 Codrean, Razvan (Nokia - RO/Timisoara) edited. Changed field(s): RD Information', '2018-03-14 15:26 Rita, Gabriel (Nokia - RO/Timisoara) Optional Value is updated with FRI Screened.', '2018-03-12 16:58 Badescu, Ciprian (Nokia - RO/Timisoara) edited. Changed field(s): Development Fault Coordinator', '2018-03-12 16:21 Szczepkowicz, Sebastian (Nokia - PL/Wroclaw) The group in charge changed from NIWRSSOAM to NITSSOAM. Reason for Transfer: @I_EXT_MBB_SRAN_SBTS_OM_FRI_GMS Please tell us what triggered that recovery action', '2018-03-12 09:02 Liu, Yanyan (NSB - CN/Hangzhou) The group in charge changed from NIHZSSOAM to NIWRSSOAM. Reason for Transfer: As to the Delta commission failure mentioned by tester, it is because MCTRL called DWN_REQ.oper_reject execution. @MCTRLcould you help check why this delta commission was rejected?', '2018-03-12 09:02 Liu, Yanyan (NSB - CN/Hangzhou) The state of the problem changed from Investigating to New', '2018-03-12 08:59 Liu, Yanyan (NSB - CN/Hangzhou) edited. Changed field(s): RD Information', '2018-03-12 08:57 Liu, Yanyan (NSB - CN/Hangzhou) Attachment URI_analysis_20180312.txt added.', '2018-03-12 03:58 Wang, Tao-Vito (NSB - CN/Hangzhou) The state of the problem changed from New to Investigating', '2018-03-11 07:07 Teng, Ming (NSB - CN/Hangzhou) Top Importance Value(s) Added :TOP_LTE_SBTS00_TDD_CIT', '2018-03-09 16:05 Zak, Mateusz (Nokia - PL/Wroclaw) The group in charge changed from NISWEBEM to NIHZSSOAM. Reason for Transfer: URI please check for what reason IM does not contain PLAN_VALIDATE_IND-4 NACK, details in email', '2018-03-09 13:24 Zak, Mateusz (Nokia - PL/Wroclaw) edited. Changed field(s): RD Information', '2018-03-09 13:24 Zak, Mateusz (Nokia - PL/Wroclaw) Additional Value is modified from PREINV WR MZAK to PREINV WR MZAK, admin', '2018-03-09 13:23 Zak, Mateusz (Nokia - PL/Wroclaw) The group in charge changed from NIWRSSOAM to NISWEBEM. Reason for Transfer: after online consultation with Radoslaw Jablonka (ute_admin) this pr is similar to PR324825\r\n@Admin please check from your pov, why  after BTS reset (recommissioning) there is no response from webem to ute_admin that ends up with timeout 300s, and please confirm if the PR324825 is same and if it can be attached.', '2018-03-09 10:35 Zak, Mateusz (Nokia - PL/Wroclaw) The group in charge changed from NISSOAM to NIWRSSOAM', '2018-03-09 10:35 Zak, Mateusz (Nokia - PL/Wroclaw) edited. Changed field(s): RD Information, Development Fault Coordinator, Group in Charge', '2018-03-09 10:35 Zak, Mateusz (Nokia - PL/Wroclaw) Additional Value is updated with PREINV WR MZAK', '2018-03-09 10:24 Jiang, Huabao (NSB - CN/Hangzhou) edited. Changed field(s): Description', '2018-03-09 10:10 Jiang, Huabao (NSB - CN/Hangzhou) Problem Report created'], 'State': ['Closed'], 'State Changed to Correction not needed': [''], 'State Changed to Closed': ['20 Mar 2018'], 'Reported Date': ['09 Mar 2018'], 'Attached PRs': ['PR327499'], 'Implementation Group': ['RABLTESWCBEOAM', 'RABLTESWCBEOAM', 'RABLTESWCBEOAM'], 'Author Group': ['LTE_DEVHZ5_CHZ_FV'], 'Reason Why Correction is Not Needed': ['']}
    # d3 = {'Transfer Hops': 0, 'Author': ['Shen, Emma (NSB - CN/Hangzhou)'], 'Problem ID': ['PR327334'], 'Revision History': ['2018-03-22 09:24 Cao, Yanjue (NSB - CN/Shanghai) The state of the problem changed from First Correction Ready For Testing to Closed', '2018-03-21 05:22 Adriano, Mark (Nokia - PH/Quezon City) Solution Description: Correction for LTE_TOOL LTE_TOOL has been deleted.', '2018-03-21 05:22 Adriano, Mark (Nokia - PH/Quezon City) Solution Description: Correction for LTE_TOOL LTE_TOOL has been deleted.', '2018-03-21 05:22 Adriano, Mark (Nokia - PH/Quezon City) Solution Description: Correction for LTE_TOOL LTE_TOOL has been deleted.', '2018-03-21 05:22 Adriano, Mark (Nokia - PH/Quezon City) Solution Description: Correction for FL00 FL00_ENB_9999_xxx_yy has been deleted.', '2018-03-21 05:22 Adriano, Mark (Nokia - PH/Quezon City) Solution Description: Correction for FL00 FL00_ENB_9999_xxx_yy has been deleted.', '2018-03-21 05:22 Adriano, Mark (Nokia - PH/Quezon City) Solution Description: Correction for FL18 FL18_ENB_0000_xxx_yyy has been deleted.', '2018-03-21 04:52 Pineda, Lezfer (Nokia - PH/Quezon City) Problem attached to PR327543.', '2018-03-21 04:41 Pineda, Lezfer (Nokia - PH/Quezon City) Problem attached to PR327942.', '2018-03-21 04:39 Pineda, Lezfer (Nokia - PH/Quezon City) Problem attached to PR328510.', '2018-03-21 04:36 Palafox, Jessica (Nokia - PH/Quezon City) The state of the problem changed from Investigating to First Correction Ready For Testing', '2018-03-20 10:01 Palafox, Jessica (Nokia - PH/Quezon City) edited. Changed field(s): RD Information', '2018-03-20 09:18 Palafox, Jessica (Nokia - PH/Quezon City) edited. Changed field(s): RD Information', '2018-03-19 08:12 Palafox, Jessica (Nokia - PH/Quezon City) edited. Changed field(s): RD Information', '2018-03-16 08:44 Palafox, Jessica (Nokia - PH/Quezon City) edited. Changed field(s): RD Information', '2018-03-16 03:58 Pineda, Lezfer (Nokia - PH/Quezon City)  The state of the problem changed from New to Investigating.', '2018-03-15 08:06 Palafox, Jessica (Nokia - PH/Quezon City) edited. Changed field(s): RD Information', '2018-03-13 10:11 Pronto, Auto (Nokia - Global) edited. Changed field(s): RD Information', '2018-03-13 10:10 Pronto, Auto (Nokia - Global) Top Importance Value(s) Added :TOP_TL00_CIT_blocker', '2018-03-13 09:28 Adriano, Mark (Nokia - PH/Quezon City) New Correction document Correction for LTE_TOOL LTE_TOOL has been created.', '2018-03-12 10:26 Adriano, Mark (Nokia - PH/Quezon City) edited. Changed field(s): Development Fault Coordinator', '2018-03-12 04:47 Shen, Emma (NSB - CN/Hangzhou) Problem Report created'], 'State': ['Closed'], 'State Changed to Correction not needed': [''], 'State Changed to Closed': ['22 Mar 2018'], 'Reported Date': ['12 Mar 2018'], 'Attached PRs': ['PR328510', 'PR327942', 'PR327543'], 'Implementation Group': ['RABLTEWTS'], 'Author Group': ['LTE_DEVHZ5_CHZ_FV'], 'Reason Why Correction is Not Needed': ['']}

    rawdata = []
    with open(raw_file,'r') as fp:
        for line in fp.readlines():
            if line.strip():
                rawdata.append(eval(line.strip()))
                
    title = rawdata[0].keys()
    data = [['' for i in range(len(rawdata))] for j in range(len(title))]
    for j in range(len(rawdata)):
        for i in range(len(title)):
            data[i][j] = rawdata[j][title[i]]
    # print data
    generate_html('VIEW643997',data,title)



