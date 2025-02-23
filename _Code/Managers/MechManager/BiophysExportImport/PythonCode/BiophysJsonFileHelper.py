
import json
from neuron import h
from BiophysJsonExportCore import BiophysJsonExportCore
from BiophysJsonImportCore import BiophysJsonImportCore
from OtherInterModularUtils import *

# !! maybe allow user to put comments in any place of JSON file using "comment" key (and leave an example comment in the exported JSON)
#    OR use some other file format but JSON to support comments


class BiophysJsonFileHelper:
    
    _biophysJsonExportCore = BiophysJsonExportCore()
    _biophysJsonImportCore = BiophysJsonImportCore()
    
    _jsonDictForImportStage3 = None
    _jsonDictForImportForSimStage2 = None
    
    
    def exportStage2(self, outJsonFilePathName, options):
        
        jsonDict = self._biophysJsonExportCore.exportCore(options)
        
        with open(outJsonFilePathName, 'w') as jsonFile:
            json.dump(jsonDict, jsonFile, indent=4)
            
        return 0
        
    def importStage1(self, inJsonFilePathName):
        
        with open(inJsonFilePathName) as jsonFile:
            jsonDict = json.load(jsonFile)
            
        donMechNames = set()    # "don" - donor
        
        compNames = h.List()
        numInhomVars = 0
        numStochVars = 0
        for (compName, mechNameToInfoDict) in jsonDict.items():
            compNames.append(h.String(compName))
            donMechNames.update(mechNameToInfoDict.keys())
            for varTypeToInfoDict in mechNameToInfoDict.values():
                for varNameToInfoDict in varTypeToInfoDict.values():
                    for varValueOrInfoDict in varNameToInfoDict.values():
                        if type(varValueOrInfoDict) is not dict:
                            continue
                        for varInfoKey in varValueOrInfoDict.keys():
                            if varInfoKey == 'inhom_model':
                                numInhomVars += 1
                            elif varInfoKey == 'stoch_model':
                                numStochVars += 1
                                
        recMechNames = self._getAllRecMechNames()   # "rec" - recipient
        
        missingMechNames = h.List()
        for mechName in donMechNames:
            if mechName not in recMechNames:        # !! h.name_declared(mechName) can give a false positive
                missingMechNames.append(h.String(mechName))
                
        if missingMechNames:
            hocObj.mwh.showWarningBox(
                "Cannot import this biophys file because it uses some mech(s) missing in the local library \"nrnmech.dll\":", \
                missingMechNames)
            return 1
            
        self._jsonDictForImportStage3 = jsonDict
        
        hocObj.beih.importStage2(compNames, numInhomVars, numStochVars)     # --> importStage3
        
        return 0
        
    def importStage3(self, options):
        try:
            return self._biophysJsonImportCore.importCore(self._jsonDictForImportStage3, options)
        finally:
            self._jsonDictForImportStage3 = None
            
    def importForSimStageA(self, inJsonFilePathName, compNames):
        
        with open(inJsonFilePathName) as jsonFile:
            jsonDict = json.load(jsonFile)
            
        for donCompName in jsonDict.keys():         # "don" - donor
            compNames.append(h.String(donCompName))
            
        self._jsonDictForImportForSimStage2 = jsonDict
        
        return 0
        
    def importForSimStageB(self, isUseThisCompNameVec):
        
        defaultOptions = h.BiophysExportImportOptions()
        defaultOptions.isUseThisCompNameVec = isUseThisCompNameVec
        
        try:
            return self._biophysJsonImportCore.importCore(self._jsonDictForImportForSimStage2, defaultOptions)
        finally:
            self._jsonDictForImportForSimStage2 = None
            
            
    def _getAllRecMechNames(self):
        mth = hocObj.mth
        mechName = h.ref('')
        allMechNames = set()
        for mechIdx in range(int(mth.getNumMechs(0))):
            mth.getMechName(0, mechIdx, mechName)
            allMechNames.add(mechName[0])
        return allMechNames
        