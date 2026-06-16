# SimMyelinatedAxon — Rules for LLM Code Assistance

Add this section to the project `CLAUDE.md`.
These rules were learned by debugging the TRPA1 KO experiment panel (June 2026).
Violating any of them produces silent failures or cryptic NEURON errors.

---

## HOC access to SimMyelinatedAxon parameters

### Rule 1 — Use `SimMyelinatedAxonParamsHelper[0]`, not `paramsHelper`

`paramsHelper` is a Python object (`self._paramsHelper` in `SimMyelinatedAxon.__init__`).
It is **not** a global HOC variable and cannot be accessed from HOC as `paramsHelper`.

The correct HOC name is `SimMyelinatedAxonParamsHelper[0]` — the HOC template instance
registered by NEURON when `h.SimMyelinatedAxonParamsHelper(...)` is called in Python.

All members declared `public` in `ParamsHelper.hoc` are writable directly:

```hoc
// CORRECT
SimMyelinatedAxonParamsHelper[0].diam_axon   = 0.73
SimMyelinatedAxonParamsHelper[0].Diff_k      = 0.20
SimMyelinatedAxonParamsHelper[0].ko0         = 3.0

// WRONG — syntax error
paramsHelper.diam_axon = 0.73

// WRONG — AttributeError from Python
h.paramsHelper.diam_axon = 0.73
```

### Rule 2 — `nrnpython()` calls do NOT share scope

Each `nrnpython("...")` call executes in a fresh Python scope.
Variables defined in one call are **not** visible in the next.

```hoc
// WRONG — _ph is lost after first call, NameError on second
nrnpython("_ph = some_object")
nrnpython("_ph.attr = value")   // NameError: _ph is not defined

// CORRECT — everything in one call, or use the HOC object directly (Rule 1)
nrnpython("some_object.attr = value")
```

If you must use `nrnpython` for Python-only objects, put all logic in a single string
or register the object as a module-level variable before the HOC file loads.

### Rule 3 — `begintemplate` does not see global HOC arrays

Global arrays declared with `double arr[1]` at the top level of a HOC file
are **not** visible inside a `begintemplate ... endtemplate` block.

```hoc
// WRONG — "arr not an array variable" error inside template
double arr[1]
begintemplate MyPanel
    proc show() {
        xpvalue("label", &arr[0], 1)   // error: arr not visible here
    }
endtemplate MyPanel

// CORRECT — put show() in a plain global proc instead
double arr[1]
proc myPanel_show() {
    xpvalue("label", &arr[0], 1)       // works: global proc sees global arrays
}
```

### Rule 4 — `(int)` cast is C syntax, not HOC

HOC does not support C-style casts. Use the `int()` function instead.

```hoc
// WRONG — syntax error
printf("%d\n", (int)myVar)

// CORRECT
printf("%d\n", int(myVar))
```

### Rule 5 — No Unicode in HOC strings

NEURON uses ASCII internally. Any Unicode character in `xlabel`, `printf`, or `strdef`
causes an ASCII codec error at load time.

```hoc
// WRONG — crashes with codec error
xlabel("Control → KO")
xlabel("g-ratio ≈ 0.79")

// CORRECT — ASCII only
xlabel("Control -> KO")
xlabel("g-ratio ~ 0.79")
```

### Rule 6 — Load order: panel after `programmaticClick`

`SimMyelinatedAxonParamsHelper[0]` does not exist until `SimMyelinatedAxon.__init__`
runs, which happens inside `simManager.programmaticClick(simIdx)`.

Any HOC file that references `SimMyelinatedAxonParamsHelper[0]` must be loaded
**after** `programmaticClick`, not before.

```hoc
// CORRECT order in init_MyelinSim.hoc
if (simIdx != -1) {
    simManager.programmaticClick(simIdx)   // creates SimMyelinatedAxonParamsHelper[0]
}
{ load_file("_Testing/TRPA1_KO_DemyelPanel.hoc") }  // safe to use it now
```

Do NOT call `panelObject.show()` automatically from the init file — this conflicts
with `IClampHelper` inside `programmaticClick`. Call `trpa1_show()` manually
from the HOC console after BrainCell finishes loading.

---

## Experiment panel: TRPA1_KO_DemyelPanel.hoc

**Location:** `_Testing/TRPA1_KO_DemyelPanel.hoc`
**Load:** automatically via `init_MyelinSim.hoc` (last two lines)
**Open:** type `trpa1_show()` in HOC console

### Presets

| Preset | `diam_sheath` | g-ratio | `paranodal_gL_scale` | Scientific basis |
|---|---|---|---|---|
| CONTROL | 0.924 µm | 0.79 | 1.0 | Arancibia-Carcamo 2017, optic nerve EM |
| TRPA1-KO MILD | 0.990 µm | 0.74 | 1.5 | Slight myelin thinning + mild CASPR cluster |
| TRPA1-KO SEVERE | 1.10 µm | 0.66 | 3.0 | Chow 2026 Fig 3 targets (CAP latency ~2x) |

### Key parameter corrections vs. BrainCell defaults

| Parameter | BrainCell default | Correct control value | Reason |
|---|---|---|---|
| `Diff_k` | 0.02 µm²/ms | **0.20 µm²/ms** | Default is 10x too low; Syková & Nicholson 2008 |
| `ko0` | 2.5 mM | **3.0 mM** | Standard CNS ECS; 2.5 mM is patch-clamp artefact |

Do NOT restore `Diff_k = 0.02`. See `MyelinatedAxon_ControlParameters.md` for full citations.

### How paranodal leak works

`paranodal_gL_scale` multiplies `g_pas` on all `axonNodeOfRanvier` sections:

```hoc
g_pas = 0.1e-3 * _p_paranodal_gL_scale[0]   // S/cm2
```

This models CASPR-only cluster phenotype (loss of mature paranodal junctions,
Fig 3i-j in Chow 2026): current leaks radially at the node instead of being confined,
slowing AP propagation and reducing CAP amplitude.

### CAP targets for validation (Chow 2026 Fig 3a-d)

| Condition | P1 latency | P1 amplitude | FWHM |
|---|---|---|---|
| Control | ~1 ms | ~8 mV | ~0.8 ms |
| KO mild | +30–50% | −20–30% | +30–50% |
| KO severe | ~2× | ~half | ~2× |

---

*Added: June 2026. Leonid Savtchenko / Rusakov Lab UCL.*
*Companion files: `MyelinatedAxon_ControlParameters.md`, `Basic.hoc`, `ParamsHelper.hoc`.*
