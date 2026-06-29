# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What This Project Is

**BrainCellDevelopment** is the active testing and development version of BrainCell — a NEURON-based simulation framework for modeling individual neurons and astrocytes with detailed biophysical mechanisms and extracellular ion dynamics. It supports multi-scale modeling: base geometry (soma, axon, dendrites) and nanogeometry (dendritic spines for neurons, stalks for astrocytes).

This directory is not under git version control — it is used for experimental changes before they are promoted to BrainCell or BrainCellClaude.

Primary languages: **HOC** (NEURON scripting), **Python** (code generation), **MOD files** (biophysical mechanisms).

Supported NEURON versions: **8.2.2** and **9.0.1** (both tested on Windows).

## Windows Installation

### NEURON 8.2.2 + Anaconda 2023.09
1. Install **Anaconda 2023.09** (x64) — enable **"Add Anaconda to PATH"** during installation
2. Restart Windows
3. Install **NEURON 8.2.2** (mingw, Python 3.7–3.11 compatible)
4. Build mechanisms: `.\build_mechs.ps1`
5. Launch: `init.bat`

### NEURON 9.0.1 + Anaconda (latest)
1. Install **Anaconda** from https://www.anaconda.com/download — use default settings (**do NOT** add to PATH during install)
2. Install **NEURON 9.0.1** (`nrn-9.0.1.w64-mingw-py-39-310-311-312-313-314-setup.exe`) to a path with no spaces (e.g. `C:\nrn`)
3. Manually add Anaconda to the **system** PATH — open Anaconda PowerShell Prompt and run:
   ```powershell
   # Find your Python folder:
   python -c "import sys; print(sys.executable)"
   # Add that folder (e.g. C:\Users\YourName\anaconda3) to system PATH:
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\YourName\anaconda3", "Machine")
   ```
   Close and reopen any command prompts afterwards.
4. Verify NEURON finds Python:
   ```
   python -c "from neuron import h; print(h.nrnversion())"
   ```
   Expected output: `NEURON -- VERSION 9.0.1 ...`
5. NEURON 9 compatibility is already patched in the codebase — no manual HOC edits needed.
6. Build mechanisms: `.\build_mechs.ps1`
7. Launch: `init.bat`

## Build & Run

**Build mechanisms (must be done after any MOD file change):**
```powershell
.\build_mechs.ps1
```
This compiles MOD files from `Mechanisms/Common/` and `Mechanisms/Astrocyte/` or `Mechanisms/Neuron/` into `nrnmech.dll`. It requires NEURON to be installed and `%NEURONHOME%` set. The script merges Common + cell-type-specific MOD files into a temp folder, then calls `mknrndll.bat` with elevated privileges. It copies the resulting DLL to both `Mechanisms/<CellType>/` and `Nanogeometry/<CellType>/`.

**Run the simulation:**
```batch
init.bat
```
Equivalent to: `%NEURONHOME%\bin\neuron.exe init.hoc`

**Run a specific test:**
```batch
_Testing\drag_&_drop_init.bat _Testing\init_BioManager.hoc
```
Drop any `_Testing\init_*.hoc` file onto `_Testing\drag_&_drop_init.bat`, or pass it as argument.

**Run an example:**
```batch
Examples\01_CA1_SingleNeuron\Run.bat
```

## Startup Flow

1. `init.hoc` — loads `InterModularLoads.hoc` (shared utilities), creates `MechsDllUtils`, loads `RoadmapWidget.hoc`, calls `theEntryPoint()`
2. **RoadmapWidget** — user chooses: base geometry vs. nanogeometry, neuron vs. astrocyte, or external simulation
3. Based on choice, loads:
   - Base geometry path: `_Code/Import/ImportBaseGeometry/Import.hoc` → `_Code/Prologue/{Astrocyte,Neuron}/init*.hoc`
   - Nanogeometry path: loads the pre-seeded `.hoc` from `Nanogeometry/`
4. Both paths end by calling `prologueCompleteHandler()` → `_Code/MainUI/MainProgram.hoc` → `runMain()`

## Architecture

### Module Layout

- **`_Code/InterModular/`** — Cross-cutting utilities (math, strings, sections, enums, widgets). Always loaded first via `InterModularLoads.hoc`. Contains shared `objref` globals like `soma_ref`, `axon_ref`, `nanoBranchesManager`, `mmAllComps`, `gjmAllGapJuncSets`, `smAllSynSets`.
- **`_Code/Managers/`** — Manager subsystems, each independently testable:
  - `MechManager/` — Biophysics parameter management; loads baseline from JSON, supports runtime editing
  - `SynManager/` — Synapse sets and placement
  - `GapJuncManager/` — Gap junction sets
  - `InhomAndStochLibrary/` — Inhomogeneous and stochastic parameter distributions
