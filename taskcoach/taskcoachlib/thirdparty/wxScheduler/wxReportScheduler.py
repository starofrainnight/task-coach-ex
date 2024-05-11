#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerPrint import *
import calendar
import wx


class wxReportScheduler( wx.Printout ):
	"""
	This is a class which demonstrate how to use the in-memory wxSchedulerPrint() 
	object on wxPython printing framework.
	You can control wxScheduler in the same way on GUI.
	For other info on wxPrintOut class and methods check the wxPython 
	documentation (RTFM for nerds ;-) ).
	"""
	def __init__( self, format, style, drawerClass, day, weekstart, periodCount, schedules ):
		self._format	= format
		self._style = style
		self._drawerClass = drawerClass
		self._day		= day
		self._schedules	= schedules
		self._weekstart = weekstart
		self._periodCount = periodCount
		self.pages		= None
		self._bitmaps = []

		wx.Printout.__init__( self )

	def _DrawPages(self, dc):
		scheduler = self._GetScheduler( dc, self._day )
		scheduler.Draw( None )
		self.pages = scheduler.pageCount

		for idx in xrange( scheduler.pageCount ):
			self._bitmaps.append( scheduler.Draw( idx + 1 ) )

	def _GetScheduler( self, dc, day ):
		"""
		Return an in-memory wxSchedulerPrint() object for adding 
		schedules and print on current wxDC
		"""

		scheduler = wxSchedulerPrint( dc )
		scheduler.SetViewType( self._format )
		scheduler.SetStyle( self._style )
		scheduler.SetDrawer( self._drawerClass )
		scheduler.SetDate( day )
		scheduler.SetWeekStart( self._weekstart )
		scheduler.SetPeriodCount( self._periodCount )

		for schedule in self._schedules:
			scheduler.Add( schedule )

		return scheduler

	def OnPrintPage( self, page ):
		"""
		This code draw a wxScheduler scaled to fit page using date, format and 
		schedules passed by the user.
		Note there is no difference on manage scheduler and schedules beetwen 
		GUI and printing framework
		"""

		dc = self.GetDC()
		if self.pages is None:
			self._DrawPages( dc )

		dc.DrawBitmap(self._bitmaps[page - 1], 0, 0, False)

		return True

	def HasPage( self, page ):
		if self.pages is None:
			self._DrawPages( self.GetDC() )
		return page <= self.pages

	def GetPageInfo( self ):
		if self.pages is None:
			self._DrawPages( self.GetDC() )

		return ( 1, self.pages, 1, 1 )
