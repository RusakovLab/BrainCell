# Myelinated Axon — Control Physiological Parameters

**Purpose:** Reference parameter set for the `SimMyelinatedAxon` simulation in BrainCell,
based on systematic literature review (May–June 2026).
Place this file alongside `CLAUDE.md` so any LLM working on the simulation reads it automatically.

**Biological context:** Mouse / rat optic nerve, adult myelinated CNS axons, retinal ganglion cells (Alpha RGC type).
Temperature: 35 °C throughout unless stated.

---

## Critical corrections vs. previous parameter set

These three must be changed before any control simulation is considered physiologically valid.

| Parameter | Previous (wrong) | Corrected | Reason |
|---|---|---|---|
| `Diff_k` | 0.02 µm²/ms | **0.20 µm²/ms** (periaxonal) | 10–100× below any physically possible value; see §3 |
| `g_Na` (node) | 3000 mS/cm² | **700 mS/cm²** | 3000 is for large peripheral motor axons (MRG model), not CNS |
| `E_rest` | −82 mV | **−67 mV** | −82 mV is peripheral myelinated fibre; mouse RGC rests at −65–70 mV |
| `τm Na activation` | 54 ms | **0.054 ms (54 µs)** | Unit transcription error; 54 ms makes AP propagation impossible |
| `ko0` | 2.5 mM | **3.0 mM** | Standard CNS ECS resting [K⁺]o; 2.5 mM is a periaxonal patch artefact |

---

## 1. Geometry — axon trunk and node of Ranvier

> Source tissue: rat / mouse optic nerve, adult. All EM-based unless stated.

| Parameter | Control value | Unit | Range | Reference |
|---|---|---|---|---|
| `diam_axon` | 0.73 | µm | 0.5–1.0 | Arancibia-Carcamo et al., *eLife* 2017 — Fig. 1, EM, n=46 |
| `L_node` | 1.02 | µm | 0.7–1.4 | Arancibia-Carcamo et al., *eLife* 2017 — confocal; EM mean 1.08 ± 0.02 |
| `L_internode` | 139 | µm | 80–200 | Arancibia-Carcamo et al. 2017; Pajevic et al. 2014 |
| `L_paranode` | 2.1 | µm | 1.5–3.0 | Arancibia-Carcamo et al. 2017, Table 1 |
| `g-ratio` | 0.79 | — | 0.75–0.83 | Arancibia-Carcamo et al. 2017, citing Sugimoto 1984; Oorschot 2013 |
| `myelin wraps` | 7 | — | 5–9 | Arancibia-Carcamo et al. 2017 (−1 wrap → −8.6% CV) |
| `periaxonal width` | 15 | nm | 10–20 | Mierzwa et al. 2010; paranodal spiral cross-section A = 170 nm² |
| `diam_sheath` | ~0.93 | µm | — | Derived: `diam_axon / g-ratio` = 0.73 / 0.79 |

### AIS geometry (mouse Alpha RGC)

| Parameter | Formula | Typical value |
|---|---|---|
| AIS distance from soma | 1.22 × soma_diam − 5.0 µm | ~18 µm (soma 19 µm) |
| AIS length | 1.38 × soma_diam − 1.6 µm | ~25 µm (soma 19 µm) |

> Reference: Zhu et al. 2006; Kolkman et al. 2011 — linear scaling in Alpha RGCs.

---

## 2. Ion channel conductances

> All conductances in mS/cm², 35 °C.

| Region | Channel | `ḡ` control | Range | Reference |
|---|---|---|---|---|
| Node of Ranvier | Nav1.6 (`g_Na`) | 700 | 500–1000 | Caldwell et al. *Brain Res. Mol.* 2000; Van Wart & Matthews *J. Neurosci.* 2006 |
| Node | Kv3.1 (`g_Ks`) | 80 | 60–100 | Arancibia-Carcamo et al. 2017, Table 1 |
| Node | Nav1.6 persistent (`g_Nap`) | 5 | 2–8 | Craner et al. *PNAS* 2004; Stys et al. 1993 |
| Node | Leak (`g_L`) | 0.1 | 0.07–0.2 | Halter & Clark 1991; Arancibia-Carcamo et al. 2017, Table 1 |
| Internode | Leak (`g_L`) | 0.001 | 0.0005–0.005 | Halter & Clark *J. Neurophysiol.* 1991 |
| AIS distal | Nav1.6 | 350 | 300–450 | Lorincz & Nusser *Science* 2010; Van Wart & Matthews 2006 |
| AIS proximal | Nav1.1 | 325 | 275–400 | Boiko et al. *Neuron* 2003 |
| AIS distal | Kv1.6 | 175 | 150–200 | Rasband & Trimmer 2001 |
| Soma (Alpha RGC) | Na⁺ | 90 | 60–158 | O'Brien et al. 2002 |
| Soma | K⁺ | 60 | 36–95 | O'Brien et al. 2002 |
| Glia / sheath | Kir4.1 (`g_kir`) | 1.44 | 1.0–2.0 | Olsen & Sontheimer *Glia* 2008; Kofuji & Newman *Nat. Rev. Neurosci.* 2004 |

