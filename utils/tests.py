# -*- coding: utf-8 -*-
import unittest
from unittest.case import _ShouldStop
from utils.client import HTTPClient, TCPClient
from settings import *
from utils.filereader import ExcelReader
from utils.exceptions import DataFileNotAvailableException
import contextlib
import collections
import json
import re

logger = logging.getLogger('itest')


class Test(unittest.TestCase):
    def __init__(self, name, test, desc='', setup=None, teardown=None):
        super(Test, self).__init__(methodName='test_case')
        self.name = name
        self.desc = desc
        self.setup = setup
        self.test = test
        self.teardown = teardown
        # validator map
        self.validators = {
            "in": self.assertIn,
            "eq": self.assertEqual,
            "ls": self.assertLess,
            "lq": self.assertLessEqual,
            "not_in": self.assertNotIn,
        }

        self._testMethodDoc = desc

    def setUp(self):
        """自定义类中的setUpClass函数，每个Test调用"""
        logger.debug('---------- Start Test %s ----------' % self.name)

    def tearDown(self):
        """自定义类中的tearDownClass函数，每个Test调用"""
        logger.debug('---------- End Test %s ----------' % self.name)

    def before(self):
        """自定义类中的setUp函数，每个sub-Test都会调用"""
        pass

    def after(self):
        """自定义类中的tearDown函数，每个sub-Test都会调用"""
        pass

    def test_case(self):
        """自定义类中的用例函数，需要在此函数中显式调用before和after"""
        pass

    def id(self):
        return "%s" % self._testMethodName

    def __str__(self):
        return "%s" % self.name

    @contextlib.contextmanager
    def subTest(self, msg=None, **params):
        """Return a context manager that will return the enclosed block
        of code in a subtest identified by the optional message and
        keyword parameters.  A failure in the subtest marks the test
        case as failed but resumes execution at the end of the enclosed
        block, allowing further test code to be executed.
        """
        if not self._outcome.result_supports_subtests:
            yield
            return
        parent = self._subtest
        if parent is None:
            params_map = collections.ChainMap(params)
        else:
            params_map = parent.params.new_child(params)
        self._subtest = _SubTest(self, msg, params_map)
        try:
            with self._outcome.testPartExecutor(self._subtest, isTest=True):
                yield
            if not self._outcome.success:
                result = self._outcome.result
                if result is not None and result.failfast:
                    raise _ShouldStop
            elif self._outcome.expectedFailure:
                # If the test is expecting a failure, we really want to
                # stop now and register the expected failure.
                raise _ShouldStop
        finally:
            self._subtest = parent

    def _feedErrorsToResult(self, result, errors):
        for test, exc_info in errors:
            if isinstance(test, _SubTest):
                result.addSubTest(test.test_case, test, exc_info)
            elif exc_info is not None:
                if issubclass(exc_info[0], self.failureException):
                    result.addFailure(test, exc_info)
                else:
                    result.addError(test, exc_info)


class _SubTest(Test):

    def __init__(self, test_case, message, params):
        super(_SubTest, self).__init__(name=test_case.name, desc=test_case.desc, test=test_case,
                                       setup=test_case.setup, teardown=test_case.teardown)
        self._message = message
        self.test_case = test_case
        self.params = params
        self.failureException = test_case.failureException

    def runTest(self):
        raise NotImplementedError("subtests cannot be run directly")

    def _subDescription(self):
        parts = []
        if self._message:
            parts.append("[{}]".format(self._message))
        if self.params:
            params_desc = ', '.join(
                "{}={}".format(k, v)
                for (k, v) in sorted(self.params.items()))
            parts.append("({})".format(params_desc))
        return " ".join(parts) or '(<subtest>)'

    def id(self):
        return u"{0} {1}".format(self.test_case.id(), self._subDescription())

    def shortDescription(self):
        """Returns a one-line description of the subtest, or None if no description has been provided."""
        return self.test_case.shortDescription()

    def __str__(self):
        return u"{0} {1}".format(str(self.test_case), self._subDescription())


