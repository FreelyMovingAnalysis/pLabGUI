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
Created on Mon Jan 31 17:59:58 2022
@author: Timothe
</div>
"""

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore, QtWidgets
import matplotlib
from PyQt5.QtCore import Qt , QObject , Signal, Slot
import numpy as np

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

class CanvasHandle(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    offset = 0.05
    spacing = 0.1
    align = "vstack"
    
    def add_axes(self,name = "", axfunc = None, **axkwargs):
        
        def get_rect(index):
            positions = np.linspace(self.offset/2,1-(self.offset/2),len(self.axes)+2)
            if self.align == "hstack" :
                rect = [positions[index]+self.spacing ,self.offset, positions[index+1]-self.spacing, 1-self.offset ]
            if self.align == "vstack" :
                rect = [self.offset, positions[index]+self.spacing , 1-self.offset , positions[index+1]-self.spacing ]
            print(rect)
            return rect
        
        if axfunc is None :
            axfunc = DynamicAxis
        rect = axkwargs.get("rect",None)
        if rect is None :
            for index, ax in enumerate(self.axes) :
                ax.set_position( get_rect(index), "original" )
            rect = get_rect(len(self.axes))

        ax = axfunc(parent_fig = self.fig_canvas, rect = rect , **axkwargs)
        self.__setattr__(name,ax)
        self.fig_canvas.add_axes(ax)
        #self.fig_canvas.add_subplot(ax)
        self.axes.append(ax)

    def __init__(self, parent=None, width=5, height=4, dpi=100, *args, **kwargs):
        self.fig_canvas = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig_canvas)
        #FigureCanvas.__init__(self, self.fig)
        self.axes = []

        self.fig_canvas.subplots_adjust(left=0.03,right=0.97,
                            bottom=0.03,top=0.97,
                            hspace=0.2,wspace=0.2)

        self.setParent(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()
        
    def add_subscription(self,plot_data):
        all_controllers = {plt_data.get_slider() for axes in self.axes for plt_data in axes.plot_data if not plt_data.get_slider() is None and not plt_data is plot_data}
        if not plot_data.slider in all_controllers:
            plot_data.data_change.connect(self.draw)
        
    
class PolarAxis(matplotlib.projections.PolarAxes):
    def __init__(self,parent_fig = None,rect = [0,0,1,1], **kwargs):
        super().__init__(parent_fig,rect = rect, **kwargs)
        
class DynamicAxis(matplotlib.axes.Axes):
    def __init__(self,parent_fig = None,rect = [0.1,0.1,0.8,0.8], **kwargs):
        super().__init__(parent_fig,rect = rect,**kwargs)
        self.plot_data = []
        
        
                        
    def imshow(self,*args,**kwargs):
        args = list(args) 
        plot_data = saved_plot_data(args.pop(0),parent = self)
        plot_data.set_args(args), plot_data.set_kwargs(kwargs)
        plot_data.set_plot_type("imshow")
                      
        self.plot_data.append(plot_data)
        
    def plot(self,*args,**kwargs):
        args = list(args) 
        plot_data_x = np.array(args.pop(0))
        try :
            plot_data_y = np.array(args.pop(0))
        except IndexError :
            plot_data_y = plot_data_x
            plot_data_x = np.arange(0,len(plot_data_y))
            
        plot_data = saved_lineplot_data((plot_data_x,plot_data_y),parent = self)
        plot_data.set_args(args), plot_data.set_kwargs(kwargs)
        plot_data.set_plot_type("plot")
          
        self.plot_data.append(plot_data)
        
    @property
    def _renderer(self):
        try :
            self._renderer_obj
        except AttributeError :
            self._renderer_obj = self.figure.canvas.renderer
        finally :
            return self._renderer_obj
        
    def _prerender_clear(self):
        #This allows to clear axis without calling clear that removes the settings that my be done via user interface
        while self.artists != []:
            self.artists[0].remove()
        
        while self.lines != []:
            self.lines[0].remove()
        
        while self.images != []:
            self.images[0].remove()
            
        while self.patches != []:
            self.patches[0].remove()
                
    def draw(self, renderer=None, inframe=False):
        self._prerender_clear()
        if len(self.plot_data) == 0 :
            return
        for plot_data in self.plot_data :
            
            function = eval(f"super(DynamicAxis,self).{plot_data.plt_type}")
            function(*plot_data.get_data(),*plot_data.args,**plot_data.kwargs)
        #self.autoscale(True,"both")
        
        if renderer is None :
            renderer = self._renderer
        
        super().draw(renderer)
                    
class saved_plot_data(QObject):
    
    data_change = Signal()
        
    def __init__(self,data,parent = None, *args,**kwargs):
        super().__init__()
        self.set_data(data)
        self.set_args(args)
        self.set_kwargs(kwargs)
        self.set_time_axis()
        self.parent = parent
        
    @property
    def index(self):
        try :
            return self.slider.value
        except AttributeError:
            return 0
        
    def set_plot_type(self,typename):
        self.plt_type = typename
        
    def set_data(self,data):
        self.data = np.array(data)
        
    def set_kwargs(self,kwargs):
        self.kwargs = kwargs
                    
    def set_args(self,args):
        self.args = tuple(args)
        
    def connect_slider(self,slider):
        if self.time_axis is None :
            raise AttributeError("You must call set_time_axis for this data before being able to connect it to a time setter")
        self.slider = slider
        self.parent.figure.canvas.add_subscription(self)
        self.slider.ValueChange.connect(self.emit_signal)
        
    def get_slider(self):
        try :
            return self.slider
        except AttributeError:
            return None
        
    def connect_selector(self,selector):
        selector.valueChanged.connect(lambda: self.update_kwarg(selector.value))
            
    def set_time_axis(self,axis = None,mode = "onpoint"):
        """
        Available modes : onpoint , progress, r_progress 
        (cooresponds to 0,1,2)
        Defaults to onpoint

        """
        available_modes = {"onpoint":0,"progress":1,"r_progress":2,"move":3}
        if mode in available_modes.keys() :
            mode = available_modes[mode]
        else :
            raise ValueError(f"Available modes are : {available_modes.keys()}")
        self.time_axis = axis
        self.time_mode = mode
        
        
    def _get_tuple(self,data):
        sliceind = []
        for dimension in range(len(data.shape)):
            if self.time_axis == dimension :
                if self.time_mode == 0:
                    sliceind.append(slice(self.index,self.index+1))
                elif self.time_mode == 1:
                    sliceind.append(slice(None,self.index))
                elif self.time_mode == 2:
                    sliceind.append(slice(self.index,None))
                else :
                    raise ValueError(f"Timemode erroneous value : {self.time_mode}")
            else :
                sliceind.append(slice(None))
        return tuple(sliceind)
    
    def get_data(self):
        if self.time_axis is None :        
            return (self.data,)
        if self.time_mode < 3:
            return (np.squeeze(self.data[self._get_tuple(self.data)]),)
        else :
            return (self.data + self.index,)
    
    def update_kwarg(self,keyval, value = None):
        self.kwargs.update(keyval)
        self.emit_signal()   
        
    def emit_signal(self):
        self.data_change.emit()
    
    
class saved_lineplot_data(saved_plot_data):
    
    def set_data(self,data):
        self.x_data = data[0]
        self.y_data = data[1]
        
    
    def get_data(self):
        if self.time_axis is None :        
            return (self.x_data,self.y_data)
        if self.time_mode < 3:
            return (self.x_data[self._get_tuple(self.x_data)],self.y_data[self._get_tuple(self.y_data)])
        else :
            return (self.x_data + self.index,self.y_data)

class PltQComboBox(QComboBox):
    
    valueChanged = Signal()
    
    def __init__(self,parent = None, option = "default"):
        super().__init__(parent)
        self.option_name = option
        self.currentIndexChanged.connect(self.valueChanged.emit)
        
    @property
    def value(self):
        return {self.option_name : self.currentText()}
    
    def addItems(self,items):
        super().addItems(items)
        self.setMaxVisibleItems(6)
        
class PltQLineEdit(QLineEdit):
    
    valueChanged = Signal()
    def __init__(self, option = "", init_value = "" ,vartype = None):
        super().__init__(str(init_value))
        self.option_name = option
        self.vartype = vartype
        self.editingFinished.connect(self.valueChanged.emit)
        
    @property
    def value(self):
        return {self.option_name : self.text()} if self.vartype is None else {self.option_name : self.vartype(self.text())}
            
class PltColorControl(QtWidgets.QWidget):
    
    valueChanged = Signal()
    
    def __init__(self):
        super().__init__()
        
        l = QGridLayout(self)
        
        self.cmap = PltQComboBox(self, option = "cmap")
        self.cmap.valueChanged.connect(self.valueChanged.emit)
        self.cmap.setMaximumWidth(50)
        self.cmap.addItems(['gray','jet', 'geo' ,'plasma', 'inferno', 'magma','Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu','GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'bone', 'pink','spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper','PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu','RdYlBu', 'RdYlGn', 'Spectral',
            'coolwarm', 'bwr', 'seismic','Pastel1', 'Pastel2', 'Paired', 'Accent','Dark2', 'Set1', 'Set2', 'Set3','tab10', 'tab20',
            'tab20b', 'tab20c','flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern','gnuplot', 'gnuplot2', 'CMRmap',
            'cubehelix', 'brg', 'hsv','gist_rainbow', 'rainbow', 'viridis', 'nipy_spectral', 'gist_ncar', 'None'])
        
        
        self.vmax = PltQLineEdit(option = "vmax", init_value = 1,vartype = float)
        self.vmax.valueChanged.connect(self.valueChanged.emit)
        self.vmax.setMaximumWidth(30)
        self.vmin = PltQLineEdit(option = "vmin", init_value = 0,vartype = float)
        self.vmin.valueChanged.connect(self.valueChanged.emit)
        self.vmin.setMaximumWidth(30)
        self.IAuto = QCheckBox("Auto")
        self.IAuto.setChecked(True)
        
        l.addWidget(QLabel("Colormap"),0,0,1,1,Qt.AlignCenter)
        l.addWidget(self.cmap,1,0,1,1,Qt.AlignCenter)
        l.addWidget(QLabel("Vmin"),0,1,1,1,Qt.AlignCenter)
        l.addWidget(self.vmin,1,1,1,1,Qt.AlignCenter)
        l.addWidget(QLabel("Vmax"),0,2,1,1,Qt.AlignCenter)
        l.addWidget(self.vmax,1,2,1,1,Qt.AlignCenter)
                
    @property
    def value(self):
        return {**self.cmap.value,**self.vmax.value,**self.vmin.value}
        
        
    
        