#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

class wxTimeFormat(object):
	"""Singleton used to format times."""

	def __init__(self):
		def defaultFormat(dt, includeMinutes=False):
			if includeMinutes:
				return dt.Format('%H:%M')
			return dt.Format('%H')
		self.__fmt = defaultFormat

	def FormatTime(self, dateTime, includeMinutes=False):
		return self.__fmt(dateTime, includeMinutes=includeMinutes)

	def SetFormatFunction(self, func):
		self.__fmt = func

wxTimeFormat = wxTimeFormat()
