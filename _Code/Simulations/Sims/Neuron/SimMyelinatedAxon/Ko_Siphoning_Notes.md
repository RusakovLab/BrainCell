## Question 1
What are the main findings and key parameters in this notebook?

### Answer

Continuing conversation 8df3a731...
Answer:
The primary findings in this notebook center on the **geometry and biophysics 
of action potential (AP) initiation and propagation** within myelinated axons, 
particularly in the optic nerve and retinal ganglion cells (RGCs). Key 
discoveries include the role of the **Node of Ranvier length** as a speed 
regulator, the **functional scaling of the Axon Initial Segment (AIS)**, and 
the mechanism of **potassium ($K^+$) siphoning** to maintain excitability.

### 1. Main Findings: Axonal Regulation and Excitability

*   **Node of Ranvier Length as a Conduction Regulator:** Research shows that 
node length varies significantly (up to 8.7-fold in the cortex) between axons 
but remains consistent along a single axon [1-3]. Modeling predicts that 
adjusting node length can **tune conduction speed by ~20%** [1, 4]. This is 
highly efficient: changing node length is **270-fold (cortex) to 1000-fold 
(optic nerve) more energy-efficient** than altering the myelin sheath to 
achieve the same speed adjustment [5-7].
*   **AIS Scaling and Spike Initiation:** The AIS is the site of AP initiation,
typically **20–40 $\mu m$ from the soma** [8, 9]. In Alpha RGCs, AIS properties
(length and distance from soma) **scale with cell size** [10-12]. Larger cells 
have longer AISs located further from the soma to normalize spiking thresholds 
and ensure that AIS-initiated spikes can successfully trigger the large somatic
capacitance (the **IS-SD break**) [10, 13, 14].
*   **Potassium ($K^+$) Siphoning and Glial Support:** Impulse conduction 
causes transient accumulation of extracellular $K^+$, which must be cleared to 
prevent conduction block [15-17]. **Astrocytes** and oligodendrocytes act as 
local buffers, moving excess $K^+$ from the periaxonal space into capillaries 
via **Kir4.1 channels**—a process called "$K^+$ siphoning" [15, 16, 18, 19].
*   **Temperature Sensitivity ("Sleepy" Channels):** Spiking behavior is highly
temperature-dependent. At very low temperatures (~7–8°C), sodium channels 
become **"sleepy,"** meaning their gating kinetics slow abruptly, leading to a 
**total loss of spiking** at 7°C [9, 20, 21].
*   **Alpha RGC Functional Symmetry:** Mouse Alpha RGCs are classified into 
**four symmetric types**: On-sustained, On-transient, Off-sustained, and 
Off-transient [22-25]. These types share a **distinctively fast AP waveform** 
that is shorter than other RGC types [22, 26, 27].

### 2. Key Geometrical Parameters

These parameters define the physical structure required for stable axonal 
simulations:

| Component | Parameter | Value / Insight | Source |
| :--- | :--- | :--- | :--- |
| **Node of Ranvier** | Mean Length ($L_{node}$) | **1.02 – 1.08 $\mu m$** 
(Optic Nerve); **1.50 $\mu m$** (Cortex) | [2, 28, 29] |
| | Diameter ($d_{node}$) | **0.73 $\mu m$** (Optic Nerve); **0.64 $\mu m$** 
(Cortex) | [29, 30] |
| **Internode** | Length ($L_{int}$) | **~139.3 $\mu m$** (Optic Nerve); 
**~81.7 $\mu m$** (Cortex) | [31, 32] |
| **Myelin Sheath** | Number of Wraps | **7 wraps** (Optic Nerve); **5 wraps** 
(Cortex) | [31, 33] |
| | G-ratio | **0.78** (Optic Nerve); **0.81** (Cortex) | [31, 33] |
| **AIS** | Distance ($AIS_D$) | Calculated as $1.22 \times 
\text{Soma}_{\text{diam}} - 5.0 \mu m$ | [34, 35] |
| | Length ($AIS_L$) | Calculated as $1.38 \times \text{Soma}_{\text{diam}} - 
1.6 \mu m$ | [34, 35] |
| **Periaxonal Space**| Optimized Width | **10 – 20 nm** (Optimized for $K^+$ 
siphoning) | [36] |

