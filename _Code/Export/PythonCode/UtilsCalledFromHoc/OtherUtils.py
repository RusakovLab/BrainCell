
from Utils.OtherUtils import getAllSectionNamesExceptNanogeometry
from OtherInterModularUtils import hocObj


def checkForNotImplementedExportScenario():
    if hocObj.gridOfSections is not None:
        hocObj.mwh.showNotImplementedWarning('Cannot export the cell with the sections grid deployed.')
        return 1
    secNames = getAllSectionNamesExceptNanogeometry()
    isNotImpl = any('.' in secName.s for secName in secNames)
    if isNotImpl:
        hocObj.mwh.showNotImplementedWarning('Cannot export the cell because, for the imported base geometry, some section(s) were created inside templates.')
    return isNotImpl
    