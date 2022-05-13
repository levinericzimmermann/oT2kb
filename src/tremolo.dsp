declare name        "tremolo";
declare version     "1.0";
declare author      "Levin Eric Zimmermann";
declare options 	"[midi:on][nvoices:16]";

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

impulseGate = ba.impulsify(gate);

fluteEnvelope = en.adsr(1.12, 0.35, 0.2, 0.5, gate) * gain;
blower = pm.blower(0.8, 0.005, 2000);
echoGainLfo = (os.lf_triangle(0.2) * 0.5) + 1;
bandpassLfo = (os.lf_triangle(0.7) * 0.5) + 1;
blowNoiseAdjustedAdjusted = os.lf_triangle(0.3) + 1.7;
blowNoiseAdjusted = (os.lf_triangle(blowNoiseAdjustedAdjusted) * 0.05) + 0.95;
blowNoise = no.pink_noise : ((fi.bandpass(2, freq * 0.3, freq * 2.3) * 0.15) + 0.9) * blowNoiseAdjusted;
flute = pm.fluteModel(pm.f2l(freq), 0.5, blowNoise) * fluteEnvelope : fi.bandpass(2, freq * 0.9, freq * (1 + (3 * bandpassLfo)));
fluteEcho = flute : ef.echo(1.3, 0.6, 0.1) * echoGainLfo;
combinedFlute = flute + fluteEcho, 0 : select2(freq > 3800 | freq < 300);

squareGainLfoLfo = ((os.lf_triangle(0.04323) + 1) * 0.5 * 0.3) + 0.1;
squareGainLfo = (os.lf_triangle(squareGainLfoLfo) * 0.5) + 1;
squareEnvelope = en.adsr(1.85, 0.24, 0.32, 0.1, gate) * gain;
electroNoise = no.noise : fi.bandpass(4, freq * 0.5, freq * 2) * 0.4;
square = (os.square(freq) + electroNoise) * squareEnvelope * 0.095 : fi.lowpass(8, freq * 3.85) * squareGainLfo;

attackNoiseEnvelope = en.ar(0.0001, 0.1, gate) * gain * 0.07;
attackNoise = no.noise : fi.bandpass(4, 700, 10000);
startAttackEnvelope = en.ar(0.0001, 2.8, gate) * gain * 0.12;
startAttackWave = os.square(freq * 0.5);
startAttack = (startAttackWave * startAttackEnvelope) + (attackNoise * attackNoiseEnvelope);

process = combinedFlute + square + startAttack : fi.lowpass(2, freq * 4) : _ * 0.5 <: _, _;
effect = dm.greyhole_demo;