class RestTest(Test):
    def __init__(self, name, test, base='', desc='', setup=None, teardown=None):
        super(RestTest, self).__init__(name=name, test=test, desc=desc, setup=setup, teardown=teardown)
        self.base = base

    def before(self):
        # setUp method
        if self.setup:
            for step in self.setup:
                step_url = step.get('url')
                if not step_url:
                    continue
                step_method = step.get('method', 'GET')
                step_headers = step.get('headers')
                step_params = step.get('params')
                step_data = step.get('data')
                # debug
                logger.debug('setup url: %s' % step_url)
                logger.debug('setup method: %s' % step_method)
                if step_headers:
                    logger.debug('setup headers: %s' % step_headers)
                if step_params:
                    logger.debug('setup params: %s' % step_params)
                if step_data:
                    logger.debug('setup data: %s' % step_data)

                HTTPClient(url=step_url, method=step_method, headers=step_headers).send(params=step_params,
                                                                                        data=step_data)

    def after(self):
        # tearDown method
        if self.teardown:
            for step in self.teardown:
                step_url = step.get('url')
                if not step_url:
                    continue
                step_method = step.get('method', 'GET')
                step_headers = step.get('headers')
                step_params = step.get('params')
                step_data = step.get('data')
                # debug
                logger.debug('teardown url: %s' % step_url)
                logger.debug('teardown method: %s' % step_method)
                if step_headers:
                    logger.debug('teardown headers: %s' % step_headers)
                if step_params:
                    logger.debug('teardown params: %s' % step_params)
                if step_data:
                    logger.debug('teardown data: %s' % step_data)

                HTTPClient(url=step_url, method=step_method, headers=step_headers).send(params=step_params,
                                                                                        data=step_data)

    def test_case(self):
        for step in self.test:
            step_url = self.base + step.get('url')
            if not step_url:
                continue
            step_method = step.get('method', 'GET')
            step_headers = step.get('headers')
            # debug
            logger.debug('test url: %s' % step_url)
            logger.debug('test method: %s' % step_method)
            if step_headers:
                logger.debug('test headers: %s' % step_headers)

            step_params = step.get('params')  # GET params
            step_data = step.get('data')  # POST data

            step_resource = step.get('resource')  # multi-lines in excel, each is a sub-case
            if step_resource:  # use excel as resource file
                rfile = step_resource.get('file')
                if os.path.exists(rfile):
                    rfile = rfile
                elif os.path.exists(BASE_DIR + '\\data\\' + rfile):
                    rfile = BASE_DIR + '\\data\\' + rfile
                else:
                    raise DataFileNotAvailableException('File not found: %s' % rfile)
                rsheet = step_resource.get('sheet', 0)
                rstart = step_resource.get('start', 0)
                rend = step_resource.get('end')

                rdata = ExcelReader(rfile, rsheet).data
                rstart = rstart - 1 if rstart > 0 else 0
                if rend and len(rdata) >= rend:
                    rdata = rdata[rstart: rend]
                else:
                    rdata = rdata[rstart:]

                # debug
                logger.debug('resource: %s' % str(step_resource))
                logger.debug('excel data: %s' % str(rdata))

                for num, line in enumerate(rdata):
                    with self.subTest(msg='SubTest_%d' % (num+1), data=line):  # SubTest
                        logger.debug('---------- SubTest %d ----------' % (num+1))  # debug
                        sub_params = {}
                        sub_data = {}
                        if step_params:
                            for p, v in step_params.items():
                                if '$resource' in str(v):
                                    sub_params[p] = line.get(v[10:])
                                else:
                                    sub_params[p] = v
                            logger.debug('test params: %s' % sub_params)  # debug
                        if step_data:
                            for d, vl in step_data.items():
                                if '$resource' in str(vl):
                                    sub_data[d] = line.get(vl[10:])
                                else:
                                    sub_data[d] = vl
                            logger.debug('test data: %s' % sub_data)  # debug
                        # test
                        self.before()
                        print('[url]\n%s' % step_url)
                        print('[send]\n%s' % (sub_params or sub_data))
                        res = HTTPClient(url=step_url, method=step_method, headers=step_headers).send(
                            params=sub_params, data=sub_data)
                        print('[receive]\n %s' % res.content.decode())

                        # validate
                        step_validators = step.get('validators')
                        if step_validators:
                            for vtype, vvalue in step_validators.items():
                                asserts = []
                                if vtype in self.validators:
                                    if isinstance(vvalue, list):
                                        for vv in vvalue:
                                            if '$resource' in vv:
                                                asserts.append(line.get(vv[10:]))
                                            elif '$res' in vv:
                                                asserts.append(res.content)
                                            else:
                                                asserts.append(vv)
                                    else:
                                        if '$resource' in vvalue:
                                            asserts = [line.get(vvalue[10:]), res.content]
                                    logger.debug('assert %s %s %s' % (asserts[0], vtype, str(asserts[1]).strip()[:20]))
                                    if isinstance(asserts[0], str) and isinstance(asserts[1], str):
                                        self.validators[vtype](asserts[0].encode(), asserts[1].encode())
                                    elif isinstance(asserts[0], str):
                                        self.validators[vtype](asserts[0].encode(), asserts[1])
                                    else:
                                        self.validators[vtype](asserts[0], asserts[1])

                        self.after()
            else:  # just use json data
                # debug
                if step_params:
                    logger.debug('test params: %s' % step_params)
                if step_data:
                    logger.debug('test data: %s' % step_data)
                # test
                self.before()
                # print('[url]\n%s' % step_url)
                # print('[send]\n%s' % (step_params or step_data))
                res = HTTPClient(url=step_url, method=step_method, headers=step_headers).send(params=step_params,
                                                                                              data=step_data)
                # print('[receive]\n %s' % res.content.decode())
                # validate
                step_validators = step.get('validators')
                if step_validators:
                    for vtype, vvalue in step_validators.items():
                        if vtype in self.validators:
                            if isinstance(vvalue, list):
                                for i, vv in enumerate(vvalue):
                                    if '$res' in str(vv):
                                        vvalue[i] = res.content
                            else:
                                if '$resource' in str(vvalue):
                                    vvalue = [vvalue, res.content]
                            logger.debug('assert %s %s %s' % (vvalue[0], vtype, str(vvalue[1]).strip()[:20]))
                            if isinstance(vvalue[0], str) and isinstance(vvalue[1], str):
                                self.validators[vtype](vvalue[0].encode(), vvalue[1].encode())
                            elif isinstance(vvalue[0], str):
                                self.validators[vtype](vvalue[0].encode(), vvalue[1])
                            else:
                                self.validators[vtype](vvalue[0], vvalue[1])

                self.after()


