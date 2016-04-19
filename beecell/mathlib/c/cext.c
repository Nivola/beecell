void churn(int n) {
  while (n > 0) {
    n--;
  }
}

PyObject *pyfunc(PyObject *self, PyObject *args) {
  // GIL Release
  Py_BEGIN_ALLOW_THREADS
  // Threaded C code
  churn();
  Py_END_ALLOW_THREADS
  // GIL Acquire
}
