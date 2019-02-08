#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import sys
import time
from unittest.result import TestResult as DefaultTestResult


class TestResult(DefaultTestResult):
    """A test result class that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity, index=0):
        super(TestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.index = index
        self.startTime = 0

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        # if self.descriptions and doc_first_line:
        #     return '\n'.join((str(test), doc_first_line))
        # else:
        return str(test)

    def write_elapsed(self):
        stopTime = time.time()
        timeTaken = stopTime - self.startTime
        timeTaken = round(timeTaken, 3)
        self.stream.write("[%s] " % timeTaken)

    def startTest(self, test):
        self.startTime = time.time()
        # self.stream.write(self.getDescription(test))
        # super(TestResult, self).startTest(test)
        # if self.showAll:
        #     self.stream.write(self.getDescription(test))
        #     self.stream.write(" ... ")
        #     self.stream.flush()

    def addSuccess(self, test):
        self.stream.write("[%s] " % self.index)
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self.write_elapsed()
        self.stream.write("ok\n")
        self.stream.flush()
        super(TestResult, self).addSuccess(test)
        # if self.showAll:
        #     self.stream.writeln("ok")
        # elif self.dots:
        #     self.stream.write('.')
        #     self.stream.flush()

    def addError(self, test, err):
        self.stream.write("[%s] " % self.index)
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self.write_elapsed()
        self.stream.write("ERROR\n")
        self.stream.flush()

        super(TestResult, self).addError(test, err)
        # if self.showAll:
        #     self.stream.writeln("ERROR")
        # elif self.dots:
        #     self.stream.write('E')
        #     self.stream.flush()

    def addFailure(self, test, err):
        self.stream.write("[%s] " % self.index)
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self.write_elapsed()
        self.stream.write("FAIL\n")
        self.stream.flush()

        super(TestResult, self).addFailure(test, err)
        # if self.showAll:
        #     self.stream.writeln("FAIL")
        # elif self.dots:
        #     self.stream.write('F')
        #     self.stream.flush()

    def addSkip(self, test, reason):
        self.stream.write("[%s] " % self.index)
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self.write_elapsed()
        self.stream.write("skipped\n")
        self.stream.flush()

        super(TestResult, self).addSkip(test, reason)
        # if self.showAll:
        #     self.stream.writeln("skipped {0!r}".format(reason))
        # elif self.dots:
        #     self.stream.write("s")
        #     self.stream.flush()
    #
    # def addExpectedFailure(self, test, err):
    #     super(TestResult, self).addExpectedFailure(test, err)
    #     if self.showAll:
    #         self.stream.writeln("expected failure")
    #     elif self.dots:
    #         self.stream.write("x")
    #         self.stream.flush()
    #
    # def addUnexpectedSuccess(self, test):
    #     super(TestResult, self).addUnexpectedSuccess(test)
    #     if self.showAll:
    #         self.stream.writeln("unexpected success")
    #     elif self.dots:
    #         self.stream.write("u")
    #         self.stream.flush()
    #
    # def printErrors(self):
    #     if self.dots or self.showAll:
    #         self.stream.writeln()
    #     self.printErrorList('ERROR', self.errors)
    #     self.printErrorList('FAIL', self.failures)
    #
    # def printErrorList(self, flavour, errors):
    #     for test, err in errors:
    #         self.stream.writeln(self.separator1)
    #         self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
    #         self.stream.writeln(self.separator2)
    #         self.stream.writeln("%s" % err)


class TestRunner(object):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultclass = TestResult

    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None, index=0):
        # self.stream = _WritelnDecorator(stream)
        self.stream = stream
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        if resultclass is not None:
            self.resultclass = resultclass
        self.index = index

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity, index=self.index)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        # registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        # result.printErrors()
        # if hasattr(result, 'separator2'):
        #     self.stream.writeln(result.separator2)
        # run = result.testsRun
        # self.stream.writeln("Ran %d test%s in %.3fs" %
        #                     (run, run != 1 and "s" or "", timeTaken))
        # self.stream.writeln()
        #
        # expectedFails = unexpectedSuccesses = skipped = 0
        # try:
        #     results = map(len, (result.expectedFailures,
        #                         result.unexpectedSuccesses,
        #                         result.skipped))
        # except AttributeError:
        #     pass
        # else:
        #     expectedFails, unexpectedSuccesses, skipped = results
        #
        # infos = []
        # if not result.wasSuccessful():
        #     self.stream.write("FAILED")
        #     failed, errored = map(len, (result.failures, result.errors))
        #     if failed:
        #         infos.append("failures=%d" % failed)
        #     if errored:
        #         infos.append("errors=%d" % errored)
        # else:
        #     self.stream.write("OK")
        # if skipped:
        #     infos.append("skipped=%d" % skipped)
        # if expectedFails:
        #     infos.append("expected failures=%d" % expectedFails)
        # if unexpectedSuccesses:
        #     infos.append("unexpected successes=%d" % unexpectedSuccesses)
        # if infos:
        #     self.stream.write(" (%s)\n" % (", ".join(infos),))
        # else:
        #     self.stream.write("\n")
        return result

    def print_result(self, result):
        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.write(" (%s)\n" % (", ".join(infos),))
        else:
            self.stream.write("\n")
