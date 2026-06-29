TITLE Juxtaparanodal Potassium Channels for CNS Axons
: Based on McIntyre et al. 2002 and Devaux et al. 2002
: References in Oozeer 2006 for CNS myelinated fibers
: Two types of K channels in juxtaparanodal regions:
: 1. DTX-I sensitive (Kv1.1/1.2 family)
: 2. KTX sensitive channels
: These are located in the juxtaparanodal/paranodal regions

NEURON {
    SUFFIX juxta_k
    USEION k READ ek WRITE ik
    RANGE gkbar_dtx, gkbar_ktx
    RANGE ik, ik_dtx, ik_ktx
    RANGE n_dtx, n_ktx
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (S) = (siemens)
}

PARAMETER {
    : Maximum conductances for juxtaparanodal K channels
    : Values based on McIntyre et al. 2002 and scaled for juxtaparanodal region
    gkbar_dtx = 0.01 (S/cm2)   : DTX-I sensitive (Kv1.1/1.2)
    gkbar_ktx = 0.005 (S/cm2)  : Kaliotoxin sensitive
    
    : Temperature parameters
    celsius = 37 (degC)
    Q10_n = 3.0                 : Q10 for activation kinetics
}

STATE {
    n_dtx    : DTX-I sensitive channel activation
    n_ktx    : KTX sensitive channel activation
}

ASSIGNED {
    v (mV)
    ek (mV)
    ik (mA/cm2)
    ik_dtx (mA/cm2)
    ik_ktx (mA/cm2)
    
    : Rate variables for DTX-I sensitive channels
    alpha_dtx (/ms)
    beta_dtx (/ms)
    
    : Rate variables for KTX sensitive channels
    alpha_ktx (/ms)
    beta_ktx (/ms)
    
    tadj
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    
    : DTX-I sensitive current (Kv1.1/1.2 - fast activating, non-inactivating)
    ik_dtx = gkbar_dtx * n_dtx^4 * (v - ek)
    
    : KTX sensitive current (similar kinetics, slightly slower)
    ik_ktx = gkbar_ktx * n_ktx^4 * (v - ek)
    
    ik = ik_dtx + ik_ktx
}

INITIAL {
    tadj = Q10_n^((celsius - 22)/10)
    rates(v)
    n_dtx = alpha_dtx / (alpha_dtx + beta_dtx)
    n_ktx = alpha_ktx / (alpha_ktx + beta_ktx)
}

DERIVATIVE states {
    rates(v)
    n_dtx' = (alpha_dtx * (1 - n_dtx) - beta_dtx * n_dtx) * tadj
    n_ktx' = (alpha_ktx * (1 - n_ktx) - beta_ktx * n_ktx) * tadj
}

PROCEDURE rates(v(mV)) {
    LOCAL vshift
    
    : DTX-I sensitive K channel (Kv1.1/1.2 type)
    : Fast activating delayed rectifier
    : Based on Kv1 family kinetics adapted for CNS axons
    
    vshift = v + 35
    if (fabs(vshift) < 1e-6) {
        alpha_dtx = 0.02
    } else {
        alpha_dtx = 0.02 * vshift / (1 - exp(-vshift/10))
    }
    beta_dtx = 0.05 * exp(-(v + 45)/80)
    
    : KTX sensitive K channel
    : Similar to DTX but with slightly shifted voltage dependence
    : and slower kinetics
    
    vshift = v + 40
    if (fabs(vshift) < 1e-6) {
        alpha_ktx = 0.015
    } else {
        alpha_ktx = 0.015 * vshift / (1 - exp(-vshift/10))
    }
    beta_ktx = 0.04 * exp(-(v + 50)/80)
}

: Note: These channels are primarily located in the juxtaparanodal region
: In CNS axons (including optic nerve), they are concentrated under the myelin
: adjacent to the node of Ranvier, as described by Devaux et al. 2002, 2004
: They contribute to:
: 1. Action potential repolarization when myelin is disrupted
: 2. Prevention of ectopic spike generation
: 3. Regulation of internodal excitability