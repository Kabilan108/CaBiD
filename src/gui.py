"""
CaBiD GUI
---------

This module contains the GUI for CaBiD.

Author: Ali Youssef <amy57@drexel.edu>

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
from matplotlib import gridspec
from pathlib import Path
import wx

# Import CaBiD modules
from dge import dge, plot_volcano, plot_heatmap
from utils import datadir, CaBiD_db
from curation import datacheck


class ControlBox(wx.StaticBox):
    """
    Custom `StaticBox` for UI controls
    """

    class TextInput(wx.BoxSizer):
        """
        Custom text input with label
        """

        def __init__(self, parent, label):
            # Initialize BoxSizer
            super().__init__(wx.HORIZONTAL)

            # Define font
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                           wx.FONTWEIGHT_NORMAL)
            
            # Create label
            self.label = wx.StaticText(parent, label=label)
            self.label.SetFont(font)
            self.Add(self.label, 1, wx.RIGHT)

            # Create text input
            self.field = wx.TextCtrl(parent, size=(60,20), style=wx.TE_PROCESS_ENTER)
            self.field.name = self.label.GetLabelText()  # type: ignore
            self.field.SetFont(font)
            self.Add(self.field, 1)


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
            elif input_type == 'text':
                # Create a text input
                _label = f"{label.replace('__', '-').replace('_', ' ')}"
                self.input[label] = self.TextInput(self, _label)
                self.sizer.Add(self.input[label], 0, wx.EXPAND | wx.ALL, 5)

                if 'value' in inputargs:
                    self.input[label].field.SetValue(inputargs['value'][label])

                # Bind events
                self.input[label].field.Bind(
                    wx.EVT_CHAR, self.GetParent().acceptInput
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
    acceptInput
        Acceptable inputs for analysis thresholds
    
    Methods
    -------
    create_figure
        Create a figure canvas
    populate_dge_table
        Populate the DGE table with results
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

        # Define controls for analysis
        self.threshold_box = ControlBox(
            parent=self,
            label='Thresholds for Analysis',
            inputs={'p__value': 'text', 'fold_change': 'text'},
            value={'p__value': '0.05', 'fold_change': '2'}
        )

        # Add controls to sizer
        left_sizer.Add(self.dataset_box.sizer, 0)
        left_sizer.AddSpacer(10)
        left_sizer.Add(self.threshold_box.sizer, 0)
        left_sizer.AddSpacer(10)
        left_sizer.Add(self.analyze, 0, wx.ALIGN_LEFT | wx.LEFT, 50)

        # Create figure canvases
        results_top = wx.BoxSizer(wx.HORIZONTAL)
        results_bottom = wx.BoxSizer(wx.HORIZONTAL)
        right_sizer.Add(results_top, 1, wx.EXPAND)
        right_sizer.Add(results_bottom, 1, wx.EXPAND)

        # DGE Table
        self.dge_table = wx.ListCtrl(
            self, -1, size=(310, 300),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        for i, col in enumerate(['Gene', 'Fold Change', 'Adj p-value']):
            self.dge_table.InsertColumn(i, col, width=100, 
                format=wx.LIST_FORMAT_CENTER)
        results_top.Add(self.dge_table, 0, wx.ALL, 15)

        # Volcano Plot
        self.volcano = self.create_figure((500,300), 'volcano', {
            'title': 'Normal - Cancer', 'x': 'Fold Change',
            'y': '-log10(p-value)'
        })
        self.volcano['fig'].subplots_adjust(  # type: ignore
            left=0.15, right=0.9, top=0.85, bottom=0.15
        )

        # Heatmap
        self.heatmap = self.create_figure((830,300), 'heatmap', {
            'title': 'Heatmap', 'x': 'Samples', 'y': 'Genes'
        })
        self.heatmap['fig'].subplots_adjust(  # type: ignore
            left=0.1, right=0.9, top=0.9, bottom=0.15
        )

        # Add figures to sizer
        results_top.Add(self.volcano['canvas'], 0, wx.ALL, 15)
        results_bottom.Add(self.heatmap['canvas'], 0, wx.EXPAND | wx.ALL, 15)

        # Add sizers to main sizer
        sizer.Add(left_sizer, 1, wx.ALIGN_LEFT | wx.ALL, 10)
        sizer.Add(right_sizer, 0, wx.EXPAND)

        # Set sizer
        self.SetSizer(sizer)


    def create_figure(self, size, figtype, labs):
        """
        Create a figure canvas
        """

        fig = Figure()
        if figtype == 'heatmap':
            gs = gridspec.GridSpec(
                2, 4, width_ratios=[0.1, 0.04, 1, 0.02], height_ratios=[0.25, 1],
                wspace=0.02, hspace=0.02
            )
            axis = dict(
                samp_dendro=fig.add_subplot(gs[1, 0]),
                gene_dendro=fig.add_subplot(gs[0, 2]),
                anot=fig.add_subplot(gs[1, 1]),
                hmap=fig.add_subplot(gs[1, 2]),
                cbar=fig.add_subplot(gs[1, 3]),
            )
            for ax in axis.values():
                if ax is not axis['hmap']:
                    ax.set_axis_off()
                ax.set_xticks([])
                ax.set_yticks([])
            axis['hmap'].text(
                0.5, 0.5, 'Heatmap', ha='center', va='center', fontsize=20
            )
            canvas = FigureCanvas(self, -1, fig)
            canvas.SetMinSize(size)
        elif figtype == 'volcano':
            axis = fig.add_subplot(111)
            canvas = FigureCanvas(self, -1, fig)
            canvas.SetMinSize(size)
            axis.set_title(labs['title'])
            axis.set_xlabel(labs['x'])
            axis.set_ylabel(labs['y'])
        else:
            raise ValueError("Invalid figure type")

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


    def acceptInput(self, event):
        """
        Acceptable inputs for analysis thresholds
        """

        key = event.GetKeyCode()

        # Allow ASCII numerals
        if ord('0') <= key <= ord('9'):
            event.Skip()
            return

        # Allow decimal point
        if key == ord('.'):
            event.Skip()
            return

        # Allow backspace, arrow keys, home, end, delete
        if key in [wx.WXK_BACK, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_HOME,
                   wx.WXK_END, wx.WXK_DELETE]:
            event.Skip()
            return

        return


    def onAnalyze(self, event):
        """
        Handle button click
        """

        # Get values from text inputs
        cancer_type = self.dataset_box.input['cancer_type'].GetValue()
        gse = self.dataset_box.input['gse'].GetValue()
        dataset = (gse, cancer_type)
        self.p_thr = float(self.threshold_box.input['p__value'].field.GetValue())
        self.fc_thr = float(self.threshold_box.input['fold_change'].field.GetValue())

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

        # Run analysis
        self.dge = dge(self.data, self.fc_thr, self.p_thr)

        # Populate DGE table
        self.populate_dge_table()

        # Volcano Plot
        plot_volcano(self.volcano['axis'], self.dge, self.fc_thr, self.p_thr)
        self.volcano['canvas'].draw()  # type: ignore

        # Heatmap
        plot_heatmap(self.heatmap['fig'], self.heatmap['axis'], self.data)
        self.heatmap['canvas'].draw()  # type: ignore

        # Reset wait state
        self.parent.SetStatusText("Ready")
        self.analyze.Enable()


    def populate_dge_table(self):
        """
        Populate the DGE table in the GUI
        """

        # Clear table
        self.dge_table.DeleteAllItems()

        # Keep only significant genes
        dge = (self.dge[self.dge['adj pval'] < self.p_thr]
            .sort_values(['fc', 'adj pval'], ascending=[False, True]))
        dge['fc'] = dge['fc'].apply(lambda x: f"{x:.2f}")
        dge['adj pval'] = dge['adj pval'].apply(lambda x: f"{x:.2e}")

        # If no DGEs, display message
        if dge.shape[0] == 0:
            wx.MessageBox('No DGEs found', 'No DGEs')

        # Add rows
        for i in range(len(dge)):
            fc = dge.iloc[i]['fc']
            p = dge.iloc[i]['adj pval']

            self.dge_table.InsertItem(i, dge.iloc[i]['gene'])
            self.dge_table.SetItem(i, 1, fc)
            self.dge_table.SetItem(i, 2, p)


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
            size=(1100, 750),
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

        # Bind event for closing the window
        self.Bind(wx.EVT_CLOSE, self.onExit)


    def create_menu(self):
        """
        Create the menu bar for the GUI
        """

        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        save_item = file_menu.Append(wx.ID_SAVE, 'Save', 'Save results')
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
        """Save analysis results to a folder"""
        
        # Check if analysis has been run
        if not hasattr(self.panel, 'dge'):
            wx.MessageBox('No results to save', 'Error')
            return
        
        # Prompt user to select a folder to save results to
        dlg = wx.DirDialog(self, "Choose a directory:", 
                           style=wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = Path(dlg.GetPath())
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Define filename prefixes
        cancer_type = self.panel.dataset_box.input['cancer_type'].GetValue()
        gse = self.panel.dataset_box.input['gse'].GetValue()
        dataset = cancer_type + '_' + gse

        # Save results
        self.SetStatusText("Saving results to %s..." % path)
        (self.panel.dge
            .to_csv(path / f"{dataset}_DGE.csv", index=False))  # type: ignore
        (self.panel.volcano['fig']
            .savefig(path / f"{dataset}_volcano.png"))  # type: ignore
        (self.panel.heatmap['fig']
            .savefig(path / f"{dataset}_heatmap.png"))  # type: ignore
        self.SetStatusText("Ready")

        # Show dialog
        wx.MessageBox('Results saved', 'Success')


    def onLoad(self, event):
        """Handle load menu item click"""
        
        wx.MessageBox(
            'This feature is not yet implemented.\n',
            'Please see github.com/kabilan108/CaBiD for updates',
        )


    def onExit(self, event):
        """Close the window"""

        self.db.close()
        self.Destroy()

    
    def onAbout(self, event):
        """Display an 'About' dialog"""

        wx.MessageBox("""
        Cancer Biomarker Discovery (CaBiD)
        Version 0.1

        This tool was designed to help identify biomarkers for cancer diagnosis.
        The provided thresholds are used to filter the results of a differential
        gene expression analysis. The results are displayed in a table and
        volcano plot.
        The heatmaps are generated after excluding the low variance genes from 
        the dataset.

        Created by: Tony K. Okeke, Ali Youssef & Cooper Molloy
        """)


if __name__ == '__main__':
    # Run the GUI
    app = wx.App()
    CaBiD_GUI().Show();
    app.MainLoop();
    del app
