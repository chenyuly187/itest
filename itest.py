# -*- coding: utf-8 -*-
import sys
import getopt
import json
from settings import *
import datetime
from utils.tests import RestTest, SocketTest
from utils.filereader import YamlReader
from utils.binding import Context
import string
import unittest
from utils.exceptions import FileTypeNotSupportException

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
                    print(usage)
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
                    print(usage)
        except getopt.error as msg:
            print(msg)
            print(usage)
            sys.exit(0)


##################################################
#                    test
##################################################
testcases = []


class JsonParser(object):
    def __init__(self, testfile):
        self.testfile = testfile
        self.project = ''
        self.api_type = ''
        self.desc = ''

    def parse(self):
        with open(self.testfile, 'rb') as fp:
            parsed = json.load(fp=fp)

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
            ip = parsed.get('ip', '127.0.0.1')
            port = parsed.get('port', 3000)
            for test in tests:
                case = test.get('case', 'Unnamed')
                case_desc = test.get('desc', '')
                logger.debug('case: %s, desc: %s' % (case, case_desc))
                # setup teardown test method
                setup = test.get('setup')
                teardown = test.get('teardown')
                tcase = test.get('test')

                r = SocketTest(name=case, desc=case_desc, ip=ip, port=port, test=tcase, setup=setup, teardown=teardown)
                testcases.append(r)
        else:
            pass


def flatten_dictionaries(input):
    """ 将一个列表中的字典合成一个字典，如果传入的不是一个列表，则直接返回 """
    output = dict()
    if isinstance(input, list):
        for map in input:
            output.update(map)
    else:  # Not a list of dictionaries
        output = input
    return output


def lowercase_keys(input_dict):
    """ 如果传入字典，则将字典中的所有key转为str并降为小写 """
    if not isinstance(input_dict, dict):
        return input_dict
    safe = dict()
    for key, value in input_dict.items():
        safe[str(key).lower()] = value
    return safe


def safe_substitute_template(template_string, variable_map):
    """ 用 string.Template 的 safe_substitute 方法将传入的模板string 使用 variable_map进行解析，替换模板变量，返回str """

    my_template = string.Template(template_string)
    my_escaped_dict = dict(map(lambda x: (x[0], x[1]), variable_map.items()))
    templated = my_template.safe_substitute(my_escaped_dict)
    return templated


