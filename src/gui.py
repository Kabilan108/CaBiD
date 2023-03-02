"""
CaBiD GUI
---------

This module contains the GUI for CaBiD.

Functions & Classes
-------------------


__main__
---------

"""

# Standard library imports
import sys
from functools import partial

# Import PyQt6 modules
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget
)

# Import CaBiD modules
from dge import dge, plot_volcano, plot_heatmap
from utils import datadir, CaBiD_db
from curation import datacheck

# Define constants
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
BUTTON_HEIGHT = 40


class ControlBox(QWidget):
    """
    Custom box for UI controls
    """

    def __init__(self, parent, label, inputs, **inputargs):
    
        assert isinstance(inputs, dict), "inputs must be a dictionary"

        # Initialize the QWidget
        super().__init__(parent)

        # Create the layout
        self.layout = QVBoxLayout()

        # Create the label
        self.label = QLabel(label)
        self.layout.addWidget(self.label)

        # Create the input widgets
        self.inputs = {}
        for key, value in inputs.items():
            # Add label
            text = key.replace("_", " ").capitalize()
            self.layout.addWidget(QLabel(text))

            if value == "select":
                # Check that appropriate arguments are provided
                assert "options" in inputargs, \
                    "options must be provided for select inputs"
                assert isinstance(inputargs["options"], list), \
                    "options must be a list"
                assert "value" in inputargs, \
                    "value must be provided for select inputs"

                # Create combobox
                self.inputs[key] = QComboBox()
                self.inputs[key].addItems(inputargs["options"])
                self.inputs[key].setCurrentText(inputargs["value"])
                self.layout.addWidget(self.inputs[key])

            elif value == "text":
                # Create line edit
                self.inputs[key] = QLineEdit()
                self.inputs[key].setText(inputargs["value"])
                self.layout.addWidget(self.inputs[key])

            else:
                raise ValueError(f"Invalid input type: {value}")

        # Set the layout
        self.setLayout(self.layout)


class Window(QMainWindow):
    """
    Main window for CaBiD GUI.

    Attributes
    ----------


    Methods
    -------

    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the main window.
        """
        # Initialize the QMainWindow class
        super().__init__(*args, **kwargs)

        # Window settings
        self.setWindowTitle("Cancer Biomarker Discovery, CaBiD")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._createMenuBar()
        self._createStatusBar()

        # Create central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # Create layout
        layout = QHBoxLayout()

        # Create left sidebar
        leftSidebar = QVBoxLayout()

        # Add ControlBox with 2 select inputs
        inputs = {
            "data": "select",
            "method": "select"
        }
        inputargs = {
            "options": ["TCGA", "GEO"],
            "value": "TCGA"
        }
        self.dataset_box = ControlBox(
            parent=self, 
            label="Select a Dataset", 
            inputs={'cancer_type': 'selector', 'gse': 'selector'}, 
            choices=
        )


        # Add left sidebar to layout
        layout.addLayout(leftSidebar)

        # Add layout to central widget
        centralWidget.setLayout(layout)


    def _createMenuBar(self):
        """
        Create Menu Bar.
        """

        menuBar = self.menuBar()
        
        # Create file menu
        fileMenu = QMenu("&File", self)
        fileMenu.addAction("&Open", self.openFile)
        fileMenu.addAction("&Save", self.saveFile)
        fileMenu.addAction("&Exit", self.close)
        menuBar.addMenu(fileMenu)

        # Create help menu
        helpMenu = QMenu("&Help", self)
        helpMenu.addAction("&About", self.showAbout)
        menuBar.addMenu(helpMenu)

        # Add menu bar to the main window
        self.setMenuBar(menuBar)

    
    def _createStatusBar(self):
        """Create Status Bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready", 5000)


    def openFile(self):
        pass

    def saveFile(self):
        pass

    def showAbout(self):
        pass

    def close(self):
        """Close the main window."""
        super().close()


class CaBiD(QApplication):
    """
    CaBiD GUI application.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the CaBiD GUI application.
        """
        # Initialize the QApplication class
        super().__init__(*args, **kwargs)

        # Set the window
        self.window = Window()
        self.window.show()

        # Connect to the database
        dbpath = datadir() / 'CaBiD.db'
        self.db = CaBiD_db(dbpath)

        # Connect the Model and View
        # ...

    def run(self):
        """
        Run the CaBiD GUI application.
        """

        sys.exit(self.exec())

    def close(self):
        """
        Close the CaBiD GUI application.
        """

        self.window.close()


if __name__ == "__main__":
    app = CaBiD(sys.argv)
    app.run()
