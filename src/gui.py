"""
CaBiD GUI
---------

This module contains the GUI for CaBiD.

Author: Tony Kabilan Okeke <tko35@drexel.edu>

Functions & Classes
-------------------
ControlBox
    A custom class for creating UI controls.
GUIPanel
    The main GUI panel.
CaBiD_GUI
    The main GUI window for CaBiD.

__main__
---------
This module can be run as a script to launch the CaBiD GUI; this application
will allow the user to select a GEO dataset and perform differential gene
expression analysis on the dataset.
"""

# Import modules
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import wx

# Import CaBiD modules
from utils import datadir, CaBiD_db
from curation import datacheck

import wx.lib.mixins.inspection as wit


class ControlBox(wx.StaticBox):
    """
    Custom `StaticBox` for UI controls
    """

    def __init__(self, parent, label, inputs, **inputargs):

        assert isinstance(inputs, dict), 'inputs must be a dictionary'
        
        # Initialize the wx.StaticBox class
        super().__init__(parent, -1, label=label, style=wx.ALIGN_CENTER)

        # Create sizer
        self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)

        # Create text inputs
        self.input = dict()
        for label, input_type in inputs.items():
            if input_type == 'selector':
                # Check that appropriate arguments are provided
                if 'choices' not in inputargs:
                    raise ValueError("Must provide choices for selector")
                if 'value' not in inputargs:
                    raise ValueError("Must provide value for selector")

                # Add label
                label_text = label.replace('_', ' ').capitalize()
                self.sizer.Add(
                    wx.StaticText(self, -1, label=label_text), 0, 
                    wx.ALIGN_LEFT | wx.LEFT, 15
                )

                # Create a selector
                self.input[label] = wx.ComboBox(self, -1, inputargs['value'][label],
                    choices=inputargs['choices'][label])
                self.input[label].name = label
                self.sizer.Add(
                    self.input[label], 0, 
                    wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 15
                )

                # Bind events
                self.input[label].Bind(
                    wx.EVT_COMBOBOX, self.GetParent().onSelect
                )
            else:
                raise ValueError("Invalid input type")
        self.SetMinSize((200, -1))


class GUIPanel(wx.Panel):
    """
    UI Panel for CaBiD GUI

    Callbacks
    ---------
    onSelect
        Populate GSE selector with GSEs for selected cancer type
    onAnalyze
        Perform differential gene expression analysis on selected dataset
    
    Methods
    -------
    create_figure
        Create a figure canvas
    """

    def __init__(self, parent):
        # Initialize the wx.Panel class
        super().__init__(parent)

        # Define database connection from the parent class
        self.parent = parent
        self.db = parent.db

        # Get choices for selectors
        self.select_choices = {
            'cancer_type': (self.db
                .select("SELECT DISTINCT CANCER FROM `datasets`")['CANCER']
                .tolist()),
            'gse': []
        }

        # Create sizers
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create controls
        self.dataset_box = ControlBox(
            parent=self,
            label='Select a Dataset',
            inputs={'cancer_type': 'selector', 'gse': 'selector'},
            choices=self.select_choices,
            value={'cancer_type': '', 'gse': ''}
        )

        # Add 'Analyze' button
        self.analyze = wx.Button(self, label="Analyze")
        self.analyze.Bind(wx.EVT_BUTTON, self.onAnalyze)

        # Add controls to sizer
        left_sizer.Add(self.dataset_box.sizer, 0)
        left_sizer.AddSpacer(10)
        left_sizer.Add(self.analyze, 0, wx.ALIGN_LEFT | wx.LEFT, 50)

        # Create figure canvases
        results_top = wx.BoxSizer(wx.HORIZONTAL)
        results_bottom = wx.BoxSizer(wx.HORIZONTAL)
        right_sizer.Add(results_top, 1, wx.EXPAND)
        right_sizer.Add(results_bottom, 1, wx.EXPAND)

        # DGE Table
        self.dge_table = wx.ListCtrl(
            self, -1, size=(300, 50),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        for i, col in enumerate(['Gene', 'Fold Change', 'Adj p-value']):
            self.dge_table.InsertColumn(i, col, width=100, 
                format=wx.LIST_FORMAT_CENTER)
        results_top.Add(self.dge_table, 0, wx.ALL, 15)

        # Volcano Plot
        self.volcano = self.create_figure((500,300), {
            'title': 'Volcano Plot', 'x': 'Fold Change', 'y': '-log10(p-value)'
        })
        self.volcano['fig'].subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.15)

        # Heatmap
        self.heatmap = self.create_figure((830,300), {
            'title': 'Heatmap', 'x': 'Samples', 'y': 'Genes'
        })
        self.heatmap['fig'].subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)

        # Add figures to sizer
        results_top.Add(self.volcano['canvas'], 0, wx.ALL, 15)
        results_bottom.Add(self.heatmap['canvas'], 0, wx.EXPAND | wx.ALL, 15)

        # Add sizers to main sizer
        sizer.Add(left_sizer, 1, wx.ALIGN_LEFT | wx.ALL, 10)
        sizer.Add(right_sizer, 0, wx.EXPAND)

        # Set sizer
        self.SetSizer(sizer)


    def create_figure(self, size, labs):
        """
        Create a figure canvas
        """

        fig = Figure()
        axis = fig.add_subplot(111)
        canvas = FigureCanvas(self, -1, fig)
        canvas.SetMinSize(size)
        fig.suptitle(labs['title'])
        axis.set_xlabel(labs['x'])
        axis.set_ylabel(labs['y'])

        return dict(fig=fig, axis=axis, canvas=canvas)


    def onSelect(self, event):
        """
        Populate GSE selector with GSEs for selected cancer type
        """
        
        # Get the triggering control
        obj = event.GetEventObject()

        if obj.name == 'cancer_type':
            # Get GSEs for the selected cancer type
            gse = self.db.select(
                f"SELECT GSE FROM `datasets` WHERE CANCER = '{obj.GetValue()}'"
            )

            # Add options to GSE selector
            self.dataset_box.input['gse'].Clear()
            self.dataset_box.input['gse'].AppendItems(gse['GSE'].tolist())
            self.dataset_box.input['gse'].SetValue(gse['GSE'].tolist()[0])
        else:
            event.Skip()


    def onAnalyze(self, event):
        """
        Handle button click
        """

        # Get values from text inputs
        cancer_type = self.dataset_box.input['cancer_type'].GetValue()
        gse = self.dataset_box.input['gse'].GetValue()
        dataset = (gse, cancer_type)

        # Set wait state
        self.parent.SetStatusText("Analyzing %s..." % gse)
        self.analyze.Disable()
        wait = wx.BusyCursor()

        # Prompt if no dataset is selected
        if cancer_type == '' or gse == '':
            wx.MessageBox('Please select a dataset to analyze', 'Error')
            self.analyze.Enable()
            return

        # Retreive data from database
        self.data = self.db.retrieve_dataset(dataset)

        # Reset wait state
        self.parent.SetStatusText("Ready")
        self.analyze.Enable()
        
        print('Analyzed!')


