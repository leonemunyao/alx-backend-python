### Unittests and Intergration Tests.

__Unit testing__ is the process of testing a particular function returns expected results for different set of inputs. A unit test should on test the logic defined inside the tested function. __Intergration Tests__ aims to test the code path end-to-end.

Execute tests using:
```bash
python -m unittest path/to/test_file.py
```
You can run tests with more detail(higher verbosity) by passing in the -v flag:
```bash
python -m unittest -v test_module
```
For a list of all the command-line options:
```bash
python -m unittest -h
```

#### Resources

* [unitttest - Unit Testing Framework](https://docs.python.org/3/library/unittest.html)
* [unittest.mock - mock object library](https://docs.python.org/3/library/unittest.mock.html)
* [How to mock a readonly property with mock?](https://stackoverflow.com/questions/11836436/how-to-mock-a-readonly-property-with-mock)
* [parameterized](https://pypi.org/project/parameterized/)
* [memoization](https://en.wikipedia.org/wiki/Memoization)

##### unittest - Unit testing framework

Unit testing supports some important concepts in an object-oriented way:

* __test fixture__:  Represents the preparation needed to perform one or more tests, and any associated cleanup actions.
* __test case__: This is the individual unit of testing. It checks for a specific response to a particular set of inputs.
* __test suite__: A collection of test cases, test suites or both. Used to aggregate tests that should be executed together.
* __test runner__: This is a component which orchestrates the execution of tests and provides the outcome to the user.

##### Test Discovery

In order to be compatible with test discovery, all test files must be modules or packages importable from the top level directory of the project. Test discovery is implemenetd in in TestLoader.discover(), but can also be used from the command line. The basic command line usage is:
```bash
python -m unittest discover
```

##### Organizing Test Code

In unittest, test cases are represented by __unittest.TestCase__ instances. To make your own test cases, you must write subclasses of __TestCase__ or use __FunctionTestCase__.

The simplest TestCase subclass will simply implement a test method. That is a method whose name starts with `test` in order to perform specific testing code.

```bash
import unittest

class DefaultWidgetSizeTestCase(unittest.TestCase):
    def test_default_widget_size(self):
        widget = Widget('The Widget')
        self.assertEqual(widget.size(), (50, 50))
```

Note that in order to test something, we use the __assert* methods__ provided by the TestCase.

#### unittesting.mock - mock object library

__unittesting.mock__ is a library for testing Python. It allows you to replace parts of your system under test with mock objects and make assertions about how the have been used.

#### parameterized

```bash
pip install parameterized
```

#### memoization

This is an optimisation technique used primarily to speed up computer programs by storing the results of expensive function calls to pure functions and retruning the cached result when the same inouts occur again.