- **`_Code/NanoCore/`** — Nanocompartment seeding and management for spines (Neuron/) and stalks (Astrocyte/)
- **`_Code/Extracellular/`** — Ion diffusion:
  - `InsideOutDiffusion/` — Intracellular → extracellular flux
  - `OutsideInDiffusion/` — Extracellular K⁺/Ca²⁺ radial diffusion with configurable Schwann cell shell
- **`_Code/Export/`** — Python-driven HOC code generation for standalone/cluster runs
- **`_Code/Import/`** — Cell geometry loaders (SWC or HOC morphologies)
- **`_Code/Prologue/`** — Cell-type initialization (`initNeuron.hoc`, `initAstrocyte.hoc`)
- **`_Code/MainUI/`** — Main UI panels, plots, and run control
- **`_Code/Simulations/`** — Simulation parameter management
- **`_Code/Clamps/`** — Voltage-clamp and current-clamp implementations
- **`_Code/Headless/`** — Non-GUI execution mode

### Key Design Constraints

**Section recreation resets biophysics.** Switching geometry modes (base ↔ nano, "Use test sines") destroys all HOC sections and reloads from JSON baseline. Any runtime edits to biophysical parameters are lost. Use Export to persist edits before switching.

**Python–HOC integration.** Python is called from HOC via `sourcePythonCode()` (defined in `InterModularPythonUtils.hoc`). The Export system uses Python to generate HOC files from skeleton templates using marker substitution (`py:`, `@`). Python warnings surface at startup via `sourcePythonCodeForExport()`.

**DLL placement matters.** `nrnmech.dll` must be present next to the HOC entry point being launched — `Mechanisms/<CellType>/nrnmech.dll` for base runs, `Nanogeometry/<CellType>/nrnmech.dll` for nano runs. The build script handles this automatically.

**`codeContractViolation()`** is used as a placeholder for abstract procedures in `InterModularLoads.hoc` (e.g., `makeSureGapJuncSetsCreatedOrImported`). Concrete implementations are provided by the manager that fulfills the contract.

### Testing

Each `_Testing/init_*.hoc` file exercises one manager in isolation. They all start with `_CommonPrologueForTests.hoc`, which sets `isBaseOrNanoStart = 0`, loads `InterModularLoads.hoc`, and loads a pre-seeded nanogeometry file. Tests are run manually inside NEURON — there is no automated test runner.

## Recent Features Added

- **Extra-cell axon compartment lists** (June 2026): `ExtraCell.py` now exposes `axon_list_ref`, `dend_list_ref`, and `soma_list_ref` as HOC-accessible attributes alongside the existing `list_ref` (all sections). Each is `hasattr`-guarded and returns `None` when the morphology lacks that compartment type. These are created by `Import3d_GUI.instantiate(self)` and simply surface the already-existing `self.axon` / `self.dend` / `self.soma` lists. File: `_Code/Import/ImportExtraCells/PythonCode/ExtraCell.py:175-178`.

- **"Generate srcs along axon" retargeted to extra cell** (June 2026): The "Basket cell GABA diffusion" simulation (`_Code/Simulations/Sims/Common/SimOutsideInDiffusion.hoc`) can now generate extracellular GABA sources along a secondary (extra) cell's axon instead of the primary CA1 axon. A new "Axon target:" radio-button panel lets the user choose between primary axon and extra cell axon. Defaults to the extra cell when one with a non-empty `axon_list_ref` is loaded. The section-gathering in `generateSrcsAlongAxonHandler()` (formerly hard-wired to `axonCompOrNil.list_ref`) now reads from `chosenExtraCellOrNil.axon_list_ref`. Source-to-segment binding and physics are unchanged — placement remains purely 3D-coordinate-driven. Related change: `ExtraCellsManagerWidget` gained a public `getFirstExtraCellWithAxon()` getter (`_Code/Import/ImportExtraCells/ExtraCellsManagerWidget.hoc`) that walks `listOfExtraCellListItems` and returns the first `pyExtraCell` with a non-empty `axon_list_ref`. Limitation: only the first qualifying extra cell is returned; an index-based selector would be needed for multiple interneurons.