### Why g_Na = 700 mS/cm², not 3000 mS/cm²

The value 3000 mS/cm² originates from the McIntyre-Richardson-Grill (MRG) CRRSS model of **large human peripheral motor axons** (diameter 10–20 µm).
CNS optic nerve axons:
- Are much smaller (0.5–1.0 µm diameter)
- Express Nav1.6 at densities of 1000–2000 channels/µm² (immunogold EM)
- Have nodal areas ~100× smaller than large peripheral nodes

Converting 1500 channels/µm² × single-channel conductance (~20 pS) → ~700 mS/cm² for CNS nodes.
Using 3000 mS/cm² will produce unrealistically large inward currents, distort AP shape, and require compensatory over-tuning of other parameters.

---

## 3. Ion concentrations and diffusion — most critical section

### 3.1 Resting concentrations

| Parameter | `ko0` | `ki0` | `[Na]o` | `[Na]i` |
|---|---|---|---|---|
| Control value | **3.0 mM** | 120 mM | 145 mM | 14 mM |
| Range | 2.5–3.5 | 115–130 | 140–150 | 12–16 |
| Reference | Syková & Nicholson *Physiol. Rev.* 2008 | Stys et al. *J. Neurochem.* 1997 | Standard | Stys et al. 1997 |

### 3.2 Diffusion coefficient — the most important correction

The diffusion coefficient hierarchy:

```
D_free (K⁺ in water, 25°C) = 1.96 µm²/ms
    ↓  tortuosity λ = 1.6 (normal brain ECS)
D_ECS  = D_free / λ² = 1.96 / 2.56 ≈ 0.76 µm²/ms
    ↓  additional confinement: 15 nm periaxonal spiral gap
D_periaxonal ≈ 0.10 – 0.30 µm²/ms
```

| Compartment | `Diff_k` value | Unit | Reference |
|---|---|---|---|
| Free aqueous (upper bound) | 1.96 | µm²/ms | Syková & Nicholson *Physiol. Rev.* 2008, Table 1 |
| Brain ECS (λ = 1.6) | 0.76 | µm²/ms | Perez-Pinzon et al. *J. Physiol.* 2002 (λ = 1.69 ± 0.05) |
| **Periaxonal — recommended control** | **0.20** | **µm²/ms** | Derived; Arancibia-Carcamo et al. 2017 (spiral geometry); Hrabe et al. *Biophys. J.* 2004 |
| BrainCell previous default | ~~0.02~~ | µm²/ms | **Incorrect — ~10× too low; do not use** |

**Recommended sensitivity sweep:** 0.10, 0.20, 0.30 µm²/ms.
Run all three and report Diff_k as a parameter, not a fixed constant.

> **Why 0.02 µm²/ms is wrong:**
> Even in the most confined biological spaces (synaptic cleft ~20 nm, our lab TCSPC data: Zheng et al. *Sci. Rep.* 2017),
> effective diffusion does not fall below ~0.10–0.15 µm²/ms for small ions.
> At 0.02 µm²/ms, K⁺ clearance is ~10–40× too slow.
> The 2-second periaxonal recovery timescale previously reported is an artefact of this wrong value.
> With Diff_k = 0.20 µm²/ms, expected recovery is 100–400 ms (consistent with Kofuji & Newman 2004).

### 3.3 K⁺ dynamics per action potential

| Quantity | Control value | Notes |
|---|---|---|
| [K⁺]o at rest | 3.0 mM | Standard CNS ECS baseline |
| [K⁺]o after single AP (periaxonal) | 3.5–4.5 mM | Rise from 3 mM baseline |
| [K⁺]o ceiling (sustained HF firing) | ~12 mM | Kofuji & Newman 2004 |
| Recovery timescale (Diff_k = 0.20) | 100–400 ms | Physiologically correct |
| Recovery timescale (Diff_k = 0.02) | ~2000 ms | **Artefact — do not cite as physiological** |

---

## 4. Equilibrium potentials (35 °C, Nernst equation)

