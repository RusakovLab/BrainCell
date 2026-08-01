COMMENT

The model of Glutamate GLT-1 Transporters.
The kinetic scheme was from the paper 

Comparison of Coupled and Uncoupled Currents during Glutamate
Uptake by GLT-1 Transporters
Dwight E. Bergles, Anastassios V. Tzingounis, and Craig E. Jahr

ENDCOMMENT

NEURON {
    SUFFIX  GluTransNew
    RANGE  C1, C2, C3, C4, C5, C6, C7, C8, C9, C100, C11, C12, C13, C14, C15
    GLOBAL k1_2, k2_1, k2_3, k3_2, k3_4, k4_3, k5_6, k6_5, k6_7, k7_6, k7_8, k8_7
	GLOBAL k8_9, k9_8, k9_10, k10_9,  k11_12, k11_10, k10_11 , k12_11, k12_13, k13_12
	GLOBAL k13_14, k14_13, k14_15, k15_14, k1_15, k15_1, k3_5, k5_3, k4_6, k6_4, k3_11, k11_3
    GLOBAL Nain, Naout, Kin,  Hout, Hin, charge
    RANGE  itrans, density, Gluout,Gluin,time, Kout 
    NONSPECIFIC_CURRENT itrans
}

UNITS {
    (l) = (liter)
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (mA) = (milliamp)
    (pS) = (picosiemens)
    (umho) = (micromho)
    (mM) = (milli/liter)
    (uM) = (micro/liter)
    F = (faraday) (coulombs)
        PI      = (pi)       (1)
}

PARAMETER {	
    : Rates

	k1_2 = 0.01         (l /mM /ms)
    k2_1 = 0.1          (/ms)
    
	k2_3 = 0.01         (l /mM /ms)
    k3_2 = 0.5          (/ms)
    
	k3_4 = 6            (l /mM /ms)
    k4_3 = 0.5          (/ms)
	
	k3_5 = 0.7          (/ms)
	k5_3 = 600000       (l /mM /ms)
	
	k4_6 = 600000       (l /mM /ms)
	k6_4 = 0.7          (/ms)
    
	
	
	k5_6 = 6          (/ms)
	k6_5 = 0.5            (l /mM /ms)
	
    k6_7 = 0.01         (l /mM /ms)
	k7_6 = 1            (/ms)
	k7_8 = 2            (/ms)
	k8_7 = 1.9          (/ms)
	k8_9 = 1            (/ms)
	k9_8 = 0.04         (l /mM /ms)
	k9_10 = 3           (/ms)
	k10_9 = 90000       (l /mM /ms)
	k10_11 = 30          (/ms) 
	k11_10 = 0.1        (l /mM /ms) 
	k11_12 = 100        (/ms)
	k12_11 = 20         (l /mM /ms)
	k12_13 = 100        (/ms)
	k13_12 = 100        (l /mM /ms)
	k13_14 = 1          (l /mM /ms)
	k14_13 = 1          (l /mM /ms)
	k14_15 = 0.04       (/ms)
	k15_14 = 0.01       (/ms)
	k15_1 = 20          (/ms)
	k1_15 = 1           (l /mM /ms)
	k3_11 = 0.0014      (/ms)
	k11_3 = 0.00001     (/ms)
    Nain = 15       (mM/l)
    Naout = 150     (mM/l)
    Kin = 120       (mM/l)
    Kout = 2.5        (mM/l)
    Gluin = 0.025     (mM/l)
	Hin = 1         (mM/l)
	Hout = 1        (mM/l)
    density = 1e12  : (/cm2) : 10000 per um2
    charge = 1.6e-19 (coulombs)
	Gluout = 4e-6      (mM/l)
	time =0         (0.001 sec)
}

ASSIGNED {
    v	   (mV)		:  voltage
    itrans (mA/cm2)            : 
    surf   (cm2)
    volin  (liter)
    volout (liter)
}



STATE {
    : Transporter  states (all fractions)
    
    C1	(/cm2)	
    C2	(/cm2)	  
    C3	(/cm2)	 
    C4	(/cm2)	 
    C5	(/cm2)	 
    C6  (/cm2)
	C7  (/cm2)
	C8  (/cm2)
	C9  (/cm2)
	C100 (/cm2)
	C11  (/cm2)
	C12  (/cm2)
	C13  (/cm2)
	C14  (/cm2)
	C15  (/cm2)
}

INITIAL {

    volin = 1
    volout = 1
    surf = 1
	SOLVE kstates STEADYSTATE sparse
}

BREAKPOINT {
    SOLVE kstates METHOD sparse
    
    :itrans = charge*density*(1e+006)*(0.46*(C1*k1_2*u(v,0.46)*Naout-C2*k2_1)+0.55*(C6*k6_7*Naout*u(v,0.55)-C7*k7_6) + 0.4*(C8*k8_9*u(v,0.4)-C9*k9_8*Nain) + 0.59*(C14*k14_15*u(v,0.04)-C15*k15_14))
	
	itrans = charge*density*(1e+006)*(0.46*(C1*k1_2*u(v,0.46)*Naout-C2*k2_1)+0.55*(C6*k6_7*Naout*u(v,0.55)-C7*k7_6) + 0.4*(C8*k8_9*u(v,0.4)-C9*k9_8*Nain) + 0.56*(C14*k14_15*u(v,0.56)-C15*k15_14))
	
	:printf("New=%g\n",Gluout)
}

KINETIC kstates {
            COMPARTMENT volin { Nain Kin Gluin Hin}
            COMPARTMENT volout { Naout Kout Gluout Hout}
            COMPARTMENT surf { C1 C2 C3 C4 C5 C6 C7 C8 C9 C100 C11 C12 C13 C14 C15}
        : surf=1 : !!!!!!!
		~ C15 <-> C1     (k15_1, k1_15*Kout)
	    ~ C1 <-> C2      (k1_2*u(v,0.46)*Naout, k2_1)
		~ C2 <-> C3      (k2_3*Naout, k3_2)
		~ C3 <-> C4      (k3_4*Gluout, k4_3)
		~ C3 <-> C5      (k3_5, k5_3*Hout)
		~ C4 <-> C6      (k4_6*Hout, k6_4)
		~ C5 <-> C6      (k5_6, k6_5*Gluout)
		~ C6 <-> C7      (k6_7*Naout*u(v,0.55), k7_6)
		~ C7 <-> C8      (k7_8, k8_7)
		~ C8 <-> C9      (k8_9*u(v,0.4), k9_8*Nain)
		~ C9 <-> C100     (k9_10, k10_9*Hin)
		~ C100 <-> C11     (k10_11, k11_10*Gluin)
		~ C11 <-> C12     (k11_12, k12_11*Nain)
		~ C12 <-> C13     (k12_13, k13_12*Nain)
		~ C13 <-> C14     (k13_14*Kin, k14_13*Kin)
		~ C14 <-> C15     (k14_15*u(v,0.56), k15_14)
		~ C3 <-> C11     (k3_11, k11_3)
		
        CONSERVE C1+C2+C3+C4+C5+C6+C7+C8+C9+C100+C11+C12+C13+C14+C15 = 1
}

FUNCTION u(x(mV), th) {
    u = exp(th*x/(2*(26.7 (mV))))
}