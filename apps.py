# -*- coding: utf-8 -*-
"""

Boilerplate:
A one line summary of the module or program, terminated by a period.

Rest of the description. Multiliner

<div id = "exclude_from_mkds">
Excluded doc
</div>

<div id = "content_index">

<div id = "contributors">
Created on Wed Feb  2 12:41:14 2022
@author: Timothe
</div>
"""

import os, sys
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

import plot_widgets, gui_widgets

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from PyQt5.QtWidgets import (QSlider, 
                             QPushButton,
                             QLineEdit, 
                             QLabel, 
                             QGroupBox,
                             QGridLayout,
                             QCheckBox,
                             QComboBox, 
                             QMenu, 
                             QSpinBox, 
                             QApplication, 
                             QStyleFactory)

import numpy as np

class DefaultAppSkin(QtWidgets.QMainWindow):
    
    def __init__(self,title= None):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if title is None :
            title = "Application main window"
        self.setWindowTitle(title)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", "ftg")
        
class TuneableApp(DefaultAppSkin):
    def __init__(self, function, **kwargs):
        super().__init__()
        
        self.pannel = QtWidgets.QWidget()
        self.setCentralWidget(self.pannel)
        
        self.figure = plot_widgets.CanvasHandle()
        self.slider = gui_widgets.SuperSlider(span = 20)
        self.color_control = plot_widgets.PltColorControl()
        
        self.layout = QGridLayout(self.pannel)
        
        function(self)
        
        self.color_control.valueChanged.emit()
        
    def clear_layout(self):
    
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    @property
    def navigation_toolbar(self):
        return NavigationToolbar

def custom_app_launcher(tuning_function,**kwargs):
    """
    example function to run : 
        ````
        def test_function(app):
    
            data = np.random.random((20,20,20))
                
            app.figure.add_axes( "image_axis" )
            app.figure.image_axis.imshow(data,zorder = 0, interpolation = "bilinear") 
            app.figure.image_axis.plot_data[0].set_time_axis(axis = 2, mode = "onpoint") 
            app.figure.image_axis.plot_data[0].connect_slider(app.slider)
            app.figure.image_axis.plot_data[0].connect_selector(app.color_control)
            
            app.figure.add_axes( "line_axis" )
            app.figure.line_axis.plot(np.arange(0,20)+1,np.squeeze(data[10,10,:]) + 10,zorder = 2,linewidth = 3,color = "red" )
            app.figure.line_axis.plot_data[0].set_time_axis(axis = 0, mode = "progress")
            app.figure.line_axis.plot_data[0].connect_slider(app.slider)
            
            app.figure.line_axis.plot([0,0],[0,19],zorder = 1,linewidth = 3,color = "blue" )   
            app.figure.line_axis.plot_data[1].set_time_axis(axis = 0, mode = "move")
            app.figure.line_axis.plot_data[1].connect_slider(app.slider)
            
            app.figure.line_axis.plot(np.arange(0,20)+1,np.squeeze(data[10,:,:]) + 5,zorder = 2,linewidth = 3,color = "green" )
            app.figure.line_axis.plot_data[2].set_time_axis(axis = 1, mode = "onpoint")
            app.figure.line_axis.plot_data[2].connect_slider(app.slider)
            
            app.figure.figure.set_tight_layout(False)
                        
            app.layout.addWidget(app.figure,0,0,1,5)
            app.layout.addWidget(app.slider,1,0,1,4)
            app.layout.addWidget(app.color_control,1,4,1,1)    
            app.addToolBar(NavigationToolbar(app.figure, app))
        ````
    """
    from PyQt5 import QtWidgets
    qApp = QtWidgets.QApplication(sys.argv)
    dlg = TuneableApp(tuning_function,**kwargs)
    dlg.show()
    _ = qApp.exec_()
    del qApp, dlg
    
    
def video_app(array):
    def function(app):
        data = array

        app.figure.add_axes( "image_axis" )
        app.figure.image_axis.imshow(data,zorder = 0, interpolation = "nearest") 
        app.figure.image_axis.plot_data[0].set_time_axis(axis = 2, mode = "onpoint") 
        app.slider.set_span(data.shape[2])
        app.figure.image_axis.plot_data[0].connect_slider(app.slider)
        app.figure.image_axis.plot_data[0].connect_selector(app.color_control)
    
        app.figure.figure.set_tight_layout(False)
    
        app.layout.addWidget(app.figure,0,0,1,5)
        app.layout.addWidget(app.slider,1,0,1,4)
        app.layout.addWidget(app.color_control,1,4,1,1)    
        app.addToolBar(app.navigation_toolbar(app.figure, app))
        
    custom_app_launcher(function)
