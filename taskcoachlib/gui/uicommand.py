import wx, task, patterns, config, gui, meta, help, command
from i18n import _


class UICommandContainer(object):
    ''' Mixin with wx.Menu or wx.ToolBar (sub)class. '''

    def appendUICommands(self, uiCommands, uiCommandNames):
        for commandName in uiCommandNames:
            if commandName:
                if type(commandName) == type(''): # commandName can be a string or an actual UICommand
                    commandName = uiCommands[commandName]
                self.appendUICommand(commandName)
            else:
                self.AppendSeparator()


class UICommand(object):
    ''' Base user interface command. An UICommand is some action that can be associated
        with menu's and/or toolbars. It contains the menutext and helptext to be displayed,
        code to deal with wx.EVT_UPDATE_UI and methods to attach the command to a menu or
        toolbar. Subclasses should implement doCommand() and optionally override enabled(). '''
        
    bitmap = 'nobitmap'
    menuText = '?'
    helpText = ''
    kind = wx.ITEM_NORMAL

    def __init__(self, *args, **kwargs):
        super(UICommand, self).__init__(*args, **kwargs)
        self._id = wx.NewId()

    def id(self):
        return self._id

    def appendToMenu(self, menu, window):
        self.menuItem = wx.MenuItem(menu, self._id, self.menuText, self.helpText, 
            self.kind)
        if self.bitmap:
            self.menuItem.SetBitmap(wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_MENU, 
                (16, 16)))
        menu.AppendItem(self.menuItem)
        self.bind(window)

    def appendToToolBar(self, toolbar, window):
        bitmap = wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_TOOLBAR, 
            toolbar.GetToolBitmapSize())
        toolbar.AddLabelTool(self._id, '',
            bitmap, wx.NullBitmap, self.kind, 
            shortHelp=wx.MenuItem.GetLabelFromText(self.menuText),
            longHelp=self.helpText)
        self.bind(window)

    def bind(self, window):
        window.Bind(wx.EVT_MENU, self.onCommandActivate, id=self._id)
        window.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI, id=self._id)

    def onCommandActivate(self, event):
        ''' For Menu's and ToolBars, activating the command is not
            possible when not enabled, because menu items and toolbar
            buttons are disabled through onUpdateUI. For other controls such 
            as the ListCtrl and the TreeCtrl the EVT_UPDATE_UI event is not 
            sent, so we need an explicit check here. Otherwise hitting return 
            on an empty selection in the ListCtrl would bring up the 
            TaskEditor. '''
        if self.enabled():
            self.doCommand(event)

    def doCommand(self, event):
        raise NotImplementedError

    def onUpdateUI(self, event):
        event.Enable(bool(self.enabled()))

    def enabled(self):
        ''' Can be overridden in a subclass. '''
        return True


class SettingsCommand(UICommand):
    ''' SettingsCommands are saved in the settings (a ConfigParser). '''
    
    section = 'view' # default section

    def __init__(self, settings, *args, **kwargs):
        self.settings = settings
        super(SettingsCommand, self).__init__(*args, **kwargs)


class BooleanSettingsCommand(SettingsCommand):
    def appendToMenu(self, *args, **kwargs):
        super(BooleanSettingsCommand, self).appendToMenu(*args, **kwargs)
        self.check()
        
    def check(self):
        checked = self.checked()
        self.menuItem.Check(checked)
        if self.commandNeedsToBeActivated(checked):
            self.sendCommandActivateEvent()

    def sendCommandActivateEvent(self):
        self.onCommandActivate(wx.CommandEvent(0, self._id))
        

class UICheckCommand(BooleanSettingsCommand):
    kind = wx.ITEM_CHECK
    bitmap = 'on' # 'on' == checkmark shaped image

    def commandNeedsToBeActivated(self, checked):
        return not checked

    def checked(self):
        return self.settings.getboolean(self.section, self.setting)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(event.IsChecked()))


class UIRadioCommand(BooleanSettingsCommand):
    kind = wx.ITEM_RADIO
    bitmap = None
    
    def commandNeedsToBeActivated(self, checked):
        return checked
        
    def checked(self):
        return self.settings.get(self.section, self.setting) == str(self.value)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(self.value))


