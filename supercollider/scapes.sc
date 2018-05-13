(
~synth = ScProphetRev2.new;
~synth.connect;
~yoshimidi_out = MIDIOut.newByName("yoshimi", "input").latency_(Server.default.latency);
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
	var melody, melody2, bass, mystery, brainpattern1, brainpattern2;
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
	var horrornotes;
	var horrorcutoff_a;
	var horrorcutoff_b;
	var horror_pitchwheel;
	var horrorpattern;
	var partyaccomp;
	var partymelody;
	var partypattern;
	var meditationchords;
	var meditationmelody;

	var osc_recv = NetAddr("127.0.0.1", nil);
	var osc_send = NetAddr("127.0.0.1", 23000);

	var notelut = Dictionary.newFrom([
		"do" : "c4",
		"dokruis" : "c#4",
		"re" : "d4",
		"rekruis" : "d#4",
		"mi" : "e4",
		"fa" : "f4",
		"fakruis" : "f#4",
		"sol" : "g4",
		"solkruis" : "g#4",
		"la" : "a4",
		"lakruis" : "a#4",
		"si" : "b4"
	]);

	~lastattentionvalue = 1;
	~lastmeditationvalue = 1;

	OSCdef(\raw).disable;
	OSCdef.new(\raw, {
		| msg, time, addr, recPort, argTemplate, dispatcher |

		x = Synth(\brainSine, [\out, 0,
			\rawval, msg[1]
		]);

		y = Synth(\brainNoise, [\out, 0,
			\rawval, msg[1]
		]);
	}, "/mindwave/raw");

	OSCdef(\attention).enable;
	OSCdef(\attention, {
		| msg, time, addr, recPort, argTemplate, dispatcher |
		//msg.postln;
		~lastattentionvalue = msg[1];
	}, "/mindwave/attention");

	OSCdef(\meditation).enable;
	OSCdef(\meditation, {
		| msg, time, addr, recPort, argTemplate, dispatcher |
		//msg.postln;
		~lastmeditationvalue = msg[1];
	}, "/mindwave/meditation");

	OSCdef(\eyeblink).disable;
	OSCdef(\eyeblink, {
		| msg, time, addr, recPort, argTemplate, dispatcher |
		//msg.postln;
		Synth(\bufplay, [\bufnum, b["eyeblink"].choose.bufnum, \speed, 1, \amp, 1.0]);
	}, "/mindwave/eyeblink");

	OSCdef(\camera).enable;
	OSCdef(\camera, {
		| msg, time, addr, recvPort |
		var command = msg[3].asString;
		command.postln;
		if (notelut[command].notNil) {
			var note = notelut[command];
			if (~melody_notes.includesEqual(note).not) {
				~melody_notes = ~melody_notes.add(note);
			};
		};
		if (command.compare("bass", ignoreCase:true) == 0) {
			~flags[\bass] = true;
		};
		if (command.compare("stopbass", ignoreCase:true) == 0) {
			~flags[\bass] = false;
		};
		if (command.compare("jam", ignoreCase:true) == 0) {
			~flags[\jam] = true;
		};
		if (command.compare("tweedestem", ignoreCase:true) == 0) {
			~flags[\secondvoice] = true;
		};
		if (command.compare("stoptweedestem", ignoreCase:true) == 0) {
			~flags[\secondvoice] = false;
		};
		if (command.compare("octavieer", ignoreCase:true) == 0) {
			~flags[\octaviate] = true;
		};
		if (command.compare("stopoctavieer", ignoreCase:true) == 0) {
			~flags[\octaviate] = false;
		};
		if (command.compare("stopnoten", ignoreCase:true) == 0) {
			if (Pdef(\notes).isPlaying) {
				Pdef(\notes).stop;
			};
		};
		if (command.compare("noten", ignoreCase:true) == 0) {
			if (Pdef(\notes).isPlaying.not) {
				Pdef(\notes).play;
			};
		};
		if (command.compare("horror", ignoreCase:true) == 0) {
			if (~hplayer.isNil) {
				~hplayer = ~horror.play();
			};
		};
		if (command.compare("stophorror", ignoreCase:true) == 0) {
			~hplayer.stop;
			~hplayer = nil;
		};
		if (command.compare("meditatie", ignoreCase:true) == 0) {
			if (~mplayer.isNil) {
				~mplayer = ~meditation.play();
			};
		};
		if (command.compare("stopmeditatie", ignoreCase:true) == 0) {
			~mplayer.stop();
			~mplayer = nil;
		};
		if (command.compare("party", ignoreCase:true) == 0) {
			if (~pplayer.isNil) {
				~pplayer = ~party.play();
			};
		};
		if (command.compare("stopparty", ignoreCase:true) == 0) {
			~pplayer.stop();
			~pplayer = nil;
		};
		if (command.compare("mysterie", ignoreCase:true) == 0) {
			if (~mysplayer.isNil) {
				~mysplayer = ~mystery.play();
			};
		};
		if (command.compare("stopmysterie", ignoreCase:true) == 0) {
			~mysplayer.stop();
			~mysplayer = nil;
		};
		if (command.compare("brein", ignoreCase:true) == 0) {
			OSCdef(\raw).enable;
			OSCdef(\attention).enable;
			OSCdef(\meditation).enable;
			OSCdef(\eyeblink).enable;
			if (~brainplayer.isNil && ~brainpattern.notNil) {
				~brainplayer = ~brainpattern.play;
			};
		};
		if (command.compare("stopbrein", ignoreCase:true) == 0) {
			OSCdef(\raw).disable;
			OSCdef(\attention).disable;
			OSCdef(\meditation).disable;
			OSCdef(\eyeblink).disable;
			if (~brainplayer.notNil) {
				~brainplayer.stop;
				~brainplayer = nil;
			};
		};
		if (command.compare("ambient", ignoreCase:true) == 0) {
			if (~ambient.isPlaying.not) {
				~ambient = Synth(\bufplay, [\bufnum, b["ambient"].choose.bufnum, \speed, 1, \amp, 1.0]);
			};
		};
		if (command.compare("stopambient", ignoreCase:true) == 0) {
			if (~ambient.notNil) {
				~ambient.free;
				~ambient = nil;
			};
		};
	}, "/camera/word", osc_recv);

	OSCdef(\minute).enable;
	OSCdef(\minute, {
		| msg, time, addr, recvPort |
		msg.postln;
		Synth(\bufplay, [\bufnum, b["shortbleep"].choose.bufnum, \speed, 1, \amp, 1.0]);
	}, "/godot/clockplate", osc_recv);

	~osc_note_handler = {
		| ev |
		var midinotes = [];
		if (ev.isRest.not) {
			if (ev[\midinote].class == Function) {
				if (ev[\freq].class == Array) {
					midinotes = ev[\freq].collect({|el| el.cpsmidi.round(1).mod(12).asInteger; });
				} /* else */ {
					//ev[\freq].class.postln;
					midinotes = [ev[\freq].cpsmidi.round(1).mod(12).asInteger];
				}
			} /* else */ {
				if (ev[\midinote].class == Array) {
					midinotes = ev[\midinote].collect({|el| el.round(1).mod(12).asInteger; });
				} /* else */ {
					if (ev[\midinote].class != TheoryNoteParser) {
						midinotes = [ ev[\midinote] ];
					};
				};
			};
			midinotes.do({
				| note |
				osc_send.sendMsg("/sc/note", note.round(1).mod(12).asInteger, ev[\dur]);
			});
		};
		1; // prevent patterns from stopping by returning nil after rest...
	};

	horrornotes = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\midinote, Pseq([Prand((30..50), 1), Prand((30..50), 1)], inf),
		\amp, Pbrown(70,100,1,inf),
		\dur, Prand((7..14), inf),
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
	);
	horrorcutoff_a = Pbind(
		\instrument, \default,
		\amp, 0,
		\number, table.str2num('LPF_CUTOFF', "A"),
		\value, Pbrown(20, 100, 1),
		\dur, Pfunc({1.rrand(5)}),
		\channel, 1,
		\receiver, Pfunc({ | event | ~synth.sendNRPN(event[\number], event[\value], event[\channel], verbose:false)}),
	);
	horrorcutoff_b = Pbindf(
		horrorcutoff_a,
		\number, table.str2num('LPF_CUTOFF', "B")
	);
	horror_pitchwheel = Pbind(
		\type, \midi,
		\midicmd, \bend,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\val, Pbrown(1,16384,10,inf),
		\dur, Pfunc({1.rrand(5)}),
	);
	horrorpattern = Ppar([horrornotes, horrorcutoff_a, horrorcutoff_b, horror_pitchwheel], 1);

	partyaccomp = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\midinote, Pseq([
			45, 50, 48
		], inf),
		\legato, 1,
		\dur, Pseq([ 4, 1, 1 ] * (8 /*duration in beats*/ /(135 /*bpm*/ /60)), inf),
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
	);
	partymelody = Pbind(
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
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
	);
	partypattern = Ppar([partyaccomp, partymelody], 1);
	meditationchords = Pbind(
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
		\amp, 0.3,
		\dur, Pseq([5],inf),
		\s, Pkey(\dur),
		\a, 0.4,
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
	);

	meditationmelody = Pbind(
		\instrument, \flute,
		\freq, Pxrand(parser.asMidi("c5 eb5 g5 bb5 c6").midicps ++ [Rest(), Rest()], inf),
		\dur, Pbrown(lo:0.1,hi:1.0, step:0.125, length:inf),
		\a, Pkey(\dur)*0.95,
		\amp, Pseq([
			Pseq((((1..16)/16)*0.5), 1),
			Pbrown(lo:0.3,hi:0.6,step:0.1,length:inf)], inf),
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
	);

	mystery = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, ~yoshimidi_out,
		\chan, 0,
		\midinote, Pseq([Prand((10..20), 1), Prand((10..20), 1)], inf),
		\amp, Pbrown(70,100,1,inf),
		\dur, Prand((7..14), inf),
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
	);

	brainpattern1 = Pmono(
		\singer,
		\freq, Pfunc({(30+(~lastattentionvalue/2)).midicps}).trace,
		\vibrato, Pfunc({(~lastmeditationvalue/10)}).trace,
		\dur, 1,
		\amp, 1.0,
	);

	~horror = wrapInit.(~synth, horrorpattern, "F3", "P28",	0);
	~party = wrapInit.(~synth, partypattern, "F2", "P56", 82, 1);
	~meditation = Ptpar([0.0, meditationchords, 8*5.0, meditationmelody]);
	~mystery = mystery;
	~brainpattern = brainpattern1;

	SynthDef(\pad, {
		| out = 0, freq = 440, amp=0.5, gate=1, a = 0.1, s = 3, r = 1|
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
		Out.ar(bus:out, channelsArray:amp*env*Splay.ar(snd.tanh));
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

	SynthDef(\brainNoise, {

		| out = 0, rawval = 0, midi=60, rq=0.005, amp=0.01, atk=0.01, rel=0.25, spread=0.1 |

		var sig, env;

		sig = {BrownNoise.ar(0.25)}!2;

		sig = BPF.ar(sig, [ ((midi-spread)),
			(midi + (2*12)).midicps,
			((midi+spread) + (2*12)).midicps], rq, mul:1/rq.sqrt);

		sig = Splay.ar(sig);
		sig = DynKlank.ar(`[[rawval*8, rawval*10, rawval*11, rawval*13], nil, [1, 1, 1, 1]], sig);
		env = EnvGen.kr(Env.perc(atk,rel), doneAction:2);

		sig = Splay.ar(sig * env * amp);

		Out.ar(out, sig);

	}).add;


	SynthDef(\brainSine, {
		| out = 0, amp=0.01, rawval|
		Out.ar(out,
			Splay.ar(
				amp*SinOsc.ar([rawval*4.9],  0, 0.5)*EnvGen.ar(Env.linen(0.01, 0.2, 0.01), doneAction:2)));
	}).add;

	SynthDef(\singer, {
		| out=0, freq=440, amp=0.5, vibrato=6|
		var lfo, lfo2, lfo3, sig;
		lfo = SinOsc.kr(1/5, 0).range(250,1000);
		lfo2 = SinOsc.kr(1/5, 0).range(0.1,0.9);
		lfo3 = SinOsc.kr(vibrato).range(0.3, 1);
		sig = lfo3*RLPF.ar(in:VarSaw.ar(freq:Lag.ar(in:K2A.ar(freq), lagTime:0.3), iphase:0, width:lfo2, mul:amp), freq:lfo, rq:200/lfo);
		Out.ar(out, sig!2);
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

	~killnotes = {
		~synth.all_notes_off;
		~hplayer = nil;
		~mplayer = nil;
		~pplayer = nil;
		~mysplayer = nil;
		~brainplayer = nil;
		CmdPeriod.remove(~killnotes);
	};


	~synth = ScProphetRev2.new;
	~synth.connect;

	~event_type = \midi;

	~flags = IdentityDictionary.newFrom([
		\jam : false,
		\octaviate  : false,
		\secondvoice : false,
		\bass : false
	]);

	~melody_notes = [];
	~allowed_durs = [1/4, 1/8, 1/16]*4;

	melody = Pbind(
		\type, Pfunc({~event_type}),
		\midicmd, \noteOn,
		\midiout, ~synth.midi_out,
		\chan, 0,
		\instrument, \default,
		\midinote, Pfunc({
			|ev|
			if (~melody_notes.size == 0) {
				Rest()
			} /* else */
			{
				var note = parser.asMidi(~melody_notes.choose);
				if (~flags[\octaviate]) {
					note = note + ((1.rand2)*12);
				};
				note;
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
		\amp, Pbrown(0.5,0.8,0.125,inf),
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})
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
		\amp, Pbrown(0.5,0.8,0.125,inf),
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})

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
		\mykey, Pfunc({
			|ev|
			~osc_note_handler.(ev);
		})

	);

	~initpattern = wrapInit.(~synth, Ppar([melody,melody2,bass], 1), "F2", "P1", 0);
	Pdef(\notes, ~initpattern);
	CmdPeriod.add(~killnotes);
});

)

Synth(\bufplay, [\bufnum, b["clocks"].choose.bufnum, \speed, 1, \amp, 5.0]);
Synth(\bufplay, [\bufnum, b["grind"].choose.bufnum, \speed, 1, \amp, 5.0]);
Synth(\bufplay, [\bufnum, b["purr"].choose.bufnum, \speed, 1, \amp, 5.0]);

~killnotes.();
