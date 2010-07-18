#!/usr/bin/env python

## Task Coach - Your friendly task manager
## Copyright (C) 2010 Task Coach developers <developers@taskcoach.org>

## Task Coach is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## Task Coach is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

This widget is yet another tree control implementation, in pure
Python. Rows may actually contain arbitrary wxPython controls. Column
headers may be hierarchical, with subheaders. It is virtual: at any
moment, only visible rows actually use up memory, allowing for any
number of rows (well, 2^31 at most, but this may change in the
future). It will soon provide Mac OS-like drag and drop: dropping a
row as a child or sibling of another row, with pretty visual cue.

The design is inspired from UIKit's UITableView.

"""

import wx, math


#=======================================
#{ Cells

class CellBase(wx.Panel):
    """
    Base class for cells.
    """

    def __init__(self, *args, **kwargs):
        super(CellBase, self).__init__(*args, **kwargs)

        wx.EVT_LEFT_UP(self, self._OnLeftUp)
        wx.EVT_LEFT_DCLICK(self, self._OnDClick)
        wx.EVT_RIGHT_UP(self, self._OnRightUp)

    def _OnLeftUp(self, evt):
        self.GetParent().GetParent()._OnCellClicked(self, evt)

    def _OnDClick(self, evt):
        self.GetParent().GetParent()._OnCellDClicked(self, evt)

    def _OnRightUp(self, evt):
        self.GetParent().GetParent()._OnCellRightClicked(self, evt)

    def GetIdentifier(self):
        """
        This method should return a string identifier for the cell's
        type. See L{DequeueCell}.
        """

        raise NotImplementedError

#}

#=======================================
#{ Events

wxEVT_COMMAND_ROW_SELECTED = wx.NewEventType()
EVT_ROW_SELECTED = wx.PyEventBinder(wxEVT_COMMAND_ROW_SELECTED)

wxEVT_COMMAND_ROW_DESELECTED = wx.NewEventType()
EVT_ROW_DESELECTED = wx.PyEventBinder(wxEVT_COMMAND_ROW_DESELECTED)

wxEVT_COMMAND_HEADER_LCLICKED = wx.NewEventType()
EVT_HEADER_LCLICKED = wx.PyEventBinder(wxEVT_COMMAND_HEADER_LCLICKED)

wxEVT_COMMAND_HEADER_RCLICKED = wx.NewEventType()
EVT_HEADER_RCLICKED = wx.PyEventBinder(wxEVT_COMMAND_HEADER_RCLICKED)

wxEVT_COMMAND_ROW_LEFT_DCLICK = wx.NewEventType()
EVT_ROW_LEFT_DCLICK = wx.PyEventBinder(wxEVT_COMMAND_ROW_LEFT_DCLICK)

wxEVT_COMMAND_ROW_RCLICKED = wx.NewEventType()
EVT_ROW_RCLICKED = wx.PyEventBinder(wxEVT_COMMAND_ROW_RCLICKED)

#}

#=======================================
#{ Style constants

ULTTREE_SINGLE_SELECTION        = 0x01
ULTTREE_STRIPE                  = 0x02

#}

def _shortenString(dc, s, w, margin=3):
    """
    Returns a shortened version of s that fits into w pixels (in
    width), adding an ellipsis in the middle of the string.
    """

    tw, th = dc.GetTextExtent(s)
    if tw + margin * 2 <= w:
        return s

    tw, th = dc.GetTextExtent('...')
    if tw + margin * 2 >= w:
        return ''

    m = int(len(s)/2)
    left = s[:m - 1]
    right = s[m + 1:]

    while True:
        r = left + '...' + right
        tw, th = dc.GetTextExtent(r)
        if tw + 2 * margin <= w:
            return r
        left = left[:-1]
        right = right[1:]


def _tupleStartsWith(tpl, otherTpl):
    """Returns True if otherTpl is a prefix of tpl"""

    return otherTpl == tpl[:len(otherTpl)]


class RowBase(object):
    """
    Base class for row. A row may hold several cells, up to one for
    each header.
    """

    def __init__(self, x, y, w, h):
        super(RowBase, self).__init__()

        self.SetDimensions(x, y, w, h)

        self.cells = dict()

    def AddCell(self, indexPath, cell):
        self.cells[indexPath] = cell

    def SetDimensions(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def Refresh(self):
        for cell in self.cells.values():
            cell.Refresh()

    def Show(self, doShow=True):
        for cell in self.cells.values():
            cell.Show(doShow)

    def SetBackgroundColour(self, colour):
        for cell in self.cells.values():
            cell.SetBackgroundColour(colour)


class Row(RowBase):
    def __init__(self, *args, **kwargs):
        super(Row, self).__init__(*args, **kwargs)

        self.columnCells = dict()

    def AddColumnCell(self, columnIndex, span, cell):
        self.cells[(columnIndex,)] = cell
        self.columnCells[columnIndex] = span

    def Layout(self, tree):
        allPaths = list()
        def addPath(p):
            allPaths.append(p)
            for idx in xrange(tree.GetHeaderChildrenCount(p)):
                addPath(p + (idx,))
        for idx in xrange(tree.GetRootHeadersCount()):
            addPath((idx,))

        heights = []

        count = tree.GetRootHeadersCount()

        for idx in xrange(count):
            heights.append(1.0 / max([len(p) for p in allPaths if p[0] == idx]))

        x = 0
        remain = self.w + self.x
        cw = self.w + self.x
        state = 0
        startX = None
        totalW = None
        span = None
        columnCell = None

        for idx in xrange(count):
            def _layout(indexPath, cell, cx, cy, cw, ch):
                h = int(math.ceil(self.h * heights[indexPath[0]]))
                if self.x > cx:
                    rect = (self.x, cy, cw - (self.x - cx), h)
                else:
                    rect = (cx, cy, cw, h)

                cell.SetDimensions(*rect)
                cell.Layout()

                xx = 0
                remain = cw
                count = tree.GetHeaderChildrenCount(indexPath)

                if count:
                    for i in xrange(count):
                        if i == count -1:
                            w = remain
                        else:
                            w = int(math.ceil(tree._headerSizes.get(indexPath + (i,), 1.0 / count) * cw))

                        _layout(indexPath + (i,), self.cells[indexPath + (i,)],
                                cx + xx, cy + h, w, ch - h)

                        remain -= w + 1
                        xx += w + 1

            if idx == count - 1:
                w = remain
            else:
                w = int(math.ceil(tree._headerSizes.get((idx,), 1.0 / count) * cw))

            remain -= w + 1

            if state == 0:
                if idx in self.columnCells:
                    startX = x
                    totalW = w
                    state = 1
                    columnCell = self.cells[(idx,)]
                    span = self.columnCells[idx]
                else:
                    _layout((idx,), self.cells[(idx,)], x, self.y, w, self.h)
            else:
                span -= 1
                totalW += w

                if span == 0:
                    if self.x > startX:
                        rect = (self.x, self.y, totalW - (self.x - startX), self.h)
                    else:
                        rect = (startX, self.y, totalW, self.h)

                    columnCell.SetDimensions(*rect)
                    columnCell.Layout()

                    _layout((idx,), self.cells[(idx,)], x, self.y, w, self.h)

                    state = 0

            x += w + 1

        if state == 1:
            if self.x > startX:
                rect = (self.x, self.y, totalW - (self.x - startX), self.h)
            else:
                rect = (startX, self.y, totalW, self.h)

            columnCell.SetDimensions(*rect)
            columnCell.Layout()

#=======================================
#{ Tree control

class UltimateTreeCtrl(wx.Panel):
    """
    Rows are identified by their index path. This is a tuple holding
    the path to the cell relative to the tree's top cells. For
    instance, (1, 3, 4) is the 5th child of the 4th child of the 2nd
    root row.
    """

    #====================
    #{ Data source

    def GetRootHeadersCount(self):
        """Return the number of root headers."""
        raise NotImplementedError

    def GetHeaderText(self, indexPath):
        """Return the title for the header."""
        raise NotImplementedError

    def GetHeaderChildrenCount(self, indexPath):
        """Return the number of children of the header."""
        raise NotImplementedError

    def GetRootCellsCount(self):
        """Return the number of root cells"""
        raise NotImplementedError

    def GetRowChildrenCount(self, indexPath):
        """Return the number of children for the given row"""
        raise NotImplementedError

    def GetRowHeight(self, indexPath):
        """Return the height of a row. Variable height is supported."""
        return 30

    def GetCell(self, indexPath, headerPath):
        """Return an actual cell; see L{DequeueCell} for usage
        pattern. If this returns None for a 0-length header path,
        L{GetColumnCell} will be called instead."""
        raise NotImplementedError

    def GetColumnCell(self, indexPath, columnIndex):
        """Return a cell that fills the whole column. This is only
        called if L{GetCell} returned None for a 0-length header path."""

    def GetRowBackgroundColour(self, indexPath):
        """Return the background colour of a row. Default is white."""
        return wx.WHITE

    #}

    #====================
    #{ Metrics

    def GetVerticalMargin(self):
        """Return the vertical margin, i.e. number of pixels between
        two rows. Default is 1."""
        return 1

    #}

    #====================
    #{ Reusable cells

    def DequeueCell(self, identifier, factory):
        """
        In order to avoid creating a new widget for each cell, those
        widgets (subclasses of L{CellBase}) should be designed to be
        reusable. Each type of widget should have a unique identifier
        (see L{GetIdentifier}); for each identifier a queue of unused
        widgets is maintained. This method returns an unused widget
        for the given identifier, which you can then update according
        to the actual underlying data.

        The second argument is a factory used to create a new widget
        in case there is no unused one for this identifier. It will be
        passed the new widget's parent as first argument.
        """
        if identifier in self._queues:
            queue = self._queues[identifier]
            if queue:
                cell = queue.pop()
                return cell

        cell = factory(self._contentView)

        return cell

    def _Queue(self, row):
        # Mark a cell as unused and put it back in its queue.

        for cell in row.cells.values():
            queue = self._queues.get(cell.GetIdentifier(), [])
            queue.append(cell)
            self._queues[cell.GetIdentifier()] = queue
            cell.Show(False)

    #}

    def __init__(self, *args, **kwargs):
        """
        @keyword treeStyle: And OR of UltimateTreeCtrl style constants.
        """

        self.__style = kwargs.pop('treeStyle', 0)

        super(UltimateTreeCtrl, self).__init__(*args, **kwargs)

        self._queues = dict()
        self._expanded = set()
        self._visibleRows = dict()
        self._buttons = list()
        self._selection = set()
        self._headerSizes = dict()

        # 0: normal
        # 1: pointer on header boundary
        # 2: resizing

        self._headerMouseState = 0

        class _Sizer(wx.PySizer):
            def __init__(self, callback):
                self.__callback = callback
                super(_Sizer, self).__init__()

            def CalcMin(self):
                return (-1, self.__callback())

        self._headerView = wx.Panel(self, style=wx.FULL_REPAINT_ON_RESIZE)
        self._contentView = wx.ScrolledWindow(self)

        self._contentView.SetScrollRate(10, 10)
        self._contentView.SetSizer(_Sizer(self._ComputeHeight))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._headerView, 0, wx.EXPAND)
        sizer.Add(self._contentView, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.FitHeader()

        wx.EVT_SCROLLWIN(self._contentView, self._OnScrollContent)
        wx.EVT_PAINT(self._contentView, self._OnPaintContent)
        wx.EVT_LEFT_UP(self._contentView, self._OnLeftUpContent)
        wx.EVT_LEFT_DCLICK(self._contentView, self._OnLeftDClickContent)
        wx.EVT_RIGHT_UP(self._contentView, self._OnRightUpContent)
        wx.EVT_SIZE(self._contentView, self._OnSizeContent)

        wx.EVT_PAINT(self._headerView, self._OnPaintHeader)
        wx.EVT_LEFT_DOWN(self._headerView, self._OnLeftDownHeader)
        wx.EVT_LEFT_UP(self._headerView, self._OnLeftUpHeader)
        wx.EVT_RIGHT_UP(self._headerView, self._OnRightUpHeader)

        wx.EVT_MOTION(self._headerView, self._OnMotionHeader)
        wx.EVT_LEAVE_WINDOW(self._headerView, self._OnLeaveHeader)

    #{ Persistence

    def SavePerspective(self):
        """
        Returns a string representing the current state of the
        tree. This includes expanded rows and header sizes. See also
        L{LoadPerspective}.
        """
        return '~'.join(['%s=%f' % (indexPath, sz) for indexPath, sz in self._headerSizes.items()]) + ':' + \
               '~'.join(map(str, self._expanded))

    def LoadPerspective(self, per):
        """
        Restore a tree state that was retrieved by L{SavePerspective}.
        """
        sizes, expanded = per.split(':')
        for pair in sizes.split('~'):
            indexPath, sz = pair.split('=')
            self._headerSizes[eval(indexPath)] = float(sz)
        self._expanded = set([eval(path) for path in expanded.split('~')])

    #}

    #{ Style

    def SetTreeStyle(self, style):
        """
        Set the current style. The following module-level constants
        are supported:

         - ULTTREE_SINGLE_SELECTION: Allows at most one row to be selected
             at once.
         - ULTTREE_STRIPE: Draw a darker background for odd rows.
        """
        self.__style = style
        self.Refresh()

    def GetTreeStyle(self):
        """
        Returns the current style; see L{SetTreeStyle}.
        """
        return self.__style

    #}

    def Refresh(self):
        """
        Refresh the whole tree. This recomputes the visible cells and
        refreshes them as well.
        """
        self._Relayout()
        super(UltimateTreeCtrl, self).Refresh()

        for cell in self._visibleRows.values():
            cell.Refresh()

    def _Check(self):
        """Resets the scrollwindow virtual size"""
        self._contentView.SetVirtualSize((-1, self._ComputeHeight()))

    def Collapse(self, indexPath):
        """
        Collapse a row. Selected children will be deselected. Their
        own expanded state is not lost.
        """

        try:
            for path in self._ExpandedNode(indexPath):
                if path != indexPath and path in self._visibleRows:
                    if path in self._selection:
                        self._Deselect(path)
                    self._Queue(self._visibleRows[path])
                    del self._visibleRows[path]
            self._expanded.remove(indexPath)
        except KeyError:
            pass

        self.Refresh()

    def Expand(self, indexPath):
        """
        Expand a row. Expansion state of children is restored.
        """

        self._expanded.add(indexPath)
        self.Refresh()

    def Toggle(self, indexPath):
        """
        Toggle a row expansion status.
        """

        if indexPath in self._expanded:
            self.Collapse(indexPath)
        else:
            self.Expand(indexPath)

    def InsertRow(self, indexPath):
        """
        Inserts a new row.
        """

        for path, row in self._visibleRows.items():
            if _tupleStartsWith(path, indexPath[:-1]) and len(path) >= len(indexPath):
                if path[len(indexPath) - 1] >= indexPath[-1]:
                    newPath = path[:len(indexPath) - 1] + (path[len(indexPath) - 1] + 1,) + path[len(indexPath) + 1:]
                    del self._visibleRows[path]
                    self._visibleRows[newPath] = row

        for path in set(self._selection):
            if _tupleStartsWith(path, indexPath[:-1]) and len(path) >= len(indexPath):
                if path[len(indexPath) - 1] >= indexPath[-1]:
                    newPath = path[:len(indexPath) - 1] + (path[len(indexPath) - 1] + 1,) + path[len(indexPath) + 1:]
                    self._selection.remove(path)
                    self._selection.add(newPath)

        self.Refresh()

    def DeleteRow(self, indexPath):
        """
        Removes a row.
        """

        for path, row in self._visibleRows.items():
            if _tupleStartsWith(path, indexPath[:-1]) and len(path) >= len(indexPath):
                if path[len(indexPath) - 1] > indexPath[-1]:
                    newPath = path[:len(indexPath) - 1] + (path[len(indexPath) - 1] - 1,) + path[len(indexPath) + 1:]
                    del self._visibleRows[path]
                    self._visibleRows[newPath] = row

        for path in set(self._selection):
            if _tupleStartsWith(path, indexPath[:-1]) and len(path) >= len(indexPath):
                if path[len(indexPath) - 1] > indexPath[-1]:
                    newPath = path[:len(indexPath) - 1] + (path[len(indexPath) - 1] - 1,) + path[len(indexPath) + 1:]
                    self._selection.remove(path)
                    self._selection.add(newPath)

        self.Refresh()

    def FitHeader(self):
        """
        Sets the header view height to what it should be.
        """
        count = self.GetRootHeadersCount()
        h = 0
        for idx in xrange(count):
            h = max(h, self._ComputeHeaderHeight((idx,)))

        self._headerView.SetSize((-1, h))

    def HeaderHitTest(self, x, y):
        """
        Returns the index path of the header at position (x, y)
        (relative to the header view), or None.
        """
        for indexPath, xx, yy, w, h in self._bounds:
            if x >= xx and y >= yy and x < xx + w and y < yy + h:
                return indexPath
        return None

    def _headerHeight(self):
        """
        Return the height of a standard header. On Windows and Linux,
        it isn't fixed and this returns 20. On Mac OS X though wx
        can't draw a header with a custom height, it needs to be 16.
        """
        if '__WXMAC__' in wx.PlatformInfo:
            return 16
        return 20

    def _ComputeHeaderHeight(self, indexPath):
        h = 0
        for idx in xrange(self.GetHeaderChildrenCount(indexPath)):
            h = max(h, self._ComputeHeaderHeight(indexPath + (idx,)))
        return h + self._headerHeight()

    def _Relayout(self):
        # Recompute visible rows

        self.Freeze()
        try:
            self._Check()

            x0, y0 = self._contentView.GetViewStart()
            xu, yu = self._contentView.GetScrollPixelsPerUnit()
            x0 *= xu
            y0 *= yu
            w, h = self._contentView.GetClientSizeTuple()
            currentIndex = 0

            # XXXFIXME this should be optimized to avoid looping over
            # the whole mess

            currentPosition = 0
            for indexPath in self._Expanded():
                height = self.GetRowHeight(indexPath)

                if currentPosition + height < y0 or currentPosition >= y0 + h:
                    currentPosition += height + self.GetVerticalMargin()

                    if indexPath in self._visibleRows:
                        cell = self._visibleRows[indexPath]
                        self._Queue(cell)
                        del self._visibleRows[indexPath]

                    continue

                # At least partially visible row. Move it and show it.

                offset = 24 * len(indexPath)

                if indexPath in self._visibleRows:
                    row = self._visibleRows[indexPath]
                else:
                    row = Row(0, 0, 0, 0)

                    def queryCell(headerPath):
                        cell = self.GetCell(indexPath, headerPath)
                        if cell is None:
                            if len(headerPath) != 1:
                                raise ValueError('You can only set column cells at header root.')
                            cell, span = self.GetColumnCell(indexPath, headerPath[0])
                            row.AddColumnCell(headerPath[0], span, cell)
                            return span
                        else:
                            row.AddCell(headerPath, cell)

                            for i in xrange(self.GetHeaderChildrenCount(headerPath)):
                                queryCell(headerPath + (i,))

                            return 1

                    idx = 0
                    while idx < self.GetRootHeadersCount():
                        idx += queryCell((idx,))

                    self._visibleRows[indexPath] = row

                if indexPath in self._selection:
                    row.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
                else:
                    col = self.GetRowBackgroundColour(indexPath)
                    r, g, b = col.Red(), col.Green(), col.Blue()

                    if (currentIndex % 2) and (self.__style & ULTTREE_STRIPE):
                        if r + g + b < 128 * 3:
                            r = min(255, r + 30)
                            g = min(255, g + 30)
                            b = min(255, b + 30)
                        else:
                            r = max(0, r - 30)
                            g = max(0, g - 30)
                            b = max(0, b - 30)

                    row.SetBackgroundColour(wx.Colour(r, g, b))

                row.SetDimensions(offset, currentPosition - y0, w - offset, height)
                row.Layout(self)
                row.Show()
                row.Refresh()

                currentPosition += height + self.GetVerticalMargin()
                currentIndex += 1
        finally:
            self.Thaw()

    def _Select(self, indexPath):
        self._selection.add(indexPath)

        evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_SELECTED)
        evt.indexPath = indexPath
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

        if indexPath in self._visibleRows:
            cell = self._visibleRows[indexPath]
            cell.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

    def _Deselect(self, indexPath):
        try:
            self._selection.remove(indexPath)

            evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_DESELECTED)
            evt.indexPath = indexPath
            evt.SetEventObject(self)
            self.ProcessEvent(evt)
        except KeyError:
            pass
        else:
            if indexPath in self._visibleRows:
                cell = self._visibleRows[indexPath]
                cell.SetBackgroundColour(self.GetRowBackgroundColour(indexPath))

    def _Expanded(self):
        """
        Generator which iterates over all rows, avoiding children of
        collapsed rows.
        """
        for idx in xrange(self.GetRootCellsCount()):
            for child in self._ExpandedNode((idx,)):
                yield child

    def _ExpandedNode(self, indexPath):
        """
        Generator which iterates over all children of a row (including
        itself), avoiding children of collapsed rows.
        """

        yield indexPath

        if indexPath in self._expanded:
            for idx in xrange(self.GetRowChildrenCount(indexPath)):
                for child in self._ExpandedNode(indexPath + (idx,)):
                    yield child

    def _ComputeHeight(self):
        height = 0

        for indexPath in self._Expanded():
            height += self.GetRowHeight(indexPath) + self.GetVerticalMargin()

        if height:
            return height - self.GetVerticalMargin()

        return 0

    def _OnScrollContent(self, evt):
        self._Relayout()
        self.Refresh()

        evt.Skip()

    def _OnSizeContent(self, evt):
        self._Relayout()

        evt.Skip()

    def _OnPaintHeader(self, evt):
        dc = wx.PaintDC(self._headerView)
        dc.BeginDrawing()
        try:
            totalW, h = self._headerView.GetClientSizeTuple()

            # Respect alignment if the scrollbar is visible
            cw1, _ = self._contentView.GetClientSizeTuple()
            cw2, _ = self._contentView.GetSizeTuple()

            wOffset = cw2 - cw1

            self._bounds = []

            count = self.GetRootHeadersCount()

            if count:
                x = 0
                remain = totalW
                cw = totalW - wOffset

                for idx in xrange(count):
                    if not (idx,) in self._headerSizes:
                        self._headerSizes[(idx,)] = 1.0 / count

                    if idx == count - 1:
                        w = remain
                    else:
                        w = int(math.ceil(self._headerSizes[(idx,)] * cw))
                        remain -= w + 1

                    self._DrawHeader(dc, (idx,), x, w)

                    x += w + 1

            self._bounds.sort(lambda x, y: cmp(len(x[0]), len(y[0])))
        finally:
            dc.EndDrawing()

    def _DrawHeader(self, dc, indexPath, x, totalW):
        y = (len(indexPath) - 1) * self._headerHeight()

        self._bounds.append((indexPath, x, y, totalW, self._headerHeight()))

        txt = _shortenString(dc, self.GetHeaderText(indexPath), totalW)
        render = wx.RendererNative.Get()
        opts = wx.HeaderButtonParams()
        opts.m_labelText = txt
        render.DrawHeaderButton(self._headerView, dc, (int(x), y, int(totalW), self._headerHeight()),
                                wx.CONTROL_CURRENT, params=opts)

        count = self.GetHeaderChildrenCount(indexPath)

        if count:
            xx = 0
            remain = totalW

            for idx in xrange(count):
                newIndexPath = indexPath + (idx,)
                if newIndexPath not in self._headerSizes:
                    self._headerSizes[newIndexPath] = 1.0 / count

                if idx == count - 1:
                    w = remain
                else:
                    w = int(math.ceil(self._headerSizes[newIndexPath] * totalW))
                    remain -= w

                self._DrawHeader(dc, newIndexPath, x + xx, w)

                xx += w

    def _OnPaintContent(self, evt):
        # Draw lines between rows and expand buttons

        dc = wx.PaintDC(self._contentView)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()

        dc.BeginDrawing()
        try:
            render = wx.RendererNative.Get()

            for indexPath, row in self._visibleRows.items():
                w, h = self._contentView.GetClientSizeTuple()

                if indexPath in self._selection:
                    col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
                else:
                    col = self.GetRowBackgroundColour(indexPath)

                dc.SetBrush(wx.Brush(col))
                dc.SetPen(wx.Pen(col))
                dc.DrawRectangle(0, row.y, w, row.h)

                if self.GetRowChildrenCount(indexPath):
                    rect = (24 * (len(indexPath) - 1) + 4,
                            row.y + (row.h - 16) / 2,
                            16,
                            16)

                    if indexPath in self._expanded:
                        render.DrawTreeItemButton(self, dc, rect,
                                                  wx.CONTROL_EXPANDED)
                    else:
                        render.DrawTreeItemButton(self, dc, rect)

                dc.SetPen(wx.BLACK_PEN)
                dc.DrawLine(0, row.y + row.h, w, row.y + row.h)
        finally:
            dc.EndDrawing()

    def _OnLeftUpContent(self, evt):
        self._ProcessLeftUpContent(evt.GetX(), evt.GetY(), evt.CmdDown())

    def _OnRightUpContent(self, evt):
        self._ProcessRightUpContent(evt.GetX(), evt.GetY())

    def _OnLeftDClickContent(self, evt):
        self._ProcessLeftDClickContent(evt.GetX(), evt.GetY())

    def _OnLeftDownHeader(self, evt):
        if self._headerMouseState == 1:
            self._headerView.CaptureMouse()
            self._headerMouseState = 2
            self._resizingOrigin = evt.GetX()
        else:
            evt.Skip()

    def _OnLeftUpHeader(self, event):
        if self._headerMouseState == 2:
            self._headerView.ReleaseMouse()
            wx.SetCursor(wx.STANDARD_CURSOR)
            self._headerMouseState = 0
        else:
            evt = wx.PyCommandEvent(wxEVT_COMMAND_HEADER_LCLICKED)
            evt.indexPath = self.HeaderHitTest(event.GetX(), event.GetY())
            evt.SetEventObject(self)
            self.ProcessEvent(evt)

    def _OnRightUpHeader(self, event):
        evt = wx.PyCommandEvent(wxEVT_COMMAND_HEADER_RCLICKED)
        evt.indexPath = self.HeaderHitTest(event.GetX(), event.GetY())
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

    def _OnMotionHeader(self, evt):
        x, y = evt.GetX(), evt.GetY()
        w, h = self.GetClientSizeTuple()

        if self._headerMouseState in [0, 1]:
            # This assumes that _bounds contains the headers from the
            # top down; see the sort in header drawing code.

            for indexPath, xx, yy, ww, hh in self._bounds:
                if x >= xx and x < xx + ww:
                    if min(x - xx, xx + ww - x) <= 4:
                        if x > 4 and x < w - 4:
                            if self._headerMouseState == 0:
                                if x - xx > xx + ww - x:
                                    left, right = (indexPath, indexPath[:-1] + (indexPath[-1] + 1,))
                                    for tpl in self._bounds:
                                        if tpl[0] == right:
                                            rx, _, rw, _ = tpl[1:]
                                            break
                                    self._resizingHeaders = (left, xx, ww, right, rx, rw)
                                else:
                                    left, right = (indexPath[:-1] + (indexPath[-1] - 1,), indexPath)
                                    for tpl in self._bounds:
                                        if tpl[0] == left:
                                            lx, _, lw, _ = tpl[1:]
                                            break
                                    self._resizingHeaders = (left, lx, lw, right, xx, ww)

                                self._headerMouseState = 1
                                wx.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
                            return

            if self._headerMouseState == 1:
                self._headerMouseState = 0
                wx.SetCursor(wx.STANDARD_CURSOR)
        elif self._headerMouseState == 2:
            left, lx, lw, right, rx, rw = self._resizingHeaders

            if x < lx + 20:
                x = lx + 20
            if x > rx + rw - 20:
                x = rx + rw - 20

            totalWeight = self._headerSizes[left] + self._headerSizes[right]
            self._headerSizes[left] = 1.0 * (x - lx) / (lw + rw) * totalWeight
            self._headerSizes[right] = totalWeight - self._headerSizes[left]

            self.Refresh()

    def _OnLeaveHeader(self, evt):
        if self._headerMouseState == 1:
            self._headerMouseState = 0
            wx.SetCursor(wx.STANDARD_CURSOR)

    def _OnCellClicked(self, cell, evt):
        x, y = cell.GetPositionTuple()
        self._ProcessLeftUpContent(x + evt.GetX(), y + evt.GetY(), evt.CmdDown())

    def _OnCellDClicked(self, cell, evt):
        x, y = cell.GetPositionTuple()
        self._ProcessLeftDClickContent(x + evt.GetX(), y + evt.GetY())

    def _OnCellRightClicked(self, cell, evt):
        x, y = cell.GetPositionTuple()
        self._ProcessRightUpContent(x + evt.GetX(), y + evt.GetY())

    def HitTestContent(self, xc, yc):
        """
        Returns the index path for the row at (xc, yc) or None.
        """
        for indexPath, row in self._visibleRows.items():
            if yc >= row.y and yc < row.y + row.h:
                return indexPath
        return None

    def _ProcessLeftDClickContent(self, x, y):
        evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_LEFT_DCLICK)
        evt.indexPath = self.HitTestContent(x, y)
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

    def _ProcessRightUpContent(self, x, y):
        evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_RCLICKED)
        evt.indexPath = self.HitTestContent(x, y)
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

    def _ProcessLeftUpContent(self, xc, yc, ctrl):
        for indexPath, row in self._visibleRows.items():
            if self.GetRowChildrenCount(indexPath):
                x, y, w, h = (24 * (len(indexPath) - 1) + 4,
                              row.y + (row.h - 16) / 2,
                              16,
                              16)

                if xc >= x and xc < x + w and \
                   yc >= y and yc < y + h:
                    self.Toggle(indexPath)
                    break
        else:
            indexPath = self.HitTestContent(xc, yc)
            if indexPath is None:
                for indexPath in set(self._selection):
                    self._Deselect(indexPath)
            else:
                if ctrl:
                    if indexPath in self._selection:
                        self._Deselect(indexPath)
                    else:
                        if self.__style & ULTTREE_SINGLE_SELECTION:
                            for path in set(self._selection):
                                self._Deselect(path)
                        self._Select(indexPath)
                else:
                    already = False
                    for path in set(self._selection):
                        if path == indexPath:
                            already = True
                        else:
                            self._Deselect(path)
                    if not already:
                        self._Select(indexPath)

                self.Refresh()

#}


#==============================================================================
# Test

class TestCell(CellBase):
    def __init__(self, *args, **kwargs):
        super(TestCell, self).__init__(*args, **kwargs)

        self.__text = wx.StaticText(self, wx.ID_ANY, '')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__text, 0, wx.ALL, 3)
        self.SetSizer(sizer)

        wx.EVT_PAINT(self, self.OnPaint)

    def OnPaint(self, evt):
        evt.Skip()

        dc = wx.PaintDC(self)
        w, h = self.GetSizeTuple()
        dc.SetPen(wx.Pen(wx.Colour(150, 150, 150)))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, w, h)

    def SetLabel(self, label):
        self.__text.SetLabel(label)

    def GetIdentifier(self):
        return 'StaticText'


class HtmlCell(CellBase):
    def __init__(self, *args, **kwargs):
        super(HtmlCell, self).__init__(*args, **kwargs)

        from wx.html import HtmlWindow
        self.__html = HtmlWindow(self, wx.ID_ANY)
        self.__html.SetPage('<html><head></head><body>And span several columns.<br /><font size="5">Any widget can play.</font><br /><b>This is a wx.HtmlWindow</b></body></html>')

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__html, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def GetIdentifier(self):
        return 'HtmlCell'


class Test(UltimateTreeCtrl):
    cells = ('Root', [('Cell #1', [('Subcell #1.1', [])]),
                      ('Cell #2', [('Subcell #2.1', [('Subsubcell #2.1.1', [])]),
                                   ('Subcell #2.2', [])]),
                      ('Dummy cell', []),
                      ('Dummy cell', [])])

                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', []),
                      ## ('Dummy cell', [])])

    _headers = ('Root', [ ('Task', []),
                          ('Cat1',
                           [('SCat 1.1', []),
                            ('SCat 1.2', [])]),
                          ('Cat2',
                           []),
                          ('Cat3',
                           [('Scat 3.1', []),
                            ('SCat 3.2',
                             [('Scat 3.2.1', []),
                              ('Scat 3.2.2', [])])])])

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)

        EVT_ROW_SELECTED(self, self.OnCellSelected)
        EVT_ROW_DESELECTED(self, self.OnCellDeselected)
        EVT_HEADER_LCLICKED(self, self.OnHeaderLeftClicked)
        EVT_HEADER_RCLICKED(self, self.OnHeaderRightClicked)
        EVT_ROW_LEFT_DCLICK(self, self.OnRowDClick)
        EVT_ROW_RCLICKED(self, self.OnRowRightClick)

    def _Get(self, indexPath, data):
        obj = data
        for idx in indexPath:
            obj = obj[1][idx]
        return obj

    def GetRootHeadersCount(self):
        return len(self._headers[1])

    def GetHeaderText(self, indexPath):
        return self._Get(indexPath, self._headers)[0]

    def GetHeaderChildrenCount(self, indexPath):
        return len(self._Get(indexPath, self._headers)[1])

    def GetRootCellsCount(self):
        return len(self.cells[1])

    def GetRowChildrenCount(self, indexPath):
        return len(self._Get(indexPath, self.cells)[1])

    def GetRowHeight(self, indexPath):
        if indexPath == (1, 1):
            return 300
        return 150

    def GetRowBackgroundColour(self, indexPath):
        if indexPath == (4,):
            return wx.Colour(200, 255, 200)
        if indexPath == (3,):
            return wx.Colour(255, 200, 200)
        return wx.WHITE

    def GetCell(self, indexPath, headerPath):
        if indexPath == (1, 0) and headerPath == (1,):
            return None

        if indexPath == (1, 1) and headerPath in [(1,), (2,), (3,)]:
            return None

        cell = self.DequeueCell('StaticText', self.CreateCell)
        text = self._Get(indexPath, self.cells)[0]
        cat = self._Get(headerPath, self._headers)[0]
        cell.SetLabel('%s (%s) at %s' % (text, cat, str(indexPath)))

        return cell

    def GetColumnCell(self, indexPath, columnIndex):
        if indexPath == (1, 0):
            cell = self.DequeueCell('StaticText', self.CreateCell)
            cell.SetLabel('You can override headers')

            return cell, 1
        else:
            cell = self.DequeueCell('HtmlCell', self.CreateHtmlCell)
            return cell, 3

    def OnCellSelected(self, evt):
        print 'Select', self._Get(evt.indexPath, self.cells)[0]

    def OnCellDeselected(self, evt):
        print 'Deselect', self._Get(evt.indexPath, self.cells)[0]

    def OnRowDClick(self, evt):
        if evt.indexPath:
            print 'Double-click', self._Get(evt.indexPath, self.cells)[0]
        else:
            print 'Double-click'

    def OnRowRightClick(self, evt):
        if evt.indexPath:
            print 'Right click', self._Get(evt.indexPath, self.cells)[0]
        else:
            print 'Right click'

    def OnHeaderLeftClicked(self, evt):
        if evt.indexPath:
            print 'Click header', self._Get(evt.indexPath, self._headers)[0]
        else:
            print 'Click headers'

    def OnHeaderRightClicked(self, evt):
        if evt.indexPath:
            print 'Right click header', self._Get(evt.indexPath, self._headers)[0]
        else:
            print 'Right click headers'

    def CreateCell(self, parent):
        return TestCell(parent, wx.ID_ANY)

    def CreateHtmlCell(self, parent):
        return HtmlCell(parent, wx.ID_ANY)


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, wx.ID_ANY, 'Test frame')

        self.tree = Test(self, wx.ID_ANY)

        stripeCheck = wx.CheckBox(self, wx.ID_ANY, 'STRIPE')
        wx.EVT_CHECKBOX(stripeCheck, wx.ID_ANY, self.OnToggleStripe)

        selCheck = wx.CheckBox(self, wx.ID_ANY, 'SINGLE_SELECTION')
        wx.EVT_CHECKBOX(selCheck, wx.ID_ANY, self.OnToggleSel)

        log = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE)

        class Out(object):
            def write(self, bf):
                log.AppendText(bf)
        import sys
        sys.stdout = Out()

        sizer = wx.BoxSizer(wx.VERTICAL)
        vsz = wx.BoxSizer(wx.HORIZONTAL)
        vsz.Add(stripeCheck, 0, wx.ALL, 3)
        vsz.Add(selCheck, 0, wx.ALL, 3)
        sizer.Add(vsz, 0, wx.EXPAND)
        sizer.Add(self.tree, 1, wx.EXPAND|wx.ALL, 3)
        sizer.Add(log, 0, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(sizer)

        import os
        if os.path.exists('perspective.data'):
            self.tree.LoadPerspective(file('perspective.data', 'rb').read())

        wx.EVT_CLOSE(self, self.OnClose)

    def OnClose(self, evt):
        file('perspective.data', 'wb').write(self.tree.SavePerspective())
        evt.Skip()

    def OnToggleStripe(self, evt):
        if evt.IsChecked():
            self.tree.SetTreeStyle(self.tree.GetTreeStyle() | ULTTREE_STRIPE)
        else:
            self.tree.SetTreeStyle(self.tree.GetTreeStyle() & ~ULTTREE_STRIPE)

    def OnToggleSel(self, evt):
        if evt.IsChecked():
            self.tree.SetTreeStyle(self.tree.GetTreeStyle() | ULTTREE_SINGLE_SELECTION)
        else:
            self.tree.SetTreeStyle(self.tree.GetTreeStyle() & ~ULTTREE_SINGLE_SELECTION)


class App(wx.App):
    def OnInit(self):
        Frame().Show()
        return True


if __name__ == '__main__':
    App(0).MainLoop()