class CaBiD_GUI(wx.Frame):
    """
    Main window class for the GUI

    Methods
    -------
    create_menu
        Create the menu bar for the GUI

    Callbacks
    ---------
    onSave
        Save generated results to a zip file
    onLoad
        Prompt user to load a csv file containing a gene expression matrix
    onExit
        Handle exit menu item click
    onAbout
        Show an 'About' dialog
    """

    def __init__(self, *args, **kwargs):
        # Initialize the wx.Frame class
        super().__init__(
            parent=None,
            title='Cancer Biomarker Discovery',
            size=(1160, 800),
            style=wx.CLOSE_BOX | wx.CAPTION,
            *args, **kwargs
        )
        
        # Check if database exists
        datacheck();

        # Connect to database
        dbpath = datadir() / 'CaBiD.db'
        self.db = CaBiD_db(dbpath)

        # Create panel and menus
        self.panel = GUIPanel(self)
        self.create_menu()
        self.CreateStatusBar()
        self.SetStatusText("Welcome to CaBiD!")


    def create_menu(self):
        """
        Create the menu bar for the GUI
        """

        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        save_item = file_menu.Append(wx.ID_SAVE, 'Save', 'Save results')
        file_menu.AppendSeparator()
        load_item = file_menu.Append(wx.ID_OPEN, 'Load', 'Load GSE matrix')
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_ANY, 'Exit', 'Exit the application')

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, 'About', 'About CaBiD')

        # Bind events
        self.Bind(wx.EVT_MENU, self.onSave, save_item)
        self.Bind(wx.EVT_MENU, self.onLoad, load_item)
        self.Bind(wx.EVT_MENU, self.onExit, exit_item)
        self.Bind(wx.EVT_MENU, self.onAbout, about_item)

        # Append menus to menu bar
        menu_bar.Append(file_menu, '&File')
        menu_bar.Append(help_menu, '&Help')
        self.SetMenuBar(menu_bar)

    
    def onSave(self, event):
        """Handle save menu item click"""
        print("Save menu item clicked")


    def onLoad(self, event):
        """Handle load menu item click"""
        print("Load menu item clicked")


    def onExit(self, event):
        """Handle exit menu item click"""
        self.Close()

    
    def onAbout(self, event):
        """Handle about menu item click"""
        wx.MessageBox(
            'Cancer Biomarker Discovery (CaBiD)\n'
            'Version 0.1\n\n'
            'Created by: Tony K. Okeke, Ali Youssef & Cooper Molloy\n'
        )


class CaBiD_App(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()
        self.frame = CaBiD_GUI()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    # Run the GUI
    # app = wx.App()
    # CaBiD_GUI().Show();
    # app.MainLoop();
    # del app

    app = CaBiD_App(redirect=False)
    app.MainLoop()
