
# !!! Ideas:
#     * think about the usage of log colourbar (if supported) or explicit expressions for the watched var, e.g. "log(gabao)"
#     * maybe make "z" axis normal to the screen by default to be consistent with PlotShape default view direction
#     * maybe cache data in Python to make the wait time for "Show the last record once again" shorter

from PlotlyPlayer import PlotlyPlayer
from PyplotPlayer import PyplotPlayer

import numpy as np
from neuron import h
from OtherInterModularUtils import codeContractViolation


class RangeVarAnimationPlayer:
    
    _record = None
    
    
    def __init__(self, record):
        self._record = record
        
    def play(self, frontEndIdx, isUseOpacitiesOrColours, isTestMode):
        
        h.mwh.showPleaseWaitBox('Preparing animation.')
        
        varNameWithIndexAndUnits = self._record.varNameWithIndexAndUnits
        
        # 3D coordinates of segment centres
        x = self._record.xVec
        y = self._record.yVec
        z = self._record.zVec
        
        # The time grid
        t = self._record.timeVec
        
        numSegms = len(x)
        numFrames = len(t)
        
        if isTestMode:
            # !!! just some random test data here
            rangeVar = np.random.rand(numFrames, numSegms)
        else:
            rangeVar = np.empty(numSegms * numFrames)
            self._record.rangeVarVec.to_python(rangeVar)
            rangeVar = np.reshape(rangeVar, (numFrames, numSegms))
            
        rangeVar_min = self._getRangeVarMin(rangeVar, varNameWithIndexAndUnits)
        rangeVar_max = rangeVar.max()
        
        if frontEndIdx == 0:
            
            player = PlotlyPlayer(x, y, z, rangeVar, t, varNameWithIndexAndUnits, isUseOpacitiesOrColours, rangeVar_min, rangeVar_max)
            
        elif frontEndIdx == 1 or frontEndIdx == 2:
            
            isDesktopOrBrowser = 2 - frontEndIdx
            player = PyplotPlayer(x, y, z, rangeVar, numFrames, varNameWithIndexAndUnits, isUseOpacitiesOrColours, isDesktopOrBrowser, rangeVar_min, rangeVar_max)
            
        else:
            codeContractViolation()
            
        h.mwh.hidePleaseWaitBox()
        
        player.show()
        
        
    def _getRangeVarMin(self, rangeVar, varNameWithIndexAndUnits):
        fallbackMin = rangeVar.min()
        varNameWithIndex = varNameWithIndexAndUnits.split(' ')[0]
        if varNameWithIndex[-1] == 'o':
            # This is probably an out concentration range var - we want to see some opacity (or elevated colour) even for the lowest value point
            # when it's higher than the base out concentration (e.g. when we have a static point source)
            ionName = varNameWithIndex[:-1]                     # e.g. "gaba"
            baseOutConcVarName = f'{ionName}o0_{ionName}_ion'   # e.g. "gabao0_gaba_ion"
            try:
                rangeVar_min = getattr(h, baseOutConcVarName)
                if fallbackMin < rangeVar_min:
                    # A case when we have some segment(s) where "{ionName}o < {ionName}o0_{ionName}_ion" - use full transparency for the lowest value point
                    rangeVar_min = fallbackMin
            except AttributeError:
                # Not an out concentration range var - use full transparency for the lowest value point
                rangeVar_min = fallbackMin
        else:
            # Not an out concentration range var - use full transparency for the lowest value point
            rangeVar_min = fallbackMin
        return rangeVar_min
        