class YamlParser(object):
    def __init__(self, testfile):
        self.parsed = YamlReader(testfile).yaml
        self.project = ''
        self.desc = ''
        self.api_type = 'http'
        self.ip = ''
        self.port = ''
        self.context = Context()

    def parse(self):
        proj_data = lowercase_keys(flatten_dictionaries(lowercase_keys(self.parsed.pop(0)[0]).get('project')))
        # print(proj_data)
        self.project = proj_data.get('name')
        self.desc = proj_data.get('desc')
        self.api_type = proj_data.get('type')
        # debug
        logger.debug('project: %s, desc: %s, type: %s' % (self.project, self.desc, self.api_type))

        bindings = proj_data.get('bindings')
        if bindings:
            self.context.bind_variables(bindings)

        for suite in self.parsed:
            suite_data = lowercase_keys(flatten_dictionaries(lowercase_keys(suite.pop(0)).get('suite')))
            suite_name = suite_data.get('name')
            suite_desc = suite_data.get('desc')
            suite_skip = suite_data.get('skip')
            # debug
            logger.debug('suite : %s, desc: %s, skip: %s' % (suite_name, suite_desc, suite_skip))
            if suite_skip:
                continue

            test_suite = unittest.TestSuite()  # test suite definition

            for case in suite:
                # print(case)
                # todo case parse
                case_data = list()
                steps = list()
                for item in lowercase_keys(case).get('testcase'):
                    if list(item.keys())[0].lower() != 'step':
                        case_data.append(lowercase_keys(item))
                    else:
                        steps.append(flatten_dictionaries(lowercase_keys(item).get('step')))
                case_data = flatten_dictionaries(case_data)
                # print('case_data: %s' % case_data)
                # print('step %s' % steps)

                case_name = case_data.get('name')
                case_desc = case_data.get('desc')
                case_skip = case_data.get('skip')
                # debug
                logger.debug('case: %s, desc: %s, skip: %s' % (case_name, case_desc, case_skip))

                if case_skip:
                    continue

                sorted_test = list()
                sorted_setup = list()
                sorted_teardown = list()

                for step in steps:
                    # print(step)
                    step_name = step.get('name', 'unnamed')
                    step_type = step.get('type', 'step')
                    step_url = step.get('url')  # can be template
                    if isinstance(step_url, dict):
                        step_url = safe_substitute_template(step_url['template'], self.context.get_values())
                    step_method = step.get('method')
                    step_params = step.get('params')
                    step_data = step.get('data')
                    step_validators = step.get('validators')
                    step_resource = step.get('resource')
                    if step_resource:
                        step_resource = flatten_dictionaries(step_resource)

                    sorted_step = {
                        'name': step_name,
                        'url': step_url,
                        'method': step_method,
                        'params': step_params,
                        'data': step_data,
                        'validators': step_validators,
                        'resource': step_resource
                    }
                    if step_type.lower() == 'step':
                        sorted_test.append(sorted_step)
                    elif step_type.lower() == 'setup':
                        sorted_setup.append(sorted_step)
                    elif step_type.lower() == 'teardown':
                        sorted_teardown.append(sorted_step)

                if self.api_type in ('http', 'rest', 'restful'):
                    r = RestTest(name=case_name, test=sorted_test, desc=case_desc, setup=sorted_setup, teardown=sorted_teardown)
                    test_suite.addTest(r)
                elif self.api_type in ('tcp', 'socket'):
                    self.ip = proj_data.get('ip')
                    self.port = proj_data.get('port')
                    s = SocketTest(name=case_name, test=sorted_test, ip=self.ip, port=self.port, desc=case_desc, setup=sorted_setup, teardown=sorted_teardown)
                    test_suite.addTest(s)

            testcases.append(test_suite)


class Runner(object):
    def __init__(self, project, api_type='http', desc='', runner='text', path=BASE_DIR, report=''):
        self.title = '%s 测试报告' % project
        self.desc = '测试类型：%s， 项目描述：%s' % (api_type, desc)
        self.runner = runner
        self.path = path
        self.report = report

    def run(self, tests):
        import unittest
        suite = unittest.TestSuite()
        suite.addTests(tests)
        if self.runner == 'text':
            unittest.TextTestRunner(verbosity=2).run(suite)
        elif self.runner == 'web':
            from utils.HTMLTestRunner import HTMLTestRunner
            if self.report:
                with open(self.path + '\\report\\' + u'\{0}_{1}.html'.format(self.report, datetime.datetime.now().strftime('%Y%m%d%H%M%S')),'wb') as stream:
                    HTMLTestRunner(stream=stream,
                                   title=self.title,
                                   description=self.desc,
                                   verbosity=2).run(suite)
            else:
                stream = sys.stdout
                HTMLTestRunner(stream=stream,
                               title=self.title,
                               description=self.desc,
                               verbosity=2).run(suite)


def main():
    argvs = sys.argv
    # argvs = ['itest.py', '-f', 'baidumap.yaml', '-w', '-r', 'baidumap']
    tp = TestProgram()
    tp.parse_args(argvs)

    if tp.testfile.split('.')[-1].lower() == 'json':
        parser = JsonParser(tp.testfile)
    elif tp.testfile.split('.')[-1].lower() in ['yaml', 'yml']:
        parser = YamlParser(tp.testfile)
    else:
        raise FileTypeNotSupportException('文件类型不支持解析，请传入json或yaml格式配置文件')

    parser.parse()

    Runner(project=parser.project,
           api_type=parser.api_type,
           desc=parser.desc,
           path=tp.path,
           report=tp.report,
           runner=tp.runner
           ).run(testcases)


if __name__ == '__main__':
    main()