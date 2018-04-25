(
~synth = ScProphetRev2.new;
~synth.connect;
MIDIClient.reset;
/*
MIDIIn.noteOn = {
	| uid, chan, key, vel |
	("key: "++key++" vel: "++vel++" chan: "++chan++" uid: "++uid).postln;
};
MIDIIn.control = {
	| uid, chan, ctrl, val |
	("controller: "++ctrl++" value: "++val++" chan: "++chan++" uid: "++uid).postln;
};
*/
)
(
s.waitForBoot({
	var melody, melody2, bass;
	var table = NrpnTable.new;
	var parser = TheoryNoteParser.new;
	var wrapInit = { |synth, pattern, bank="F1", program="P1", modwheelval=nil, initLag = 0|
		Pfset(
			{
				"initialization now: %\n".postf(thisThread.clock.beats);
				synth.select_patch_by_id(bank, program);
				if (modwheelval.notNil) {
					synth.midi_out.control(0, 1, modwheelval);
				};
				Event.silent(initLag).yield;
			},
			pattern,
			{
				"finished now: %\n".postf(thisThread.clock.beats);
			}
		)
	};
	var horrornotes = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\midinote, Pseq([Prand((30..50), 1), Prand((30..50), 1)], inf),
		\amp, Pbrown(70,100,1,inf),
		\dur, Prand((3..7), inf)
	);
	var horrorcutoff_a = Pbind(
		\instrument, \default,
		\amp, 0,
		\number, table.str2num('LPF_CUTOFF', "A"),
		\value, Pbrown(20, 100, 10),
		\dur, Pfunc({1.rrand(5)}),
		\channel, 1,
		\receiver, Pfunc({ | event | ~synth.sendNRPN(event[\number], event[\value], event[\channel], verbose:false)}),
	);
	var horrorcutoff_b = Pbindf(
		horrorcutoff_a,
		\number, table.str2num('LPF_CUTOFF', "B")
	);
	var horror_pitchwheel = Pbind(
		\type, \midi,
		\midicmd, \bend,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\val, Pbrown(1,16384,100,inf),
		\dur, Pfunc({1.rrand(5)}),
	);
	var horrorpattern = Ppar([horrornotes, horrorcutoff_a, horrorcutoff_b, horror_pitchwheel], 1);

	var partyaccomp = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\midinote, Pseq([
			45, 50, 48
		], inf).trace,
		\legato, 1,
		\dur, Pseq([ 4, 1, 1 ] * (8 /*duration in beats*/ /(135 /*bpm*/ /60)), inf)
	);
	var partymelody = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\midinote, Pseq([
			Pseq([
				72, 72, 72, 71, 72,
				76, 76, 76, 75, 76,
				81, 80, 79, 78, 77, 76, 75, 74,
				73
			], 4),
			Pseq([
				64, 67, 71, 74,
				65, 69, 72, 76,
				67, 71, 74, 77,
				69, 72, 76, 79,
				71, 74, 77, 81,
				72, 76, 79, 83,
				74, 77, 81, 84,
				76, 79, 83, 86,
				77, 81, 84, 88,
				79, 83, 86, 89,
				81, 84, 88, 91,
				83, 86, 89, 93,
				84, 88, 91, 95,
				86, 89, 93, 96,
				88, 91, 95, 98,
				89, 93, 96, 100,
				91, 95, 98, 101,
				93, 96, 100, 103,
				95, 98, 101, 105,
				96, 100, 103, 107,
				108, 112, 115, 119,
			].mirror2, 2),
			Pseq([
				Rest()
			], 1),
			/*
			Ppatlace([
				Pseq((78..96), 1),
				Pseq((77..60), 1),
			], 38),*/
		], inf),
		\dur,  Pseq([
			Pseq([
				1, 1, 1, 0.5, 0.5,
				1, 1, 1, 0.5, 0.5,
				0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
				4,
			] * (60 / 135 /*bpm*/), 4),
			Pseq([
				0.125
			]* (60/135), 42*4*2),
			Pseq([
				6
			]* (60/135), 1),
			/*Pseq([
				0.125
			]* (60/135), 38);*/
		], inf),
		\legato, 0.95,
	);
	var partypattern = Ppar([partyaccomp, partymelody], 1);

	var meditationchords = Pbind(
		\instrument, \pad,
		\freq, Pseq([
			Pseq([
				"c2 g3 eb4 g4",
			].collect({|el| parser.asMidi(el).midicps}), 1),
			Pseq([
				"g2 g3 d4 f4 g4",
				"c3 g3 eb4 g4 c5",
				"f2 f4 ab4 c5 eb5",
				"eb2 c4 eb4 g4",
				"g2 d4 f4 g4 b4 d5",
				"ab2 c4 eb4 ab4",
				"f2 c4 f4 g4 ab4 f5",
				"c2 g3 eb4 g4 eb5",
		].collect({|el| parser.asMidi(el).midicps}), inf)], 1),
		\dur, Pseq([5],inf),
		\s, Pkey(\dur),
		\a, 0.4
	);

	var meditationmelody = Pbind(
		\instrument, \flute,
		\freq, Pxrand(parser.asMidi("c5 eb5 g5 bb5 c6").midicps ++ [Rest(), Rest()], inf),
		\dur, Pbrown(lo:0.1,hi:1.0, step:0.125, length:inf),
		\a, Pkey(\dur)*0.95,
		\amp, Pseq([
			Pseq((((1..16)/16)*0.5), 1),
			Pbrown(lo:0.3,hi:0.6,step:0.1,length:inf)], inf)
	);

	~horror = wrapInit.(~synth, horrorpattern, "F3", "P28",	0);
	~party = wrapInit.(~synth, partypattern, "F2", "P56", 82, 1);
	~meditation = Ptpar([0.0, meditationchords, 8*5.0, meditationmelody]);

	SynthDef(\pad, {
		| out = 0, freq = 440, gate=1, a = 0.1, s = 3, r = 1|
		var freqs = { freq * LFNoise2.kr(freq:1,mul:0.01,add:1) }!24;
		var gen = LFSaw.ar(freq:freqs) * 0.1;
		//var fmod = 1;
		var fmod = LFCub.kr(freq:1/12).range(1, LFNoise2.kr(freq:1).range(6,7)); // sharper sound
		var rqmod = LFNoise2.kr(freq:1/8).range(0.1,1.0);
		var modspeed = 1/s;
		//var modspeed = 10;
		//var modspeed = SinOsc.kr(0.1,phase:0).range(1/s, 10);
		var snd = RLPF.ar(in:gen, freq:SinOsc.kr(modspeed).range(freqs*0.8, freqs*1.2) * fmod, rq:rqmod);
		var env = EnvGen.ar(Env.new(levels:[0,1,1,0], times:[a, s, r]), gate, doneAction:2);
		Out.ar(bus:out, channelsArray:env*Splay.ar(snd.tanh));
	}).add;

	SynthDef(\flute, {
		| out = 0, freq = 440, amp = 1.0, a = 0.1, r = 0.1|
		//var fmod = 1; // clean
		//var fmod = LFCub.kr(freq:1/12).range(1, LFNoise2.kr(freq:12.0).range(1,1.1)); // tone deaf flute
		var fmod = LFCub.kr(freq:1/12).range(1, LFNoise2.kr(freq:12.0).range(1,1.02)); // flute-like sound
		var env = EnvGen.ar(Env.perc(a, r), levelScale:0.5, doneAction:2);
		var snd = SinOsc.ar(freq * fmod)!2;
		Out.ar(bus:out, channelsArray:(env*(amp*snd).tanh));
	}).add;

	SynthDef(\bass, {
		| out = 0, freq = 50, amp=0.8, atk = 0.01, dur = 0.15|
		Out.ar(out, BPF.ar(LFSaw.ar(freq), freq, 2, mul: EnvGen.kr( Env.perc( atk, dur-atk, amp, 6 ), doneAction: 2 )) ! 2);
	}).add;


	SynthDef(\bufplay, {
		| out = 0, bufnum = 0, speed = 1.0, amp = 1.0 |
		Out.ar(out, amp*PlayBuf.ar(numChannels:2, bufnum:bufnum, rate:speed, trigger:1, startPos:0, loop:0, doneAction:2));
	}).add;

	~wavPath = PathName(thisProcess.nowExecutingPath).parentPath++"wavs/";
	~allocBuffers = {
		b = Dictionary.new;
	};
	~makeBuffers = {
		PathName(~wavPath).entries.do({
			| subfolder, idx |
			b = b.add(
				subfolder.allFolders.last ->
				Array.fill(
					subfolder.entries.size,
					{
						arg i;
						//subfolder.entries.postln;
						Buffer.read(s, subfolder.entries[i].fullPath);
					}
				);
			);
		});
	};
	~allocBuffers.();
	~makeBuffers.();

	s.sync;

	~killnotes = { ~synth.all_notes_off; CmdPeriod.remove(~killnotes); };


	~synth = ScProphetRev2.new;
	~synth.connect;

	~event_type = \midi;

	~flags = IdentityDictionary.newFrom([
		\jam : false,
		\octaviate  : false,
		\secondvoice : false,
		\bass : false
	]);

	~melody_notes = ["c4"];
	~bass_notes = ["a3", "a2"];
	~allowed_durs = [1/4, 1/8, 1/16]*4;

	melody = Pbind(
		\type, Pfunc({~event_type}),
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\instrument, \default,
		\midinote, Pfunc({
			|ev|
			var note = parser.asMidi(~melody_notes.choose);
			if (~flags[\octaviate]) {
				note = note + ((1.rand2)*12);
			};

			note;
		}),
		\dur, Pfunc({
			|ev|
			if (~flags[\jam]) {
				~allowed_durs.choose;
			} {
				1;
			};
		}),
		\amp, Pbrown(0.5,0.8,0.125,inf)
	);

	melody2 = Pbind(
		\type, Pfunc({~event_type}),
		\instrument, \default,
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\midinote, Pfunc({
			|ev|
			if (~flags[\secondvoice]) {
				var note = parser.asMidi(~melody_notes.choose);
				if (~flags[\octaviate]) {
					note = note + ((1.rand2)*12);
				};
				note;
			} {
				Rest();
			};
		}),
		\dur, Pfunc({
			|ev|
			if (~flags[\jam]) {
				~allowed_durs.choose;
			} {
				1;
			};
		}),
		\amp, Pbrown(0.5,0.8,0.125,inf)
	);

	bass = Pbind(
		\type, \default,
		\instrument, \bass,
		\out, 0,
		\midinote, Pfunc({
			|ev|
			if (~flags[\bass]) {
				var note = parser.asMidi(~bass_notes.choose);
				if (~flags[\octaviate]) {
					note = note + ((1.rand2)*12);
				};
				note;
			} {
				Rest();
			};
		}),
		\dur, Pfunc({
			|ev|
			if (~flags[\jam]) {
				~allowed_durs.choose;
			} {
				1;
			};
		}),
		\amp, 0.8,
	);

	~initpattern = wrapInit.(~synth, Ppar([melody,melody2,bass], 1), "F2", "P1", 0);
	Pdef(\notes, ~initpattern);

	CmdPeriod.add(~killnotes);
});

)

~event_type = \default;

Pdef(\notes).play;

~melody_notes = ["c4", "e4"];
~melody_notes = ["c4", "e4", "g4"];
~melody_notes = ["c4", "e4", "g4", "bb4"];
~melody_notes = ["c4", "e4","g4", "bb4", "f#4"];
~bass_notes = ["c2"];
~flags[\jam] = true;
~flags[\octaviate] = true;
~flags[\bass] = true;
~flags[\secondvoice] = true;

~event_type = \midi;

~bass_notes = ["c2", "g2"];

~flags[\bass] = false;

Pdef(\notes).stop;

~hplayer = ~horror.play();
~hplayer.stop;
~mplayer = ~meditation.play();
~mplayer.stop;
~pplayer = ~party.play();
~pplayer.stop;

Synth(\bufplay, [\bufnum, b["clocks"].choose.bufnum, \speed, 1, \amp, 5.0]);
Synth(\bufplay, [\bufnum, b["grind"].choose.bufnum, \speed, 1, \amp, 5.0]);
Synth(\bufplay, [\bufnum, b["purr"].choose.bufnum, \speed, 1, \amp, 5.0]);

~killnotes.();