class SocketTest(Test):
    def __init__(self, name, test, ip='127.0.0.1', port=3030, desc='', setup=None, teardown=None):
        super(SocketTest, self).__init__(name=name, test=test, desc=desc, setup=setup, teardown=teardown)
        self.ip = ip
        self.port = port
        self.client = TCPClient(domain=self.ip, port=self.port)

    def tearDown(self):
        self.client.close()

    def test_case(self):
        for step in self.test:
            step_data = step.get('data', '')  # step data
            step_resource = step.get('resource')
            if step_resource:  # use excel as resource file
                rfile = step_resource.get('file')
                if os.path.exists(rfile):
                    rfile = rfile
                elif os.path.exists(BASE_DIR + '\\data\\' + rfile):
                    rfile = BASE_DIR + '\\data\\' + rfile
                else:
                    raise DataFileNotAvailableException('File not found: %s' % rfile)
                rsheet = step_resource.get('sheet', 0)
                rstart = step_resource.get('start', 0)
                rend = step_resource.get('end')

                rdata = ExcelReader(rfile, rsheet).data
                rstart = rstart - 1 if rstart > 0 else 0
                if rend and len(rdata) >= rend:
                    rdata = rdata[rstart: rend]
                else:
                    rdata = rdata[rstart:]

                # debug
                logger.debug('resource: %s' % str(step_resource))
                logger.debug('excel data: %s' % str(rdata))

                for num, line in enumerate(rdata):
                    with self.subTest(msg='SubTest_%d' % (num + 1), data=line):  # SubTest
                        logger.debug('---------- SubTest %d ----------' % (num + 1))  # debug
                        sub_data = step_data
                        if step_data:  # 用正则匹配里面的$resource.xxx$出来
                            pattern = re.compile('\$resource\.(.*?)\$')
                            for r in pattern.findall(step_data):
                                r1 = line.get(r)
                                if r1:
                                    sub_data = pattern.sub(r1, sub_data, 1)
                            logger.debug('test data: %s' % sub_data)  # debug
                        # test
                        res = self.client.send(sub_data)

                        # validate
                        step_validators = step.get('validators')
                        if step_validators:
                            for vtype, vvalue in step_validators.items():
                                asserts = []
                                if vtype in self.validators:
                                    if isinstance(vvalue, list):
                                        for vv in vvalue:
                                            if '$resource' in vv:
                                                asserts.append(line.get(vv[10:]))
                                            elif '$res' in vv:
                                                asserts.append(res)
                                            else:
                                                asserts.append(vv)
                                    else:
                                        if '$resource' in vvalue:
                                            asserts = [line.get(vvalue[10:]), res]

                                    logger.debug('assert %s %s %s' % (asserts[0], vtype, str(asserts[1]).strip()[:20]))
                                    if isinstance(asserts[0], str) and isinstance(asserts[1], str):
                                        self.validators[vtype](asserts[0].encode(), asserts[1].encode())
                                    elif isinstance(asserts[0], str):
                                        self.validators[vtype](asserts[0].encode(), asserts[1])
                                    else:
                                        self.validators[vtype](asserts[0], asserts[1])
            else:
                # debug
                if step_data:
                    logger.debug('test data: %s' % step_data)
                # test
                res = self.client.send(step_data)
                # validate
                step_validators = step.get('validators')
                if step_validators:
                    for vtype, vvalue in step_validators.items():
                        asserts = []
                        if vtype in self.validators:
                            if isinstance(vvalue, list):
                                for vv in vvalue:
                                    if '$resource' in vv:
                                        asserts.append(line.get(vv[10:]))
                                    elif '$res' in vv:
                                        asserts.append(res)
                                    else:
                                        asserts.append(vv)
                            else:
                                if '$resource' in vvalue:
                                    asserts = [line.get(vvalue[10:]), res]

                            logger.debug('assert %s %s %s' % (asserts[0], vtype, str(asserts[1]).strip()[:20]))
                            if isinstance(asserts[0], str) and isinstance(asserts[1], str):
                                self.validators[vtype](asserts[0].encode(), asserts[1].encode())
                            elif isinstance(asserts[0], str):
                                self.validators[vtype](asserts[0].encode(), asserts[1])
                            else:
                                self.validators[vtype](asserts[0], asserts[1])