class IOCommand(UICommand):
    def __init__(self, iocontroller, *args, **kwargs):
        self.iocontroller = iocontroller
        super(IOCommand, self).__init__(*args, **kwargs)


class MainWindowCommand(UICommand):
    def __init__(self, mainwindow, *args, **kwargs):
        self.mainwindow = mainwindow
        super(MainWindowCommand, self).__init__(*args, **kwargs)


class EffortCommand(UICommand):
    def __init__(self, effortList, *args, **kwargs):
        super(EffortCommand, self).__init__(*args, **kwargs)
        self.effortList = effortList

        
class ViewerCommand(UICommand):
    def __init__(self, viewer, *args, **kwargs):
        self.viewer = viewer
        super(ViewerCommand, self).__init__(*args, **kwargs)


class FilterCommand(UICommand):
    def __init__(self, filteredTaskList, *args, **kwargs):
        self.filteredTaskList = filteredTaskList
        super(FilterCommand, self).__init__(*args, **kwargs)


class UICommandsCommand(UICommand):
    def __init__(self, uiCommands, *args, **kwargs):
        self.uiCommands = uiCommands
        super(UICommandsCommand, self).__init__(*args, **kwargs)    

# Mixins: 

class NeedsSelection(object):
    def enabled(self):
        return self.viewer.curselection()
 
class NeedsSelectedTasks(NeedsSelection):
    def enabled(self):
        return super(NeedsSelectedTasks, self).enabled() and self.viewer.isShowingTasks()

class NeedsSelectedEffort(NeedsSelection):
    def enabled(self):
        return super(NeedsSelectedEffort, self).enabled() and self.viewer.isShowingEffort()
               
class NeedsTasks(object):
    def enabled(self):
        return self.viewer.isShowingTasks()
        
class NeedsItems(object):
    def enabled(self):
        return self.viewer.size() 

 
# Commands:

class FileOpen(IOCommand):
    bitmap = 'fileopen'
    menuText = '&Open...\tCtrl+O'
    helpText = 'Open a %s file'%meta.name

    def doCommand(self, event):
        self.iocontroller.open()

class FileMerge(IOCommand):
    bitmap = 'merge'
    menuText = '&Merge...'
    helpText = 'Merge tasks from another file with the current file'

    def doCommand(self, event):
        self.iocontroller.merge()

class FileClose(IOCommand):
    bitmap = 'close'
    menuText = '&Close'
    helpText = 'Close the current file'

    def doCommand(self, event):
        self.iocontroller.close()

class FileSave(IOCommand):
    bitmap = 'save'
    menuText = '&Save\tCtrl+S'
    helpText = 'Save the current file'

    def doCommand(self, event):
        self.iocontroller.save()
        
    def enabled(self):
        return self.iocontroller.needSave()

class FileSaveAs(IOCommand):
    bitmap = 'saveas'
    menuText = 'S&ave as...'
    helpText = 'Save the current file under a new name'

    def doCommand(self, event):
        self.iocontroller.saveas()
        
class FileSaveSelection(NeedsSelectedTasks, IOCommand, ViewerCommand):
    bitmap = 'saveselection'
    menuText = 'Sa&ve selection...'
    helpText = 'Save the selected tasks to a separate file'
    
    def doCommand(self, event):
        self.iocontroller.saveselection(self.viewer.curselection()), 

class FileQuit(MainWindowCommand):
    bitmap = 'exit'
    menuText = '&Quit\tCtrl+Q'
    helpText = 'Exit %s'%meta.name

    def doCommand(self, event):
        self.mainwindow.quit()

def getUndoMenuText():
    return '&%s\tCtrl+Z'%patterns.CommandHistory().undostr() 

class EditUndo(UICommand):
    bitmap = 'undo'
    menuText = getUndoMenuText()
    helpText = 'Undo the last command'

    def doCommand(self, event):
        patterns.CommandHistory().undo()

    def onUpdateUI(self, event):
        event.SetText(getUndoMenuText())
        super(EditUndo, self).onUpdateUI(event)

    def enabled(self):
        return patterns.CommandHistory().hasHistory()


