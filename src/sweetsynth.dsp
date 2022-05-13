declare name        "sweetsynth";
declare version     "1.0";
declare author      "Levin Eric Zimmermann";
declare options 	"[midi:on][nvoices:16]";

//-----------------------------------------------
//      FM based sweet synth engine
//-----------------------------------------------

import("stdfaust.lib");

f = hslider("freq",300,50,2000,0.01);
bend = ba.semi2ratio(hslider("bend[midi:pitchwheel]",0,-2,2,0.01)) : si.polySmooth(gate,0.999,1);
minimalGain = 0.1;
gain = hslider("gain", 0.5, minimalGain, 1, 0.01);
gate = button("gate");
freq = f * bend; 

impulseGate = ba.impulsify(gate);

rangeLfo(minima, maxima, frequency) = lfo
with {
	span = maxima - minima;
	lfo = ((os.lf_triangle(frequency) + 1) * 0.5 * span) + minima;
};


attackDuration = rangeLfo(0.28, 0.6, 0.5122321) : ba.sAndH(impulseGate);
releaseDuration = rangeLfo(0.3, 0.8, 0.432) : ba.sAndH(impulseGate);
envelope = en.adsr(attackDuration, 0.1, 0.3, releaseDuration, gate) * gain;

modulator(
	modulatorFreq,
	index,
	freqLfo,
	indexLfo,
	minimalGain
) = result
with {
	oscillator = os.osc(modulatorFreq * freqLfo) * indexLfo * index;
	result = 0, oscillator : select2(gain >= minimalGain);
};

modulators = (
	modulator(
		freq * 2,
		300,
		rangeLfo(0.985, 1.005, 0.72312),
		rangeLfo(0.5, 1.2, 0.3),
		0.1
	) +
	modulator(
		freq * 3,
		200,
		rangeLfo(0.98, 1, 0.5),
		rangeLfo(0.1, 1.2, 0.4142),
		0.14
	) +
	modulator(
		freq * 4,
		100,
		rangeLfo(0.99, 1.01, 0.9),
		rangeLfo(0.2, 1.2, 0.7142),
		0.2
	)
);
carrier = os.osc(freq + modulators);

lowpassEnvelope = en.asr(0.8, 4, 0.7, gate) + 1;

fmsynth = carrier * envelope * 0.5 : fi.lowpass(3, freq * lowpassEnvelope);
attackNoise = no.noise : fi.bandpass(8, freq * 0.2, freq * 2) : _ * en.ar(0.001, 0.005, gate) * gain * 1;

process = fmsynth + attackNoise <: _, _;
effect = dm.greyhole_demo;