| Potential | Control value | Formula basis |
|---|---|---|
| E_Na | +58 mV | [Na]o = 145, [Na]i = 14 mM |
| E_K (rest, [K]o = 3.0 mM) | −93 mV | [K]i = 120 mM |
| E_K ([K]o = 5.0 mM) | −84 mV | After moderate K⁺ accumulation |
| E_leak | −64.6 mV | Halter & Clark 1991 |
| **E_rest (mouse RGC)** | **−67 mV** | **−65 to −70 mV from whole-cell patch; see note** |

> **E_rest note:** The value −82 mV appears in peripheral myelinated fibre models (Frankenhaeuser-Huxley frog node;
> Schwarz-Eikhof rat sciatic). Mouse retinal ganglion cells rest at −65 to −70 mV
> (O'Brien et al. 2002; Borghuis et al. *J. Neurosci.* 2013 — standard holding potential −70 mV).
> Using −82 mV displaces the AP threshold window by ~15 mV and requires compensatory rescaling of channel densities.

---

## 5. Electrical constants

| Parameter | Control value | Unit | Reference |
|---|---|---|---|
| `Cm` (membrane) | 0.9 | µF/cm² | Gentet et al. *Biophys. J.* 2000; Arancibia-Carcamo et al. 2017, Table 1 |
| `Cm` (per myelin lamella) | 0.9 | µF/cm² | Halter & Clark 1991 (two membranes per lamella) |
| `Ri` (axial, 20 °C) | 70 | Ω·cm | Rall, *Handbook of Physiology* 1977 |
| `Ri` (axial, 35 °C) | 110 | Ω·cm | Temperature-corrected via viscosity ratio ~1.57 |
| AP threshold (AIS) | −49 | mV | Bhatt et al. *J. Physiol.* 2017; Grubb & Burrone 2010 |
| Soma regeneration threshold | −16 | mV | ~33 mV above AIS threshold |
| AP amplitude | 70–90 | mV | O'Brien et al. 2002 |
| Conduction velocity (optic nerve) | 2.5–15 | m/s | Gasser & Grundfest 1939; peak ~6–8 m/s for median diameter |
| Temperature | 35 | °C | Mammalian physiological |

---

## 6. Kinetic parameters (channel gating, 35 °C)

| Parameter | Control value | Unit | Notes | Reference |
|---|---|---|---|---|
| **τm Na activation** | **0.054** | **ms (= 54 µs)** | **Previously listed as 54 ms — unit error** | Rush et al. *J. Neurophysiol.* 2005; HH Q₁₀ = 3 |
| τh Na inactivation | 1.8 | ms | Fast inactivation | Rush et al. 2005; Schwarz & Eikhof 1987 |
| τn K activation | 1.0 | ms | Delayed rectifier at 35 °C | HH 1952; Schwarz & Eikhof 1987 |
| τ_Ca (sequestering) | 50 | ms | Calcium buffering/pump | Helmchen et al. 1996 |
| Kv1 fast inactivation τ | 227 ± 26 | ms | 35% amplitude; slow τ = 3.6 ± 0.4 s (65%) | Bhatt et al. 2017; Rasband & Trimmer 2001 |
| Kv1 fast recovery τ | 246 ± 20 | ms | Slow τ = 2.29 ± 0.4 s | Bhatt et al. 2017 |
| AP half-width (Alpha RGC soma) | 0.6 | ms | At 34 °C; distal AIS ≈ 0.26 ms | Margolis & Detwiler 2007; Baden et al. *Nature* 2016 |
| τm (membrane, passive) | 50 | ms | 40–120 ms range; 50 ms canonical fit | Borghuis et al. 2013; Dhingra & Smith 2004 |

---

## 7. Simulation settings (BrainCell / NEURON)

| Parameter | Control value | Unit | Notes |
|---|---|---|---|
| `dt` | 0.01 | ms | BrainCell default; resolves τm Na activation (0.054 ms) correctly |
| `tstop` | 500 | ms | Covers single AP + corrected periaxonal K⁺ recovery (100–400 ms) |
| `numShells` | 5 | — | Minimum for stable radial gradient; test convergence up to 10 |
| `nseg_axon` | 100 | — | ~10 µm/segment for 1 mm axon; satisfies d-lambda rule |
| `maxNumSchwannCells` | 10 | — | BrainCell default; covers typical optic nerve fibre length |

---

## 8. BrainCell implementation notes for LLMs

When modifying `SimMyelinatedAxon` or `ParamsHelper.hoc`, respect the following:

### Diff_k

```hoc
// CORRECT control value:
Diff_k = 0.20    // um2 / ms  (periaxonal, corrected)

// WRONG — do not restore this value:
// Diff_k = 0.02  // was 10x too low; produces artefactual 2s K+ recovery
```

Run a sensitivity sweep {0.10, 0.20, 0.30} and report all three.

### ko0

```hoc
// CNS ECS physiological baseline:
ko0 = 3.0    // mM  (not 2.5 mM)
```

### g_Na at node

The `biophysics.hoc` / JSON preset value for nodal sodium must be set to ~700 mS/cm² for CNS optic nerve.
Do not inherit the 3000 mS/cm² value from peripheral nerve models.

### E_rest / resting potential

If using a passive leak (`g_L`, `e_pas`) to set resting potential, target −67 mV for mouse RGC.
Check against `ki0`, `ko0` and the Nernst-derived E_K to ensure consistency.

### τm Na activation

In any HOC or NMODL file that lists `54` as a time constant for Na channel activation:
this is **54 µs = 0.054 ms**. Verify units before changing. A value of 54 ms in milliseconds
will prevent action potential propagation entirely.

### Periaxonal K⁺ recovery

With the corrected Diff_k = 0.20 µm²/ms, the expected [K⁺]o recovery after a single AP
is 100–400 ms. If simulation shows ~2000 ms recovery, check that Diff_k has not reverted to 0.02.

---

## 9. Primary references (full citations)

1. **Arancibia-Carcamo IL, et al.** Node of Ranvier length as a potential regulator of myelinated axon conduction speed. *eLife* 2017; **6**: e23329. https://doi.org/10.7554/eLife.23329

2. **Syková E, Nicholson C.** Diffusion in brain extracellular space. *Physiol. Rev.* 2008; **88**(4): 1277–1340. https://doi.org/10.1152/physrev.00027.2007

3. **Halter JA, Clark JW Jr.** A distributed-parameter model of the myelinated nerve fiber. *J. Neurophysiol.* 1991; **65**(3): 564–571.

4. **Kofuji P, Newman EA.** Potassium buffering in the central nervous system. *Nat. Rev. Neurosci.* 2004; **5**(10): 771–781.

5. **Rush AM, Dib-Hajj SD, Waxman SG.** Electrophysiological properties of two axonal sodium channels, Nav1.2 and Nav1.6, expressed in mouse spinal sensory neurones. *J. Physiol.* 2005; **564**(Pt 3): 803–815.

6. **Lorincz A, Nusser Z.** Molecular identity of dendritic voltage-gated sodium channels. *Science* 2010; **328**(5980): 906–909.

7. **Craner MJ, et al.** Molecular changes in neurons in multiple sclerosis: Altered axonal expression of Nav1.2 and Nav1.6 sodium channels and Na⁺/Ca²⁺ exchanger. *PNAS* 2004; **101**(21): 8168–8173. https://doi.org/10.1073/pnas.0402765101

8. **Van Wart A, Matthews G.** Impaired firing and cell-specific compensation in neurons lacking Nav1.6 sodium channels. *J. Neurosci.* 2006; **26**(27): 7172–7180. https://pmc.ncbi.nlm.nih.gov/articles/PMC6742039/

9. **Borghuis BG, et al.** Imaging light responses of targeted neuron populations in the rodent retina. *J. Neurosci.* 2013; **33**(13): 5875–5885. https://pmc.ncbi.nlm.nih.gov/articles/PMC3684038/

10. **Perez-Pinzon MA, et al.** Independence of extracellular tortuosity and volume fraction during osmotic challenge in rat neocortex. *J. Physiol.* 2002; **543**(Pt 2): 533–541. https://pmc.ncbi.nlm.nih.gov/articles/PMC2290424/

11. **Hrabe J, Hrabetova S, Segeth K.** A model of effective diffusion and tortuosity in the extracellular space of the brain. *Biophys. J.* 2004; **87**(3): 1606–1617. https://pmc.ncbi.nlm.nih.gov/articles/PMC1304566/

12. **Zheng K, et al.** Nanoscale diffusion in the synaptic cleft and beyond measured with time-resolved fluorescence anisotropy imaging. *Sci. Rep.* 2017; **7**: 42022. https://doi.org/10.1038/srep42022

13. **Baden T, et al.** The functional diversity of retinal ganglion cells in the mouse. *Nature* 2016; **529**(7586): 345–350.

14. **Gentet LJ, Stuart GJ, Clements JD.** Direct measurement of specific membrane capacitance in neurons. *Biophys. J.* 2000; **79**(1): 314–320.

15. **Stys PK, et al.** Intracellular concentrations of major ions in rat myelinated axons and glia. *J. Neurochem.* 1997; **68**(5): 1920–1928.

---

*Document created: June 2026. Leonid Savtchenko / Rusakov Lab, UCL.*
*To be kept alongside `CLAUDE.md` in the BrainCell project root.*
*Update when new morphometry or electrophysiology data for mouse optic nerve becomes available.*
