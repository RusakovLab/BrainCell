: calcium flux gap junction. 2018
: 04 01 2018
: Modification of ica

NEURON {
    POINT_PROCESS GapCaExtr
    
    USEION ca READ cai WRITE ica
    RANGE TimeRelex, BasicCa, ExtraCaConcentration, fluxion
   
}

UNITS {
    (molar) =	(1/liter)
    (mM) =	(millimolar)
    (um) =	(micron)
    (mA) =	(milliamp)
    FARADAY =	(faraday)	(10000 coulomb)
    PI = (pi)	(1)
}

PARAMETER {
    TimeRelex = 1e20 (ms)   : !!! was: 10000
    BasicCa = 1 (mM)
	
	ExtraCaConcentration = 50e-6 (mM)
	
	
}

ASSIGNED {
    cai (mM)
  
    fluxion (mM ms)
    ica  (nanoamp) : so you can plot the calcium current generated by this mechanism
}

BREAKPOINT {
    fluxion=BasicCa*TimeRelex 
    ica = (1e+16)*(((cai - ExtraCaConcentration)/fluxion)*(2*FARADAY))            : Gap junction between Astrocytes
	
   
}