### 3. Key Biophysical and Electrical Parameters

These constants set the "physics" for compartmental models like NEURON:

*   **Specific Membrane Capacitance ($C_m$):** 0.9 – 1.0 $\mu F/cm^2$ [34, 37, 
38].
*   **Intracellular (Axial) Resistivity ($R_i$):** 100 $\Omega \cdot cm$ 
(standard) or **143.2 $\Omega \cdot cm$** at 35°C [34, 39].
*   **Nodal Sodium Conductance ($g_{Na}$):** **3000 $mS/cm^2$** [31, 37].
*   **AIS Channel Density:** Approximately **5x to 7x greater** than somatic 
densities [34, 40].
*   **Ion Reversal Potentials (at 35°C):**
    *   $V_{Na}$: +50 to +60.6 mV [29, 41, 42].
    *   $V_K$: -84 to -101.3 mV [29, 41].
    *   Resting potential ($E_r$): **-82 mV** [29, 34].
*   **Potassium Dynamics:** A single AP raises periaxonal $[K^+]_o$ from **5 mM
to 8 mM**, with a 2-second return to baseline [36].

### 4. Propagation and Failure Parameters
*   **Conduction Velocity:** Typically **2.5 – 15 m/s** in the rat optic nerve 
[43, 44].
*   **Conduction Block Conditions:** Propagation failure can be induced by 
**$K^+$ accumulation** in the periaxonal space (related to volume) or by 
removing the myelin mechanism (low capacitance/high resistance) [17, 45, 46].
*   **AIS-Soma Threshold Difference:** AP initiation in the AIS occurs at 
significantly lower voltages (~ -49 mV) compared to the somatic regeneration 
threshold (~ -16 mV) [10, 47].

Resumed conversation: 8df3a731-785f-4736-910c-b7902a6c593d


================================================================================

## Question 2
What are all the modelling parameters: periaxonal space dimensions, K+ concentrations, diffusion coefficients, time constants?

### Answer

Continuing conversation 8df3a731...
Answer:
Based on the sources, the following parameters are used for modeling the 
periaxonal space and potassium dynamics in myelinated axons, particularly in 
the context of the optic nerve and retinal ganglion cells (RGCs).

### 1. Periaxonal Space Dimensions
The periaxonal space is a critical narrow region between the axonal membrane 
and the myelin sheath.

*   **Internodal Width:** The standard thickness is **15 nm** [1-3].
*   **Optimized Width:** Simulations indicate that a diameter of **10–20 nm** 
is optimized for efficient $K^+$ siphoning [4].
*   **Effective Paranodal Width ($w$):** Because myelin attaches to the axon at
the paranode, the periaxonal space is modeled as a spiral resistance pathway 
rather than a direct gap. The effective width used to simulate this pathway is:
    *   **Rat Optic Nerve:** **0.0077 nm** [1, 5].
    *   **Rat Cortex:** **0.0123 nm** [1, 6].
*   **Extracellular Volume:** For internodal regions under the myelin (Schwann 
cells), the volume is typically between **4 and 14 $\mu m^3$**, a parameter 
that influences $K^+$-dependent conduction block [7].

### 2. Potassium ($K^+$) Concentrations
These parameters define the ionic environment and the gradients that drive 
excitability.

