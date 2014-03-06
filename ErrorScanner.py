# -*- coding: utf-8 -*-
from IDBServerErrorReporterConfig import Config

__author__ = 'theochen'

import re

class ErrorScanner(object):
    def __init__(self):
        self.error_text = u''
        self.error_html = u''
        self.last_scanned_number_in_record = 0
        self.error_count = 0

    def scanning_error(self):
        # Open a file
        f = open(Config.path_for_log_file, 'r')
        try:
            self.line_number_scanned = 0
            while True:
                # We get the each line in the log file, furthermore,
                # considering it may have Chinese characters, we also need to decode it to utf-8
                line_str = f.next().decode('utf-8')
                self.line_number_scanned += 1

                # Bypass the already scanned lines
                if self.line_number_scanned <= self.last_scanned_number_in_record:
                    continue

                # Check whether current output line has any error
                self.check_error(line_str, f)


                #print last_scanned_line
        except StopIteration:
            #print self.error_text
            #print self.error_html
            print u'Find %d new errors' % self.error_count

        f.close()


    def check_error(self, line_str, file):
        # Case 1: Error with 'ERROR'
        if line_str.find(' ERROR ') != -1:
            self.error_count += 1
            self.error_text += u'--- Error %d ---\n' % self.error_count
            self.error_text += u'Line %d: %s' % (self.line_number_scanned, line_str)

            self.error_html += '''<hr><h3>Error %d:</h3>''' % self.error_count
            self.error_html += '''<table><tr><td>Line %d: &nbsp;&nbsp; %s</tr></td></table>''' % (self.line_number_scanned, line_str)

            #print self.line_number_scanned, line_str

        # Case 2: Error with Java Exception
        elif self.is_java_exception_header(line_str):
            # If the line string is a Java Exception
            # We will get all the Exception

            #print self.line_number_scanned, line_str

            self.error_count += 1
            self.error_text += u'--- Error %d ---\n' % self.error_count
            self.error_text += u'Line %d: %s' % (self.line_number_scanned, line_str)

            self.error_html += u'''<hr><h3>Error %d:</h3>''' % self.error_count
            self.error_html += u'''<table><tr><td>Line %d: &nbsp;&nbsp; %s''' % (self.line_number_scanned, line_str)

            line_str = self.pickup_java_exception_body(file) # line_str is the last line without Java Exception

            self.error_html += u'''</tr></td></table>'''

            # We need check whether line_str is a type of error recursively
            self.check_error(line_str, file)


    def is_java_exception_header(self, text):
        '''
        This method will to check whether a string is a Java Exception string via regular expression.
        True for yes
        False for not
        '''
        pattern = re.compile('.\w*Exception[^a-zA-Z0-9.=]')

        match = pattern.search(text)
        #if match != None:
        #    print '--- for debug ---\n', match.group()

        return match != None

    def pickup_java_exception_body(self, file):
        '''
        This method will pickup the contents of Java Exception
        '''
        line_str = file.next().decode('utf-8')
        self.line_number_scanned += 1
        while line_str.strip().find('at ') == 0:
            self.error_text += u'Line %d: %s' % (self.line_number_scanned, line_str)

            self.error_html += u'''<br>Line %d: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; %s''' % (self.line_number_scanned, line_str)

            line_str = file.next().decode('utf-8')
            self.line_number_scanned += 1

        return line_str

