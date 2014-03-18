# -*- coding: utf-8 -*-
import os
from stat import *
import time
import ntpath
from ErrorScanner import ErrorScanner
from IDBServerErrorReporterConfig import Config
from MailSender import MailSender
#from watchdog.observers import Observer
#from watchdog.events import PatternMatchingEventHandler

__author__ = 'theochen'

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def path_root(path):
    head, tail = ntpath.split(path)
    return head

def read_config_from_file():
    '''
    Get the the last time scanned line number from the file
    '''
    f = open('config.ini', 'r')
    ret_val = []
    s = f.readline().strip('get_last_scanned_number_in_record=').strip()
    ret_val.append(int(s))
    s = f.readline().strip('size_for_log_file_in_record=').strip()
    ret_val.append(int(s))
    s = f.readline().strip('log_file_last_created_time_in_record=').strip()
    ret_val.append(int(s))
    f.close()

    return ret_val

def write_config_to_file():
    '''
    Write back the latest line number scanned to the file
    '''
    f = open('config.ini', 'w')
    f.write(u'get_last_scanned_number_in_record=%d\n' % Config.last_scanned_number_in_record)
    f.write(u'size_for_log_file_in_record=%d\n' % Config.size_for_log_file_in_record) # The size of log file last time checked
    f.write(u'log_file_last_created_time_in_record=%d\n' % Config.log_file_last_created_time_in_record) # The created time of log file last time checked
    f.close()


def start_reporter():
    print '--- Start Scanning --- '
    print 'From line number %d ' % Config.last_scanned_number_in_record

    # Scanning error, and constructing error text
    scanner = ErrorScanner()
    scanner.last_scanned_number_in_record = Config.last_scanned_number_in_record
    scanner.scanning_error()

    if scanner.error_count > 0:
        print '------------------------- Sending Mail ------------------------'
        # Sending error text
        mail_sender = MailSender()
        mail_sender.sending_email(scanner)

    # Store the last scanned line number
    Config.last_scanned_number_in_record = scanner.line_number_scanned

    print '--- End Scanning ---'
    print 'Last line number %d' % (Config.last_scanned_number_in_record + 1)
    write_config_to_file()


"""
def start_file_observer(file_path):
    '''
    Check whether the log file has been modified
    '''
    print u'Monitoring %s' % path_leaf(Config.path_for_log_file)
    # We only need to monitor the file *catalina.out
    event_handler = MyHandler(patterns=["*%s" % path_leaf(Config.path_for_log_file)], ignore_directories=True)
    #event_handler = MyHandler(patterns=["*.txt", ], ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, path_root(Config.path_for_log_file), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
"""

def start_file_observer(file_path):
    print u'Monitoring %s' % path_leaf(Config.path_for_log_file)
    handler = MyHandler()
    while True:
        handler.check_file_info()
        time.sleep(10)

#class MyHandler(PatternMatchingEventHandler):
class MyHandler(object):
    def __init__(self, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        #PatternMatchingEventHandler.__init__(self, patterns, ignore_patterns, ignore_directories, case_sensitive)
        pass

	
	def on_any_event(event):
		print event		

    def on_modified(self, event):
        print event
        if event.src_path == Config.path_for_log_file:
            time.sleep(5)
            self.check_file_info()


    def check_file_info(self):
        try:
            st = os.stat(Config.path_for_log_file)
            print Config.path_for_log_file

        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except WindowsError as e:
            print "WindowsError error({0}): {1}".format(e.errno, e.strerror)
        except Exception as e:
            print "Unknown error({0}): {1}".format(e.errno, e.strerror)
        else:
            if st[ST_SIZE]/1024/1024/1024 > 0:
                filesize = u'file size: %.2f GB' % (st[ST_SIZE]/1024.0/1024.0/1024.0)
            elif st[ST_SIZE]/1024/1024 > 0:
                filesize = u'file size: %.2f MB' % (st[ST_SIZE]/1024.0/1024.0)
            elif st[ST_SIZE]/1024 > 0:
                filesize = u'file size: %.2f KB' % (st[ST_SIZE]/1024.0)
            else:
                filesize = u'file size: %d B' % st[ST_SIZE]

            # 首先，查看create time whether changed, if changed, we should rescan the whole log file
            if st[ST_CTIME] < Config.log_file_last_created_time_in_record:
                print u'file recreated:', time.asctime(time.localtime(st[ST_CTIME]))
                print filesize
                Config.last_scanned_number_in_record = 0 # 要从0行开始扫描
                Config.log_file_last_created_time_in_record = st[ST_MTIME]
                Config.size_for_log_file_in_record = 0 # Size重新记为0
                start_reporter()
            # 如果Size发生了变化，我们认为，文件是真正发生了改变化
            elif st[ST_SIZE] > Config.size_for_log_file_in_record:
                print u'file modified:', time.asctime(time.localtime(st[ST_MTIME]))
                print filesize
                Config.size_for_log_file_in_record = st[ST_SIZE]
                start_reporter()

        print u'file recreated:', time.asctime(time.localtime(st[ST_CTIME]))
        print u'file modified:', time.asctime(time.localtime(st[ST_MTIME]))
        print u'file size', st[ST_SIZE]
        Config.log_file_handler = open('log.txt', 'a')
        Config.log_file_handler.write(u'file recreated: %s\n'  % time.asctime(time.localtime(st[ST_CTIME])) )
        Config.log_file_handler.write(u'file modified: %s\n' % time.asctime(time.localtime(st[ST_MTIME])))
        Config.log_file_handler.write(u'file size %s\n' % st[ST_SIZE])
        Config.log_file_handler.close()





if __name__ == '__main__':

    # 初始化
    # Get the last scanned number recorded in file when program start
    values = read_config_from_file()
    Config.last_scanned_number_in_record = values[0]
    Config.log_file_last_created_time_in_record = values[1]
    Config.size_for_log_file_in_record = values[2]

    # If log file has been modified, we need to scanning the error report
    start_file_observer(Config.path_for_log_file)