- **NLMorphologyConverter Python wrapper** (June 2026): `_Code/Import/3rdParty/NLMorphologyConverter/nlmc_swc.py` — a thin subprocess wrapper around `NLMorphologyConverter.exe` for converting morphology files to SWC. Public API: `convert_to_swc(input_path, ...)` and `convert_folder(input_dir, ...)`. Validates output (file exists, non-empty, >=2 valid SWC data lines, at least one root), strips non-ASCII bytes with a warning (NEURON crashes on non-ASCII), and surfaces the exe's captured stdout/stderr on failure. CLI entry point: `python nlmc_swc.py INPUT [OUTPUT] [--stats] [--overwrite]` or `python nlmc_swc.py --batch DIR [--pattern "*.hoc"] [--out DIR]`. Standard library only. Companion batch file: `convert_hoc_to_swc.bat` double-click converts all `.hoc` files in the same folder, outputs to `swc_out\`.

- **Save/Load myelination config**: two buttons in the `SimMyelinatedAxon` GUI allow saving and loading all myelination parameters to/from `.hoc` files in the `Nanogeometry/` folder. Uses `h.string_dialog()` for filename input and direct HOC line execution via Python `open()` + `h(line)` (not `h.load_file()`) to avoid NEURON's file-caching behaviour. Implemented in `_Code/Simulations/Sims/Neuron/SimMyelinatedAxon/SimMyelinatedAxon.py`.

- **Ko data recording toggle**: an `xcheckbox` "Save Ko data" in the `SimMyelinatedAxon` panel controls whether extracellular K⁺ concentration data is recorded to the `ko_output/` folder during simulation. `KoDataSaver.py` handles recording at `recordInterval=0.1 ms`, saving per-shell MATLAB-compatible matrix files and mid-node-of-Ranvier voltage/ion traces. The toggle syncs to `SimCore.isSaveKoData` and persists across runs within a session. Implemented across `SimMyelinatedAxon.py`, `SimCore.py`, and `KoDataSaver.py`.

- **`init_MyelinSim.hoc`**: new test entry point in `_Testing/` that launches `SimMyelinatedAxon` (simIdx=13) automatically with the correct myelinated neuron morphology (`Nanogeometry/Neuron/Myelinatedaxon.hoc`) via a custom `_MyelinPrologueForTests.hoc`. Run with `drag_&_drop_init.bat`.

## Known Bugs / Open Issues

- **HOC extra-cell Y-offset after export → re-import** (diagnosed June 2026, not yet fixed): When a secondary cell is imported from a `.hoc` file (rather than `.swc`), re-importing an exported session places the cell's geometry at the correct position but sources generated from its axon appear offset in Y. Root cause: `hoc2swc` (`_Code/Import/ImportExtraCells/PythonCode/Separated/ThirdParty/hoc2swc.py`) calls `h.define_shape()` and assigns SWC type 1 to soma sections (via `swc_type_from_section_name`). The export soma-stripping filter (`GeneratorsForMainHocFile.py:853`) then removes all type-1 points. At re-import, NEURON synthesises a new soma from the first child connection point, whose Y coordinate differs from the original soma centre Y (`getSomaSecCentreCoords`, `InterModularSectionUtils.hoc:292`). This mismatch causes a constant Y shift applied to geometry but not to ECS sources (absolute coordinates). X and Z are unaffected because soma cylinders extend along Y in the default layout. **Workaround: use SWC format for secondary cells.** For HOC morphologies, convert once with `nlmc_swc.py` or `convert_hoc_to_swc.bat` and import the resulting SWC. Proposed fix (not applied): bake the export-time `_cy` literal into the shift string in `createExtraCells()` (`GeneratorsForMainHocFile.py:887`) rather than re-deriving it from fresh synthesis. Backward-compatibility caveat: old exported HOC files lacking the baked constant would continue to use the re-derived path.

## NotebookLM Integration

NotebookLM is connected and can be queried directly from Codex to access scientific documentation, user guides, and research papers.

### How to query NotebookLM

Use this command pattern:

    C:\Users\savtc\anaconda3\Scripts\notebooklm.exe ask --notebook <NOTEBOOK_ID> "your question" > C:\Users\savtc\nlm_answer.txt 2>&1

Then read `C:\Users\savtc\nlm_answer.txt` for the answer.

### Available notebooks (key ones for BrainCell work)

Always run `notebooklm list --json` first to get the current list 
of notebooks and their IDs before making any ask query. 
Do not rely on hardcoded IDs.

