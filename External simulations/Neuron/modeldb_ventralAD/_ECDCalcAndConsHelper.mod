
COMMENT
    Extracellular Diffusion Calculation and Consumption Helper (membrane mechanism)
    
    This membrane mechanism plays the next roles: ... !!
    
    In case you want to add new species (or delete old ones), look for 7 blocks of code below marked as "Edit here when changing the species list"
    Warning: Any changes to the blocks must be done synchronously with the changes to the file "diffusible_species.json".
             The lists of species in this MOD file and the JSON file must always be in sync (including the total number of species, their order and "ionMechName").
ENDCOMMENT

: !! when variable time step is used, it's important to schedule calls of our code in this MOD file on each "on-off" event and each "spike" event of each extracellular source

: !! investigate whether enlisting all available ions here causes significant performance or memory penalties compared to the case when we enlist only the used ones
:    if it does, then consider creation of individual MOD file for each ion OR generation of this single MOD file from Python, then compile it and load dynamically

: !! we could add READ for all the ions, but we already WRITE, so an attempt to use the read value of the concentration like "*oinit"
:    would lead to cumulative effect of summation (unless we integrate the diffusion PDE step by step rather than calculate the closed-form solution)

NEURON {
    SUFFIX ECDCalcAndConsHelper
    
    : !!
    : Warning: Be cautious specifying VALENCE below because it's easy to introduce a regression that will mainfest itself
    :          sometimes as a clear error message in NEURON (best case), but sometimes as a hanging of NEURON without any error messages (worst case) *
    :
    :          To do everything right, make sure that:
    :          1. Each ion has VALENCE specified in this file or some other MOD file. The only three ions for which NEURON already "knows" the valence are:
    :             Na+, K+ and Ca2+ (even though the last one is not "visible" to NEURON without a custom MOD file).
    :             You don't need to specify the valence for these three ions explicitly, but for all other ions specifying VALENCE somewhere is a must.
    :          2. The valence of a given ion doesn't have different values in different MOD files.
    :             If an ion used in 2+ MOD files, it's OK to specify VALENCE in only one MOD file and omit it in all other files.
    :
    :          * The hanging takes place when NEURON tries to load "nrnmech.dll" automatically from the current folder at start
    :            (e.g. when you export with "Export manager" and then run the exported HOC file in the standalone mode).
    :            The clear error message is printed when the DLL is loaded from a custom folder with "proc nrn_load_dll" (which corresponds to the common BrainCell workflow).
    :
    : Be aware: If an ion has no VALENCE specified anywhere, then no error in BrainCell program, but silent hanging in the exported file.
    
    : vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
    : Basic ions
    USEION na WRITE nao
    USEION k WRITE ko
    USEION ca WRITE cao
    USEION cl WRITE clo VALENCE -1
    : Neurotransmitters
    USEION ach WRITE acho VALENCE 1
    USEION glu WRITE gluo
    USEION gaba WRITE gabao VALENCE 0
    : Specific
    USEION frapion WRITE frapiono
    USEION ip3 WRITE ip3o
    : User-defined
    USEION extra1 WRITE extra1o VALENCE 1
    USEION extra2 WRITE extra2o VALENCE -1
    : ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
    
    : !! just for test of the "Unrecognized" species category (don't forget to change NUM_SPECIES_IN_MOD)
    : USEION test_unrec WRITE test_unreco
    
    : !! it would be better to pass them with POINTER to array
    
    : vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
    : Basic ions
    GLOBAL naoinit, koinit, caoinit, cloinit
    : Neurotransmitters
    GLOBAL achoinit, gluoinit, gabaoinit
    : Specific
    GLOBAL frapionoinit, ip3oinit
    : User-defined
    GLOBAL extra1oinit, extra2oinit
    : ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
    
    : !! compiler warning here: Use of POINTER is not thread safe
    : !! try to make ptr_ecSrcLibDataVec a GLOBAL POINTER or POINTER GLOBAL. UPD: compiler error
    : !! try to reuse a simple GLOBAL variable (of type double or double[]) as a POINTER
    
    : The pointer to an object of type "struct SpeciesLibrary"
    POINTER ptr_spcLibDataVec
    
    : The pointer to an object of type "struct ExtracellularSourcesLibrary"
    POINTER ptr_ecSrcLibDataVec
    
    : The pointer to a matrix row (effectively a vector) such that given extracellular source index "ecsIdx",
    : the value "ptr_segm3DSpecificDataMatRow[ecsIdx]" has different meaning depending on the source shape:
    :   * "point"  - distance from the 3D point to the segment centre
    :   * "sphere" - 0/1 flag indicating whether the segment centre is inside the sphere
    POINTER ptr_segm3DSpecificDataMatRow
    
    POINTER ptr_numImpsSoFarDataVec
    
    : !! maybe combine these two into a special template/struct
    GLOBAL maxNumImpsPerECS
    POINTER ptr_impTimesDataMatrix
}

UNITS {
    (molar) = (1/liter)
    (mM)    = (millimolar)
    PI      = (pi)       (1)
}

PARAMETER {
    : !! can I read the values directly from GLOBAL vars? UPD: try to declare them as EXTERNAL or BBCOREPOINTER:
    :    https://nrn.readthedocs.io/en/latest/python/modelspec/programmatic/mechanisms/nmodl2.html
    :    having pointers to GLOBAL-s would be a better solution because it allows user to change a GLOBAL variable
    :    during the simulation on the fly and immediately have the effect in this MOD file
    :    also, think about passing a POINTER to array
    
    : vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
    : Basic ions            : Will be copied from:
    naoinit = -1 (mM)       :   na_ion\GLOBAL\nao0_na_ion
    koinit = -1 (mM)        :   k_ion\GLOBAL\ko0_k_ion
    caoinit = -1 (mM)       :   ca_ion\GLOBAL\cao0_ca_ion
    cloinit = -1 (mM)       :   cl_ion\GLOBAL\clo0_cl_ion
    : Neurotransmitters
    achoinit = -1 (mM)      :   ach_ion\GLOBAL\acho0_ach_ion
    gluoinit = -1 (mM)      :   glu_ion\GLOBAL\gluo0_glu_ion
    gabaoinit = -1 (mM)     :   gaba_ion\GLOBAL\gabao0_gaba_ion
    : Specific
    frapionoinit = -1 (mM)  :   frapion_ion\GLOBAL\frapiono0_frapion_ion
    ip3oinit = -1 (mM)      :   ip3_ion\GLOBAL\ip3o0_ip3_ion
    : User-defined
    extra1oinit = -1 (mM)   :   extra1_ion\GLOBAL\extra1o0_extra1_ion
    extra2oinit = -1 (mM)   :   extra2_ion\GLOBAL\extra2o0_extra2_ion
    : ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
    
    ptr_spcLibDataVec
    ptr_ecSrcLibDataVec
    
    ptr_segm3DSpecificDataMatRow
    
    ptr_numImpsSoFarDataVec
    
    maxNumImpsPerECS = -1
    ptr_impTimesDataMatrix
}

ASSIGNED {
    : vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
    : Basic ions
    nao (mM)
    ko (mM)
    cao (mM)
    clo (mM)
    : Neurotransmitters
    acho (mM)
    gluo (mM)
    gabao (mM)
    : Specific
    frapiono (mM)
    ip3o (mM)
    : User-defined
    extra1o (mM)
    extra2o (mM)
    : ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
    
    : !! just for test of the "Unrecognized" species category (don't forget to change NUM_SPECIES_IN_MOD)
    : test_unreco
}

: !! compiler warning here: VERBATIM blocks are not thread safe
VERBATIM
    // vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
    #define NUM_SPECIES_IN_MOD 11
    // ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
    
    struct SpeciesInfo {
        double diff;
        double isEnableUptake;
        double t_alpha;
    };
    
    struct SpeciesLibrary {
        double numSpeciesInHOC;
        struct SpeciesInfo speciesInfo[0];  // !! keep this one last not to specify the actual array size
    };
    
    struct ECSSpatialInfo {
        double enumPointSphere;
        double x;               // !! no need to pass x, y, z into MOD file
        double y;               //
        double z;               //
        double radiusOrMinus1;  // !! maybe no need to pass this as well (and merge with ECSCapacityInfo.pointCapacityRadiusOrMinus1)
    };
    
    struct ECSTemporalInfo {
        double enumStaticSwitchSpike;
        double offsetTimeOrMinus1;
        double durationOrMinus1;
        double isSeriesOrMinus1;
    };
    
    struct ECSCapacityInfo {
        double ssOrMinus1;
        double pointCapacityRadiusOrMinus1;     // !! maybe merge this with ECSSpatialInfo.radiusOrMinus1
        double numMoleculesOrMinus1;
        double delta_oOrMinus1;
    };
    
    /* !!
    struct ECSSeriesInfo {
        double *ptr_vec_numImpsSoFar;
        double *impTimes;
    };
    */
    
    struct ExtracellularSource {
        double speciesIdx;
        struct ECSSpatialInfo spatialInfo;
        struct ECSTemporalInfo temporalInfo;
        struct ECSCapacityInfo capacityInfo;
        // !! struct ECSSeriesInfo seriesInfo;        // !! don't add it here because we pass the array of ExtracellularSource-s from HOC
    };
    
    struct ExtracellularSourcesLibrary {
        double numECSs;
        struct ExtracellularSource ecs[0];  // !! keep this one last not to specify the actual array size
    };
    
    static struct SpeciesLibrary *ptr_spcLib;
    static struct ExtracellularSourcesLibrary *ptr_ecSrcLib;
    
    
    static double *ptr_vec_segm3DSpecificData;
    
    // !! ideally, we need to hide these two into "struct ECSSeriesInfo" being a part of "struct ExtracellularSource"
    static double *ptr_vec_numImpsSoFar;
    static double *ptr_mat_impTimes;
    
    // !! do not convert maxNumImpsPerECS to int each time
    #define IMPULSE_TIME(ecsIdx, impIdx) (ptr_mat_impTimes[(ecsIdx) * (int)maxNumImpsPerECS + (impIdx)])
    
    static double *ptr_vec_o[NUM_SPECIES_IN_MOD];
    
    // !! will be defined below the first call (just for convenience)
    void updateOutConcGivenECSAndImp(int ecsIdx, int impIdxOrMinus1);
    
    void codeContractViolation() {
        hoc_execerror("\n\n    Bug in BrainCell program: Code contract violation", "\n    Please report this problem to the developer along with the call stack shown below\n");
    }
ENDVERBATIM

FUNCTION getNumSpeciesInMOD() {
    VERBATIM
        _lgetNumSpeciesInMOD = NUM_SPECIES_IN_MOD;
    ENDVERBATIM
}

INITIAL {
    checkPointers()
    assignPointers()    : !! maybe merge into one
    calcAllOutConcs()   :
}

BREAKPOINT {
    assignPointers()    : !! try to use "static" to remove this. UPD: "static" doesn't help (strange), so maybe remove "static"
    calcAllOutConcs()
}

PROCEDURE checkPointers() {
    VERBATIM
        if (&ptr_spcLibDataVec == NULL ||
            &ptr_ecSrcLibDataVec == NULL ||
            &ptr_segm3DSpecificDataMatRow == NULL ||
            &ptr_numImpsSoFarDataVec == NULL ||
            maxNumImpsPerECS == -1 ||
            &ptr_impTimesDataMatrix == NULL) {
            
            // This membrane mechanism was inserted, but its params were not initialized
            codeContractViolation();
        }
        
        // !! think about two more checks as well (use codeContractViolation):
        //    1. for each "*oinit" PARAMETER, make sure it doesn't equal -1
        //    2. loop through all used "*OrMinus1" vars and make sure they don't equal -1
    ENDVERBATIM
}

PROCEDURE assignPointers() {
    
    VERBATIM
        // !! why do I need to assign the next pointers on each breakpoint?
        //    (they behave like shared between the segments - need to look into C code)
        //    UPD 1: VERBATIM block is not allowed inside NEURON, PARAMETER or ASSIGNED,
        //           so cannot move the declarations of the pointers there
        //    UPD 2: if I declare 2 vars with the same name in different MOD files, compiler gives an error
        
        // !! maybe I can call some HOC code here to do this in order to be more flexible with regard to adding/deleting species
        
        // vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
        // Basic ions
        ptr_vec_o[0] = &nao;
        ptr_vec_o[1] = &ko;
        ptr_vec_o[2] = &cao;
        ptr_vec_o[3] = &clo;
        // Neurotransmitters
        ptr_vec_o[4] = &acho;
        ptr_vec_o[5] = &gluo;
        ptr_vec_o[6] = &gabao;
        // Specific
        ptr_vec_o[7] = &frapiono;
        ptr_vec_o[8] = &ip3o;
        // User-defined
        ptr_vec_o[9] = &extra1o;
        ptr_vec_o[10] = &extra2o;
        // ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
        
        
        // ptr_b = (void*)&ptr_a;   // !! would work fine below as well (but won't work after migration from C to C++)
        
        ptr_spcLib = (struct SpeciesLibrary*)&ptr_spcLibDataVec;
        ptr_ecSrcLib = (struct ExtracellularSourcesLibrary*)&ptr_ecSrcLibDataVec;
        ptr_vec_segm3DSpecificData = (double*)&ptr_segm3DSpecificDataMatRow;
        
        ptr_vec_numImpsSoFar = (double*)&ptr_numImpsSoFarDataVec;
        ptr_mat_impTimes = (double*)&ptr_impTimesDataMatrix;
        
        /* !! is there a better way to pass the pointers directly into the structs?
        for (int ecsIdx = 0; ecsIdx < (int)ptr_ecSrcLib->numECSs; ecsIdx++) {
            struct ECSSeriesInfo *seriesInfo = &ptr_ecSrcLib->ecs[ecsIdx].seriesInfo;
            seriesInfo->ptr_vec_numImpsSoFar = &((double*)&ptr_numImpsSoFarDataVec)[ecsIdx];
            
            // !! when NEURON will resize the Vector, this pointer won't be correct anymore
            
            seriesInfo->impTimes = &((double*)&ptr_impTimesDataMatrix)[(int)maxNumImpsPerECS * ecsIdx];
            
            // !! do not convert maxNumImpsPerECS from double to int on each iteration
        }
        */
        
        // Make sure HOC and MOD code is synced with regard to the species list
        // !! move this check to the beginning of this PROCEDURE (before we start writing to "ptr_vec_o[*]");
        //    to do this, maybe it makes sense to move numSpeciesInHOC out of the "ptr_spcLib"
        //    alternatively, expose NUM_SPECIES_IN_MOD here, read it in HOC and do this check on the HOC side (because earlier is better)
        if (ptr_spcLib->numSpeciesInHOC != NUM_SPECIES_IN_MOD) {
            codeContractViolation();    // !! replace with a message saying that the MOD files list and this MOD file are out of sync and how to fix this problem
        }
    ENDVERBATIM
    
}

PROCEDURE calcAllOutConcs() {
    
    VERBATIM
        
        
        /* !!
        static double last_printed_t = -1;
        if (t != last_printed_t) {
            printf("MM-BREAKPOINT: t=%g\n", t);
            last_printed_t = t;
        }
        */
        
        
        // !! maybe I can call some HOC code here to do this in order to be more flexible with regard to adding/deleting species
        // !! maybe do not modify the species for which we don't have any sources
        // !! it would be better to pass all "*oinit" with POINTER to array and use a cycle here
        
        // vvvvvvvvvv Edit here when changing the species list vvvvvvvvvv
        // Basic ions
        *ptr_vec_o[0] = naoinit;
        *ptr_vec_o[1] = koinit;
        *ptr_vec_o[2] = caoinit;
        *ptr_vec_o[3] = cloinit;
        // Neurotransmitters
        *ptr_vec_o[4] = achoinit;
        *ptr_vec_o[5] = gluoinit;
        *ptr_vec_o[6] = gabaoinit;
        // Specific
        *ptr_vec_o[7] = frapionoinit;
        *ptr_vec_o[8] = ip3oinit;
        // User-defined
        *ptr_vec_o[9] = extra1oinit;
        *ptr_vec_o[10] = extra2oinit;
        // ^^^^^^^^^^ Edit here when changing the species list ^^^^^^^^^^
        
        for (int ecsIdx = 0; ecsIdx < (int)ptr_ecSrcLib->numECSs; ecsIdx++) {
            
            struct ExtracellularSource *ptr_ecSrc = &ptr_ecSrcLib->ecs[ecsIdx];
            
            if (ptr_ecSrc->temporalInfo.isSeriesOrMinus1 != 1.0) {
                updateOutConcGivenECSAndImp(ecsIdx, -1);
            } else {
                int numImpsSoFar = (int)ptr_vec_numImpsSoFar[ecsIdx];
                for (int impIdx = 0; impIdx < numImpsSoFar; impIdx++) {
                    updateOutConcGivenECSAndImp(ecsIdx, impIdx);
                }
            }
        }
    ENDVERBATIM
    
}

VERBATIM

    void updateOutConcGivenECSAndImp(int ecsIdx, int impIdxOrMinus1) {
        
        struct ExtracellularSource *ptr_ecSrc = &ptr_ecSrcLib->ecs[ecsIdx];
        
        int spcIdx = ptr_ecSrc->speciesIdx;
        
        struct SpeciesInfo *ptr_spcInfo = &ptr_spcLib->speciesInfo[spcIdx];
        
        double *ptr_o = ptr_vec_o[spcIdx];
        
        switch ((int)ptr_ecSrc->spatialInfo.enumPointSphere) {
            case 0: {   // "point" shape
                
                // Distance from the 3D point to the segment centre
                double distance = ptr_vec_segm3DSpecificData[ecsIdx];
                
                switch ((int)ptr_ecSrc->temporalInfo.enumStaticSwitchSpike) {
                    case 0: {       // "static" dynamics
                        // !! I can pass one product var instead of two factor vars into this MOD file
                        // !! very similar to "on-off" dynamics
                        *ptr_o += ptr_ecSrc->capacityInfo.ssOrMinus1 * ptr_ecSrc->capacityInfo.pointCapacityRadiusOrMinus1 / distance;
                        
                        break;
                    } case 1: {     // "on-off" dynamics
                        
                        // !! code dupl. with "on-off" dynamics for sphere
                        double offsetTime;
                        if (impIdxOrMinus1 == -1) {
                            offsetTime = ptr_ecSrc->temporalInfo.offsetTimeOrMinus1;
                        } else {
                            offsetTime = IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                        }
                        
                        // For t == offsetTime, we would have 1/0 in timeFactor below
                        if (t <= offsetTime) {
                            break;
                        }
                        
                        // !! think about creating a cache matrix to save all the constants in INITIAL block (not to calc. on each BREAKPOINT)
                        double diffFactor = 4.0 * ptr_spcInfo->diff;
                        
                        double delta_t = t - offsetTime;
                        double timeFactor = erfc(distance / sqrt(diffFactor * delta_t));    //
                        if (ptr_spcInfo->isEnableUptake) {                                  // !! make a func and reuse
                            timeFactor *= exp(-delta_t / ptr_spcInfo->t_alpha);             //
                        }                                                                   //
                        
                        double endTime = offsetTime + ptr_ecSrc->temporalInfo.durationOrMinus1;
                        
                        // For t == endTime, we would have 1/0 in timeFactor below
                        if (t > endTime) {
                            delta_t = t - endTime;
                            timeFactor -= erfc(distance / sqrt(diffFactor * delta_t));      //
                            if (ptr_spcInfo->isEnableUptake) {                              // !! make a func and reuse
                                timeFactor *= exp(-delta_t / ptr_spcInfo->t_alpha);         //
                            }                                                               //
                            
                            // !! to achieve better performance, investigate if we can express the difference of two "erfc"
                            //    with some single special function available in <math.h>, e.g. "lgamma" or "tgamma":
                            //    https://en.wikibooks.org/wiki/C_Programming/math.h
                        }
                        
                        // !! very similar to "static" dynamics
                        double delta_o = ptr_ecSrc->capacityInfo.ssOrMinus1 * ptr_ecSrc->capacityInfo.pointCapacityRadiusOrMinus1 * timeFactor / distance;
                        
                        *ptr_o += delta_o;
                        
                        if (*ptr_o < 0) {
                            if (ptr_spcInfo->isEnableUptake && t > endTime) {
                                *ptr_o = 0;
                            } else {
                                codeContractViolation();
                            }
                        }
                        
                        break;
                    } case 2: {     // "spike" dynamics
                        double delta_t;
                        if (impIdxOrMinus1 == -1) {
                            delta_t = t - ptr_ecSrc->temporalInfo.offsetTimeOrMinus1;
                        } else {
                            delta_t = t - IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                        }
                        
                        // For delta_t == 0, we would have 0/0 in delta_o below
                        if (delta_t <= 0) {
                            break;
                        }
                        
                        // !! optimize the equation:
                        // -pow(Distance, 2.0) / (4.0 * Diff) -> use Distance*Distance and cache before 1st iteration
                        
                        double prod = 4.0 * ptr_spcInfo->diff * delta_t;
                        double delta_o = ptr_ecSrc->capacityInfo.numMoleculesOrMinus1 / pow(PI * prod, 1.5) * exp(-pow(distance, 2.0) / prod);
                        
                        if (ptr_spcInfo->isEnableUptake) {
                            delta_o *= exp(-delta_t / ptr_spcInfo->t_alpha);
                        }
                        
                        *ptr_o += delta_o;
                        
                        break;
                    } default: {
                        codeContractViolation();
                    }
                }
                
                break;
                
            } case 1: {     // "sphere" shape
                
                // 0/1 flag indicating whether the segment centre is inside the sphere
                double isInsideSphere = ptr_vec_segm3DSpecificData[ecsIdx];
                
                if (!isInsideSphere) {
                    break;
                }
                
                // !! no "bool" in this C by default, and cannot #include <stdbool.h>
                int isOnOrOff;
                
                switch ((int)ptr_ecSrc->temporalInfo.enumStaticSwitchSpike) {
                    case 0: {       // "static" dynamics
                        isOnOrOff = 1;
                        
                        break;
                    } case 1: {     // "on-off" dynamics
                    
                        // !! this won't work well, especially for variable time step method
                        //    the best solution would be to schedule 2 "edge" iterations
                        //    alternatively, for fixed dt, we can show a warning to user when they specify the interval shorter than dt
                        
                        // !! code dupl. with "on-off" dynamics for point
                        double offsetTime;
                        if (impIdxOrMinus1 == -1) {
                            offsetTime = ptr_ecSrc->temporalInfo.offsetTimeOrMinus1;
                        } else {
                            offsetTime = IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                        }
                        double endTime = offsetTime + ptr_ecSrc->temporalInfo.durationOrMinus1;
                        isOnOrOff = (t >= offsetTime && t < endTime);
                        
                        break;
                    } case 2: {     // "spike" dynamics
                    
                        // !! this won't work neither for fixed time step, not for variable time step method
                        //    the best solution would be to schedule an "edge" iteration
                        //    alternatively, for fixed dt, we can show a warning to user when they specify the spike time not being a multiple of dt
                        
                        // !! isOnOrOff = (t == ptr_ecSrc->temporalInfo.offsetTimeOrMinus1);
                        
                        // !! do not use "dt" if CVode is enabled
                        
                        // !! just a temp solution
                        double offsetTime;
                        if (impIdxOrMinus1 == -1) {
                            offsetTime = ptr_ecSrc->temporalInfo.offsetTimeOrMinus1;
                            isOnOrOff = (t >= offsetTime - dt/2 && t < offsetTime + dt/2);  // !! inconsistent
                        } else {
                            offsetTime = IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                            isOnOrOff = (t > offsetTime - dt && t <= offsetTime + dt);      // !!
                        }
                        
                        break;
                    } default: {
                        codeContractViolation();
                    }
                }
                
                if (isOnOrOff) {
                    *ptr_o += ptr_ecSrc->capacityInfo.delta_oOrMinus1;
                }
                
                break;
                
            } default: {
                codeContractViolation();
            }
        }
    
    }

ENDVERBATIM