def getRedoMenuText():
    return '&%s\tCtrl+Y'%patterns.CommandHistory().redostr() 

class EditRedo(UICommand):
    bitmap = 'redo'
    menuText = getRedoMenuText()
    helpText = 'Redo the last command that was undone'

    def doCommand(self, event):
        patterns.CommandHistory().redo()

    def onUpdateUI(self, event):
        event.SetText(getRedoMenuText())
        super(EditRedo, self).onUpdateUI(event)

    def enabled(self):
        return patterns.CommandHistory().hasFuture()


class EditCut(NeedsSelectedTasks, FilterCommand, ViewerCommand): # FIXME: only works for tasks atm
    bitmap = 'cut'
    menuText = 'Cu&t\tCtrl+X'
    helpText = 'Cut the selected task(s) to the clipboard'

    def doCommand(self, event):
        cutCommand = command.CutTaskCommand(self.filteredTaskList, self.viewer.curselection())
        cutCommand.do()

class EditCopy(NeedsSelectedTasks, FilterCommand, ViewerCommand): # FIXME: only works for tasks atm
    bitmap = 'copy'
    menuText = '&Copy\tCtrl+C'
    helpText = 'Copy the selected task(s) to the clipboard'

    def doCommand(self, event):
        copyCommand = command.CopyTaskCommand(self.filteredTaskList, self.viewer.curselection())
        copyCommand.do()

class EditPaste(FilterCommand):
    bitmap = 'paste'
    menuText = '&Paste\tCtrl+V'
    helpText = 'Paste task(s) from the clipboard'

    def doCommand(self, event):
        pasteCommand = command.PasteTaskCommand(self.filteredTaskList)
        pasteCommand.do()

    def enabled(self):
        return task.Clipboard()


class EditPasteAsSubtask(FilterCommand, ViewerCommand):
    bitmap = 'pasteassubtask'
    menuText = 'P&aste as subtask'
    helpText = 'Paste task(s) as children of the selected task'

    def doCommand(self, event):
        pasteCommand = command.PasteTaskAsSubtaskCommand(self.filteredTaskList, 
            self.viewer.curselection())
        pasteCommand.do()

    def enabled(self):
        return task.Clipboard() and self.viewer.curselection()


class SelectAll(NeedsItems, ViewerCommand):
    menuText = '&All\tCtrl+A'
    helpText = 'Select all items in the current view'

    def doCommand(self, event):
        self.viewer.selectall()


class SelectCompleted(NeedsTasks, ViewerCommand):
    menuText = '&Completed tasks' 
    helpText = 'Select all completed tasks'

    def doCommand(self, event):
        self.viewer.select_completedTasks(), 


class InvertSelection(NeedsItems, ViewerCommand):
    menuText = '&Invert selection\tCtrl+I'
    helpText = 'Select unselected items and unselect selected items'

    def doCommand(self, event):
        self.viewer.invertselection()


class ClearSelection(NeedsSelection, ViewerCommand):
    menuText = 'C&lear selection'
    helpText = 'Unselect all items'

    def doCommand(self, event):
        self.viewer.clearselection()


class ViewAllTasks(FilterCommand, SettingsCommand, UICommandsCommand):
    menuText = '&All tasks'
    helpText = 'Show all tasks (reset all filters)'
    bitmap = 'viewalltasks'
    
    def doCommand(self, event):
        for uiCommandName in ['viewcompletedtasks', 'viewinactivetasks', 
            'viewoverduetasks', 'viewactivetasks', 'viewoverbudgettasks', 
            'viewcompositetasks']:
            uiCommand = self.uiCommands[uiCommandName]
            self.settings.set(uiCommand.section, uiCommand.setting, 'True')
            uiCommand.check()
        
        self.settings.set(self.section, 'tasksdue', 'Unlimited')    
        for uiCommandName in ['viewdueunlimited', 'viewduetoday', 'viewduetomorrow',
            'viewdueworkweek', 'viewdueweek', 'viewduemonth', 'viewdueyear']:
            self.uiCommands[uiCommandName].check()
        self.filteredTaskList.setViewAll()


