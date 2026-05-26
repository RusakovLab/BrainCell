# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

**BRAINCELL** is a computational neuroscience simulation platform developed by the Savtchenko/Rusakov Lab at UCL. It combines:
- **NEURON 8.2.2 / 9.0.1** — the core electrophysiology simulator (both versions supported)
- **HOC** — NEURON's native scripting language (355 `.hoc` files)
- **MOD files** — NEURON mechanism definitions for ion channels, transporters, gap junctions (137 files across `Mechanisms/Astrocyte/`, `Mechanisms/Neuron/`, `Mechanisms/Common/`)
- **Python 3.11+** — export framework, AI agents, utilities (82 `.py` files)
- **JSON** — version-controlled biophysics configurations in `Biophysics/`

## Running the Project

### Docker (recommended)
```bash
docker compose run --rm braincell-shell      # interactive shell with compiled mechanisms
docker compose run --rm braincell-gui        # NEURON GUI (Linux, requires X11)
docker compose run --rm braincell-headless   # batch simulation (set BRAINCELL_SCRIPT env var)
```

### Local (macOS / Linux)
```bash
pip install neuron==8.2.2   # or neuron==9.0.1
# Compile MOD files in each mechanisms directory:
cd Mechanisms/Astrocyte/MOD_files && nrnivmodl
cd Mechanisms/Neuron/MOD_files    && nrnivmodl
cd Mechanisms/Common/MOD_files    && nrnivmodl
# Launch:
nrngui init.hoc
```

### Windows — NEURON 8.2.2 + Anaconda 2023.09
1. Install **Anaconda 2023.09** (x64) — enable **"Add Anaconda to PATH"** during installation
2. Restart Windows
3. Install **NEURON 8.2.2** (mingw, Python 3.7–3.11 compatible)
4. Compile MOD files (run in each `MOD_files` directory):
   ```
   nrnivmodl
   ```
5. Launch: `nrngui init.hoc`

### Windows — NEURON 9.0.1 + Anaconda (latest)
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
   (The fix delegates mechanism introspection to Python in `_Code/InterModular/UtilsAndHelpers/InterModularMechSettings.hoc`)
6. Compile MOD files and launch: `nrngui init.hoc`

### After adding/removing files
```bash
python braincell_mapper.py   # regenerates braincell_map.json (used by AI agents)
```

### Testing
Test entrypoints live in `_Testing/` as `init_*.hoc` files (e.g., `init_BioManager.hoc`, `init_ExportManager.hoc`). Run them individually with `nrngui _Testing/init_<Manager>.hoc`.

## Architecture

### Execution flow
```
init.hoc
  → InterModular/InterModularLoads.hoc
  → RoadmapWidget (user selects cell type + geometry)
  → roadmapChosenHandler()
      → Import morphology (_Code/Import/)
      → Prologue (biophysics init, _Code/Prologue/)
      → MainProgram.hoc → SimulationManager (15 ready-to-run sims)
```

### Manager pattern
All functionality is exposed through independent **Managers** in `_Code/Managers/`. Each manager controls one concern:
- `BioManager` — biophysical properties (channels, pumps, passive params)
- `SynManager` — synaptic transmission (AMPA, GABA, point processes)
- `GapJuncManager` — electrical and gap junction coupling
- `InhomManager` — inhomogeneous parameter distributions
- `StochManager` — stochastic mechanism variable mapping
- `ExportManager` — saves/exports simulation states

### Simulations
`_Code/Simulations/SimManager.hoc` orchestrates 15 simulations across four categories (Voltage, Electrical, FRAP, Calcium, Species). Simulation-specific HOC lives in `_Code/Simulations/Sims/Astrocyte/`, `.../Common/`, `.../Neuron/`.

### Export / code-generation framework
`_Code/Export/PythonCode/Framework.py` generates standalone HOC packages:
1. Loads a skeleton template from `_Code/Export/OutHocFileStructures/Skeletons/`
2. Scans for markers: `py:` (call a Python generator), `@` (meta-generator), `)` (end-marker)
3. Generator classes in `GeneratorsForMainHocFile/` and `GeneratorsForAuxHocFiles/` substitute or insert lines
4. Outputs `params.hoc`, `runner.hoc`, and copies `nrnmech.dll`

### Biophysics configs
JSON files in `Biophysics/` map directly to NEURON PARAMETER/STATE variables. These are version-controlled presets for reproducibility. Astrocyte presets: `SimCalcium.json`, `SimFrap.json`, `SimGlutamate.json`, `SimPotassium.json`. Neuron adds `SimMyelinatedAxon.json`, `SimVoltageCA1Neuron.json`.

### MOD files
Each subdirectory under `Mechanisms/` compiles independently with `nrnivmodl`, producing one `libnrnmech.so` (Linux/macOS) or `nrnmech.dll` (Windows) per folder. Do not move MOD files between directories without recompiling.

### AI agents (built-in)
- `braincell_mapper.py` — indexes all `.mod`, `.hoc`, `.py` files into `braincell_map.json`
- `braincell_agent.py` — CLI agent using Claude API with `braincell_map.json` as its knowledge base
- `braincell_panel.py` — GUI variant of the agent
- Requires `ANTHROPIC_API_KEY` env var and `pip install anthropic`

## Key Conventions

- `_Code/InterModular/` holds cross-cutting utilities and Tk widget wrappers used across managers.
- `_Testing/` mirrors manager names; add `init_<ManagerName>.hoc` when testing a new manager.
- Geometry files (`.hoc`, `.swc`, `.asc`) go in `Geometry/` (base) or `Nanogeometry/` (with procedural nano-structures from `_Code/NanoSeeding/`).
- Biophysics JSON changes must remain backward-compatible; the manager reads these at runtime.
- After any structural code change, re-run `braincell_mapper.py` so the AI agents stay in sync.
