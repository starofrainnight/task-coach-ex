/*
  Task Coach - Your friendly task manager
  Copyright (C) 2004-2016 Task Coach developers <developers@taskcoach.org>

  Task Coach is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Task Coach is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


#import "main.h"

#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>

//==========================================================================
// Init/dealloc

static void pyidle_dealloc(PyIdle *self)
{
    if (self->regEntry)
    {
        IOObjectRelease(self->regEntry);
    }

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject* pyidle_new(PyTypeObject *type,
                            PyObject *args,
                            PyObject *kwargs)
{
    PyIdle *self;

    self = (PyIdle*)type->tp_alloc(type, 0);

    self->machPort = 0;
    self->regEntry = 0;

    return (PyObject*)self;
}

static int pyidle_init(PyIdle *self,
                       PyObject *args,
                       PyObject *kwargs)
{
     if (!PyArg_ParseTuple(args, ":__init__"))
        return -1;

     if (self)
     {
         io_iterator_t iterator;
         int ret;

         if ((ret = IOMasterPort(MACH_PORT_NULL, &self->machPort)) != kIOReturnSuccess)
         {
             PyErr_Format(PyExc_RuntimeError, "IOMasterPort failed: %d", ret);
             return -1;
         }

         if ((ret = IOServiceGetMatchingServices(self->machPort, IOServiceMatching("IOHIDSystem"), &iterator)) != kIOReturnSuccess)
         {
             PyErr_Format(PyExc_RuntimeError, "IOServiceGetMatchingServices failed: %d", ret);
             return -1;
         }

         if (!(self->regEntry = IOIteratorNext(iterator)))
         {
             PyErr_SetString(PyExc_RuntimeError, "Empty IO iterator");
             return -1;
         }

         IOObjectRelease(iterator);
     }

     return 0;
}

//==========================================================================
// methods

static PyObject *pyidle_get(PyIdle *self,
                            PyObject *args,
                            PyObject *kwargs)
{
    CFMutableDictionaryRef props;
    CFTypeRef obj;
    uint64_t idleTime;
    CFTypeID type;
    int ret;

    if ((ret = IORegistryEntryCreateCFProperties(self->regEntry, &props, kCFAllocatorDefault, 0)) != kIOReturnSuccess)
    {
      PyErr_Format(PyExc_RuntimeError, "IORegistryEntryCreateCFProperties failed: %d", ret);
        return NULL;
    }

    obj = CFDictionaryGetValue(props, CFSTR("HIDIdleTime"));
    CFRetain(obj);

    type = CFGetTypeID(obj);
    if (type == CFDataGetTypeID())
    {
        CFDataGetBytes((CFDataRef)obj,
                       CFRangeMake(0, sizeof(idleTime)),
                       (UInt8*)&idleTime);
    }
    else if (type == CFNumberGetTypeID())
    {
        CFNumberGetValue((CFNumberRef)obj,
                         kCFNumberSInt64Type,
                         &idleTime);
    }
    else
    {
        PyErr_Format(PyExc_RuntimeError, "Unsupported type: %d", (int)type);
        CFRelease(obj);
        CFRelease((CFTypeRef)props);
        return NULL;
    }

    CFRelease(obj);
    CFRelease(props);

    return Py_BuildValue("L", idleTime >> 30);
}

static PyMethodDef pyidle_methods[] = {
   { "get", (PyCFunction)&pyidle_get, METH_VARARGS, "Get idle time in seconds" },

   { NULL }
};

//==========================================================================
// Type object

PyDoc_STRVAR(idle_doc,
"Idle class");

static PyTypeObject PyIdleType = {
   PyObject_HEAD_INIT(NULL)
   0,
   "_idle.Idle",
   sizeof(PyIdle),
   0,
   (destructor)pyidle_dealloc,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
   idle_doc,
   0,
   0,
   0,
   0,
   0,
   0,
   pyidle_methods,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   (initproc)pyidle_init,
   0,
   pyidle_new,
};

PyTypeObject* PPyIdleType = &PyIdleType;

static PyMethodDef functions[] = {
    { NULL }
};

void init_idle(void)
{
    PyObject *mdl = Py_InitModule3("_idle", functions, "Computer idle time utilities");

    if (PyType_Ready(PPyIdleType) < 0)
        return;

    Py_INCREF((PyObject *)PPyIdleType);
    PyModule_AddObject(mdl, "Idle", (PyObject *)PPyIdleType);
}