class ViewCompletedTasks(FilterCommand, UICheckCommand):
    menuText = '&Completed'
    helpText = 'Show/hide completed tasks'
    setting ='completedtasks'

    def doCommand(self, event):
        super(ViewCompletedTasks, self).doCommand(event)
        self.filteredTaskList.setViewCompletedTasks(event.IsChecked())


class ViewInactiveTasks(FilterCommand, UICheckCommand):
    menuText = '&Inactive'
    helpText = 'Show/hide inactive tasks (tasks with a start date in the future)'
    setting = 'inactivetasks'

    def doCommand(self, event):
        super(ViewInactiveTasks, self).doCommand(event)
        self.filteredTaskList.setViewInactiveTasks(event.IsChecked())

class ViewOverDueTasks(FilterCommand, UICheckCommand):
    menuText = '&Over due'
    helpText = 'Show/hide over due tasks (tasks with a due date in the past)'
    setting = 'overduetasks'
    
    def doCommand(self, event):
        super(ViewOverDueTasks, self).doCommand(event)
        self.filteredTaskList.setViewOverDueTasks(event.IsChecked())

class ViewActiveTasks(FilterCommand, UICheckCommand):
    menuText = '&Active'
    helpText = 'Show/hide active tasks (tasks with a start date in the past and a due date in the future)'
    setting = 'activetasks'
    
    def doCommand(self, event):
        super(ViewActiveTasks, self).doCommand(event)
        self.filteredTaskList.setViewActiveTasks(event.IsChecked())    
 
class ViewOverBudgetTasks(FilterCommand, UICheckCommand):
    menuText = 'Over &budget'
    helpText = 'Show/hide tasks that are over budget'
    setting = 'overbudgettasks'
    
    def doCommand(self, event):
        super(ViewOverBudgetTasks, self).doCommand(event)
        self.filteredTaskList.setViewOverBudgetTasks(event.IsChecked())
               

class ViewCompositeTasks(ViewerCommand, FilterCommand, UICheckCommand):
    menuText = 'Tasks with subtasks'
    helpText = 'Show/hide tasks with subtasks'
    setting = 'compositetasks'
    
    def doCommand(self, event):
        super(ViewCompositeTasks, self).doCommand(event)
        self.viewer.setViewCompositeTasks(event.IsChecked())
        
class ViewColumn(ViewerCommand, UICheckCommand):
    
    def doCommand(self, event):
        super(ViewColumn, self).doCommand(event)
        self.viewer.showColumn(self.column, event.IsChecked())
        
        
class ViewStartDate(ViewColumn):
    menuText = '&Start date'
    helpText = 'Show/hide start date column'
    setting = 'startdate'
    column = 'Start date'

class ViewDueDate(ViewColumn):
    menuText = '&Due date'
    helpText = 'Show/hide due date column'
    setting = 'duedate'
    column = 'Due date'

class ViewDaysLeft(ViewColumn):
    menuText = 'Days &left'
    helpText = 'Show/hide days left column'
    setting = 'daysleft'
    column ='Days left'

class ViewCompletionDate(ViewColumn):
    menuText = 'Co&mpletion date'
    helpText = 'Show/hide completion date column'
    setting = 'completiondate'
    column = 'Completion date'

class ViewTimeSpent(ViewColumn):
    menuText = '&Time spent'
    helpText = 'Show/hide time spent column'
    setting = 'timespent'
    column = 'Time spent'

class ViewTotalTimeSpent(ViewColumn):
    menuText = 'T&otal time spent'
    helpText = 'Show/hide total time spent column (total time includes time spent on subtasks)'
    setting = 'totaltimespent'
    column = 'Total time spent'
    
class ViewBudget(ViewColumn):
    menuText = '&Budget'
    helpText = 'Show/hide budget column'
    setting = 'budget'
    column = 'Budget'
    
class ViewTotalBudget(ViewColumn):
    menuText = 'Total budget'
    helpText = 'Show/hide total budget column (total budget includes budget for subtasks)'
    setting = 'totalbudget'
    column = 'Total budget'
    
