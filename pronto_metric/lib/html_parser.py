#! /usr/bin/env python
# -*- coding: utf-8

from variables import *
import os,sys
from HTMLParser import HTMLParser  # python standard library，解析HTML的工具，使用时一般继承这个类然后重载它的方法，用来从HTML内容里解析出自己想要的数据

"""
    解析网页HTML内容里的Table表格里的data
    <table>   表格
    <tr>      表格中的一行        table row
    <th>      表格中的一个单元格  table header   加粗显示,一般是表格的第一行表头采用<th> xxx </th>
    <td>      表格中的一个单元格  table data     一般是表格的内容行采用<td> xxx </td>

    <table></table>之间有多少个<tr></tr>,这个表格就有多少行;<tr></tr>之间有多少个<td></td>或者<th></th>,这个表格就有多少列
"""

class TableParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self._current_header = None
        self._current_data = None
        self._current_row = []

        self._header = []
        self._data = []
        self._rows = []

        self._table = []   # 二维列表，第1个元素是表头,接下来每个元素是一行
        self._result = []

    def handle_starttag(self,tag,attrs):
        if tag == 'th':
            self._current_header = ''
        if tag == 'td':
            self._current_data = ''
        if tag == 'br' or 'BR':
            if self.lasttag == 'th' and self._current_header != None:
                self._current_header += LINE_BREAK_TAG
            elif self.lasttag == 'td' and self._current_data != None:
                self._current_data += LINE_BREAK_TAG
        if tag == 'a' and attrs[0][-1].find('prid=') != -1:     # 专门解析超链接格式的PR ID的
            pr_id = attrs[0][-1].split('=')[-1].strip()
            if self._current_data != None:
                self._current_data += pr_id

    def handle_data(self,data):

        if data != None and len(data.strip()) > 0:
            if type(data) == unicode:
                data = str(data)         # 这里"<"和">"的type是unicode的，不支持，只支持ascii，也就是<type 'str'>，要转换一下

            if self.lasttag == 'th':
                self._current_header += data.strip()
            elif self.lasttag == 'td':
                self._current_data += data.strip()

    def handle_endtag(self,tag):
        if tag == 'th':
            current_header = self._current_header.strip()
            if current_header in self._header:
                current_header = current_header + '_2'
            self._header.append(current_header)
            self.current_header = None
        if tag == 'td':
            #print '***************************'
            #print self._current_data
            #print '***************************'
            if LINE_BREAK_TAG in self._current_data:
                self._current_data = self._current_data.split(LINE_BREAK_TAG)    # 很多内容中间有换行另起一行,转成一个列表

            if isinstance(self._current_data, str):   # 如果没有换行，它还是字符串类型
                self._current_data = self._current_data.strip()
            else:
                self._current_data = [x.strip() for x in self._current_data]
            self._current_row.append(self._current_data)
            self._current_data = None
        if tag == 'tr':
            if self.lasttag == 'th':
                self._table.append(self._header)
            if self._current_row != []:
                self._table.append(self._current_row)     # 一行内容收集结束
                self._current_row = []
        #if tag == 'table':
        #    return self._table

    '''
    有些显示出来的内容就有<BR>,&,所以得特殊处理

    # handle_entityref()处理字符实体，比如HTML里"<"写成"&lt"
    # html_parser.unescape() 将HTML转义字符转成正常字符; cgi模块的cgi.escape()是将正常字符转为转义字符
    '''
    def handle_entityref(self,ref):
        if ref.strip() in ['lt','gt','nbsp']:   # view页面里的&开头的转义字符目前只遇到这3个
            self.handle_data(HTMLParser.unescape(self,'&{};'.format(ref)))
        elif ref.strip() == 'D':
            pass
            # 表头有一列名是"R&D Information",如果不做任何处理,列名就会变为"Information"

    '''
    handle_charref()处理特殊字符串，一般就是以"&#"开头的,内码表示的，比如"&#039;"是指" ' "单引号
    '''
    def handle_charref(self,ref):
        self.handle_data(HTMLParser.unescape(self,'&#{};'.format(ref)))

    '''
    所有的解析都完成后，生成的self._header和self._rows里有很多空行，空列表和空元素，需要对self._result做处理
    '''
    def HandleAfterFeed(self):
        self._table[0] = self._table[0][1:]    # 表头第一个单元格是<BR>，删掉
        self._table[0] = [x[4:] for x in self._table[0]]

        if 'RInformation' in self._table[0]:  # 合法的列数一共是14个
            self._table[0][self._table[0].index('RInformation')] = r'R&D Information'

        tmptable = []
        for i in self._table:
            if self._table.index(i) > 0:
                i = i[1:]               # 每一行的第一个单元格也是空列表  ['', '']
                i = [x[1:] for x in i]  # 其余每一个元素列表的第一个元素也是'',删掉
                tmptable.append(i)
        tmptable.insert(0,self._table[0])
        self._table = tmptable   # 最终生成的table除了第一行表头，其它的每一行的每个单元格都是list格式,后面处理时要注意

        counter = 1
        for time in range(len(self._table[1:])):
            tmp_pr_dict = {}
            for i in range(len(self._table[0])):
                tmp_pr_dict[self._table[0][i]] = self._table[counter][i]
            self._result.append(tmp_pr_dict)
            counter += 1

        return True


if __name__ == "__main__":
    pass
    """
    html = open(r'D:\userdata\erjiang\Desktop\test.html').read()
    f = TableParser()
    f.feed(html)
    f.HandleAfterFeed()
    print len(f._result)
    for i in f._result:
        print i
        print '----------------------------'
    """



















