declare name        "bells";
declare version     "1.0";
declare author      "Levin Eric Zimmermann";
declare options 	"[midi:on][nvoices:12]";

//-----------------------------------------------
//      Oscillator based synthesis
//-----------------------------------------------

import("stdfaust.lib");

f = hslider("freq",300,50,2000,0.01);
bend = ba.semi2ratio(hslider("bend[midi:pitchwheel]",0,-2,2,0.01)) : si.polySmooth(gate,0.999,1);
minimalGain = 0.1;
gain = hslider("gain", 0.5, minimalGain, 1, 0.01);
gate = button("gate");
freq = f*bend; 

// process = pm.russianBell(3,7000,0.25,gain,gate) <: _,_;
 process = pm.strikeModel(10,10000,0.7,gain,gate) : pm.marimbaModel(freq,0.5) <: _,_;
effect = dm.greyhole_demo;