class ViewBudgetLeft(ViewColumn):
    menuText = 'Budget &left'
    helpText = 'Show/hide budget left'
    setting = 'budgetleft'
    column = 'Budget left'
        
class ViewTotalBudgetLeft(ViewColumn):
    menuText = 'Total budget left'
    helpText = 'Show/hide total budget left (total budget left includes budget left for subtasks)'
    setting = 'totalbudgetleft'
    column = 'Total budget left'

class ViewExpandAll(ViewerCommand):
    menuText = '&Expand all tasks'
    helpText = 'Expand all tasks with subtasks'
    
    def doCommand(self, event):
        self.viewer.expandAll()

class ViewExpandSelected(NeedsSelectedTasks, ViewerCommand):
    bitmap = 'viewexpand'
    menuText = 'E&xpand'
    helpText = 'Expand the selected tasks with subtasks'
    
    def doCommand(self, event):
        self.viewer.expandSelectedItems()
            
class ViewCollapseAll(ViewerCommand):
    menuText = '&Collapse all tasks'
    helpText = 'Collapse all tasks with subtasks'
    
    def doCommand(self, event):
        self.viewer.collapseAll()
 
class ViewCollapseSelected(NeedsSelectedTasks, ViewerCommand):
    bitmap = 'viewcollapse'
    menuText = 'C&ollapse'
    helpText = 'Collapse the selected tasks with subtasks'
    
    def doCommand(self, event):
        self.viewer.collapseSelectedItems()
             
        
class ViewToolBar(MainWindowCommand, UIRadioCommand):
    setting = 'toolbar'

    def doCommand(self, event):
        super(ViewToolBar, self).doCommand(event)
        self.mainwindow.setToolBarSize(self.value)

class ViewToolBarHide(ViewToolBar):
    value = None
    menuText = '&Hide'
    helpText = 'Hide the toolbar'

class ViewToolBarSmall(ViewToolBar):
    value = (16, 16)
    menuText = '&Small images' 
    helpText = 'Small images (16x16) on the toolbar'

class ViewToolBarMedium(ViewToolBar):
    value = (22, 22)
    menuText = '&Medium-sized images'
    helpText = 'Medium-sized images (22x22) on the toolbar'

class ViewToolBarBig(ViewToolBar):
    value = (32, 32)
    menuText = '&Large images'
    helpText = 'Large images (32x32) on the toolbar'


class ViewFindDialog(MainWindowCommand, UICheckCommand):
    menuText = '&Find dialog'
    helpText = 'Show/hide find dialog'
    setting = 'finddialog'
    
    def doCommand(self, event):
        super(ViewFindDialog, self).doCommand(event)
        self.mainwindow.showFindDialog(event.IsChecked())


class ViewStatusBar(MainWindowCommand, UICheckCommand):
    menuText = 'Status&bar'
    helpText = 'Show/hide status bar'
    setting = 'statusbar'

    def doCommand(self, event):
        super(ViewStatusBar, self).doCommand(event)
        self.mainwindow.GetStatusBar().Show(event.IsChecked())
        self.mainwindow.SendSizeEvent()


class ViewSplashScreen(UICheckCommand):
    menuText = 'S&plash screen'
    helpText = 'Show/skip splash screen when starting %s'%meta.name
    section = 'window'
    setting = 'splash'


class ViewDueBefore(FilterCommand, UIRadioCommand):
    setting = 'tasksdue'

    def doCommand(self, event):
        super(ViewDueBefore, self).doCommand(event)
        self.filteredTaskList.viewTasksDueBefore(self.value) 


class ViewDueToday(ViewDueBefore):
    value = 'Today'
    menuText = '&Today'
    helpText = 'Only show tasks due today'

class ViewDueTomorrow(ViewDueBefore):
    value = 'Tomorrow'
    menuText = 'T&omorrow' 
    helpText = 'Only show tasks due today and tomorrow'

class ViewDueWorkWeek(ViewDueBefore):
    value = 'Workweek'
    menuText = 'Wo&rk week' 
    helpText = 'Only show tasks due this work week (i.e. before Friday)'

class ViewDueWeek(ViewDueBefore):
    value = 'Week'
    menuText = '&Week'
    helpText = 'Only show tasks due this week (i.e. before Sunday)'