*   **Initial Extracellular $[K^+]_o$:** Typically set to **2.5 mM** [8] or 
**3.0 mM** [9] for standard physiological models. One specific model uses a 
baseline of **5 mM** for nodal activity simulations [4].
*   **Initial Intracellular $[K^+]_i$:** Set to **120 mM** [8, 10] or **128 
mM** [11] in RGC models.
*   **Minimum Extracellular $[K^+]_o$:** Defined as **1e-05 mM** to set 
boundary conditions for simulations [8].
*   **Action Potential (AP) Induced Shifts:** A single AP at a node is 
suggested to raise periaxonal $[K^+]_o$ from **5 mM to 8 mM** [4].
*   **Equilibrium Potentials ($E_K$):** 
    *   At 35°C: **-84 mV** [1] or **-101.34 mV** [12].
    *   In biophysical models for RGCs: **-90 mV** [13].

### 3. Diffusion Coefficients
These values govern the movement of ions between compartments.

*   **$K^+$ Diffusion Coefficient ($Diff_k$):** Set to **0.02 $\mu m^2/ms$** in
the BrainCell computational platform for myelinated axon firing [8].
*   **Intracellular (Axial) Resistivity ($R_i$):** While not a diffusion 
coefficient, this determines the resistive flow of ions along the axon. Values 
include **70 $\Omega \cdot cm$** [1], **100 $\Omega \cdot cm$** [14, 15], and a
temperature-corrected value of **143.2 $\Omega \cdot cm$** at 35°C [12, 16].

### 4. Time Constants
Time constants ($\tau$) define the kinetics of channel gating and the passive 
response of the membrane.

*   **Membrane Time Constant ($\tau_m$):** 
    *   Physiological range for RGCs: **40 – 120 ms** [17, 18].
    *   Model fit for tiger salamander RGCs: **50 ms** [19].
*   **Ion Channel Gating (at ~34-35°C):**
    *   **Na Activation ($\tau_m$):** **54 ms** (temperature corrected) [13].
    *   **Na Inactivation ($\tau_h$):** **1.8 ms** (temperature corrected) 
[13].
    *   **K Activation ($\tau_n$):** **1.0 ms** [13].
*   **Kv1 Channel Inactivation (at 34°C):** This follows a double-exponential 
decay:
    *   **$\tau_{fast}$:** **227 ± 26 ms** (accounting for 35% of the 
amplitude) [20].
    *   **$\tau_{slow}$:** **3.6 ± 0.4 s** (accounting for 65% of the 
amplitude) [20].
*   **Recovery from Kv1 Inactivation:** 
    *   **$\tau_{fast}$:** **246 ± 20 ms** [21].
    *   **$\tau_{slow}$:** **2.29 ± 0.4 s** [21].
*   **Calcium Kinetics:** The time constant for calcium sequestering 
($\tau_{Ca}$) is set to **50 ms** [22, 23].
*   **Ionic Concentration Recovery:** After an AP-induced shift, $[K^+]_o$ in 
the periaxonal space returns to baseline in **2 seconds** [4].

Resumed conversation: 8df3a731-785f-4736-910c-b7902a6c593d


================================================================================

## Question 3
What are the key conclusions about Kir4.1 channels and potassium buffering mechanisms?

### Answer

Continuing conversation 8df3a731...
Answer:
Based on the sources, **Kir4.1 (inwardly rectifying potassium) channels** are 
the primary molecular drivers of **potassium ($K^+$) buffering**, a critical 
glial mechanism that maintains axonal excitability by clearing excess ions from
the periaxonal space [1-3].

