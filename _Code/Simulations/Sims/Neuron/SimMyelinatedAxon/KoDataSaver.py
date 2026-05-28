# KoDataSaver.py - Modified to use mid-index logic
import numpy as np
from datetime import datetime
import os
from neuron import h

class KoDataSaver:
    """
    Automatically saves extracellular K+ concentration (ko) heatmap data
    and voltage/ion traces (v, ko, ki, nao, nai) at the mid-node-of-Ranvier.
    Records from specific positions with error handling.
    """
    
    def __init__(self, outputDir='ko_output', recordInterval=0.1):
        """
        Args:
            outputDir: Directory where output files will be saved
            recordInterval: Time interval between recordings in ms (default: 0.1 ms)
        """
        self.outputDir = os.path.abspath(outputDir)
        self.recordInterval = recordInterval
        self.nextRecordTime = 0.0
        
        self.timePoints = []
        self.koData = []
        self.positions = []
        self.positionLabels = []
        self.segments = []
        self.isRecording = False
        self.shells = None
        self.k = None
        
        # Mid-node-of-Ranvier voltage/ion traces
        self._midNodeSeg = None         # segment for mid-node-of-Ranvier
        self._midNodeLabel = ''
        self._traceData = {             # dict of variable name -> list of float values
            'v':   [],
            'ko':  [],
            'ki':  [],
            'nao': [],
            'nai': [],
        }
        
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
            print(f"Created output directory: {self.outputDir}")
    
    def startRecording(self, shells, k, axonTrunkSecsExceptTerms,
                      axonUnderSchwannSecsList, axonNodeOfRanvierSecsList,
                      axonAfterLastSchwannSecOrNone,
                      numInnerShells=None, schwannKoShellIdx=None):
        """
        Initialize recording from specific positions.
        Records from: middle of AxonUnderSchwann, middle of AxonNodeOfRanvier,
        and AxonAfterLastSchwann (or last trunk section as fallback).

        Args:
            shells:                      List of RxD shell regions (len = totalNumShells)
            k:                           RxD Species (potassium)
            axonTrunkSecsExceptTerms:    All axon trunk sections
            axonUnderSchwannSecsList:    List of axon sections under Schwann cells
            axonNodeOfRanvierSecsList:   List of nodes of Ranvier
            axonAfterLastSchwannSecOrNone: Section after last Schwann cell (or None)
            numInnerShells:              Number of inner-zone shells (axon -> R_sheath).
                                         If None, assumes all shells are inner zone (old behaviour).
            schwannKoShellIdx:           0-based index of the shell used for Schwann-cell
                                         flux coupling / ko read-out. Stored in metadata only.
        """
        print("Starting Ko data recording from SPECIFIC positions...")

        self.shells = shells
        self.k = k
        self.numShells = len(shells)     # = totalNumShells in Config B

        # Store zone-boundary info for labelling / metadata
        self.numInnerShells  = numInnerShells if numInnerShells is not None else self.numShells
        self.numExtShells    = self.numShells - self.numInnerShells
        self.schwannKoShellIdx = schwannKoShellIdx  # may be None if not provided
        
        # Clear previous data
        self.positions = []
        self.positionLabels = []
        self.segments = []
        self.timePoints = []
        self.koData = []
        
        # Clear voltage/ion trace data
        for key in self._traceData:
            self._traceData[key] = []
        self._midNodeSeg = None
        self._midNodeLabel = ''
        
        # Helper function to check if segment has RxD nodes
        def hasRxDNodes(segm):
            try:
                nodes = self.k.nodes(segm)
                return len(nodes) > 0
            except:
                return False
        
        # 1. Record from middle of axonUnderSchwann - using same logic as voltage graph
        if len(axonUnderSchwannSecsList) > 0:
            middleIdx = int(len(axonUnderSchwannSecsList) / 2)
            sec = axonUnderSchwannSecsList[middleIdx]
            segm = sec(0.5)
            if hasRxDNodes(segm):
                pos = h.distance(segm)
                self.positions.append(pos)
                self.positionLabels.append(f"AxonUnderSchwann[{middleIdx}](0.5)")
                self.segments.append(segm)
                print(f"  Position {len(self.positions)}: AxonUnderSchwann[{middleIdx}](0.5) at {pos:.2f} um")
            else:
                print(f"  WARNING: AxonUnderSchwann[{middleIdx}] has no RxD shells")
        else:
            print(f"  WARNING: No Schwann cells available")
        
        # 2. Record from middle of axonNodeOfRanvier - using same logic as voltage graph
        if len(axonNodeOfRanvierSecsList) > 0:
            nodeIdx = int(len(axonNodeOfRanvierSecsList) / 2)
            sec = axonNodeOfRanvierSecsList[nodeIdx]
            segm = sec(0.5)
            if hasRxDNodes(segm):
                pos = h.distance(segm)
                self.positions.append(pos)
                self.positionLabels.append(f"AxonNodeOfRanvier[{nodeIdx}](0.5)")
                self.segments.append(segm)
                print(f"  Position {len(self.positions)}: AxonNodeOfRanvier[{nodeIdx}](0.5) at {pos:.2f} um")
            else:
                print(f"  WARNING: AxonNodeOfRanvier[{nodeIdx}] has no RxD shells")
            
            # Also store mid-node segment for voltage/ion trace recording (even if no RxD shells)
            self._midNodeSeg = segm
            self._midNodeLabel = f"AxonNodeOfRanvier[{nodeIdx}](0.5)"
            print(f"  Mid-node trace target: {self._midNodeLabel}")
        else:
            print(f"  WARNING: No nodes of Ranvier available")
            self._midNodeSeg = None
            self._midNodeLabel = ''
        
        # 3. Record from axonAfterLastSchwann(1.0) - end of section after last Schwann
        if axonAfterLastSchwannSecOrNone is not None:
            segm = axonAfterLastSchwannSecOrNone(1.0)
            if hasRxDNodes(segm):
                pos = h.distance(segm)
                self.positions.append(pos)
                self.positionLabels.append("AxonAfterLastSchwann(1.0)")
                self.segments.append(segm)
                print(f"  Position {len(self.positions)}: AxonAfterLastSchwann(1.0) at {pos:.2f} um")
            else:
                print(f"  WARNING: AxonAfterLastSchwann has no RxD shells")
        elif len(axonTrunkSecsExceptTerms) > 0:
            # Fallback: use the last axon section if no section after last Schwann
            lastAxonSec = axonTrunkSecsExceptTerms[-1]
            segm = lastAxonSec(1.0)
            if hasRxDNodes(segm):
                pos = h.distance(segm)
                self.positions.append(pos)
                self.positionLabels.append("LastAxonSection(1.0)")
                self.segments.append(segm)
                print(f"  Position {len(self.positions)}: LastAxonSection(1.0) at {pos:.2f} um")
        else:
            print(f"  WARNING: No section after last Schwann cell")
        
        if len(self.segments) == 0:
            print("  ERROR: No valid recording positions found!")
            self.isRecording = False
            return
        
        self.isRecording = True
        self.nextRecordTime = 0.0
        
        print(f"\nKo data recording started: {len(self.positions)} positions, "
              f"{self.numShells} shells total "
              f"({self.numInnerShells} inner / {self.numExtShells} outer)")
        if self.schwannKoShellIdx is not None:
            print(f"  Schwann-coupling shell index: {self.schwannKoShellIdx} "
                  f"(0-based, zone boundary at {self.numInnerShells - 1})")
        if self.recordInterval > 0:
            expectedPoints = int(h.tstop / self.recordInterval) + 1
            print(f"  Recording interval: {self.recordInterval} ms (~{expectedPoints} points)")
    
    def shouldRecord(self):
        """Check if we should record at current time"""
        if not self.isRecording:
            return False
        
        if self.recordInterval <= 0:
            return True
        
        return h.t >= (self.nextRecordTime - 1e-9)
    
    def recordTimePoint(self):
        """Record ko concentration at current time from specific positions only"""
        if not self.shouldRecord():
            return
        
        # Safety check - make sure we have valid references
        if self.k is None or len(self.segments) == 0:
            return
        
        self.timePoints.append(h.t)
        
        # Record voltage/ion traces at mid-node-of-Ranvier
        if self._midNodeSeg is not None:
            try:
                sec = self._midNodeSeg.sec
                self._traceData['v'].append(  self._midNodeSeg.v)
                self._traceData['ko'].append( self._midNodeSeg.ko)
                self._traceData['ki'].append( self._midNodeSeg.ki)
                self._traceData['nao'].append(self._midNodeSeg.nao)
                self._traceData['nai'].append(self._midNodeSeg.nai)
            except Exception as e:
                print(f"  WARNING: Error reading trace from mid-node at t={h.t:.2f}: {e}")
                for key in self._traceData:
                    self._traceData[key].append(0.0)
        
        # Extract ko values ONLY from the specific segments we stored
        currentData = []
        for segm in self.segments:
            try:
                nodes = self.k.nodes(segm)
                shellConcs = [node.concentration for node in nodes]
                currentData.append(shellConcs)
            except Exception as e:
                print(f"  WARNING: Error reading data from segment at t={h.t:.2f}: {e}")
                # Add empty data to maintain matrix structure
                currentData.append([0.0] * self.numShells)
        
        self.koData.append(currentData)
        
        # Print progress every 10 recordings
        if len(self.timePoints) % 10 == 0:
            print(f"  Recording progress: {len(self.timePoints)} points at t={h.t:.2f} ms")
        
        # Schedule next recording
        if self.recordInterval > 0:
            self.nextRecordTime = h.t + self.recordInterval
    
    def saveAllShellsAsMatrices(self, prefix="ko_shell"):
        """Save each shell as a separate MATLAB-compatible matrix file"""
        if not self.koData:
            print("No data to save!")
            return []
        
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepaths = []
        
        numTimePoints = len(self.timePoints)
        numPositions = len(self.positions)
        
        print(f"Saving {self.numShells} shells ({self.numInnerShells} inner / {self.numExtShells} outer) "
              f"with {numTimePoints} time points and {numPositions} positions...")
        
        for shellIdx in range(self.numShells):
            isInnerZone = shellIdx < self.numInnerShells
            zoneLabel = "Inner zone (axon->sheath)" if isInnerZone else "Outer zone (sheath->Rmax)"
            
            filename = f"{prefix}{shellIdx+1}_{timestamp}.txt"
            filepath = os.path.join(self.outputDir, filename)
            
            print(f"  Writing shell {shellIdx+1} [{zoneLabel}]...", end='', flush=True)
            
            # Create 2D matrix: rows = time points, columns = positions
            matrix = np.zeros((numTimePoints, numPositions))
            
            # Safely populate matrix with error checking
            for timeIdx in range(numTimePoints):
                for posIdx in range(numPositions):
                    try:
                        matrix[timeIdx, posIdx] = self.koData[timeIdx][posIdx][shellIdx]
                    except (IndexError, TypeError) as e:
                        # If data is missing, use 0
                        matrix[timeIdx, posIdx] = 0.0
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header with metadata
                isInnerZone = shellIdx < self.numInnerShells
                zoneDesc = "Inner zone (axon membrane -> sheath boundary)" if isInnerZone \
                           else "Outer zone (sheath boundary -> Rmax, Schwann wall)"
                f.write(f"% K+ Concentration - Shell {shellIdx+1} of {self.numShells}\n")
                f.write(f"% Zone: {zoneDesc}\n")
                f.write(f"% Inner shells: 1..{self.numInnerShells}   "
                        f"Outer shells: {self.numInnerShells+1}..{self.numShells}\n")
                if self.schwannKoShellIdx is not None:
                    f.write(f"% Schwann-coupling shell index (0-based): {self.schwannKoShellIdx} "
                            f"= shell {self.schwannKoShellIdx+1} in file numbering\n")
                f.write(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"% Rows = Time points ({numTimePoints}), Columns = Positions ({numPositions})\n")
                f.write(f"% Recording interval: {self.recordInterval} ms\n")
                f.write(f"%\n")
                f.write(f"% Recorded positions:\n")
                for i, label in enumerate(self.positionLabels):
                    f.write(f"%   Position {i+1}: {label} at {self.positions[i]:.2f} um\n")
                f.write(f"%\n")
                
                # Time vector
                f.write("% Time (ms): ")
                f.write(" ".join([f"{t:.6f}" for t in self.timePoints]))
                f.write("\n")
                
                # Position vector with labels
                f.write("% Position (um): ")
                f.write(" ".join([f"{p:.6f}" for p in self.positions]))
                f.write("\n")
                
                f.write("% Position labels: ")
                f.write(", ".join(self.positionLabels))
                f.write("\n")
                f.write("%\n")
                
                # Data matrix
                for timeIdx in range(numTimePoints):
                    row = " ".join([f"{matrix[timeIdx, posIdx]:.8f}" 
                                   for posIdx in range(numPositions)])
                    f.write(row + "\n")
            
            print(f" Done!")
            filepaths.append(filepath)
        
        self._saveMatlabMetadata(timestamp)
        
        # Save voltage/ion traces at mid-node-of-Ranvier
        if self._midNodeSeg is not None and len(self.timePoints) > 0:
            self._saveTraces(timestamp)
        
        print(f"Data saved to: {self.outputDir}")
        return filepaths
    
    def _saveTraces(self, timestamp):
        """Save v, ko, ki, nao, nai traces at the mid-node-of-Ranvier to a single text file."""
        
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        
        filename = f"midnode_traces_{timestamp}.txt"
        filepath = os.path.join(self.outputDir, filename)
        
        print(f"  Writing mid-node traces...", end='', flush=True)
        
        numPoints = len(self.timePoints)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"% Mid-node-of-Ranvier Voltage and Ion Traces\n")
            f.write(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"% Location: {self._midNodeLabel}\n")
            f.write(f"% Recording interval: {self.recordInterval} ms\n")
            f.write(f"% Rows = Time points ({numPoints})\n")
            f.write(f"% Columns: time(ms)  v(mV)  ko(mM)  ki(mM)  nao(mM)  nai(mM)\n")
            f.write(f"%\n")
            
            for i in range(numPoints):
                t   = self.timePoints[i]
                v   = self._traceData['v'][i]   if i < len(self._traceData['v'])   else 0.0
                ko  = self._traceData['ko'][i]  if i < len(self._traceData['ko'])  else 0.0
                ki  = self._traceData['ki'][i]  if i < len(self._traceData['ki'])  else 0.0
                nao = self._traceData['nao'][i] if i < len(self._traceData['nao']) else 0.0
                nai = self._traceData['nai'][i] if i < len(self._traceData['nai']) else 0.0
                f.write(f"{t:.6f} {v:.8f} {ko:.8f} {ki:.8f} {nao:.8f} {nai:.8f}\n")
        
        print(f" Done!")
        return filepath
    
    def _saveMatlabMetadata(self, timestamp):
        """Save a metadata file for easy MATLAB loading"""
        
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        
        filename = f"ko_metadata_{timestamp}.m"
        filepath = os.path.join(self.outputDir, filename)
        
        print(f"  Writing MATLAB metadata...", end='', flush=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("% MATLAB script to load K+ concentration data\n")
            f.write(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"% Recording interval: {self.recordInterval} ms\n\n")
            
            f.write("% Metadata\n")
            f.write(f"numShells      = {self.numShells};       % total = inner + outer\n")
            f.write(f"numInnerShells = {self.numInnerShells};  % inner zone: axon membrane -> R_sheath\n")
            f.write(f"numExtShells   = {self.numExtShells};    % outer zone: R_sheath -> Rmax (Schwann wall)\n")
            if self.schwannKoShellIdx is not None:
                f.write(f"schwannKoShellIdx = {self.schwannKoShellIdx}; "
                        f"% 0-based; shell {self.schwannKoShellIdx+1} in file numbering\n")
            f.write(f"numTimePoints  = {len(self.timePoints)};\n")
            f.write(f"numPositions   = {len(self.positions)};\n")
            f.write(f"recordInterval = {self.recordInterval}; % ms\n\n")
            
            f.write("% Position labels\n")
            f.write("positionLabels = {")
            f.write(", ".join([f"'{label}'" for label in self.positionLabels]))
            f.write("};\n\n")
            
            f.write("% Time vector (ms)\n")
            f.write("time = [")
            f.write(", ".join([f"{t:.6f}" for t in self.timePoints]))
            f.write("];\n\n")
            
            f.write("% Position vector (um)\n")
            f.write("position = [")
            f.write(", ".join([f"{p:.6f}" for p in self.positions]))
            f.write("];\n\n")
            
            f.write("% Load data for each shell\n")
            f.write(f"% Shells 1..{self.numInnerShells}: inner zone (axon membrane -> sheath boundary)\n")
            if self.numExtShells > 0:
                f.write(f"% Shells {self.numInnerShells+1}..{self.numShells}: "
                        f"outer zone (sheath boundary -> Rmax, Schwann wall)\n")
            for shellIdx in range(self.numShells):
                zoneTag = 'inner' if shellIdx < self.numInnerShells else 'outer'
                f.write(f"ko_shell{shellIdx+1} = load('ko_shell{shellIdx+1}_{timestamp}.txt'); "
                        f"% {zoneTag} zone\n")
            
            f.write("\n% Load mid-node-of-Ranvier traces\n")
            f.write(f"% File: midnode_traces_{timestamp}.txt\n")
            f.write(f"% Columns: time(ms)  v(mV)  ko(mM)  ki(mM)  nao(mM)  nai(mM)\n")
            f.write(f"midnode_traces = load('midnode_traces_{timestamp}.txt');\n")
            f.write(f"midnode_label = '{self._midNodeLabel}';\n")
            f.write(f"midnode_time = midnode_traces(:,1);\n")
            f.write(f"midnode_v    = midnode_traces(:,2);\n")
            f.write(f"midnode_ko   = midnode_traces(:,3);\n")
            f.write(f"midnode_ki   = midnode_traces(:,4);\n")
            f.write(f"midnode_nao  = midnode_traces(:,5);\n")
            f.write(f"midnode_nai  = midnode_traces(:,6);\n")
            
            f.write("\n% Example: Plot time course for all positions in shell 1\n")
            f.write("% figure;\n")
            f.write("% hold on;\n")
            f.write("% for i = 1:numPositions\n")
            f.write("%     plot(time, ko_shell1(:,i), 'DisplayName', positionLabels{i});\n")
            f.write("% end\n")
            f.write("% xlabel('Time (ms)');\n")
            f.write("% ylabel('K+ Concentration (mM)');\n")
            f.write("% title('K+ Concentration - Shell 1');\n")
            f.write("% legend('Location', 'best');\n")
            f.write("% grid on;\n")
        
        print(f" Done!")
    
    def stopRecording(self):
        """Stop recording and auto-save"""
        if self.isRecording:
            self.isRecording = False
            print(f"\n{'='*60}")
            print(f"Recording stopped. Total time points recorded: {len(self.timePoints)}")
            print(f"{'='*60}")
            if len(self.timePoints) > 0:
                print("Final save...")
                self.saveAllShellsAsMatrices()
                print(f"{'='*60}")
            else:
                print("No data was recorded!")
            
            # Clear RxD references after saving to prevent stale references
            self.shells = None
            self.k = None
    
    def clear(self):
        """Clear all recorded data and references"""
        if len(self.timePoints) > 0:
            print(f"Clearing {len(self.timePoints)} recorded time points...")
        
        # Clear all data
        self.timePoints = []
        self.koData = []
        self.positions = []
        self.positionLabels = []
        self.segments = []
        
        # Clear voltage/ion trace data
        for key in self._traceData:
            self._traceData[key] = []
        self._midNodeSeg = None
        self._midNodeLabel = ''
        
        # Clear RxD references
        self.shells = None
        self.k = None
        
        # Stop recording
        self.isRecording = False
        self.nextRecordTime = 0.0