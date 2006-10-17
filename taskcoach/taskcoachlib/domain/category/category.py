import patterns

class Category(patterns.ObservableComposite):
    def __init__(self, subject, tasks=None, children=None, filtered=False, 
                 parent=None):
        super(Category, self).__init__(children=children or [], parent=parent)
        self.__subject = subject
        self.__tasks = tasks or []
        self.__filtered = filtered
        
    def __getstate__(self):
        state = super(Category, self).__getstate__()
        state.update(dict(subject=self.__subject, tasks=self.__tasks[:], 
                          filtered=self.__filtered))
        return state
        
    def __setstate__(self, state):
        super(Category, self).__setstate__(state)
        self.__subject = state['subject']
        self.__tasks = state['tasks']
        self.__filtered = state['filtered']
        
    def __repr__(self):
        return self.__subject
            
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.subject(recursive=True) == other.subject(recursive=True)
    
    def setSubject(self, newSubject):
        self.__subject = newSubject
        
    def subject(self, recursive=False):
        if recursive and self.parent():
            return '%s -> %s'%(self.parent().subject(recursive=True), 
                               self.__subject)
        else:
            return self.__subject
    
    def tasks(self, recursive=False):
        result = []
        if recursive:
            for child in self.children():
                result.extend(child.tasks(recursive))
        result.extend(self.__tasks)
        return result
    
    def addTask(self, task):
        self.__tasks.append(task)
        
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True):
        if filtered != self.__filtered:
            self.__filtered = filtered
            self.notifyObservers(patterns.Event(self, 'category.filter', 
                filtered))
        for child in self.children():
            child.setFiltered(filtered)

    def contains(self, task, treeMode=False):
        containedTasks = self.tasks(recursive=True)
        if treeMode:
            tasksToInvestigate = task.family()
        else:
            tasksToInvestigate = [task] + task.ancestors()
        for task in tasksToInvestigate:
            if task in containedTasks:
                return True
        return False