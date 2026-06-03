# Periaxonal Space Potassium Dynamics Parameters

**Source Notebook:** Astrocyte-Mediated Node of Ranvier Plasticity

**Question:** What are the key parameters for periaxonal space potassium dynamics from the latest findings?

## Answer

Continuing conversation a2e4dfd8...
Answer:
Based on the latest findings in the sources, the key parameters governing the 
physical environment and electrochemical response of the periaxonal space to 
potassium dynamics include specific structural dimensions, ion concentration 
thresholds, and membrane conductance values used in predictive modeling.

### **1. Structural Dimensions of the Periaxonal Space**
Computer simulations of callosal-like axons define the physical limits of the 
periaxonal space, which is the gap between the axon and the myelin sheath:
*   **Internodal Thickness:** The periaxonal space thickness is typically set 
at **15 nm** [1].
*   **Paranodal Narrowing:** At the paranodes (the 1.9 µm end parts of the 
internodes), the space is significantly constricted to a width of **0.0123 nm**
[1].
*   **Myelin Periodicity:** The myelin wrap periodicity is defined as **15.6 
nm**, which helps determine the g-ratio (set at approximately 0.8) [1].

### **2. Potassium ([K⁺]ₒ) Concentrations and Activity Triggers**
The research identifies specific potassium levels that act as a signal for 
activity-dependent plasticity:
*   **Baseline vs. Stimulated Levels:** Physiological extracellular potassium 
is approximately **3 mM**, while high neuronal activity is simulated by 
increasing [K⁺]ₒ to **15 mM** [2, 3].
*   **Effect on Node Length:** In young mice, this elevation in potassium for 
45 minutes increases the fraction of elongating nodes from **62% to 78%** [4].
*   **NKCC1 Activation:** High [K⁺]ₒ levels promote the phosphorylation of the 
Na⁺-K⁺-Cl⁻ co-transporter (NKCC1) [5, 6]. The occurrence of phosphorylated 
NKCC1 (pNKCC1) in paranodes increases from roughly **11–13%** under baseline 
conditions to **49%** following exposure to 15 mM [K⁺]ₒ [5].

### **3. Electrochemical and Conductance Parameters**
To understand how potassium dynamics influence conduction, the sources provide 
several electrical parameters:
*   **Myelin Conductance Density:** The specific conductivity of the internodal
myelin membrane is estimated at **15.85 pS/μm²** at baseline [7, 8].
*   **Activity-Induced Rise:** Activation of A2b receptors (triggered by 
activity-dependent adenosine release) increases this conductance density to 
**54.16 pS/μm²** [7, 9].
*   **Nodal Potentials:** The node resting potential is set to **-82 mV**, with
a leak conductance reversal potential of **-84 mV** (representing potassium 
leak channels like TRAAK) [10].
*   **Ion Channel Densities:** For simulations, the fully-activated conductance
density for slow potassium (KV) channels at the nodes is set at **0.4 mS/mm²** 
[1].

### **4. Impact on Conduction Speed**
These parameters demonstrate that the system is tuned for high performance. The
existing node lengths and myelin conductance are set to generate nearly the 
maximum possible conduction speed [11]. However, the rise in myelin conductance
and node elongation triggered by potassium-mediated signaling can collectively 
reduce conduction speed by up to **1.48-fold** [11, 12].

Resumed conversation: a2e4dfd8-b83f-408a-8970-167591fa5657