### List all notebooks

    C:\Users\savtc\anaconda3\Scripts\notebooklm.exe list --json > C:\Users\savtc\nlm_list.txt 2>&1

### Notes
- Responses may take 60-180 seconds
- Auth is stored at: `~/.notebooklm/profiles/default/storage_state.json`
- If auth expires, run: `C:\Users\savtc\anaconda3\Scripts\notebooklm.exe login`

---

## SimMyelinatedAxon — HOC Panel Rules (learned June 2026)

### Graph recording in HOC panels

When recording from Python-created sections inside a HOC panel file:

- Use `forsec "sectionname" { vec.record(&v(0.5)) }` with a done-flag to stop after the first match — inside the `forsec` block, `v(0.5)` is a plain HOC ref, no `_pysec` needed
- **Do NOT** use `vec.record()` inside `proc run()` or `proc alt_run()` overrides — `AltRunControlWidget` passes section pointers through the call stack and they are in a transient state during HOC→Python→HOC re-entry, causing `"size: object prefix is NULL"`
- **Do NOT** use `FInitializeHandler` to arm recording — it fires while NEURON section state is in flux
- Arm recording at explicit user-driven moments only: button click ("Open graphs"), or "Clear graphs"
- Use `FInitializeHandler` only for things that do not touch section references

### Plotting dV/dt vs V (phase portrait) in NEURON 8.2

`Vector.plotvs()` does not exist in NEURON 8.2. Use `graph.beginline()` + `graph.line()` loop instead:

```hoc
// WRONG -- plotvs does not exist in NEURON 8.2
dvdt_vec.plotvs(graph, v_vec)

// CORRECT -- manual point-by-point
graph.beginline(2, 2)
for i = 1, dvdt_vec.size()-1 {
    graph.line(v_vec.x[i], dvdt_vec.x[i])
}
graph.flush()
```

Compute dV/dt using central difference with recorded time vector (CVode-compatible):

```hoc
for i = 1, vRec.size()-2 {
    dvdt_vec.x[i-1] = (vRec.x[i+1] - vRec.x[i-1]) / (tRec.x[i+1] - tRec.x[i-1])
}
```

### Graph.erase_all() removes addexpr bindings

After `graph.erase_all()`, the graph no longer knows what to record. Must re-call `addexpr` immediately after:

```hoc
proc _trpa1_btnClearGraphs() {
    _trpa1_gVt.erase_all()
    _trpa1_gVt.addexpr("_pysec.axonUnderSchwann[0].v(.5)", 2, 2)   // re-arm
    _trpa1_gKot.erase_all()
    _trpa1_gKot.addexpr("_pysec.axonUnderSchwann[0].ko(.5)", 2, 2)  // re-arm
}
```

### Correct section names for addexpr in SimMyelinatedAxon

Sections are created in Python via `h.Section(name=...)`. The exact names are:

```
axonUnderSchwann[0], axonUnderSchwann[1], ...   (internodes)
axonNodeOfRanvier[0], axonNodeOfRanvier[1], ... (nodes)
axonAfterLastSchwann                             (axon end)
```

Use in `addexpr`:

```hoc
graph.addexpr("_pysec.axonUnderSchwann[0].v(.5)", 2, 2)   // V at first internode
graph.addexpr("_pysec.axonUnderSchwann[0].ko(.5)", 2, 2)  // K+ at first internode
graph.addexpr("_pysec.axonAfterLastSchwann.v(1)", 3, 2)   // V at axon end
```

Middle internode (SimCore default): `axonUnderSchwann[3]` for 7 Schwann cells.

### TRPA1 KO experiment panel

**File:** `_Testing/TRPA1_KO_DemyelPanel.hoc`  
**Open:** type `trpa1_show()` in HOC console after BrainCell loads.

**Workflow:**

1. Launch `init_MyelinSim.hoc`
2. Type `trpa1_show()` in console
3. Set time to 5 ms, run once (initialisation step)
4. Set desired time (e.g. 5000 ms)
5. Click preset (Control / KO Mild / KO Severe)
6. Click "Open comparison graphs"
7. In each graph window click "Keep Line"
8. Run simulation — graphs 1 and 2 fill automatically
9. Click "Update phase portrait" to populate graph 3
10. Repeat with new preset — change line colours manually between runs

**Scientific basis:** Chow et al. Nat Commun 2026 (SNAP-23 icKO optic nerve).  
**Parameter corrections applied:** Diff_k 0.02→0.20 µm²/ms, ko0 2.5→3.0 mM.
