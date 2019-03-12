#! /usr/bin/env python
# -*- coding: utf-8
import logging,time,os

"""
   logging模块的日志级别有5种,默认对应的数字值如下：
      DEBUG           10     调试信息
      INFO            20     有用信息      证明程序还在按流程运行
      WARNING(默认)   30     警告信息      有意外，但程序仍旧能正常工作
      ERROR           40     错误信息      有错误，程序的部分功能可能不能正常运行了
      CRITICAL        50     严重错误信息  整个程序都可能无法正常运行了
   设置了日志的level后，低于这个level的信息就不会输出

   logging模块里的几个重要的概念：
      Logger     记录器      一个log实例,接口,用来按设置的level记录日志
      Handler    处理器      将Logger记录的日志发送到指定的地方，如StreamHandler ，FileHandler...很多种
      Filter     过滤器      粒度控制，决定输出哪些日志
      Formatter  格式化器    配置日志内容输出的格式布局等

   %(levelno)s: 打印日志级别的数值
   %(levelname)s: 打印日志级别名称
   %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
   %(filename)s: 打印当前执行程序名
   %(funcName)s: 打印日志的当前函数
   %(lineno)d: 打印日志的当前行号
   %(asctime)s: 打印日志的时间
   %(thread)d: 打印线程ID
   %(threadName)s: 打印线程名称
   %(process)d: 打印进程ID
   %(message)s: 打印日志信息

   %(module)s   处于哪个py文件
   %(lineno)s


"""

filename = 'ProntoLog_%s.log'%(time.strftime("%Y%m%d_%H-%M-%S",time.localtime(time.time())))

path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'log',filename)

def setup_logger(filename=path, loggername='pronto_logger', console=logging.INFO):
    logger = logging.getLogger(loggername)   # logger对象不是直接实例化的,而是调用一个module级别的函数getLogger()实现
    logger.setLevel(logging.DEBUG)          # 设置日志对象的级别,>=该level的才能输出,必须显式设置这一步,否则什么级别的log都无法输出,DEBUG是最低级别

    formatter = logging.Formatter('%(asctime)s %(levelname)s:   %(module)s@%(lineno)s:  %(message)s','%H:%M:%S')   # 输出log消息的格式,\t代表空格

    ch = logging.StreamHandler()  # logging.StreamHandler()意思是输出日志到流上,流可以是sys.stdout,sys.stderr或文件，没有参数默认是输出到console控制台上
    ch.setLevel(console)          # 控制台的级别是INFO
    ch.setFormatter(formatter)    # 控制台的格式
    logger.addHandler(ch)

    fh = logging.FileHandler(filename, mode='w')  # logging.FileHandler()用于写入log文件(不给绝对路径,默认就是当前工作目录)  mode是文件的打开方式,'w'是覆盖,默认是'a'是追加
    fh.setLevel(logging.DEBUG)    # log文件的显示级别是DEBUG
    fh.setFormatter(formatter)    # 文件采用同样的格式
    logger.addHandler(fh)

    return logger

