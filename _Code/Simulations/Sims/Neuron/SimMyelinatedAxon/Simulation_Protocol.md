# Myelinated Axon Simulation Protocol
Based on Xiaolan Wu simulation plan (2026-06)

## Experiment 1: Structural parameter sweep

### Parameters to vary (one at a time)
| Parameter | BrainCell variable | Range to test |
|---|---|---|
| Axon diameter | myelParam_diam_axon | 0.5 - 2.0 µm |
| Periaxonal space | myelParam_diam_sheath | controls gap width |
| Myelin compartments | myelParam_maxNumSchwannCells | 10 - 80 |
| Internode length | myelParam_schwann1_end | vary |

### Outputs to record
- Conduction block time point
- AP amplitude, latency, frequency
- [K+]o peak and recovery time
- Ko data saved to ko_output/ (enable "Save Ko data" checkbox)

## Experiment 2: Functional parameter sweep (reproduce CAP)

### Parameters to vary
| Parameter | BrainCell variable | Condition |
|---|---|---|
| Kir4.1 conductance | (in MOD file) | WT vs blocked |
| BaCl2 effect | reduce all Kir | 100 µM |
| VU0134992 effect | reduce Kir4.1 only | Kir4.1 blocker |
| Na/K pump | nkpump conductance | vary |
| Diff_k in myelin | myelParam_Diff_k | vary |
| Initial ko | myelParam_ko0 | 2.5 or 5.0 mM |

### Protocol per condition
1. Load ExperimentalParams_KoSiphoning.hoc (baseline)
2. Modify target parameter
3. Run 1Hz stimulation (baseline)
4. Run 100Hz stimulation (HFS)
5. Run recovery 1Hz
6. Save Ko data and note recovery time

## Reference
- Nature Communications 2016: https://www.nature.com/articles/ncomms11298
- Key finding: Kir4.1 in OL NOT responsible for K+ siphoning
- Gap junctions contribute ~50% of K+ siphoning
