
from OtherInterModularUtils import hocObj

class NeuronPlayer:
    
    def __init__(self, rangeVar, t, varNameWithIndexAndUnits, rangeVar_min, rangeVar_max):
        varNameWithIndex = varNameWithIndexAndUnits.split(' (', 1)[0]
        hocObj.neuronPlayerWidget.onPlayerInit(rangeVar, t, varNameWithIndex, rangeVar_min, rangeVar_max)
        
    def show(self):
        hocObj.neuronPlayerWidget.onPlayerShow()
        