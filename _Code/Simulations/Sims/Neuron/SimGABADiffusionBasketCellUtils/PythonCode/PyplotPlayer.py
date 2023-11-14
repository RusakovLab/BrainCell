
# !!! BUGs:
#     * when the first pyplot figure is created, all NEURON widgets become smaller;
#       this happens only when "Size of text, apps, and other items" parameter in Display settings of Windows OS is greater than 100%;
#       the root cause is that the command "plt.figure()" changes the DPI awareness of the process from False to True and increases its DPI from 96 to a higher value
#     * when creating the second animation using "Pyplot (desktop)" front end, it stops shortly, the button and the slider become unresponsive and the next message is printed to console:
#           QCoreApplication::exec: The event loop is already running
#     * when _isUseOpacitiesOrColours is True and rotating the scene, the markers disappear randomly
#     * when resizing the figure to full screen, the "Max" TextBox obstructs the RangeSlider label
#       (and the same problem when showing the default random test data)

# https://matplotlib.org/stable/gallery/animation/random_walk.html

import webbrowser

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider, RangeSlider, TextBox

from scipy.special import logit, expit
import numpy as np


class PyplotPlayer:
    
    _defaultMarkerSize = 500
    
    # Used only when isDesktopOrBrowser is False
    _animationEmbedLimit = 300  # MB
    _tempHtmlFileName = 'temp.html'
    
    # Used only when _isUseOpacitiesOrColours is True
    _defaultBalance = 0
    _markerColour = 'c'
    
    # Used only when _isUseOpacitiesOrColours is False
    _alpha = 0.25
    _palette = 'viridis'
    
    
    _rangeVar = None
    _numFrames = None
    _isUseOpacitiesOrColours = None
    _isDesktopOrBrowser = None
    
    _rangeVar0To1 = None
    _rangeVar0To1Balanced = None
    _numSegms = None
    _scatter = None
    _buttonStartStop = None
    _sliderFrame = None
    _sliderOpacity = None
    _sliderRange = None
    _textBoxMin = None
    _textBoxMax = None
    
    _ani = None
    _frameIdx = -1
    _isRunning = True
    _isProgrammaticSliderFrameChange = False
    _isProgrammaticTextBoxMinMaxChange = False
    
    _balance = 0            #
    _min = None             #
    _max = None             # Used only when _isUseOpacitiesOrColours is True
    _rangeVar_min = None    #
    _rangeVar_range = None  #
    
    
    def __init__(self, x, y, z, rangeVar, numFrames, varNameWithIndexAndUnits, isUseOpacitiesOrColours, isDesktopOrBrowser, rangeVar_min, rangeVar_max):
        
        # !!! not enough to avoid "QCoreApplication::exec: The event loop is already running" message and hanging
        # plt.close('all')
        
        self._numFrames = numFrames
        self._isUseOpacitiesOrColours = isUseOpacitiesOrColours
        self._isDesktopOrBrowser = isDesktopOrBrowser
        
        if isUseOpacitiesOrColours:
            # Make a linear transformation of the data to fit [0, 1] range
            # !!! code dup. with PlotlyPlayer._initForOpacities
            rangeVar_range = rangeVar_max - rangeVar_min
            self._rangeVar0To1 = (rangeVar - rangeVar_min) / rangeVar_range
            
            self._balance = self._defaultBalance
            self._min = rangeVar_min
            self._max = rangeVar_max
            self._rangeVar_min = rangeVar_min
            self._rangeVar_range = rangeVar_range
            
            self._transformRangeVarToOpacities()    # This sets self._rangeVar0To1Balanced
        else:
            self._rangeVar = rangeVar
            
        # Create a 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        if isDesktopOrBrowser and isUseOpacitiesOrColours:
            # Reserve some space for sliders and title
            ax.set_position([0.2, 0.2, 0.6, 0.6])
            
        if isUseOpacitiesOrColours:
            # Plot the 3D point cloud
            self._scatter = ax.scatter(x, y, z, alpha=self._rangeVar0To1Balanced[0], s=self._defaultMarkerSize, c=self._markerColour, linewidths=0)
        else:
            # Create a colormap
            cmap = plt.get_cmap(self._palette)
            
            # Set the colormap normalization based on the global min and max
            norm = plt.Normalize(vmin=rangeVar_min, vmax=rangeVar_max)
            
            # Plot the 3D point cloud
            self._scatter = ax.scatter(x, y, z, c=self._rangeVar[0], alpha=self._alpha, cmap=cmap, norm=norm, s=self._defaultMarkerSize, linewidths=0)
            
            # Add a color bar to indicate the values
            colorBar = plt.colorbar(self._scatter)
            colorBar.ax.set_title(varNameWithIndexAndUnits)
            
            # Adjust the margins of the entire figure to bring the colorbar closer to the edge
            fig.subplots_adjust(right=1)
            
        # Set the aspect ratio to be equal (preserve proportions)
        ax.set_aspect('equal')
        
        # Set labels for the axes
        ax.set_xlabel('x (μm)')
        ax.set_ylabel('y (μm)')
        ax.set_zlabel('z (μm)')
        
        fig.suptitle(varNameWithIndexAndUnits)
        
        # !!! use blit=True and update method _onNewFrame when we show the extracellular sources
        interval = 0 if isDesktopOrBrowser else 1
        self._ani = FuncAnimation(fig, self._onNewFrame, frames=numFrames, interval=interval)
        self._ani.frame_seq = self._getFrameSeq()
        
        if isDesktopOrBrowser:
            
            sh = 0.05
            
            ax = plt.axes([0.1, 0.05, 0.8, sh])
            # !!! maybe show "t (ms)" instead of "Frame"
            self._sliderFrame = Slider(ax, 'Frame', valmin=0, valmax=numFrames - 1, valstep=1)
            self._sliderFrame.on_changed(self._onSliderFrameChange)
            
            sz = fig.get_size_inches()
            ratio = sz[1] / sz[0]
            sw = sh * ratio
            
            ax = plt.axes([0.025, 0.125, 0.1, 0.05])
            self._buttonStartStop = Button(ax, 'Stop')
            self._buttonStartStop.on_clicked(self._onButtonStartStopClick)
            
            ax = plt.axes([0.025, 0.25, sw, 0.65])
            self._sliderSize = Slider(ax, 'Size', orientation='vertical', valmin=10, valmax=2000, valinit=self._defaultMarkerSize)
            self._sliderSize.on_changed(self._onSliderSizeChange)
            
            if isUseOpacitiesOrColours:
                ax = plt.axes([0.1, 0.25, sw, 0.65])
                self._sliderOpacity = Slider(ax, 'Opacity', orientation='vertical', valmin=-10, valmax=10, valinit=self._balance)
                self._sliderOpacity.on_changed(self._onSliderOpacityChange)
                
                tokens = varNameWithIndexAndUnits.split(' ', 1) # Spaces in units is OK
                if len(tokens) == 2:
                    units = '\n' + tokens[1]
                    sh = 0.6
                else:
                    units = ''
                    sh = 0.65
                    
                ax = plt.axes([1-0.085-sw, 0.25, sw, sh])
                self._sliderRange = RangeSlider(ax, 'Range' + units + '\n', orientation='vertical', valmin=rangeVar_min, valmax=rangeVar_max, valinit=(self._min, self._max), valfmt='%d')
                self._sliderRange.on_changed(self._onSliderRangeChange)
                
                ax = plt.axes([1-0.14-sw, 0.863, 0.15, 0.05])
                self._textBoxMax = TextBox(ax, 'Max: ', initial=self._formatForTextBox(self._max))
                self._textBoxMax.on_submit(self._onTextBoxMaxChange)
                
                ax = plt.axes([1-0.14-sw, 0.186, 0.15, 0.05])
                self._textBoxMin = TextBox(ax, 'Min: ', initial=self._formatForTextBox(self._min))
                self._textBoxMin.on_submit(self._onTextBoxMinChange)
                
            self._numSegms = len(x)
        else:
            
            # Increase the animation size limit
            plt.rcParams['animation.embed_limit'] = self._animationEmbedLimit
            
            html = self._ani.to_jshtml()
            
            # Save the HTML string to a temporary HTML file
            with open(self._tempHtmlFileName, 'w') as f:
                f.write(html)
                
    def show(self):
        if self._isDesktopOrBrowser:
            plt.show()
        else:
            # Open the temporary HTML file in the default web browser
            webbrowser.open(self._tempHtmlFileName)
            
            
    def _onNewFrame(self, frameIdx):
        self._setOpacitiesOrColours(frameIdx)
        
        if not self._isDesktopOrBrowser:
            return
            
        self._isProgrammaticSliderFrameChange = True
        self._sliderFrame.set_val(frameIdx)             # --> _onSliderFrameChange
        self._isProgrammaticSliderFrameChange = False
        
    def _onButtonStartStopClick(self, _):
        if self._isRunning:
            self._ani.event_source.stop()
            self._buttonStartStop.label.set_text('Start')
        else:
            self._ani.event_source.start()
            self._buttonStartStop.label.set_text('Stop')
        self._isRunning = not self._isRunning
        
        # Refresh the button text
        plt.draw()
        
    def _onSliderFrameChange(self, val):
        frameIdx = int(val)
        self._frameIdx = frameIdx
        
        if self._isProgrammaticSliderFrameChange:
            return
            
        self._ani.event_source.stop()
        self._isRunning = False
        
        self._setOpacitiesOrColours(frameIdx)
        self._buttonStartStop.label.set_text('Start')
        
        # Refresh the button text
        plt.draw()
        
    def _onSliderSizeChange(self, val):
        markerSize = int(val)
        self._scatter.set_sizes(np.full(self._numSegms, markerSize))
        
    def _onSliderOpacityChange(self, val):
        self._balance = val
        self._transformRangeVarToOpacities()
        
    def _onSliderRangeChange(self, val):
        self._min = val[0]
        self._max = val[1]
        self._isProgrammaticTextBoxMinMaxChange = True
        self._textBoxMin.set_val(self._formatForTextBox(val[0]))    # --> _onTextBoxMinChange
        self._textBoxMax.set_val(self._formatForTextBox(val[1]))    # --> _onTextBoxMaxChange
        self._isProgrammaticTextBoxMinMaxChange = False
        self._transformRangeVarToOpacities()
        
    def _onTextBoxMaxChange(self, val):
        if self._isProgrammaticTextBoxMinMaxChange:
            return
        try:
            val = float(val)
        except ValueError:
            return
        self._max = val
        val = (self._min, val)
        self._sliderRange.set_val(val)      # --> _onSliderRangeChange
        
    def _onTextBoxMinChange(self, val):
        if self._isProgrammaticTextBoxMinMaxChange:
            return
        try:
            val = float(val)
        except ValueError:
            return
        self._min = val
        val = (val, self._max)
        self._sliderRange.set_val(val)      # --> _onSliderRangeChange
        
        
    def _formatForTextBox(self, val):
        return '%g' % val
        
    def _getFrameSeq(self):
        while True:
            self._frameIdx = (self._frameIdx + 1) % self._numFrames
            yield self._frameIdx
            
    def _transformRangeVarToOpacities(self):
        temp = logit(self._rangeVar0To1)            # Mapping [0, 1] to (-inf, inf)
        temp += self._balance                       # Balancing opacities
        self._rangeVar0To1Balanced = expit(temp)    # Mapping (-inf, inf) back to [0, 1]
        
        # Replace all values outside the range with 0
        min0To1 = (self._min - self._rangeVar_min) / self._rangeVar_range
        max0To1 = (self._max - self._rangeVar_min) / self._rangeVar_range
        mask = (self._rangeVar0To1 < min0To1) | (self._rangeVar0To1 > max0To1)
        self._rangeVar0To1Balanced[mask] = 0
        # !!! np.clip(self._rangeVar0To1Balanced, min0To1, max0To1, out=self._rangeVar0To1Balanced)
        
        if not self._isRunning:
            self._setOpacitiesOrColours(self._frameIdx)
            
    def _setOpacitiesOrColours(self, frameIdx):
        if self._isUseOpacitiesOrColours:
            self._scatter.set_alpha(self._rangeVar0To1Balanced[frameIdx])
        else:
            self._scatter.set_array(self._rangeVar[frameIdx])
            