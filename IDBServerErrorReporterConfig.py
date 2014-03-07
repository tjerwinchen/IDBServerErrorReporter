# -*- coding: utf-8 -*-

__author__ = 'theochen'

class DefaultConfig(object):

    # Mail --------------------------------------------------------------
    # SMTP server, e.g. "mail.provider.com" (None to disable mail)
    mail_smarthost = u'smtp.qiye.163.com'

    # The return address, e.g u"IDB Wiki <noreply@mywiki.org>" [Unicode]
    mail_from = u'theo.chen@sumscope.com'

    # "user pwd" if you need to use SMTP AUTH
    auth_user = u'theo.chen@sumscope.com'
    auth_passwd = u'xxxxxx'

    mail_receiptants = [u'theo.chen@sumscope.com',]

    # Location of error log file
    path_for_log_file = u'D:\\svn\\Tools\\IDBServerErrorReporter\\catalina.out'

    # The line number from last scanned
    last_scanned_number_in_record = 0

    # The size of log file last time checked
    size_for_log_file_in_record = 0
    # The created time of log file last time checked
    log_file_last_created_time_in_record = 0


# DEVELOPERS! Do not add or change your configuration items there,
# you could accidentally commit them! Instead, create a
# IDBServerErrorReporterConfig_Local.py file containing this:
#
# from IDBServerErrorReporterConfig import DefaultConfig
#
# class LocalConfig(DefaultConfig):
#     configuration_item_1 = 'value1'
#

try:
    from IDBServerErrorReporterConfig_Local import Config
except ImportError, err:
    if not str(err).endswith('IDBServerErrorReporterConfig_Local'):
        raise
    Config = DefaultConfig
