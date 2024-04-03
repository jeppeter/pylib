/* File : example.i */

/* This file has a few "typical" uses of C++ references. */

%module example

%{
#include "example.h"
%}

%rename(cprint) print;

class Vector {
public:
    Vector(double x, double y, double z);
   ~Vector();
    char *print();
};

/* This helper function calls an overloaded operator */
%inline %{
Vector addv(Vector &a, Vector &b) {
  return a+b;
}
%}

%extend Vector {
  double magnitude() {
    return sqrt($self->gx()*$self->gx() + $self->gy() * $self->gy() + $self->gz() * $self->gz());
  }
}

/* Wrapper around an array of vectors class */

class VectorArray {
public:
  VectorArray(int maxsize);
  ~VectorArray();
  int size();
  
  /* This wrapper provides an alternative to the [] operator */
  %extend {
    Vector &get(int index) {
      return (*$self)[index];
    }
    void set(int index, Vector &a) {
      (*$self)[index] = a;
    }
  }
};




