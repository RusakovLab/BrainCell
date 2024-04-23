
# !!!!!
# * don't forget to get rid of the old gens/utils for syns (see the old skeleton)
# * make sure we export each "Reduced*" template somewhere
# * maybe replace everywhere:
#   * exportOptions.isExportGapJuncs -> exportOptions.isExportAnyGapJuncSets()
#   * exportOptions.isExportSyns -> exportOptions.isExportAnySynSets()

from neuron import h, nrn
from Utils.CleanupHelper import CleanupHelper
from GeneratorsForMainHocFile.GensForHomogenVars import GensForHomogenVars
from GeneratorsForMainHocFile.GensForInhomAndStochModels import GensForInhomAndStochModels
from GeneratorsForMainHocFile.GensForTaps import GensForTaps
from GeneratorsForMainHocFile.GensForExtracellularDiffusion import GensForExtracellularDiffusion
from Utils.LoopUtils import LoopUtils
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GeneratorsForMainHocFile:
    
    _defaultNseg = 1
    _defaultRa = 35.4
    
    _cleanupHelper = CleanupHelper()
    
    _gensForHomogenVars = GensForHomogenVars()
    _gensForInhomAndStochModels = GensForInhomAndStochModels()
    _gensForTaps = GensForTaps(_cleanupHelper, _gensForHomogenVars, _gensForInhomAndStochModels)
    _gensForExtracellularDiffusion = GensForExtracellularDiffusion()
    
    def getUtilsPrologue(self):
        if not hocObj.exportOptions.isAnyCustomSweptVars():
            return emptyParagraphHint()
            
        lines = self.insertAllLinesFromFile('_Code\\Export\\OutHocFileStructures\\MainHocUtils\\MainHocSweptVarsUtils.hoc')
        
        return lines
        
    # Keep in sync with GenForParamsHoc.getParamsCode
    def getParams(self):
        lines = []
        if hocObj.exportOptions.isCreateParamsHoc:
            
            lines.append('{ load_file("params.hoc") }')
            lines.append('')
            
            lines.append('// Exposed vars')
            concExposedVarsList = list(hocObj.exportOptions.stdExposedVarsList) + list(hocObj.exportOptions.exposedVarsList)
            newLines = self._initCustOrStdExposedOrSweptVars(concExposedVarsList, getExposedVarName, False)
            lines.extend(newLines)
        else:
            for stdExposedVar in hocObj.exportOptions.stdExposedVarsList:
                value = stdExposedVar.getValue()
                if stdExposedVar.isInteger:
                    value = int(value)
                unitsCommentOrEmpty = UnitsUtils.getUnitsCommentOrEmptyForExposedOrSweptVar2(stdExposedVar)
                lines.append(f'{stdExposedVar.customExpr} = {value}{unitsCommentOrEmpty}')
                
        if hocObj.exportOptions.isAnySweptVars():
            newLines = self._initCustOrStdExposedOrSweptVars(hocObj.exportOptions.sweptVarsList, getSweptVarName, True)
            if len(newLines) != 0:
                lines.append('')
                lines.append('// Swept vars')
                lines.extend(newLines)
                
        if hocObj.cvode.active():
            lines.append('')
            lines.append('// CVode')
            lines.append('{ cvode.active(1) }')
            lines.append(f'{{ cvode.atol({hocObj.cvode.atol()}) }}')
            
        return lines
        
    def getUtils(self):
        lines = []
        
        lines.append('objref nil')
        lines.append('')
        
        fileNames = [
            'InterModularErrWarnUtilsPart1_Exported.hoc',
            'InterModularErrWarnUtilsPart2_Exported.hoc',
            'InterModularListUtils_Exported.hoc',
            'InterModularStringUtils_Exported.hoc',
            'InterModularSectionUtilsPart1_Exported.hoc',
        ]
        if hocObj.exportOptions.isExportExtracellularLibrary():
            fileNames.append('InterModularSectionUtilsPart2_Exported.hoc')
        fileNames.append('InterModularOtherUtils_Exported.hoc')
        
        for fileName in fileNames:
            newLines = self.insertAllLinesFromFile('_Code\\InterModular\\Exported\\' + fileName)
            lines.extend(newLines)
            lines.append('')
            
        # The instances of the next reduced templates from "InterModular" folder are created
        # only in standalone mode; otherwise we just reuse the instances created earlier in the main program
        
        newLines = getAllLinesFromReducedVersionFile('InterModular\\ReducedBasicMath.hoc')  # Keep in sync with hoc:loadNanoHocFile
        lines.extend(newLines)
        
        if hocObj.exportOptions.isExportAltRunControl():
            lines.append('')
            newLines = getAllLinesFromReducedVersionFile('InterModular\\ReducedRNGUtils.hoc')
            lines.extend(newLines)
            
        if hocObj.exportOptions.isAnySweptVars() and not hocObj.exportOptions.isAnyCustomSweptVars():
            lines.append('')
            newLines = self.insertAllLinesFromFile('_Code\\Export\\OutHocFileStructures\\MainHocUtils\\MainHocSweptVarsUtils.hoc')
            lines.extend(newLines)
            
        return lines
        
    def checkPrerequisites(self):
        if not hocObj.exportOptions.isPythonRequired():
            return emptyParagraphHint()
            
        lines = []
        
        lines = self.insertAllLinesFromFile('_Code\\Export\\OutHocFileStructures\\PythonCheck.hoc')
        lines.append('')
        
        lines.append('objref pyObj')
        lines.append('pyObj = new PythonObject()')
        
        # !!!!!
        if hocObj.exportOptions.isExportSyns:
            lines.append('')
            newLines = self.insertAllLinesFromFile('_Code\\InterModular\\Exported\\InterModularPythonUtils_Exported.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getAllCreateStatementsExceptNanogeometry(self):
        # output: a string like 'create name1, name2[123], name3[456][7], ...'
        
        secNames = getAllSectionNamesExceptNanogeometry()
        
        createdNames = []
        for secName in secNames:
            createdName = secName.s
            
            secObj = self._getHocVar(createdName)
            while True:
                isSecObjOrArray = self._isSecObjOrArray(secObj)
                if isSecObjOrArray:
                    break
                else:
                    createdName += '[{}]'.format(len(secObj))
                    secObj = secObj[0]
                    
            createdNames.append(createdName)
            
        resStr = 'create ' + ', '.join(createdNames)
        
        return resStr
        
    def createListOfSectionRef(self, usedNamesHocListName, secRefHocListName):
        allLines = []
        newLine = '{} = new List()'.format(secRefHocListName)
        allLines.append(newLine)
        for usedNameHocString in self._getHocVar(usedNamesHocListName):
            usedName = usedNameHocString.s
            secObj = self._getHocVar(usedName)
            isSecObjOrArray = self._isSecObjOrArray(secObj)
            if isSecObjOrArray:
                newLine = '{} {}.append(new SectionRef())'.format(usedName, secRefHocListName)
                allLines.append(newLine)
            else:
                newLines = [
                    'for idx = 0, {} {{'.format(len(secObj) - 1),
                    '    {}[idx] {}.append(new SectionRef())'.format(usedName, secRefHocListName),
                    '}']
                allLines.extend(newLines)
        return allLines
        
    # !! maybe split topology by blocks for soma, dendrites, axon, nanogeometry, other
    def initTopology(self):
        lines = []
        for sec in h.allsec():
            secRef = h.SectionRef(sec)
            if not secRef.has_parent():
                continue
            # Some comments:
            # 1. The syntax "connect child(x), parent(y)" looks simpler than "parent connect child(x), y",
            #    but the former does not work for the sections owned by templates (all nanogeometry in our case)
            # 2. The syntax "sec=sec" is important here; do not replace it with "sec", because the called methods will always return 0
            # 3. Max. precision is applied in the next line by Python automatically
            line = '{} connect {}({}), {}'.format(secRef.parent.name(), sec.name(), h.section_orientation(sec=sec), h.parent_connection(sec=sec))
            lines.append(line)
        return lines
        
    # !! for file "Geometry\Neuron\test.hoc", we have:
    #    AstrocyteNanoBranch[0].SmallGlia[0] { ... pt3dadd(0.075074203312397, -0.07739131152629852, 0.0, 0.10000000149011612
    #    why garbage in diam?
    # !! for file "Geometry\Astrocyte\New Style\AstrocyteBasicGeometry.hoc", we have:
    #    soma[0] { ... pt3dadd(0.23000000417232513, 5.829999923706055, 0.0, 7.22599983215332)
    #    why garbage in x?
    # !! for file "Geometry\Neuron\cellmorphology.hoc", the value of "y" passed to "pt3dadd" is unstable,
    #    i.e. it varies from one export to other
    # !! investigate at which stage of the program the 3D-coordinates of 1st point of 1st imported dendrite become changed (at least in the next files: AstrocyteBasicGeometry.hoc and cellmorphology.hoc)
    #    "connect" command does not change them, so maybe "finitialize"?
    def initGeometry(self):
        lines = []
        for sec in h.allsec():
            line = '{} {{'.format(sec.name())
            lines.append(line)
            lines.append('    pt3dclear()') # Almost sure that not needed, but Cell Builder's Exporter adds this
            for ptIdx in range(sec.n3d()):
                # Max. precision is applied here automatically
                line = '    pt3dadd({}, {}, {}, {})'.format(sec.x3d(ptIdx), sec.y3d(ptIdx), sec.z3d(ptIdx), sec.diam3d(ptIdx))
                lines.append(line)
            if sec.nseg != self._defaultNseg:
                line = '    nseg = {}'.format(sec.nseg)
                lines.append(line)
            if sec.Ra != self._defaultRa:
                line = '    Ra = {}'.format(sec.Ra)
                lines.append(line)
            lines.append('}')
        return lines
        
    def createImportAndEditMeasures(self):
        
        exportOptions = hocObj.exportOptions
        
        lines = []
        
        # Check whether we are in "start with BrainCell export" mode or "standalone" mode
        lines.append('isLoadedFromMainProgram = 1')
        lines.append('{ makeSureDeclared("isBaseOrNanoStart", "isLoadedFromMainProgram = 0") }')
        lines.append('')
        
        # Make sure "nrnmech.dll" is loaded and valid
        # (doing it even though user could disable the export of biophysics, gap juncs and syns)
        lines.append('{ makeSureDeclared("mechsDllUtils") }')
        lines.append('objref mechType')
        lines.append('if (isLoadedFromMainProgram) {')
        lines.append('    mechsDllUtils.ifMissingInThisFolderThenLoadDefaultMechsDllDependingOnCellType()')
        if exportOptions.isExportDistMechs or exportOptions.isExportGapJuncs or exportOptions.isExportSyns:
            lines.append('} else {')
            lines.append('    platformId = unix_mac_pc()')
            lines.append('    strdef msg')
            lines.append('    if (platformId == 1) {')
            lines.append('        // Assuming NSG supercomputer environment')
            lines.append('        msg = "Please make sure the file \\"x86_64/.libs/libnrnmech.so\\" was built successfully."')
            lines.append('    } else if (platformId == 3) {')
            lines.append('        // Assuming desktop environment')
            lines.append('        msg = "Please make sure the correct file \\"nrnmech.dll\\" is present in the same folder with this HOC file."')
            lines.append('    } else {')
            lines.append('        codeContractViolation()')
            lines.append('    }')
            if exportOptions.isExportDistMechs:
                newLines = self._createCheckForNumMechs(0, 'Distributed Membrane Mechanisms')
                lines.extend(newLines)
            if exportOptions.isExportGapJuncs or exportOptions.isExportSyns:
                newLines = self._createCheckForNumMechs(1, 'Point Processes')
                lines.extend(newLines)
        lines.append('}')
        lines.append('')
        
        if hocObj.isAstrocyteOrNeuron:
            varName = 'GPassive'
            line = '{} = {}    // ({})'.format(varName, hocObj.GPassive, h.units(varName))
            lines.append(line)
            line = '{{ units(&{}, units("g_pas")) }}'.format(varName)
            lines.append(line)      # These units are used by biophys export module
            lines.append('')
            
        # Make sure the staff from ReducedVersions\InterModular is either:
        #   preserved ("start with BrainCell export" mode)
        #   created ("standalone" mode with real usage)
        #   declared as nil ("standalone" mode without real usage OR we'll use it, but first need to bound as template's external, and only then define)
        
        lines.append('{ makeSureDeclared("math", "objref %s", "%s = new ReducedBasicMath()") }')
        
        if exportOptions.isExportAltRunControl():
            # !! BUG: The random sequences won't be the same in the main program and the exported file until
            #         each seed given by rngUtils.getFor_stochFunc_withUniqueSeed is saved into corresponding stocDistFunc
            #         and exported/imported as a part of it
            lines.append('{ makeSureDeclared("rngUtils", "objref %s", "%s = new ReducedRNGUtils()") }')
        elif exportOptions.isExportSyns or exportOptions.isExportInhomAndStochLibrary():    # !!!!!
            lines.append('{ makeSureDeclared("rngUtils") }')
            
        # !!!!!!!!!! review vvvvv
        
        lines.append('')
        
        # Make sure all the required objref-s are declared as nil
        names = []
        names.append('mmAllComps')
        if exportOptions.isExportInhomAndStochLibrary() or exportOptions.isExportGapJuncs:
            names.append('gjmAllGapJuncSets')
        if exportOptions.isExportInhomAndStochLibrary() or exportOptions.isExportSyns:
            names.append('smAllSynSets')
        if exportOptions.isExportAnyInhomSynModels() or exportOptions.isExportAnyInhomGapJuncModels():  # review !!!!!
            names.append('mcu')     # !!!!! how about mcu4t ?
        if exportOptions.isExportAltRunControl():
            names.append('mmIcrHelper')
        line = 'objref ' + ', '.join(names)
        lines.append(line)
        
        lines.append('objref _comp')
        self._cleanupHelper.scheduleCleanup(lines[-1])
        
        # !!!!! was: if exportOptions.isExportInhomAndStochLibrary() or (exportOptions.isExportSyns and hocObj.synSet.is3Or1PartInSynStruc()):
        if exportOptions.isExportInhomAndStochLibrary() or exportOptions.isExportSyns and exportOptions.isExportGapJuncs:
            lines.append('')
            newLines = getAllLinesFromReducedVersionFile('ReducedMechTypeHelper.hoc')
            lines.extend(newLines)
        
        # !!!!!!!!!! review ^^^^^
        
        return lines
        
    def createInhomAndStochLibrary(self):
        if not hocObj.exportOptions.isExportInhomAndStochLibrary():
            return emptyParagraphHint()
            
        lines = []
        
        newLines = self.insertAllLinesFromFile('_Code\\Managers\\InhomAndStochLibrary\\Exported\\VarLibId.hoc')
        lines.extend(newLines)
        lines.append('')
        
        # !! try to avoid exporting the RNG staff in ReducedInhomAndStochTarget if not hocObj.exportOptions.isExportAnyStochFuncs()
        newLines = getAllLinesFromReducedVersionFile('InhomAndStochLibrary\\ReducedInhomAndStochTarget.hoc')
        lines.extend(newLines)
        lines.append('')
        
        newLines = getAllLinesFromReducedVersionFile('InhomAndStochLibrary\\ReducedInhomAndStochLibrary.hoc')
        lines.extend(newLines)
        lines.append('')
        
        if hocObj.exportOptions.isExportAltRunControl():
            newLines = self.insertAllLinesFromFile('_Code\\Managers\\InhomAndStochLibrary\\Exported\\InhomAndStochApplicator.hoc')
            lines.extend(newLines)
            lines.append('')
            
        lines.append('objref _vecOfVals, _listOfStrs')
        self._cleanupHelper.scheduleCleanup(lines[-1])
        
        return lines
        
    # !! some code dupl. with insertAllUsedStochFuncs
    def insertAllUsedDistFuncs(self):
        if not hocObj.exportOptions.isExportAnyDistFuncs():
            return emptyParagraphHint()
            
        lines = []
        
        dfhTemplNames = set()
        isTablePlusLinInterpDistFuncExported = False
        for actSpecVar in hocObj.inhomAndStochLibrary.activeSpecVars:
            if not hocObj.exportOptions.isExportedInhomVar(actSpecVar):
                continue
            dfhTemplNames.add(getTemplateName(actSpecVar.distFuncHelper))
            if actSpecVar.distFuncCatIdx == hocObj.dfc.tablePlusLinInterpDistFuncCatIdx:
                isTablePlusLinInterpDistFuncExported = True
            
        if isTablePlusLinInterpDistFuncExported:
            # !! just a temp solution: to get rid of this, we need to split TablePlusLinInterpDistFuncHelper template into two:
            #    table from TextEditor/Vector-s and table from file (only the first one will be exported)
            lines.append('{ makeSureDeclared("mwh") }')
            lines.append('')
            lines.append('func selectDistFuncInputFile_deprecated() { codeContractViolation() }')
            lines.append('')
        
        relDirPath = '_Code\\Managers\\InhomAndStochLibrary\\InhomModels\\DistFuncHelpers\\Exported'
        exportTheseTemplatesFromThisDir(lines, relDirPath, dfhTemplNames)
        lines.append('')
        
        if hocObj.exportOptions.isExportSegmentationHelper():
            newLines = getAllLinesFromReducedVersionFile('MechManager\\ReducedSegmentationHelper.hoc')
            lines.extend(newLines)
            lines.append('')
            
        lines.append('objref _segmentationHelper, _distFuncHelper')
        self._cleanupHelper.scheduleCleanup(lines[-1])
        
        return lines
        
    # !! some code dupl. with insertAllUsedDistFuncs
    def insertAllUsedStochFuncs(self):
        if not hocObj.exportOptions.isExportAnyStochFuncs():
            return emptyParagraphHint()
            
        lines = []
        
        # We need to bind these names as templates' external-s even though
        # they won't be used (because we don't call all the methods in the exported file);
        # at the same time, when the file is loaded from the main program, the file needs to:
        # (1) preserve all already created "InterModular" objects and callables (e.g. "mwh" and "eachPointInGrid")
        # (2) stub all required objects and callables allowing them to be defined later in the main program (e.g. "specMath" and "callPythonFunction")
        lines.append('{ makeSureDeclared("mwh") }')
        lines.append('{ makeSureDeclared("eachPointInGrid", "iterator %s() { codeContractViolation() }") }')
        lines.append('{ makeSureDeclared("graphUtils") }')
        lines.append('objref specMath')
        lines.append('func callPythonFunction() { codeContractViolation() }')
        lines.append('proc definePythonFunction() { codeContractViolation() }')
        lines.append('func loadPythonFile() { codeContractViolation() }')
        lines.append('func selectDistFuncInputFile_deprecated() { codeContractViolation() }')
        lines.append('')
        
        sdhTemplNames = set()
        sfhTemplNames = set()
        for actSpecVar in hocObj.inhomAndStochLibrary.activeSpecVars:
            if not hocObj.exportOptions.isExportedStochVar(actSpecVar):
                continue
            stochFuncHelper = actSpecVar.stochFuncHelper
            if actSpecVar.stochFuncCatIdx == hocObj.sfc.simpleModelStochFuncCatIdx:
                sdhTemplNames.add(getTemplateName(stochFuncHelper.distHelper))
            sfhTemplNames.add(getTemplateName(stochFuncHelper))
            
        relDirPath = '_Code\\Managers\\InhomAndStochLibrary\\StochModels\\StochDistHelpers\\Exported'
        exportTheseTemplatesFromThisDir(lines, relDirPath, sdhTemplNames)
        
        relDirPath = '_Code\\Managers\\InhomAndStochLibrary\\StochModels\\StochFuncHelpers\\Exported'
        exportTheseTemplatesFromThisDir(lines, relDirPath, sfhTemplNames)
        
        newLines = self.insertAllLinesFromFile('_Code\\Managers\\Widgets\\Stochasticity\\Exported\\ColourizationHelper.hoc')
        lines.extend(newLines)
        lines.append('')
        
        newLines = self.insertAllLinesFromFile('_Code\\Managers\\Widgets\\Stochasticity\\Exported\\BoundingHelper.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('objref _colourizationHelper, _boundingHelper, _stochFuncHelper')
        self._cleanupHelper.scheduleCleanup(lines[-1])
        
        return lines
        
    def createReducedMechComps(self):
    
        lines = []
        
        if not hocObj.exportOptions.isExportDistMechs:
            fileName = 'ReducedMechComp1.hoc'   # name, list_ref
        else:
            fileName = 'ReducedMechComp2.hoc'   # name, list_ref, isMechInserted, mechStds
        newLines = getAllLinesFromReducedVersionFile('MechManager\\' + fileName)
        lines.extend(newLines)
        lines.append('')
        
        mmAllComps = hocObj.mmAllComps
        
        # Create number of obfunc-s to prepare "list_ref" for each comp
        # !! BUG: In rare cases, an error "procedure too big" may occur when user loads the exported file.
        #         This error takes place when sourcing one of obfunc-s named "getListOfSecRefsFor*Comp".
        #         The root cause is that the base geometry file imported earlier
        #         created so many sections on the top level, that we cannot create now in the scope of just one obfunc.
        #         To fix this error, we'll have to init all list_ref-s on the top level rather than in the obfunc-s.
        obfuncNames = []
        for compIdx in range(len(mmAllComps)):
            comp = mmAllComps[compIdx]
            obfuncName = '_getListOfSecRefsForComp{}'.format(compIdx + 1)
            obfuncNames.append(obfuncName)
            lines.append('// "{}"'.format(comp.name))
            lines.append('obfunc {}() {{ local idx1, idx2 localobj list_ref'.format(obfuncName))
            lines.append('    list_ref = new List()')
            newLines = []
            for sec_ref in comp.list_ref:
                newLines.append('    {} list_ref.append(new SectionRef())'.format(sec_ref.sec))
            newLines = LoopUtils.tryInsertLoopsToShorten(newLines, True)
            lines.extend(newLines)
            lines.append('    return list_ref')
            lines.append('}')
            lines.append('')
            
        lines.append('mmAllComps = new List()')
        
        for (comp, obfuncName) in zip(mmAllComps, obfuncNames):
            lines.append('')
            lines.append('_comp = new ReducedMechComp("{}", {}())'.format(comp.name, obfuncName))
            lines.append('{ mmAllComps.append(_comp) }')
            
        return lines
        
    def initHomogenBiophysics(self):
        return self._gensForHomogenVars.initHomogenBiophysics()
        
    def createInhomBiophysModels(self):
        return self._gensForInhomAndStochModels.createInhomBiophysModels()
        
    def createStochBiophysModels(self):
        return self._gensForInhomAndStochModels.createStochBiophysModels()
        
    def createTemplatesForTaps(self):
        return self._gensForTaps.createTemplatesForTaps()
        
    def createTemplatesForGapJuncs(self):
        return self._gensForTaps.createTemplatesForGapJuncs()
        
    def createTemplatesForSyns(self):
        return self._gensForTaps.createTemplatesForSyns()
        
    def createLocsGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForTaps.createGapJuncLocs(tapSetIdx)
        else:
            return self._gensForTaps.createSynLocs(tapSetIdx)
            
    def createReducedCompsGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForTaps.createReducedGapJuncComps(tapSetIdx)
        else:
            return self._gensForTaps.createReducedSynComps(tapSetIdx)
            
    def initHomogenVarsGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForTaps.initHomogenGapJuncVars(tapSetIdx)
        else:
            return self._gensForTaps.initHomogenSynVars(tapSetIdx)
            
    def createImportAndEditMeasuresGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForTaps.createImportAndEditMeasuresForGapJuncs(tapSetIdx)
        else:
            return self._gensForTaps.createImportAndEditMeasuresForSyns(tapSetIdx)
            
    def createMainPartGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForTaps.createMainPartForGapJuncs(tapSetIdx)
        else:
            return self._gensForTaps.createMainPartForSyns(tapSetIdx)
            
    def createInhomModelsGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForInhomAndStochModels.createInhomGapJuncModels(tapSetIdx)
        else:
            return self._gensForInhomAndStochModels.createInhomSynModels(tapSetIdx)
            
    def createStochModelsGivenTapSet(self, isGapJuncOrSyn, tapSetIdx):
        if isGapJuncOrSyn:
            return self._gensForInhomAndStochModels.createStochGapJuncModels(tapSetIdx)
        else:
            return self._gensForInhomAndStochModels.createStochSynModels(tapSetIdx)
            
    def createCleanup(self):
        return self._cleanupHelper.makeCleanup()
        
    def createDiffSpeciesLibrary(self):
        return self._gensForExtracellularDiffusion.createSpeciesLibrary()
        
    def createExtraSourcesLibrary(self):
        return self._gensForExtracellularDiffusion.createSourcesLibrary()
        
    def createExtraDiffFinale(self):
        return self._gensForExtracellularDiffusion.createExtraDiffFinale()
        
    def insertAltRunControlWidget(self):
        if not hocObj.exportOptions.isExportAltRunControl():
            return emptyParagraphHint()
            
        lines = self.insertAllLinesFromFile('_Code\\AltRunControl\\Exported\\alt_stdrun.hoc')
        lines.append('')
        
        lines.append('{ makeSureDeclared("mwh") }')
        lines.append('')
        
        newLines = self.insertAllLinesFromFile('_Code\\AltRunControl\\Exported\\AltRunControlWidget.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('objref altRunControlWidget')
        lines.append('altRunControlWidget = new AltRunControlWidget()')
        lines.append('{ altRunControlWidget.show() }')
        
        return lines
        
    # Keep the filtration logic in sync with hoc:ExportOptions.isAnyWatchedAPCounts and .getFirstValidAPCountOrNil
    def createAPCounts(self):
        
        # By design, we export APCount-s independently on hocObj.exportOptions
        
        allAPCs = h.List('APCount')
        numAPCs = len(allAPCs)
        if numAPCs == 0:
            return emptyParagraphHint()
            
        newLines = []
        threshUnits = UnitsUtils.getUnitsForWatchedVar('APCount[0].thresh')
        for apcIdx in range(numAPCs):
            apc = allAPCs[apcIdx]
            seg = apc.get_segment()
            if seg is None:
                # !! maybe we need to warn user that we skip exporting those APCount-s not attached to any section
                #    (but even an attempt to set or get "thresh" for them leads to an error)
                continue
            newLines.append('')
            newLines.append('{} apCounts[{}] = new APCount({})'.format(seg.sec, apcIdx, seg.x))
            newLines.append('apCounts[{}].thresh = {}    // ({})'.format(apcIdx, apc.thresh, threshUnits))
            
        if len(newLines) == 0:
            return emptyParagraphHint()
            
        lines = []
        lines.append('objref apCounts[{}]'.format(numAPCs))
        lines.extend(newLines)
        
        return lines
        
    def insertAllLinesFromFile(self, relFilePathName):
        return getAllLinesFromFile(relFilePathName)
        
    def getIntegerValueFromTopLevel(self, varName):
        return self._generateAssignment(varName, True)
        
    def getDoubleValueFromTopLevel(self, varName):
        return self._generateAssignment(varName, False)
        
    def getListOfStringsFromTopLevel(self, varName):
        lines = []
        lines.append('objref {}'.format(varName))
        lines.append('{} = new List()'.format(varName))
        listOfStrs = self._getHocVar(varName)
        for thisStr in listOfStrs:
            lines.append('{{ {}.append(new String("{}")) }}'.format(varName, thisStr.s))
        return lines
        
        
    def _initCustOrStdExposedOrSweptVars(self, varsList, getVarName, isSwept):
        lines = []
        for varIdx in range(len(varsList)):
            var = varsList[varIdx]
            if var.enumBioGjSynCeSt < 3:
                continue
            varName = getVarName(varIdx)
            if isSwept:
                notRunnedModeValue = var.getValue()
                sweptVarInitializer = f'getSweptVarValue("{varName}", {notRunnedModeValue})'
                unitsCommentOrEmpty = UnitsUtils.getUnitsCommentOrEmptyForExposedOrSweptVar2(var)
                lines.append(f'{var.customExpr} = {sweptVarInitializer}{unitsCommentOrEmpty}')
            else:
                lines.append(f'{var.customExpr} = {varName}')
        return lines
        
    def _createCheckForNumMechs(self, isDmOrPp, hint):
        lines = []
        lines.append('    mechType = new MechanismType({})    // {}: "{}"'.format(isDmOrPp, isDmOrPp, hint))
        lines.append('    if (mechType.count() != {}) {{'.format(int(hocObj.mth.getNumMechs(isDmOrPp))))
        lines.append('        printMsgAndRaiseError(msg)')
        lines.append('    }')
        return lines
        
    def _getHocVar(self, varName):
        return getattr(hocObj, varName)
        """ !!
        if '.' not in varName:
            return getattr(hocObj, varName)
        else:
            return eval(f'hocObj.{varName}')    # !! for the sections owned by custom templates
        """
        
    def _generateAssignment(self, varName, isIntegerOrDouble):
        value = self._getHocVar(varName)
        if isIntegerOrDouble:
            value = int(value)
        return '{} = {}'.format(varName, value)
        
    def _isSecObjOrArray(self, secObj):
        tp = type(secObj)
        # !! we could use "match-case" here, but it was introduced only in Python 3.10 (2021),
        #    and user may have an older version installed
        if tp == nrn.Section:
            return 1
        elif tp == hoc.HocObject:
            return 0
        else:
            codeContractViolation()
            