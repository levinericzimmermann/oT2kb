declare name        "multiguitar";
declare version     "1.0";
declare author      "Levin Eric Zimmermann";
declare options 	"[midi:on][nvoices:16]";

//-----------------------------------------------
//      Odd guitar
//-----------------------------------------------

import("stdfaust.lib");

baseFreq = hslider("freq",300,50,2000,0.01);
bend = ba.semi2ratio(hslider("bend[midi:pitchwheel]",0,-2,2,0.01)) : si.polySmooth(gate,0.999,1);
minimalGain = 0.1;
gain = hslider("gain", 0.5, minimalGain, 1, 0.01);
gate = button("gate");
freq = bend * baseFreq; 

impulseGate = ba.impulsify(gate);

scale(value, old_min, old_max, new_min, new_max) = new_value
with {
	old_range = old_max - old_min;
	new_range = new_max - new_min;
	percentage = (value - old_min) * old_range;
	new_value = (percentage * new_range) + new_min;
};

oddGuitar(
	freqFactor,
	minDelayLength,
	maxDelayLength,
	delayModulationFrequency,
	guitarModelTypeLfoFrequency,
	pluckPositionLfoRate,
	minimalGain,
	nModes,
	bodySizeLfoFrequency,
	bodyFormLfoFrequency,
	freqEnvelopeDurationLfoFrequency
) = filteredGuitar
with {
	envelopeDuration = (no.lfnoise0(freqEnvelopeDurationLfoFrequency) + 1) * 0.5 * 0.23;
	freqEnvelope = (en.asr(envelopeDuration, 1, 0, gate) * 0.06) + 0.94;
	adjustedFreqEnvelope = 1, freqEnvelope : select2(gate);
	stringLength = pm.f2l(freqFactor * freq * adjustedFreqEnvelope);
	sharpness = scale(gain, 0, 1, 0.5, 1);
	pluck = pm.pluckString(stringLength, 1, 1.5, sharpness, gain, gate);
	// pluckPosition = (no.lfnoise0(pluckPositionLfoRate) + 1) * 0.5 : ba.sAndH(impulseGate);
	// pluckPosition = (no.lfnoise0(pluckPositionLfoRate) + 1) * 0.5;
	pluckPosition = 0.5;
	strings = pluck <: 
		pm.nylonGuitarModel(stringLength, pluckPosition),
		pm.elecGuitarModel(stringLength, pluckPosition, 1);
	stringSelectorLfo = 0.5 * (os.lf_triangle(guitarModelTypeLfoFrequency) + 1);
	string = strings : _ * stringSelectorLfo, _ * abs(1 - stringSelectorLfo) :> _;
	maxDelayLengthAsSamples = int(ma.SR * maxDelayLength);
	delayLength = (
		(os.lf_triangle(delayModulationFrequency) + 1) *
		0.5 *
		(maxDelayLength - minDelayLength)) +
		minDelayLength;
	delayLengthAsSamples = int(ma.SR * delayLength);
	guitarString = string : de.sdelay(maxDelayLengthAsSamples, 1024, delayLengthAsSamples);
	// bodySize = (os.lf_triangle(bodySizeLfoFrequency) + 1) * 1;
	// bodyForm = (os.lf_triangle(bodyFormLfoFrequency) + 1) * 1;
	// guitar = guitarString : pm.modeInterpRes(nModes, bodyForm, bodySize);
	// filteredGuitar= 0, guitar : select2(gain >= minimalGain);
	filteredGuitar= 0, guitarString : select2(gain >= minimalGain);
};

strings = 	(oddGuitar(1, 0, 0.001, 0.001, 0.312, 11, 0, 32, 0.1032, 0.10842, 7) * 0.5) +
		  		// (oddGuitar(1.0001, 0.08, 0.192, 0.02, 0.12, 23, 0.12, 20, 0.232, 0.2832, 23) * 0.24) +
		  		(oddGuitar(2, 0.03, 0.214, 0.01, 0.12, 13, 0.2, 20, 0.232, 0.2832, 33) * 0.25);
		  		// (oddGuitar(0.5, 0.1, 0.21, 0.009242, 0.132, 17, 0.22, 27, 0.072, 0.098, 19) * 0.15);


bodySize = (os.lf_triangle(0.22) + 1) * 1;
bodyForm = (os.lf_triangle(0.292) + 1) * 1;
marimba = pm.marimba(freq, 1, 2000, 0.15, gain, gate);
instruments = strings : pm.modeInterpRes(25, bodyForm, bodySize) : (_ * 0.5) + (strings * 0.3);


firstHarmonic = os.osc(freq);
secondHarmonic = os.osc(freq * 2) * 0.5;
thirdHarmonic = os.osc(freq * 2) * 0.2;

harmonicsEnvelope = en.asr(0.35, 1, 1.2, gate);
harmonics = firstHarmonic + secondHarmonic + thirdHarmonic : _ * harmonicsEnvelope * gain * 0.0185;

guitarEnvelope = en.asr(0.0001, 1, 2, gate);

attack = no.noise : _ * en.ar(0.0008, 0.001, gate) * 0.06 * gain : fi.bandpass(4, 40, 8000);

process = (instruments * guitarEnvelope) + harmonics + attack <: _, _;
effect = dm.greyhole_demo;