class ViewDueMonth(ViewDueBefore):
    value = 'Month'
    menuText = '&Month'
    helpText = 'Only show tasks due this month'

class ViewDueYear(ViewDueBefore):
    value = 'Year'
    menuText = '&Year'
    helpText = 'Only show tasks due this year'

class ViewDueUnlimited(ViewDueBefore):
    value = 'Unlimited'
    menuText = '&Unlimited'
    helpText = 'Show all tasks' 

class ViewLanguage(MainWindowCommand, UIRadioCommand):
    setting = 'language'

    def __init__(self, language, menuText, helpText, *args, **kwargs):
        self.value = language
        self.menuText = menuText
        self.helpText = helpText
        super(ViewLanguage, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        if self.settings.get(self.section, self.setting) == self.value:
            return
        self.settings.set(self.section, self.setting, self.value)
        dialog = wx.MessageDialog(self.mainwindow,
            'This setting will take effect after you restart %s'%meta.name,
            'Language setting', wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()    
    
    
    
class TaskNew(MainWindowCommand, FilterCommand, UICommandsCommand, SettingsCommand):
    bitmap = 'new'
    menuText = '&New task...\tINS' 
    helpText = 'Insert a new task'

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewTaskCommand(self.filteredTaskList),
            self.uiCommands, self.settings, bitmap=self.bitmap)
        editor.Show(show)
        return editor


class TaskNewSubTask(NeedsSelectedTasks, MainWindowCommand,
        FilterCommand, ViewerCommand, UICommandsCommand, SettingsCommand):
    bitmap = 'newsubtask'
    menuText = 'New &subtask...\tCtrl+INS'
    helpText = 'Insert a new subtask into the selected task'

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewSubTaskCommand(self.filteredTaskList, 
                self.viewer.curselection()),
            self.uiCommands, self.settings, bitmap='new')
        editor.Show(show)
        return editor


class TaskEdit(NeedsSelectedTasks, MainWindowCommand, FilterCommand, 
        ViewerCommand, UICommandsCommand, SettingsCommand):

    bitmap = 'edit'
    menuText = '&Edit task...'
    helpText = 'Edit the selected task'

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.EditTaskCommand(self.filteredTaskList, 
                self.viewer.curselection()), self.uiCommands, self.settings)
        editor.Show(show)
        return editor


class TaskMarkCompleted(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    bitmap = 'markcompleted'
    menuText = '&Mark completed'
    helpText = 'Mark the selected task(s) completed'

    def doCommand(self, event):
        markCompletedCommand = command.MarkCompletedCommand(self.filteredTaskList, 
            self.viewer.curselection())
        markCompletedCommand.do()

    def enabled(self):
        return super(TaskMarkCompleted, self).enabled() and \
            [task for task in self.viewer.curselection() if not task.completed()]


class TaskDelete(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    bitmap = 'delete'
    menuText = '&Delete task\tCtrl+D'
    helpText = 'Delete the selected task(s)'

    def doCommand(self, event):
        deleteCommand = command.DeleteTaskCommand(self.filteredTaskList, 
            self.viewer.curselection())
        deleteCommand.do()


class EffortNew(NeedsSelectedTasks, MainWindowCommand, EffortCommand,
        ViewerCommand, UICommandsCommand):
    bitmap = 'start'
    menuText = '&New effort'
    helpText = 'Add a effort period to the selected task(s)'
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow, 
            command.NewEffortCommand(self.effortList, self.viewer.curselection()),
            self.uiCommands)
        editor.Show()
        return editor 

class EffortEdit(NeedsSelectedEffort, MainWindowCommand, EffortCommand, 
        ViewerCommand, UICommandsCommand):
    bitmap = 'edit'
    menuText = '&Edit effort'
    helpText = 'Edit the selected effort period(s)'
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow,
            command.EditEffortCommand(self.effortList, 
                self.viewer.curselection()), self.uiCommands)
        editor.Show()
        return editor

