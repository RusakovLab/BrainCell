
import os
import json
from OtherInterModularUtils import *

# !! encapsulate all the code here into a class


_settingsDirPath = os.getcwd() + '\\..\\..\\Mechanisms\\Settings\\'


def _ms_loadJsonFileAndDeleteHintKey(fileName, keyToDel):
    with open(_settingsDirPath + fileName) as jsonFile:
        jsonDict = json.load(jsonFile)
        try:
            del jsonDict[keyToDel]
        except KeyError:
            pass
    return jsonDict
    
_ms_jsonDict1 = _ms_loadJsonFileAndDeleteHintKey('hide_stoch_btn_for.json', 'JustExampleOfMechName')
_ms_jsonDict2 = _ms_loadJsonFileAndDeleteHintKey('gap_junc_ptr_info.json', 'JustExampleOfGapJuncPointProcessName')
_ms_jsonDict3 = _ms_loadJsonFileAndDeleteHintKey('diffusible_species.json', 'Legend')


def ms_isHideStochButton(mechName, varNameWithIndex):
    return mechName in _ms_jsonDict1 and varNameWithIndex in _ms_jsonDict1[mechName]
    
    
def ms_warnIfNoRecordForGapJunc(mechName):
    if mechName not in _ms_jsonDict2:
        line1 = f'Please add the missing record for "{mechName}" PP to the JSON file "Mechanisms\\Settings\\gap_junc_ptr_info.json".'
        line2 = f'Without the record, we don\'t know if it has a POINTER and, if so, with what biophys var to connect it.'
        line3 = f'For now we assume that "{mechName}" PP has no POINTER.'
        hocObj.mwh.showWarningBox(line1, line2, line3)
        
def ms_doesGapJuncHavePtr(mechName):
    try:
        return _ms_jsonDict2[mechName] is not None
    except KeyError:
        return False
        
def ms_getGapJuncPtrName(mechName):
    return _ms_jsonDict2[mechName]['ppPtrName']
    
def ms_getGapJuncExtVarNameWithIndex(mechName):
    return _ms_jsonDict2[mechName]['dmVarNameWithIndex']
    
    
def ms_setIonGlobalVars():
    for subDict in _ms_jsonDict3.values():
        for value in subDict.values():
            ionMechName = value['ionMechName']
            suffix = ms_ionMechNameToSuffix(ionMechName)
            baseInnerConc = value['baseInnerConc (mM)']
            baseOuterConc = value["baseOuterConc (mM)"]
            try:
                setattr(hocObj, f'{suffix}i0_{suffix}_ion', baseInnerConc)
                setattr(hocObj, f'{suffix}o0_{suffix}_ion', baseOuterConc)
            except LookupError:
                # The ion is present in JSON file, but missing in MOD files
                # !! it would be better to skip the assignment attempt rather than suppress the error
                #    (can user have such vars in HOC without having the ion?)
                pass
                
def ms_getAllSpcCatNames():
    return convertPyIterableOfStrsToHocListOfStrObjs(_ms_jsonDict3.keys())
    
def ms_getTotalNumExpIons():
    numIons = 0
    for subDict in _ms_jsonDict3.values():
        numIons += len(subDict)
    return numIons
    
def ms_getAllExpIonNames():
    lst = []
    for spcCatName in _ms_jsonDict3:
        lst.extend(ms_getAllExpIonNamesInThisCat(spcCatName, 0))
    return convertPyIterableOfStrsToHocListOfStrObjs(lst)
    
def ms_getAllExpIonNamesInThisCat(spcCatName, isConvertToHocListOfStrObjs):
    lst = []
    for value in _ms_jsonDict3[spcCatName].values():
        lst.append(value['ionMechName'])
    if isConvertToHocListOfStrObjs:
        lst = convertPyIterableOfStrsToHocListOfStrObjs(lst)
    return lst
    
def ms_getUserFriendlyIonNameOrEmpty(actIonName):
    for subDict in _ms_jsonDict3.values():
        for key, value in subDict.items():
            if value['ionMechName'] == actIonName:
                return key
    return ''
    
def ms_isActIonInThisCat(actIonName, spcCatName):
    return any(value['ionMechName'] == actIonName for value in _ms_jsonDict3[spcCatName].values())
    
def ms_getDiff(spcCatName, actIonName):
    return _ms_getVar(spcCatName, actIonName, 'Diff (um2/ms)')
    
def ms_gett_alpha(spcCatName, actIonName):
    return _ms_getVar(spcCatName, actIonName, 't_alpha (ms)')
    
    
# !! maybe move to some intermodular utils
def ms_ionMechNameToSuffix(ionMechName):
    ionSuffix = '_ion'          # !! already defined in HOC
    if not ionMechName.endswith(ionSuffix):
        raise Exception     # !! replace with either codeContractViolation or an error saying that the JSON file is malformed
    return ionMechName[: -len(ionSuffix)]
    
    
def _ms_getVar(spcCatName, actIonName, varKey):
    for value in _ms_jsonDict3[spcCatName].values():
        if value['ionMechName'] == actIonName:
            return value[varKey]
    raise Exception         # !! replace with either codeContractViolation or an error saying that the JSON file is malformed
    