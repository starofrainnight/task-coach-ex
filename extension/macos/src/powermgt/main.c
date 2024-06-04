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

#include <IOKit/IOKitLib.h>
#include <IOKit/IOMessage.h>
#include <IOKit/hidsystem/IOHIDParameter.h>
#include <IOKit/hidsystem/IOHIDShared.h>
#include <IOKit/pwr_mgt/IOPMLib.h>

#import "main.h"

#define POWERON    1
#define POWEROFF   2

static void powerCallback (void *args, io_service_t y, natural_t msgType, void *msgArgument)
{
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();

    switch (msgType)
    {
        case kIOMessageCanSystemSleep:
	    IOAllowPowerChange (((PyPowerObserver *)args)->rootPort, (long) msgArgument);
	    break;
        case kIOMessageSystemWillSleep:
	    PyObject_CallMethod((PyObject *)args, "PowerNotification", "i", POWEROFF);
	    IOAllowPowerChange (((PyPowerObserver *)args)->rootPort, (long) msgArgument);
	    break;
        case kIOMessageSystemHasPoweredOn:
	    PyObject_CallMethod((PyObject *)args, "PowerNotification", "i", POWERON);
	    break;
    }

    PyGILState_Release(gstate);
}

//==========================================================================
// Init/dealloc

static void pypowerobserver_dealloc(PyPowerObserver *self)
{
    if (self->rootPort)
    {
        IODeregisterForSystemPower(&self->rootPort);
    }

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject* pypowerobserver_new(PyTypeObject *type,
                                     PyObject *args,
                                     PyObject *kwargs)
{
    PyPowerObserver *self;

    self = (PyPowerObserver*)type->tp_alloc(type, 0);

    if (self)
        self->rootPort = 0;

    return (PyObject*)self;
}

static int pypowerobserver_init(PyPowerObserver *self,
                                PyObject *args,
                                PyObject *kwargs)
{
     if (!PyArg_ParseTuple(args, ":__init__"))
        return -1;

     if (self)
     {
         io_object_t            notifier;

         self->rootPort = IORegisterForSystemPower(self, &self->notificationPort, powerCallback, &notifier);
         if (!self->rootPort)
         {
             PyErr_SetString(PyExc_RuntimeError, "IORegisterForSystemPower failed");
             return -1;
         }
     }

     return 0;
}

//==========================================================================
// methods

static PyObject *pypowerobserver_run(PyPowerObserver *self,
				     PyObject *args,
				     PyObject *kwargs)
{
    if (!PyArg_ParseTuple(args, ":run"))
        return NULL;

    self->runLoop = CFRunLoopGetCurrent();
    CFRunLoopAddSource (self->runLoop, IONotificationPortGetRunLoopSource(self->notificationPort), kCFRunLoopDefaultMode);

    Py_BEGIN_ALLOW_THREADS
        CFRunLoopRun();
    Py_END_ALLOW_THREADS

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *pypowerobserver_stop(PyPowerObserver *self,
				      PyObject *args,
				      PyObject *kwargs)
{
    CFRunLoopStop(self->runLoop);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef pypowerobserver_methods[] = {
   { "run", (PyCFunction)&pypowerobserver_run, METH_VARARGS, "enter main loop" },
   { "stop", (PyCFunction)&pypowerobserver_stop, METH_VARARGS, "exit main loop" },

   { NULL }
};

//==========================================================================
// Type object

PyDoc_STRVAR(powerobserver_doc,
"PowerObserver class");

static PyTypeObject PyPowerObserverType = {
   PyObject_HEAD_INIT(NULL)
   0,
   "_powermgt.PowerObserver",
   sizeof(PyPowerObserver),
   0,
   (destructor)pypowerobserver_dealloc,
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
   powerobserver_doc,
   0,
   0,
   0,
   0,
   0,
   0,
   pypowerobserver_methods,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   (initproc)pypowerobserver_init,
   0,
   pypowerobserver_new,
};

PyTypeObject* PPyPowerObserverType = &PyPowerObserverType;

static PyMethodDef functions[] = {
    { NULL }
};

void init_powermgt(void)
{
    PyObject *mdl = Py_InitModule3("_powermgt", functions, "Power management extension");

    if (PyType_Ready(PPyPowerObserverType) < 0)
        return;

    Py_INCREF((PyObject *)PPyPowerObserverType);
    PyModule_AddObject(mdl, "PowerObserver", (PyObject *)PPyPowerObserverType);

    PyModule_AddIntConstant(mdl, "POWERON", POWERON);
    PyModule_AddIntConstant(mdl, "POWEROFF", POWEROFF);
}
