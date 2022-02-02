# -*- coding: utf-8 -*-

"""Boilerplate:
A one line summary of the module or program, terminated by a period.

Rest of the description. Multiliner

<div id = "exclude_from_mkds">
Excluded doc
</div>

<div id = "content_index">

<div id = "contributors">
Created on Fri Aug 27 17:37:58 2021
@author: Timothe
</div>
"""

import os, sys
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
    def __init__(self, function):
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
    
        
class TestApp(DefaultAppSkin):

    def __init__(self, widget_function):
        super().__init__()
        
        slider = gui_widgets.SuperSlider(span = 20)
        color_control = plot_widgets.PltColorControl()
        widget_to_test = widget_function()
        
        
        data = np.random.random((20,20,20))
        widget_to_test.add_axes( "image_axis" )
        widget_to_test.image_axis.imshow(data,zorder = 0, interpolation = "bilinear") 
        widget_to_test.image_axis.plot_data[0].set_time_axis(axis = 2, mode = "onpoint") 
        widget_to_test.image_axis.plot_data[0].connect_slider(slider)
        widget_to_test.image_axis.plot_data[0].connect_selector(color_control)
        
        widget_to_test.add_axes( "line_axis" )
        widget_to_test.line_axis.plot(np.arange(0,20)+1,np.squeeze(data[10,10,:]) + 10,zorder = 2,linewidth = 3,color = "red" )
        widget_to_test.line_axis.plot_data[0].set_time_axis(axis = 0, mode = "progress")
        widget_to_test.line_axis.plot_data[0].connect_slider(slider)
        widget_to_test.line_axis.plot([0,0],[0,19],zorder = 1,linewidth = 3,color = "blue" )   
        widget_to_test.line_axis.plot_data[1].set_time_axis(axis = 0, mode = "move")
        widget_to_test.line_axis.plot_data[1].connect_slider(slider)
        
        widget_to_test.figure.set_tight_layout(False)
                    
        central_widget = QtWidgets.QWidget()
        l = QGridLayout(central_widget)
        l.addWidget(widget_to_test,0,0,1,5)
        l.addWidget(slider,1,0,1,4)
        l.addWidget(color_control,1,4,1,1)
        
        color_control.valueChanged.emit()
        
        self.setCentralWidget(central_widget)
        self.addToolBar(NavigationToolbar(widget_to_test, self))
        
    
        
    



if __name__ == "__main__":
    # progname = os.path.basename(sys.argv[0])
    # qApp = QtWidgets.QApplication(sys.argv)

    # aw = TestApp(plot_widgets.CanvasHandle)
    # aw.setWindowTitle("%s" % progname)
    # aw.show()
    # sys.exit(qApp.exec_())
    
    progname = os.path.basename(sys.argv[0])
    qApp = QtWidgets.QApplication(sys.argv)

    aw = TuneableApp(test_function)
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
    