class EffortDelete(NeedsSelectedEffort, EffortCommand, ViewerCommand):
    bitmap = 'delete'
    menuText = '&Delete effort'
    helpText = 'Delete the selected effort period(s)'

    def doCommand(self, event):
        delete = command.DeleteEffortCommand(self.effortList,
            self.viewer.curselection())
        delete.do()


class EffortStart(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    bitmap = 'start'
    menuText = '&Start tracking effort'
    helpText = 'Start tracking effort for the selected task(s)'
    adjacent = False
    
    def doCommand(self, event):
        start = command.StartEffortCommand(self.filteredTaskList, self.viewer.curselection(),
            adjacent=self.adjacent)
        start.do()
        
    def enabled(self):
        if not self.viewer.isShowingTasks():
            return False
        return [task for task in self.viewer.curselection() if not
            (task.isBeingTracked() or task.completed() or task.inactive())]


class EffortStartAdjacent(EffortStart):
    menuText = 'S&tart tracking from last stop time'
    helpText = 'Start tracking effort for the selected task(s) with start time ' \
         'equal to end time of last effort'
    adjacent = True
        
    def enabled(self):
        return (self.filteredTaskList.maxDateTime() is not None) and super(EffortStartAdjacent, self).enabled()


class EffortStop(FilterCommand):
    bitmap = 'stop'
    menuText = 'St&op tracking effort'
    helpText = 'Stop tracking effort for the active task(s)'

    def doCommand(self, event):
        stop = command.StopEffortCommand(self.filteredTaskList)
        stop.do()

    def enabled(self):
        return bool([task for task in self.filteredTaskList if task.isBeingTracked()])


class HelpCommand(UICommand):
    bitmap = 'help'

class HelpTasks(HelpCommand):
    menuText = '&Tasks'
    helpText = 'Help about the possible states of tasks'

    def doCommand(self, event):
        help.Tasks()

class HelpColors(HelpCommand):
    menuText = '&Colors'
    helpText = 'Help about the possible colors of tasks'

    def doCommand(self, event):
        help.Colors()


class InfoCommand(UICommand):
    bitmap = 'info'

class HelpAbout(InfoCommand):
    menuText = '&About'
    helpText = 'Version and contact information about %s'%meta.name

    def doCommand(self, event):
        help.About()

class HelpLicense(InfoCommand):
    menuText = '&License'
    helpText = '%s license'%meta.name

    def doCommand(self, event):
        help.License()


class MainWindowRestore(MainWindowCommand):
    menuText = '&Restore'
    helpText = 'Restore the window to its previous state'
    bitmap = 'restore'

    def doCommand(self, event):
        self.mainwindow.restore(event)
    


class UICommands(dict):
    def __init__(self, mainwindow, iocontroller, viewer, settings, 
            filteredTaskList, effortList):
        super(UICommands, self).__init__()
    
        # File commands
        self['open'] = FileOpen(iocontroller)
        self['merge'] = FileMerge(iocontroller)
        self['close'] = FileClose(iocontroller)
        self['save'] = FileSave(iocontroller)
        self['saveas'] = FileSaveAs(iocontroller)
        self['saveselection'] = FileSaveSelection(iocontroller, viewer)
        self['quit'] = FileQuit(mainwindow)

        # menuEdit commands
        self['undo'] = EditUndo()
        self['redo'] = EditRedo()
        self['cut'] = EditCut(filteredTaskList, viewer)
        self['copy'] = EditCopy(filteredTaskList, viewer)
        self['paste'] = EditPaste(filteredTaskList)
        self['pasteassubtask'] = EditPasteAsSubtask(filteredTaskList, viewer)

        # Selection commands
        self['selectall'] = SelectAll(viewer)
        self['selectcompleted'] = SelectCompleted(viewer)
        self['invertselection'] = InvertSelection(viewer)
        self['clearselection'] = ClearSelection(viewer)

        # View commands
        self['viewalltasks'] = ViewAllTasks(filteredTaskList, settings, self)
        self['viewcompletedtasks'] = ViewCompletedTasks(filteredTaskList, 
            settings)
        self['viewinactivetasks'] = ViewInactiveTasks(filteredTaskList,
            settings)
        self['viewactivetasks'] = ViewActiveTasks(filteredTaskList,
            settings)    
        self['viewoverduetasks'] = ViewOverDueTasks(filteredTaskList,
            settings)    
        self['viewoverbudgettasks'] = ViewOverBudgetTasks(filteredTaskList,
            settings)
        self['viewcompositetasks'] = ViewCompositeTasks(viewer, filteredTaskList,
            settings)
            
        self['viewstartdate'] = ViewStartDate(viewer, settings)
        self['viewduedate'] = ViewDueDate(viewer, settings)
        self['viewdaysleft'] = ViewDaysLeft(viewer, settings)
        self['viewcompletiondate'] = ViewCompletionDate(viewer, settings)
        self['viewbudget'] = ViewBudget(viewer, settings)
        self['viewtotalbudget'] = ViewTotalBudget(viewer, settings)
        self['viewtimespent'] = ViewTimeSpent(viewer, settings)
        self['viewtotaltimespent'] = ViewTotalTimeSpent(viewer, settings)
        self['viewbudgetleft'] = ViewBudgetLeft(viewer, settings)
        self['viewtotalbudgetleft'] = ViewTotalBudgetLeft(viewer, settings)

        self['viewexpandall'] = ViewExpandAll(viewer)
        self['viewcollapseall'] = ViewCollapseAll(viewer)
        self['viewexpandselected'] = ViewExpandSelected(viewer)
        self['viewcollapseselected'] = ViewCollapseSelected(viewer)
        
        self['viewlanguageenglish'] = ViewLanguage('en', _('&English'),
            _('Show English user interface after restart'), mainwindow, settings)
        self['viewlanguagedutch'] = ViewLanguage('nl', _('&Dutch'), 
            _('Show Dutch user interface after restart'), mainwindow, settings)
        
        self['toolbarhide'] = ViewToolBarHide(mainwindow, settings)
        self['toolbarsmall'] = ViewToolBarSmall(mainwindow, settings)
        self['toolbarmedium'] = ViewToolBarMedium(mainwindow, settings)
        self['toolbarbig'] = ViewToolBarBig(mainwindow, settings)
        self['viewfinddialog'] = ViewFindDialog(mainwindow, settings)
        self['viewstatusbar'] = ViewStatusBar(mainwindow, settings)
        self['viewsplashscreen'] = ViewSplashScreen(settings)

        self['viewduetoday'] = ViewDueToday(filteredTaskList, settings)
        self['viewduetomorrow'] = ViewDueTomorrow(filteredTaskList, settings)
        self['viewdueworkweek'] = ViewDueWorkWeek(filteredTaskList, settings)
        self['viewdueweek'] = ViewDueWeek(filteredTaskList, settings)
        self['viewduemonth'] = ViewDueMonth(filteredTaskList, settings)
        self['viewdueyear'] = ViewDueYear(filteredTaskList, settings)
        self['viewdueunlimited'] = ViewDueUnlimited(filteredTaskList, settings)

        # Task menu
        self['new'] = TaskNew(mainwindow, filteredTaskList, self, settings)
        self['newsubtask'] = TaskNewSubTask(mainwindow, filteredTaskList, 
            viewer, self, settings)
        self['edit'] = TaskEdit(mainwindow, filteredTaskList, viewer, self, settings)
        self['markcompleted'] = TaskMarkCompleted(filteredTaskList, viewer)
        self['delete'] = TaskDelete(filteredTaskList, viewer)
        
        # Effort menu
        self['neweffort'] = EffortNew(mainwindow, effortList, viewer, self)
        self['editeffort'] = EffortEdit(mainwindow, effortList, viewer, self)
        self['deleteeffort'] = EffortDelete(effortList, viewer)
        self['starteffort'] = EffortStart(filteredTaskList, viewer)
        self['starteffortadjacent'] = EffortStartAdjacent(filteredTaskList, viewer)
        self['stopeffort'] = EffortStop(filteredTaskList)
        
        # Help menu
        self['helptasks'] = HelpTasks()
        self['helpcolors'] = HelpColors()
        self['about'] = HelpAbout()
        self['license'] = HelpLicense()

        # Taskbar menu
        self['restore'] = MainWindowRestore(mainwindow)


