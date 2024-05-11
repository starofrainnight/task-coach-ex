#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerCore import *


class wxSchedulerPrint( wxSchedulerCore ):

	def __init__( self, dc ):
		super( wxSchedulerPrint, self ).__init__()
		
		self.SetDc( dc )
		
	def Draw( self, page ):
		"""
		Draw object on bitmap
		"""
		if page is None:
			self.DrawBuffer()
		else:
			self.pageNumber = page
			self.DrawBuffer()

		return self._bitmap
		
	def GetSize( self ):
		"""
		Return a wx.Size() object representing the page's size
		"""
		return self.GetDc().GetSize()

	def Refresh( self ):
		pass
