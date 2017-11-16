// yoshimi channel 1: 35. Fantasy, patch: impossible dream 4
//                    14. Fantasy, patch: glass voices
// yoshimi channel 2: 110. Will Godfrey companion, patch Muffled Bells
//                    110. Will Godfrey companion, patch Muted Synth
//                    100. Mysterious bank, patch UFO invasion
//                    115. chip bank, patch chips thing
// yoshimi channel 3: 90. synth bank, patch resonance synth
(
s.waitForBoot({
	var mo;
	var mo2;
	var notes_per_chan = (
		0 : [],
		1 : [],
		2 : [],
		3 : [],
		4 : [],
		5 : [],
		6 : [],
		7 : [],
		8 : [],
		9 : [],
		10 : [],
		11 : [],
		12 : [],
		13 : [],
		14 : [],
		15 : [],
	);

	MIDIdef.freeAll;
	MIDIClient.free;
	MIDIClient.init;
	MIDIClient.destinations.postln;
	MIDIIn.connectAll;

	mo = MIDIOut.newByName("yoshimi", "input").latency_(Server.default.latency);
	mo2 = MIDIOut.newByName("LinuxSampler", "Port 0").latency_(Server.default.latency);

	n = NetAddr("127.0.0.1"); // local machine; port left unspecified

	OSCdef(\startFluit).free; // free old OSCdefs that may still be around
	OSCdef(\startFluit, {
		| msg, time, addr, port |
		("sfeer " ++ msg[1]).postln;
		if (notes_per_chan[0] != [], {mo.noteOff(chan:0, note:notes_per_chan[0])}, {});
		mo.noteOn(chan:0, note:(10..30).choose, veloc:(80..110).choose);
	}, '/fluit', n);

	OSCdef(\start8iaho).free;
	OSCdef(\start8iaho, {
		| msg, time, addr, port |
		var pat, pat2;
		("8iaho " ++ msg[1]).postln;
		if (notes_per_chan[1] != [], {mo.noteOff(chan:1, note:notes_per_chan[1])}, {});

		pat = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 1,
			\degree, Prout({
				var sequence = [0];
				var ranlen = 3.rrand(6);
				var ranrepeat = 1.rrand(3);
				var octave = (-1).rrand(1);
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + (1.rrand(3)));
				});
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + ((-1).rrand(-3)));
				});

				ranrepeat.do({
					0.7.coin.if({
						sequence = sequence ++ sequence;
					}, {
						sequence = sequence.mirror;
					});
				});

				sequence.do({
					| deg |
					(deg + (octave*12)).yield;
				});
			}),

			\dur, Prout({
				| event |
				// introduce some (subtle) timing irregularities without going out of sync
				loop {
					var durs = 1.dup(4);
					durs = durs.collect({
						| val |
						val + (-0.05).rrand(0.05)
					});
					durs = (durs.normalizeSum/(0.5.rrand(2)));
					durs.do({ | dur |
						dur.yield;
					});
				}
			}),
			\amp, Pexprand(0.4, 0.6, inf)
		);
		pat.play;
		pat2 = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 2,
			\degree, Prand([20,21,19,18]+12, 20),
			\dur, 0.1
		);
		pat2.play;

	}, '/8iaho', n);

	OSCdef(\startSfeer).free; // free old OSCdefs that may still be around
	OSCdef(\startSfeer, {
		| msg, time, addr, port |
		("sfeer " ++ msg[1]).postln;
		if (notes_per_chan[0] != [], {mo.noteOff(chan:0, note:notes_per_chan[0])}, {});
		mo.noteOn(chan:0, note:(10..30).choose, veloc:(80..110).choose);
	}, '/sfeer', n);

	OSCdef(\startBel).free;
	OSCdef(\startBel, {
		| msg, time, addr, port |
		var pat, pat2;
		("bel " ++ msg[1]).postln;
		if (notes_per_chan[1] != [], {mo.noteOff(chan:1, note:notes_per_chan[1])}, {});

		pat = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 1,
			\degree, Prout({
				var sequence = [0];
				var ranlen = 3.rrand(6);
				var ranrepeat = 1.rrand(3);
				var octave = (-1).rrand(1);
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + (1.rrand(3)));
				});
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + ((-1).rrand(-3)));
				});

				ranrepeat.do({
					0.7.coin.if({
						sequence = sequence ++ sequence;
					}, {
						sequence = sequence.mirror;
					});
				});

				sequence.do({
					| deg |
					(deg + (octave*12)).yield;
				});
			}),

			\dur, Prout({
				| event |
				// introduce some (subtle) timing irregularities without going out of sync
				loop {
					var durs = 1.dup(4);
					durs = durs.collect({
						| val |
						val + (-0.05).rrand(0.05)
					});
					durs = (durs.normalizeSum/(0.5.rrand(2)));
					durs.do({ | dur |
						dur.yield;
					});
				}
			}),
			\amp, Pexprand(0.4, 0.6, inf)
		);
		pat.play;
		pat2 = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 2,
			\degree, Prand([20,21,19,18]+12, 20),
			\dur, 0.1
		);
		pat2.play;

	}, '/bel', n);

	OSCdef(\startRobot).free; // free old OSCdefs that may still be around
	OSCdef(\startRobot, {
		| msg, time, addr, port |
		var pat;
		("robot " ++ msg[1]).postln;
		if (notes_per_chan[2] != [], {mo.noteOff(chan:2, note:notes_per_chan[2])}, {});
		pat = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 1,
			\degree, Prout({
				var sequence = [0];
				var ranlen = 3.rrand(4);
				var ranrepeat = 1.rrand(2);
				var octave = (-1).rrand(1);
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + (1.rrand(5)));
				});
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + ((-1).rrand(-5)));
				});

				ranrepeat.do({
					0.7.coin.if({
						sequence = sequence ++ sequence;
					}, {
						sequence = sequence.mirror;
					});
				});

				sequence.do({
					| deg |
					(deg + (octave*12)).yield;
				});
			}),

			\dur, Prout({
				| event |
				// introduce some (subtle) timing irregularities without going out of sync
				loop {
					var durs = 1.dup(4);
					durs = durs.collect({
						| val |
						val + (-0.01).rrand(0.01)
					});
					durs = (durs.normalizeSum/(0.5.rrand(2)));
					durs.do({ | dur |
						dur.yield;
					});
				}
			}),
			\amp, Pexprand(0.4, 0.6, inf)
		);
		pat.play;
	}, '/robot', n);

	OSCdef(\startDrum).free; // free old OSCdefs that may still be around
	OSCdef(\startDrum, {
		| msg, time, addr, port |
		var pat;
		("drum " ++ msg[1]).postln;
		if (notes_per_chan[3] != [], {mo.noteOff(chan:3, note:notes_per_chan[3])}, {});
		pat = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo2,
			\chan, 0,
			\midinote, Pbrown(35,64,1,30),
			\dur, Pfunc({0.1.rrand(0.2)}),
			\amp, Pexprand(0.9,1.0,inf)
		);
		pat.play;
	}, '/drum', n);

	OSCdef(\startNoise).free; // free old OSCdefs that may still be around
	OSCdef(\startNoise, {
		| msg, time, addr, port |
		var pat;
		("noise " ++ msg[1]).postln;
		if (notes_per_chan[4] != [], {mo.noteOff(chan:4, note:notes_per_chan[4])}, {});
		pat = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 1,
			\degree, Prout({
				var sequence = [0];
				var ranlen = 3.rrand(6);
				var ranrepeat = 1.rrand(3);
				var octave = (-1).rrand(1);
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + (1.rrand(3)));
				});
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + ((-1).rrand(-3)));
				});

				ranrepeat.do({
					0.7.coin.if({
						sequence = sequence ++ sequence;
					}, {
						sequence = sequence.mirror;
					});
				});

				sequence.do({
					| deg |
					(deg + (octave*12)).yield;
				});
			}),

			\dur, Prout({
				| event |
				// introduce some (subtle) timing irregularities without going out of sync
				loop {
					var durs = 1.dup(4);
					durs = durs.collect({
						| val |
						val + (-0.05).rrand(0.05)
					});
					durs = (durs.normalizeSum/(0.5.rrand(2)));
					durs.do({ | dur |
						dur.yield;
					});
				}
			}),
			\amp, Pexprand(0.4, 0.6, inf)
		);
		pat.play;
	}, '/noise', n);

	OSCdef(\startUfo).free; // free old OSCdefs that may still be around
	OSCdef(\startUfo, {
		| msg, time, addr, port |
		var pat;
		("ufo " ++ msg[1]).postln;
		if (notes_per_chan[5] != [], {mo.noteOff(chan:5, note:notes_per_chan[5])}, {});
		pat = Pbind(
			\type, \midi,
			\midicmd, \noteOn,
			\midiout, mo,
			\chan, 1,
			\degree, Prout({
				var sequence = [0];
				var ranlen = 3.rrand(6);
				var ranrepeat = 1.rrand(3);
				var octave = (-1).rrand(1);
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + (1.rrand(3)));
				});
				ranlen.do({
					| i |
					sequence = sequence ++ (sequence[sequence.size-1] + ((-1).rrand(-3)));
				});

				ranrepeat.do({
					0.7.coin.if({
						sequence = sequence ++ sequence;
					}, {
						sequence = sequence.mirror;
					});
				});

				sequence.do({
					| deg |
					(deg + (octave*12)).yield;
				});
			}),

			\dur, Prout({
				| event |
				// introduce some (subtle) timing irregularities without going out of sync
				loop {
					var durs = 1.dup(4);
					durs = durs.collect({
						| val |
						val + (-0.05).rrand(0.05)
					});
					durs = (durs.normalizeSum/(0.5.rrand(2)));
					durs.do({ | dur |
						dur.yield;
					});
				}
			}),
			\amp, Pexprand(0.4, 0.6, inf)
		);
		pat.play;
	}, '/ufo', n);
});
)

/* test patterns */

(
//var pat = Pbind(
//
//);
//pat.play;
s.waitForBoot({
	var mo2;
	var pat;
	/*
	MIDIdef.freeAll;
	MIDIClient.free;
	MIDIClient.init;
	MIDIClient.destinations.postln;
	MIDIIn.connectAll;
	*/
	mo2 = MIDIOut.newByName("LinuxSampler", "Port 0").latency_(Server.default.latency);
	pat = Pbind(
		\type, \midi,
		\midicmd, \noteOn,
		\midiout, mo2,
		\chan, 0,
		\midinote, Pbrown(35,64,1,30),
		\dur, Pfunc({0.1.rrand(0.2)}),
		\amp, Pexprand(0.9,1.0,inf)
	);
	pat.play;
});

)
