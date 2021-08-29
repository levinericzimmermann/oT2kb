import time
import typing

import rtmidi
from rtmidi import midiconstants
from rtmidi import midiutil

import PySimpleGUI as sg

from ot2kb import config


class MidiChannel(int):
    def __init__(self, value: int):
        super().__init__()
        self._is_busy = False
        self._note_in = None
        self._note_out = None
        self._midi_out = None
        self._start_time = time.time()
        self._occupation_time = 0

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    @property
    def occupation_time(self) -> int:
        return self._occupation_time

    @property
    def note_in(self) -> typing.Optional[int]:
        return self._note_in

    def occupy(self, note_in: int, note_out: int, midi_out):
        if self.is_busy:
            self.release()
        self._note_in = note_in
        self._note_out = note_out
        self._is_busy = True
        self._occupation_time = time.time() - self._start_time
        self._midi_out = midi_out

    def release(self):
        if self._note_in:
            self._midi_out.send_message(
                [midiconstants.NOTE_OFF | int(self), self._note_out, 0]
            )
        self._note_in = None
        self._note_out = None
        self._is_busy = False
        self._occupation_time = 0
        self._midi_out = None


class MidiInputHandler(object):
    message_type_to_text = {
        midiconstants.NOTE_ON: "NOTE ON",
        midiconstants.NOTE_OFF: "NOTE OFF",
        midiconstants.PITCH_BEND: "PITCH BEND",
        midiconstants.CONTROLLER_CHANGE: "CONTROLLER CHANGE",
        midiconstants.PROGRAM_CHANGE: "PROGRAM CHANGE",
    }

    def __init__(
        self,
        port: str,
        window: sg.Window,
        get_active_cue: typing.Callable,
        set_active_cue: typing.Callable,
        engines,
    ):
        self.port = port
        self._midi_channels = tuple(
            MidiChannel(nth_channel) for nth_channel in range(16)
        )
        self._wallclock = time.time()
        self._window = window
        self._get_active_cue = get_active_cue
        self._set_active_cue = set_active_cue
        self._engines = engines

    @staticmethod
    def get_message_type(message: typing.List[int]) -> typing.Optional[int]:
        return message[0] & 0xF0

    def update_monitor(self, message: typing.List[int], message_type: int):
        try:
            message_type_as_text = self.message_type_to_text[message_type]
        except KeyError:
            message_type_as_text = "Unknown"
        formatted_message = "{}, ".format(message_type_as_text)
        if message_type in (midiconstants.NOTE_ON, midiconstants.NOTE_OFF):
            formatted_message += "pitch: {}, vel: {}".format(*message[1:])
        else:
            formatted_message += "{}, {}".format(*message[1:])
        self._window[config.MIDI_RECEIVE_KEY].update(formatted_message)

    def update_cue(self):
        pass

    def get_midi_channel(self) -> int:
        return min(self._midi_channels, key=lambda channel: channel.occupation_time)

    def release_midi_channel(self, note: int):
        for midi_channel in self._midi_channels:
            if midi_channel.note_in == note:
                midi_channel.release()

    def pass_message(self, message: typing.List[int], message_type: int):
        if message_type == midiconstants.NOTE_ON:
            active_cue = self._get_active_cue()
            try:
                data = active_cue[message[1]]
            except KeyError:
                data = None

            if data is not None:
                midi_pitch, pitch_bend, engine_id = data
                engine = self._engines[engine_id]
                midi_channel = self.get_midi_channel()
                midi_channel.occupy(message[1], midi_pitch, engine._midi_out)
                engine.send_message(
                    [
                        midiconstants.PITCH_BEND | midi_channel,
                        pitch_bend & 0x7F,
                        (pitch_bend >> 7) & 0x7F,
                    ]
                )
                engine.send_message(
                    [message_type | midi_channel, midi_pitch, message[2]]
                )
        elif message_type == midiconstants.NOTE_OFF:
            self.release_midi_channel(message[1])

    def __call__(self, event, _: typing.Any = None):
        message, deltatime = event
        self._wallclock += deltatime
        message_type = MidiInputHandler.get_message_type(message)
        self.pass_message(message, message_type)
        self.update_monitor(message, message_type)


def initialise_midi_in(
    window: sg.Window,
    get_active_cue: typing.Callable,
    set_active_cue: typing.Callable,
    engines,
) -> typing.Tuple[rtmidi.MidiIn, rtmidi.MidiOut]:
    midi_in, port_name = midiutil.open_midiinput(api=config.API, use_virtual=True)
    midi_input_handler = MidiInputHandler(
        port_name, window, get_active_cue, set_active_cue, engines
    )
    midi_in.set_callback(midi_input_handler)
    return midi_in
