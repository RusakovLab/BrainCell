
from neuron import h
from Utils.OtherUtils import hocObj


# See also: InterModularUnitsUtils.hoc and hoc:MechTypeHelper.getVarUnits
class UnitsUtils:
    
    # e.g. 'mV'
    def getUnitsForSweptVar(var):
        comment = h.ref('')
        units = h.ref('')
        var.getUnitsCommentOrEmpty(comment, units)
        return units[0]
        
    # e.g. 'mV'
    def getUnitsForWatchedVar(customExpr):
        
        # The next command gives errors like "Cannot find the symbol for  dendA1_00.PcalBar_CAl( 0.05 )"
        #   return h.units(customExpr)
        
        # This works fine for any vars from DMs, PPs/ACs and top-level vars
        # !! BUG: it gives an empty string for NetCon vars, e.g. "NetCon[0].delay"
        units = h.ref('')
        h.getWatchedVarUnits(customExpr, units)
        return units[0]
        
    # e.g. ' (mV)'
    def getUnitsCommentOrEmptyForExposedOrSweptVar1(var):
        comment = h.ref('')
        var.getUnitsCommentOrEmpty(comment)
        return comment[0]
        
    # e.g. '    // (mV)'
    @classmethod
    def getUnitsCommentOrEmptyForExposedOrSweptVar2(cls, var):
        comment = cls.getUnitsCommentOrEmptyForExposedOrSweptVar1(var)
        if comment:
            comment = '    //' + comment
        return comment
        
    # e.g. '    // (mV)'
    def getUnitsCommentOrEmptyForDmOrTapPart(enumDmPpFk, mechIdx, varName, varNameWithIndex):
        units = h.ref('')
        hocObj.mth.getVarUnits(enumDmPpFk, mechIdx, varName, varNameWithIndex, units)
        units = units[0]
        if units:
            unitsCommentOrEmpty = '    // ({})'.format(units)
        else:
            unitsCommentOrEmpty = ''
        return unitsCommentOrEmpty
        