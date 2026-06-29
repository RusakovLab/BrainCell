TITLE Optic Nerve Nodal Membrane Channels - Complete Model
: Based on Oozeer et al. 2006 - Model of mammalian optic nerve fibre
: Includes: Fast Na (INa), Fast K (IA), Delayed Rectifier K (IKdr), 
:           Persistent Na (Ip), Slow K (Is), Leak
: Modified from RGC somatic model (Fohlmeister et al. 1990) and 
: McIntyre et al. 2002 for CNS myelinated axons
: Added delayed rectifier to represent juxtaparanodal K channel contribution

NEURON {
    SUFFIX node_Oozeer
    USEION na READ ena WRITE ina
    USEION k READ ek WRITE ik
    NONSPECIFIC_CURRENT ileak
    RANGE gnabar, gkAbar, gkdrbar, gnapbar, gksbar, gleak, eleak
    RANGE ina, ik, ileak, ina_fast, ina_pers, ik_fast, ik_dr, ik_slow
    RANGE m, h, a, b, n, p, s
}

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (S) = (siemens)
}

PARAMETER {
    : Maximum conductances (from Oozeer 2006, modified)
    gnabar = 0.075 (S/cm2)    : Fast sodium
    gkAbar = 0.025 (S/cm2)    : Fast transient K (A-current)
    gkdrbar = 0.012 (S/cm2)   : Delayed rectifier K (from juxtaparanodes)
    gnapbar = 0.001 (S/cm2)   : Persistent sodium
    gksbar = 0.012 (S/cm2)    : Slow potassium
    
    : Leak conductance
    gleak = 0.00001 (S/cm2)   : Very low for high excitability
    eleak = -72 (mV)
    
    : Temperature parameters
    celsius = 37 (degC)
    Q10 = 3.0
}

STATE {
    m h    : Fast sodium activation and inactivation
    a b    : Fast potassium (A-current) activation and inactivation
    n      : Delayed rectifier K activation
    p      : Persistent sodium activation
    s      : Slow potassium activation
}

ASSIGNED {
    v (mV)
    ena (mV)
    ek (mV)
    ina (mA/cm2)
    ik (mA/cm2)
    ileak (mA/cm2)
    ina_fast (mA/cm2)
    ina_pers (mA/cm2)
    ik_fast (mA/cm2)
    ik_dr (mA/cm2)
    ik_slow (mA/cm2)
    
    : Rate variables
    alpha_m (/ms)
    beta_m (/ms)
    alpha_h (/ms)
    beta_h (/ms)
    alpha_a (/ms)
    beta_a (/ms)
    alpha_b (/ms)
    beta_b (/ms)
    alpha_n (/ms)
    beta_n (/ms)
    alpha_p (/ms)
    beta_p (/ms)
    alpha_s (/ms)
    beta_s (/ms)
    
    tadj
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    
    : Fast sodium current (SFCM model)
    ina_fast = gnabar * m*m*m * h * (v - ena)
    
    : Persistent sodium current
    ina_pers = gnapbar * p*p*p * (v - ena)
    
    : Fast transient potassium (A-current)
    ik_fast = gkAbar * a*a*a * b * (v - ek)
    
    : Delayed rectifier potassium (from juxtaparanodes)
    ik_dr = gkdrbar * n*n*n*n * (v - ek)
    
    : Slow potassium current
    ik_slow = gksbar * s * (v - ek)
    
    : Leak current
    ileak = gleak * (v - eleak)
    
    ina = ina_fast + ina_pers
    ik = ik_fast + ik_dr + ik_slow
}

INITIAL {
    tadj = Q10^((celsius - 22)/10)
    rates(v)
    m = alpha_m / (alpha_m + beta_m)
    h = alpha_h / (alpha_h + beta_h)
    a = alpha_a / (alpha_a + beta_a)
    b = alpha_b / (alpha_b + beta_b)
    n = alpha_n / (alpha_n + beta_n)
    p = alpha_p / (alpha_p + beta_p)
    s = alpha_s / (alpha_s + beta_s)
}

DERIVATIVE states {
    rates(v)
    m' = (alpha_m * (1 - m) - beta_m * m) * tadj
    h' = (alpha_h * (1 - h) - beta_h * h) * tadj
    a' = (alpha_a * (1 - a) - beta_a * a) * tadj
    b' = (alpha_b * (1 - b) - beta_b * b) * tadj
    n' = (alpha_n * (1 - n) - beta_n * n) * tadj
    p' = (alpha_p * (1 - p) - beta_p * p) * tadj
    s' = (alpha_s * (1 - s) - beta_s * s) * tadj
}

PROCEDURE rates(v(mV)) {
    LOCAL vshift_m
    
    : ========== FAST SODIUM (SFCM) ==========
    vshift_m = v + 37
    if (fabs(vshift_m) < 1e-6) {
        alpha_m = 0.45 * 0.75
    } else {
        alpha_m = 0.45 * vshift_m / (1 - exp(-vshift_m/10)) * 0.75
    }
    beta_m = 15 * exp(-(v + 62)/18) * 0.75
    
    alpha_h = 0.16 * exp(-(v + 77)/20) *0.4
    beta_h = 2.4 / (1 + exp(-(v + 47)/10)) *0.4
    
    : ========== FAST TRANSIENT K (A-CURRENT) ==========
    vshift_m = v + 90
    if (fabs(vshift_m) < 1e-6) {
        alpha_a = 0.015 * 2.5
    } else {
        alpha_a = 0.015 * vshift_m / (1 - exp(-vshift_m/10)) * 2.5
    }
    beta_a = 0.25 * exp(-(v + 30)/10) * 2.5
    
    alpha_b = 0.04 * exp(-(v + 75)/20)
    beta_b = 0.6 / (1 + exp(-(v + 45)/10))
    
    : ========== DELAYED RECTIFIER K (n-gate, from spike.mod) ==========
    : This represents the juxtaparanodal Kv1.1/1.2 channels
    vshift_m = v + 37
    if (fabs(vshift_m) < 1e-6) {
        alpha_n = 0.09575
    } else {
        alpha_n = 0.09575 * (-vshift_m) / (1 - exp(vshift_m/10))
    }
    beta_n = 1.915 * exp(-(v + 47)/80)
    
    : ========== PERSISTENT SODIUM ==========
    vshift_m = v + 19
    if (fabs(vshift_m) < 1e-6) {
        alpha_p = 0.0151 * 1.3
    } else {
        alpha_p = 0.0151 * vshift_m / (1 - exp(-vshift_m/10.2)) * 1.3
    }
    
    vshift_m = v + 26
    if (fabs(vshift_m) < 1e-6) {
        alpha_p = alpha_p
        beta_p = 0.000379 * 1.3
    } else {
        beta_p = 0.000379 * (-vshift_m) / (1 - exp(vshift_m/10)) * 1.3
    }
    
    : ========== SLOW POTASSIUM ==========
    vshift_m = v + 23.5
    if (fabs(vshift_m) < 1e-6) {
        alpha_s = 0.0032 / 2.5
    } else {
        alpha_s = 0.0032 * (-vshift_m) / (1 - exp(vshift_m/7.1)) / 2.5
    }
    
    vshift_m = v + 41.1
    if (fabs(vshift_m) < 1e-6) {
        beta_s = 0.0019 / 2.5
    } else {
        beta_s = 0.0019 * vshift_m / (1 - exp(-vshift_m/12.2)) / 2.5
    }
}