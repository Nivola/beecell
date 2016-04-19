#include "Extest.h"
#include "Python.h"

static PyObject *Extest_fac(PyObject *self, PyObject *args) {
	int num;
	if (!PyArg_ParseTuple(args, "l", &num))
		return NULL;
	return (PyObject*)Py_BuildValue("l", fac(num));
}

static PyObject *Extest_fib(PyObject *self, PyObject *args) {
	int num;
	if (!PyArg_ParseTuple(args, "l", &num))
		return NULL;
	long res = fib(num);
	return (PyObject*)Py_BuildValue("l", res);
}

static PyObject *Extest_fib2(PyObject *self, PyObject *args) {
	int num;
	long res;
	if (!PyArg_ParseTuple(args, "l", &num))
		return NULL;

	// GIL Release
	Py_BEGIN_ALLOW_THREADS
	// Threaded C code
	res = fib(num);
	Py_END_ALLOW_THREADS
	// GIL Acquire

	return (PyObject*)Py_BuildValue("l", res);
}

static PyObject *Extest_doppel(PyObject *self, PyObject *args) {
	char *orig_str;
	char *dupe_str;
	PyObject* retval;
	if (!PyArg_ParseTuple(args, "s", &orig_str))
		return NULL;
	retval = (PyObject*)Py_BuildValue("ss", orig_str, dupe_str=reverse(strdup(orig_str)));
	free(dupe_str);
	return retval;
}

static PyObject *Extest_countdown(PyObject *self, PyObject *args) {
	int num;
	if (!PyArg_ParseTuple(args, "i", &num))
		return NULL;

	// GIL Release
	//Py_BEGIN_ALLOW_THREADS
	// Threaded C code
	countdown(num);
	//Py_END_ALLOW_THREADS
	// GIL Acquire

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *Extest_test(PyObject *self, PyObject *args) {
	test();
	/*return (PyObject*)Py_BuildValue("");*/
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef
ExtestMethods[] = {
	{ "fac", Extest_fac, METH_VARARGS },
	{ "fib", Extest_fib, METH_VARARGS },
	{ "fib2", Extest_fib2, METH_VARARGS },
	{ "doppel", Extest_doppel, METH_VARARGS },
	{ "countdown", Extest_countdown, METH_VARARGS },
	{ "test", Extest_test, METH_VARARGS },
	{ NULL, NULL },
};

void initExtest() {
	Py_InitModule("Extest", ExtestMethods);
}


