from tkinter import *
from tkinter import filedialog
from tkinter import ttk, font
from functools import partial
from contextlib import suppress
import os
import re
import configparser

class App:

    ### KEY BINDINGS
    def ctrlU(self, event):
        self.askForPath()

    def ctrlO(self, event):
        self.openFile()

    def ctrlX(self, event):
        self.clearFilters()
    
    def ctrlQ(self, event):
        self.quitProgram()

    def upArrow(self, event):
        self.scrollUp()

    def downArrow(self, event):
        self.scrollDown()

    def returnKey(self, event):
        self.openFile()

    ### WINDOW MANAGEMENT
    def quitProgram(self):
        self.root.destroy()

    ### FILTER CONDITION
    def isFiltered(self, path):
        deconstructedPathSplit = path.replace(self.current_path + '\\','').split('\\')
        hasChildren = bool(self.tree.get_children(self.pathList[path]))
        # Looks for any string of characters with a . and 2-8 alphabetical characters at the end of the string to identify a file
        isAFile = not(bool(re.match('^(.*\.(?!(\w{2,8})$))?[^.]*$', deconstructedPathSplit[-1])))
        containsFilterInFileName = self.filterVar.get().lower() in deconstructedPathSplit[-1].lower()
        if (hasChildren or (isAFile and containsFilterInFileName)):
            # Should not be deleted
            return False
        else:
            # Should be deleted
            return True
    
    ### FONT CONTROLS
    def increaseFont(self):
        self.fontSize += 1
        self.rowHeight += 2
        self.configureAppFont()

    def decreaseFont(self):
        self.fontSize -= 1
        self.rowHeight -= 2
        self.configureAppFont()

    def configureAppFont(self):
        self.style.configure('Treeview', font=('Arial', self.fontSize), rowheight=self.rowHeight)
        self.style.configure('TLabel', font=('Arial', self.fontSize + 2))
        self.style.configure('TButton', font=('Arial', self.fontSize))
        self.writeToConfig()

    ### SEARCH FUNCTION
    def updateFilters(self, var, indx, mode):
        if len(self.filterVar.get()) > len(self.previousVar):
            self.previousVar = self.filterVar.get()
            itemsToDelete = filter(self.isFiltered, self.pathList.copy())
            for i in itemsToDelete:
                self.tree.delete(self.pathList[i])
                self.pathList.pop(i)
        elif len(self.filterVar.get()) < len(self.previousVar):
            self.previousVar = self.filterVar.get()
            if len(self.filterVar.get()) == 0:
                self.refreshTree()
        else:
            pass

    def clearFilters(self):
        self.filterVar.set('')

    ### SCROLLING
    def scrollUp(self):
        if bool(self.tree.next(self.tree.focus())):
            with suppress(TypeError):
                self.tree.focus(self.tree.next())

    def scrollDown(self):
        if bool(self.tree.prev(self.tree.focus())):
            with suppress(TypeError):
                self.tree.focus(self.tree.prev())

    ### ROOT PATH DIALOG
    def askForPath(self):
        self.current_path = filedialog.askdirectory()
        self.writeToConfig()
        self.refreshTree()

    ### CONFIGURATION
    def writeToConfig(self):
        cfgfile = open('config.ini', 'w')
        config = configparser.ConfigParser()
        config.add_section('GENERAL')
        config.set('GENERAL', 'path', self.current_path)
        config.set('GENERAL', 'fontSize', str(self.fontSize))
        config.set('GENERAL', 'rowHeight', str(self.rowHeight))
        config.write(cfgfile)
        cfgfile.close()

    ### DIRECTORY SEARCH AND OS MANAGEMENT
    def refreshTree(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        self.pathList.clear()
        self.idList.clear()
        self.walkPath()

    def openFile(self):
        id = self.tree.focus()
        os.startfile(self.idList[id])
        
    def walkPath(self):
        for root, dirs, files in os.walk(self.current_path):
            for file in files:
                if (root == self.current_path):
                    id = self.tree.insert('', 'end', text=file)
                    self.pathList[os.path.join(root, file)] = id
                    self.idList[id] = os.path.join(root, file)
                else:
                    id = self.tree.insert(self.pathList[root], 'end', text=file)
                    self.pathList[os.path.join(root, file)] = id
                    self.idList[id] = os.path.join(root, file) 
            for dir in dirs:
                if (root == self.current_path):
                    id = self.tree.insert('', 'end', text=dir)
                    self.pathList[os.path.join(root, dir)] = id
                    self.idList[id] = os.path.join(root, dir)
                else:
                    id = self.tree.insert(self.pathList[root], 'end', text=dir)
                    self.pathList[os.path.join(root, dir)] = id  
                    self.idList[id] = os.path.join(root, dir)

    # Main Window
    root = Tk()
    root.option_add('*tearOff', FALSE)

    # App variables (includes variables to be written to config)
    pathList = {}
    idList = {}
    current_path = os.getcwd()
    fontSize = 13
    rowHeight = 24        
    previousVar = ""

    # Window Style (controls font sizes)
    style = ttk.Style(root)
    style.configure('Treeview', font=('Arial', fontSize), rowheight=rowHeight)
    style.configure('TLabel', font=('Arial', fontSize + 2))
    style.configure('TButton', font=('Arial', fontSize))
    
    # Main Frame
    mainframe = ttk.Frame(root, padding='5 5 5 5')
    
    # Directory Tree
    fileviewl = ttk.Label(mainframe, text='File View', style='TLabel')
    tree = ttk.Treeview(mainframe, style="Treeview")
    treeScrollY = ttk.Scrollbar(mainframe, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=treeScrollY.set)
    
    # Search Bar
    searchl = ttk.Label(mainframe, text='Filter Files', style='TLabel')
    filterVar = StringVar()
    search = ttk.Entry(mainframe, textvariable=filterVar)

    def __init__(self):

        # Initialize window, add title, and set hotkey functions
        self.root.title('Consent Form Database')
        self.root.geometry('800x300')
        self.root.bind('<Control-u>',self.ctrlU)
        self.root.bind('<Control-o>',self.ctrlO)
        self.root.bind('<Control-x>',self.ctrlX)
        self.root.bind('<Control-q>',self.ctrlQ)
        self.root.bind('<Down>',self.downArrow)
        self.root.bind('<Up>',self.upArrow)
        self.root.bind('<Return>',self.returnKey)

        # Set up menu bar and include File and Font controls there
        menubar = Menu(self.root)
        menu_file = Menu(menubar)
        menu_file.add_command(label='Set/Update Root Folder Path',command=partial(self.askForPath),accelerator='Ctrl+U')
        menu_file.add_command(label='Open Selected File',command=partial(self.openFile),accelerator='Ctrl+O')
        menu_file.add_command(label='Clear Filter',command=partial(self.clearFilters),accelerator='Ctrl+X')
        menu_file.add_separator()
        menu_file.add_command(label='Quit Program',command=partial(self.quitProgram),accelerator='Ctrl+Q')
        menubar.add_cascade(menu=menu_file, label='File')
        menu_font = Menu(menubar)
        menu_font.add_command(label='Increase Font Size',command=partial(self.increaseFont))
        menu_font.add_command(label='Decrease Font Size',command=partial(self.decreaseFont))
        menubar.add_cascade(menu=menu_font, label='Font')
        self.root.config(menu=menubar)

        # Configure grid placement for items in the window
        self.mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
        self.fileviewl.grid(column=0, row=0, sticky=(N))
        self.searchl.grid(column=1, row=0, columnspan=3, sticky=(N))
        self.tree.grid(column=0, row=1, rowspan=3, sticky=(N, W, E, S))
        self.treeScrollY.grid(column=1, row=1, rowspan=3, sticky=(N, S))
        self.search.grid(column=2,row=1, columnspan=2, sticky=(N, W, E))

        # Include new buttons and configure them to the grid
        clearFilterButton = ttk.Button(self.mainframe, text='Clear Filter', style='TButton', command=partial(self.clearFilters))
        clearFilterButton.grid(column=2,row=2,columnspan=2,sticky=(S,W,E))
        updatePathButton = ttk.Button(self.mainframe, text='Update Folder Path', style='TButton', command=partial(self.askForPath))
        updatePathButton.grid(column=2,row=3,sticky=(S, W, E))
        openFileButton = ttk.Button(self.mainframe, text='Open File', style='TButton', command=partial(self.openFile))
        openFileButton.grid(column=3,row=3,sticky=(W, E, S))
        
        # Trace changes to the search bar to update the filtered items in the directory tree
        self.filterVar.trace_add('write', partial(self.updateFilters))
        
        # Configure sizing weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=3)
        self.mainframe.columnconfigure(2, weight=2)
        self.mainframe.rowconfigure(1, weight=3)
        
        # If there's no config file, create the config file with the default values
        if not os.path.isfile('config.ini'):
            self.writeToConfig()

        # Open the config file and load in the values from there
        with open('config.ini') as f:
            config = configparser.RawConfigParser(allow_no_value=True)
            config.readfp(f)
            self.current_path = config.get('GENERAL', 'path')
            self.fontSize = config.getint('GENERAL', 'fontSize')
            self.rowHeight = config.getint('GENERAL', 'rowHeight')
        
        self.configureAppFont()
        self.walkPath()
        
        

app = App()
app.root.mainloop()        