### Key Conclusions about Kir4.1 and Glial Mechanisms
*   **Glial Distribution:** Kir4.1 is most heavily expressed in **astrocytes** 
(approximately **88.2%**) and is also present in **oligodendrocytes** 
(**87.3%**) and their precursor cells (OPCs) [2]. These cells surround the 
nodes of Ranvier and the axon initial segment (AIS), effectively shielding the 
nodal membrane and modulating the extracellular ionic composition [4, 5].
*   **The "Siphoning" Pathway:** The mechanism, often called **"$K^+$ 
siphoning,"** involves moving excess $K^+$ accumulated during action potentials
(APs) from the **periaxonal space** into glial cells and ultimately directing 
it into **capillaries** for removal [1, 6].
*   **The "Pre-buffering" Effect:** Computational models suggest that Kir4.1 
channels contribute to an initial **drop in $[K^+]_o$** that occurs just before
hyperpolarisation, a phenomenon researchers have termed **"pre-buffering"** 
[3].
*   **Dynamics of Action Potentials:** A single AP is predicted to raise the 
$K^+$ concentration in the periaxonal space from a baseline of **5 mM to 8 mM**
[3]. This concentration shift takes approximately **2 seconds** to return to 
its original baseline [3].

### Geometrical and Modelling Insights
*   **Optimized Periaxonal Width:** Simulations indicate that a periaxonal 
space diameter of **10–20 nm** is the structural optimum for efficient $K^+$ 
siphoning [3]. While increasing this width does not significantly alter the 
axon's conduction velocity, it is vital for ionic management [3].
*   **Experimental Limitations:** Despite these detailed modelling conclusions,
it remains **impossible to experimentally measure $[K^+]_o$** directly within 
the narrow (15 nm) periaxonal space to verify these findings [3, 5].

### Pathological Consequences of Kir4.1 Loss
Dysregulation of these potassium dynamics is linked to severe neurological 
disorders:
*   **Myelin Damage:** Loss of Kir4.1 function leads to **vacuole formation** 
and structural myelin damage [1, 7, 8].
*   **Seizure Susceptibility:** In Kir4.1 conditional knockout (cKO) models, 
there is a **decreased latency to seizure** and a significant reduction in 
overall survival rates, as the inability to buffer $K^+$ disrupts normal action
potential firing and membrane stability [1, 9].

Resumed conversation: 8df3a731-785f-4736-910c-b7902a6c593d


================================================================================

## Key reference: OL-Astrocyte network and gap junctions
Nature Communications 2016: https://www.nature.com/articles/ncomms11298

Key findings:
- OL-astrocyte gap junction network contributes ~50% of K+ siphoning
- Kir4.1 in oligodendrocytes is NOT responsible for K+ siphoning
- OL actively senses AP via capacitive transients (Fig 3)
- Gap junctions between OL and astrocytes are critical for K+ clearance

Experimental observation (Xiaolan Wu):
- Kir4.1 blocker: almost no CAP response during 100Hz but instant recovery
- This is inconsistent with standard K+ siphoning model - unexplained


================================================================================

## Xiaolan Wu - Experimental Data (Simulation_plan.pptx, 2026-06)

### Structural parameters to investigate
- Axon diameter
- Periaxonal space diameter (diam_sheath)
- Number of myelin compartments per axon: 10-80
- Internode length
- Outputs to measure: conduction block time point, AP shape (amplitude, latency, frequency), [K+]o changes

### Functional parameters to investigate
- K+ channel conductance on myelin (from patch-clamp data)
- Na/K pump conductance
- Kv in juxtaparanode
- Diff_k in myelin
- Initial ko

### Drug experiments (WT mouse)
- BaCl2 (100 µM, Kir blocker): neuronal hyperexcitability at 1Hz, delayed recovery after 100Hz HFS
- VU0134992 (Kir4.1 blocker): almost no CAP response during 100Hz but instant recovery — UNEXPLAINED
- BaCl2 + C101248 (Kir + THIK1 blocker): combined effect

### Key reference
Nature Communications 2016: https://www.nature.com/articles/ncomms11298
- OL-astrocyte gap junction network contributes ~50% of K+ siphoning
- Kir4.1 in OL is NOT responsible for K+ siphoning (Fig 5)
- OL actively senses AP via capacitive transients (Fig 3)

### Oligodendrocyte model (Slide 3)
- OL patch data from Sunny Du
- Parameters: membrane resistance, capacitance, leak reversal potential
- Voltage clamp configuration
