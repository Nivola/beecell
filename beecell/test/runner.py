# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import logging
import sys
import time
from unittest.result import TestResult as DefaultTestResult


logger = logging.getLogger(__name__)


class TestResult(DefaultTestResult):
    """A test result class that can print formatted text results to a stream.

    Used by TextTestRunner.
    """

    separator1 = "=" * 70
    separator2 = "-" * 70

    def __init__(self, stream, descriptions, verbosity, index=0):
        super(TestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.index = index
        self.startTime = 0

    def getDescription(self, test):
        return str(test)

    def _write_elapsed(self):
        stopTime = time.time()
        timeTaken = stopTime - self.startTime
        timeTaken = round(timeTaken, 3)
        self.stream.write("[%s] " % timeTaken)

    def _print_runner(self):
        self.stream.write("[runner-%s] " % self.index)

    def startTest(self, test):
        self.startTime = time.time()

    def addSuccess(self, test):
        self._print_runner()
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self._write_elapsed()
        self.stream.write("ok\n")
        self.stream.flush()
        super(TestResult, self).addSuccess(test)

    def addError(self, test, err):
        self._print_runner()
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self._write_elapsed()
        self.stream.write("ERROR\n")
        self.stream.flush()
        super(TestResult, self).addError(test, err)

    def addFailure(self, test, err):
        self._print_runner()
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self._write_elapsed()
        self.stream.write("FAIL\n")
        self.stream.flush()
        super(TestResult, self).addFailure(test, err)

    def addSkip(self, test, reason):
        self._print_runner()
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self._write_elapsed()
        self.stream.write("skipped\n")
        self.stream.flush()
        super(TestResult, self).addSkip(test, reason)

    def printErrors(self):
        # if self.dots or self.showAll:
        #     self.stream.writeln()
        self.printErrorList("ERROR", self.errors)
        self.printErrorList("FAIL", self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.write("\n" + self.separator1)
            self.stream.write("\n%s: %s" % (flavour, self.getDescription(test)))
            self.stream.write("\n" + self.separator2)
            self.stream.write("\n%s" % err)


class TestRunner(object):
    """A test runner class that displays results in textual form whene run parallel test.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """

    resultclass = TestResult
    separator1 = "=" * 70
    separator2 = "-" * 70

    def __init__(
        self,
        stream=sys.stderr,
        descriptions=True,
        verbosity=1,
        failfast=False,
        buffer=False,
        resultclass=None,
        index=0,
    ):
        # self.stream = _WritelnDecorator(stream)
        self.stream = stream
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        if resultclass is not None:
            self.resultclass = resultclass
        self.index = index

    def _print_runner(self):
        self.stream.write("[runner-%s] " % self.index)

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity, index=self.index)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        # registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, "startTestRun", None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, "stopTestRun", None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        return result

    def print_error_list(self, flavour, errors):
        for test, err in errors:
            self.stream.write("\n" + self.separator1)
            # self.stream.write("\n%s: %s" % (flavour, self.getDescription(test)))
            self.stream.write("\n" + self.separator2)
            self.stream.write("\n%s" % err)

    def print_result(self, result):
        self._print_runner()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(
                len,
                (result.expectedFailures, result.unexpectedSuccesses, result.skipped),
            )
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

        self.print_error_list("ERROR", result.errors)
        self.print_error_list("FAIL", result.failures)
