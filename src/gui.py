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
import pandas as pd
import numpy as np
import wx

# Import CaBiD modules
from utils import datadir, CaBiD_db


class ControlBox(wx.StaticBox):
    """
    Custom `StaticBox` for UI controls
    """

    def __init__(self, parent, label, inputs, **inputargs):

        assert isinstance(inputs, dict), 'inputs must be a dictionary'
        
        # Initialize the wx.StaticBox class
        super().__init__(parent, -1, label=label)

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

                # Create a selector
                self.input[label] = wx.ComboBox(self, -1, inputargs['value'][label],
                    choices=inputargs['choices'][label])
                self.input[label].name = label
                self.sizer.Add(self.input[label], 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 7)

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
    """

    def __init__(self, parent):

        super().__init__(parent)

        pass

        # # Create a SQLite object
        # dbpath = datadir() / 'CaBiD.db'
        # if dbpath.exists():
        #     self.db = CaBiD_db(dbpath)
        # else:
        #     raise FileNotFoundError(f'Could not find database at {dbpath}')

        # # Get choices for selectors
        # self.choices = dict(
        #     cancer_type=(self.db.select("SELECT `CANCER` FROM datasets")
        #         ['CANCER'].unique().tolist()),
        #     gse=[]
        # )

        # # Create sizers
        # sizer = wx.BoxSizer(wx.HORIZONTAL)

        # # Create controls
        # self.dataset_box = ControlBox(
        #     parent=self,
        #     label='Select a Dataset',
        #     inputs={'cancer_type': 'selector', 'gse': 'selector'},
        #     choices=self.choices,
        #     value={'cancer_type': self.choices['cancer_type'][0], 'gse': ''}
        # )

        # # Add button
        # self.analyze = wx.Button(self, label="Analyze")
        # self.analyze.Bind(wx.EVT_BUTTON, self.onAnalyze)


        # # Add controls to sizer
        # sizer.Add(self.dataset_box.sizer, 0)
        # # sizer.AddSpacer(15)
        # sizer.Add(self.analyze, 0, wx.ALIGN_BOTTOM)

        # self.SetSizer(sizer)


    def onSelect(self, event):
        """
        Handle selection events
        """
        
        # obj = event.GetEventObject()

        # if obj.name == 'cancer_type':
        #     # Get GSEs for selected cancer type
        #     res = self.db.select(
        #         f"SELECT GSE FROM `datasets` WHERE CANCER = '{obj.GetValue()}'"
        #     )

        #     # Add options to GSE selector
        #     self.dataset_box.input['gse'].Clear()
        #     self.dataset_box.input['gse'].AppendItems(res['GSE'].tolist())
        #     self.dataset_box.input['gse'].SetValue(res['GSE'].tolist()[0])
        # else:
        #     event.Skip()

        pass


    def onAnalyze(self, event):
        """
        Handle button click
        """

        # Get values from text inputs
        # values = dict()
        # for label, input in self.dataset_box.input.items():
        #     values[label] = input.GetValue()
        #     if values[label] == '':
        #         raise ValueError(f"{label} cannot be empty")

        # Retreive data from database
        # self.data = self.db.retrieve_dataset()

        print('Analyze button clicked')


class CaBiD_GUI(wx.Frame):
    """
    Main window class for the GUI
    """

    def __init__(self, *args, **kwargs):
        # Initialize the wx.Frame class
        super().__init__(
            parent=None,
            title='Cancer Biomarker Discovery',
            *args, **kwargs
        )

        # Check if the database exists
        # if dbpath.exists():
        #     with CaBiD_db(dbpath) as db:
        #         if  db.check_table('expression') and db.check_table('datasets'):
        #             # Connect to the databa
        # else:
        #     flag = False

        # # Window settings
        # self.SetSize((750, 450))
        # self.panel = GUIPanel(self)


if __name__ == '__main__':
    # Run the GUI
    app = wx.App()
    frame = CaBiD_GUI()
    frame.Show()
    app.MainLoop()
    del app
