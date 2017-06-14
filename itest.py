# -*- coding: utf-8 -*-
import sys
import getopt
import json
from settings import *
import datetime

logger = logging.getLogger('itest')

##################################################
#                    argv
##################################################
USAGE = """\
Usage: %(progname)s [options] [...]

Options:
  -h,  --help           Show this message

  -p,  --path          Path to run test
  -f,  --file          Test json file
  -r,  --report        Report name
  -t,  --text           TextTestRunner Report
  -w,  --web            HTMLTestRunner Report
Examples:
  %(progname)s -p E:\\itest -f itest.json -r itest_report.html
"""


class TestProgram(object):

    def __init__(self, path=BASE_DIR, testfile='itest.json', report='itest', runner='text'):
        self.path = path
        self.testfile = testfile
        self.report = report
        self.runner = runner
        logger.debug('================ Begin Test ================')

    def parse_args(self, argv):
        argv = argv
        progname = argv[0]
        long_opts = ['help', 'path=', 'file=', 'report=']
        usage = USAGE % {'progname': progname}
        try:
            options, args = getopt.getopt(argv[1:], 'hHp:f:r:tw', long_opts)
            for opt, value in options:
                if opt in ('-h', '-H', '--help'):
                    print usage
                elif opt in ('-p', '--path'):
                    self.path = value
                    logger.debug('Set path: %s' % self.path)
                elif opt in ('-f', '--file'):
                    if os.path.exists(self.path+value):
                        self.testfile = self.path+value
                    elif os.path.exists(value):
                        self.testfile = value
                    elif os.path.exists(BASE_DIR+'\\test\\'+value):
                        self.testfile = BASE_DIR+'\\test\\'+value
                    else:
                        raise getopt.error('File not found: %s' % value)
                    logger.debug('Set test file: %s' % self.testfile)
                elif opt in ('-r', '--report'):
                    self.report = value
                    logger.debug('Set report: %s' % self.report)
                elif opt in ('-t', '--text'):
                    self.runner = 'text'
                    logger.debug('Set TextTestRunner')
                elif opt in ('-w', '--web'):
                    self.runner = 'web'
                    logger.debug('Set HTMLTestRunner')
                else:
                    print usage
        except getopt.error, msg:
            print msg
            print usage
            sys.exit(0)


##################################################
#                    test
##################################################
from utils.tests import RestTest
testcases = []


class TestParser(object):
    def __init__(self, testfile):
        self.testfile = testfile
        self.project = ''
        self.api_type = ''
        self.desc = ''

    def parse(self):
        parsed = json.load(fp=file(self.testfile))

        try:
            self.project = parsed['project']
        except KeyError:
            raise KeyError('Key "project" is Required.')
        self.api_type = parsed.get('type', 'http').lower()
        self.desc = parsed.get('desc', '')
        # debug
        logger.debug('project: %s, desc: %s' % (self.project, self.desc))
        logger.debug('type: %s' % self.api_type)

        tests = parsed['tests']
        if self.api_type in ('http', 'rest', 'restful'):
            # RESTFul interface (HTTP protocol)
            base = parsed.get('base', '')
            if base:
                logger.debug('base: %s' % base)
            for test in tests:
                case = test.get('case', 'Unnamed')
                case_desc = test.get('desc', '')
                logger.debug('case: %s, desc: %s' % (case, case_desc))
                # setup teardown test method
                setup = test.get('setup')
                teardown = test.get('teardown')
                tcase = test.get('test')

                r = RestTest(name=case, desc=case_desc, base=base, test=tcase, setup=setup, teardown=teardown)
                testcases.append(r)
        elif self.api_type in ('tcp', 'socket'):
            # socket interface (TCP protocol)
            pass
        else:
            pass


class Runner(object):
    def __init__(self, project, api_type='http', desc='', runner='text', path=BASE_DIR, report=''):
        self.title = u'%s 测试报告' % project
        self.desc = u'测试类型：{1}，    项目描述：{2}'.format(project, api_type, desc)
        self.runner = runner
        self.path = path
        self.report = report

    def run(self, tests):
        import unittest2
        suite = unittest2.TestSuite()
        suite.addTests(tests)
        if self.runner == 'text':
            unittest2.TextTestRunner(verbosity=2).run(suite)
        elif self.runner == 'web':
            from utils.HTMLTestRunner import HTMLTestRunner, stdout_redirector
            stream = file(
                self.path + '\\report\\' + u'\{0}_{1}.html'.format(self.report, datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
                'wb') if self.report else sys.stdout
            HTMLTestRunner(stream=stream,
                           title=self.title,
                           description=self.desc,
                           verbosity=2).run(suite)


if __name__ == '__main__':
    argvs = sys.argv
    # argvs = ['itest.py', '-f', 'baidumap.json', '-t', '-r', 'baidumap']
    tp = TestProgram()
    tp.parse_args(argvs)

    parser = TestParser(tp.testfile)
    parser.parse()

    Runner(project=parser.project,
           api_type=parser.api_type,
           desc=parser.desc,
           path=tp.path,
           report=tp.report,
           runner=tp.runner
           ).run(testcases)

