import widgets, wx, dummy, TreeCtrlTest

class TreeListCtrlTestCase(TreeCtrlTest.TreeCtrlTestCase):
    def setUp(self):
        super(TreeListCtrlTestCase, self).setUp()
        self.treeCtrl = widgets.TreeListCtrl(self.frame, self.columns(), 
            self.getItemText, self.getItemImage, self.getItemAttr,
            self.getItemId, self.getRootIndices, self.getChildIndices,
            self.onSelect, dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        imageList.Add(wx.ArtProvider_GetBitmap('task', wx.ART_MENU, (16,16)))
        self.treeCtrl.AssignImageList(imageList)

    def columns(self):
        columnHeaders = ['Tree Column'] + ['Column %d'%index for index in range(1, 5)]
        return [widgets.Column(columnHeader) for columnHeader in columnHeaders]
        
    def getItemText(self, index, columnHeader=None):
        itemText = super(TreeListCtrlTestCase, self).getItemText(index)
        if columnHeader is None:
            return itemText
        else:
            return '%s in %s'%(itemText, columnHeader)
    
    
class TreeListCtrlTest(TreeListCtrlTestCase, TreeCtrlTest.CommonTests):
    pass


class TreeListCtrlColumnsTest(TreeListCtrlTestCase):
    def setUp(self):
        super(TreeListCtrlColumnsTest, self).setUp()
        self.setTree('item')
        self.treeCtrl.refresh()
        self.visibleColumns = self.columns()[1:]
        
    def assertColumns(self):
        self.assertEqual(len(self.visibleColumns)+1, self.treeCtrl.GetColumnCount())
        for index, column in enumerate(self.visibleColumns):
            self.assertEqual(self.getItemText(0, column.header()), 
                             self.treeCtrl.GetItemText(self.treeCtrl[0], index+1))
    
    def showColumn(self, columnHeader, show=True):
        self.treeCtrl.showColumn(columnHeader, show)
        column = widgets.Column(columnHeader)
        if show:
            index = self.columns()[1:].index(column)
            self.visibleColumns.insert(index, column)
        else:
            self.visibleColumns.remove(column)
    
    def testAllColumnsVisible(self):
        self.assertColumns()
        
    def testHideColumn(self):
        self.showColumn('Column 2', False)
        self.assertColumns()
        
    def testHideLastColumn(self):
        lastColumnHeader = 'Column %d'%len(self.visibleColumns)
        self.showColumn(lastColumnHeader, False)
        self.assertColumns()
        
    def testShowColumn(self):
        self.showColumn('Column 2', False)
        self.showColumn('Column 2', True)
        self.assertColumns()
        