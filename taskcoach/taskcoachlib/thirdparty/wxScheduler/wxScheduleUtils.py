#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx


def timeFunction(func):
	"""Decorator which displays the total time a function used at exit, grouped by stack frame."""
	import atexit, time, traceback
	func.elapsed = dict()
	def wrapper(*args, **kwargs):
		t0 = time.time()
		try:
			return func(*args, **kwargs)
		finally:
			exc = '\n'.join(traceback.format_stack(limit=2)[:-1])
			elapsed, count = func.elapsed.get(exc, (0.0, 0))
			func.elapsed[exc] = (elapsed + (time.time() - t0), count + 1)

	def printit():
		elapsed = [(tm, count, exc) for exc, (tm, count) in func.elapsed.items()]
		elapsed.sort()
		totalElapsed = 0.0
		totalCount = 0
		for tm, count, exc in elapsed:
			print '========== %d ms / %d calls' % (int(tm * 1000), count)
			print exc
			totalElapsed += tm
			totalCount += count
		print '==========='
		print 'Total time: %d ms' % int(totalElapsed * 1000)
		print 'Total calls: %d' % totalCount

	atexit.register(printit)

	return wrapper

def copyDate(value):
	""" Simple method for copy the date (Y,M,D).
	"""
	return wx.DateTimeFromDMY(value.GetDay(), value.GetMonth(), value.GetYear())

def copyDateTime(value):
	""" Return a copy of input wxDateTime object
	"""
	if value.IsValid():
		return wx.DateTimeFromDMY(
			value.GetDay(), 
			value.GetMonth(),
			value.GetYear(),
			value.GetHour(),
			value.GetMinute(),
			value.GetSecond(),
			value.GetMillisecond(),
		)
	else:
		return wx.DateTime()

def setToWeekDayInSameWeek(day, offset, startDay=1):
	"""wxDateTime's    SetToWeekDayInSameWeek   appears    to   be
	buggish. When told that the  week starts on Monday, it results
	in   the  following   'week'  on   Jan,  31st,   2010:  31/01,
	25/01-30/01..."""
	# Loop backwards until we find the start day
	while True:
		if day.GetWeekDay() == startDay:
			break
		day.SubtractDS(wx.DateSpan(days=1))
	day.AddDS(wx.DateSpan(days=offset))
	return day
