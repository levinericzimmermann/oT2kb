import time
import typing

import rtmidi
from rtmidi import midiconstants
from rtmidi import midiutil

import PySimpleGUI as sg

from ot2kb import config


class MidiChannel(int):
    def __init__(self, nth_channel: int):
        super().__init__()
        self._nth_channel = nth_channel
        self._is_busy = False
        self._note_in = None
        self._note_out = None
        self._midi_out = None
        self._start_time = time.time()
        self._occupation_time = 0
        self._release_time = 0

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    @property
    def occupation_time(self) -> int:
        return self._occupation_time

    @property
    def release_time(self) -> int:
        return self._release_time

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
        self._release_time = 0

    def release(self):
        if self._note_in:
            self._midi_out.send_message(
                [midiconstants.NOTE_OFF | int(self), self._note_out, 0]
            )
        self._note_in = None
        self._note_out = None
        self._is_busy = False
        self._occupation_time = 0
        self._release_time = time.time() - self._start_time
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
            formatted_message += ",".join(map(str, message[1:]))
        self._window[config.MIDI_RECEIVE_KEY].update(formatted_message)

    def update_cue(self, midi_note: int):
        spin = self._window[config.CUE_KEY]
        current_value = spin.get()
        if midi_note == config.PREVIOUS_CUE_MIDI_NOTE:
            new_value = current_value - 1
        else:
            new_value = current_value + 1

        if new_value > spin.Values[-1]:
            new_value = spin.Values[0]
        elif new_value < spin.Values[0]:
            new_value = spin.Values[-1]

        self._set_active_cue(new_value)
        spin.update(new_value)

    def get_midi_channel(self) -> int:
        occupation_times = tuple(
            map(lambda channel: channel.occupation_time, self._midi_channels)
        )
        minimal_occupation_time = min(occupation_times)
        # All channels are occupied: release the channel which has been occupied
        # the longest.
        if minimal_occupation_time > 0:
            self._midi_channels[occupation_times.index(minimal_occupation_time)]
        # There a one ore more than one free channels.
        # Take the free channel which has been released the longest.
        else:
            filtered_midi_channels = filter(
                lambda channel: channel.occupation_time == minimal_occupation_time,
                self._midi_channels,
            )
            return min(filtered_midi_channels, key=lambda channel: channel.release_time)

    def occupy_midi_channel(self, message: typing.List[int], message_type: int):
        """Send midi message to engine."""

        active_cue = self._get_active_cue()

        try:
            data = active_cue[message[1]]
        except KeyError:
            data = None

        if data is not None:
            midi_pitch, pitch_bend, engine_id = data
            engine = self._engines[engine_id]
            midi_channel = self.get_midi_channel()
            midi_channel.occupy(message[1], midi_pitch, engine.midi_out)
            engine.send_message(
                [
                    midiconstants.PITCH_BEND | midi_channel,
                    pitch_bend & 0x7F,
                    (pitch_bend >> 7) & 0x7F,
                ]
            )
            engine.send_message([message_type | midi_channel, midi_pitch, message[2]])

    def release_midi_channel(self, note: int):
        """Release midi note at respective engine."""

        for midi_channel in self._midi_channels:
            if midi_channel.note_in == note:
                midi_channel.release()

    def pass_message(self, message: typing.List[int], message_type: int):
        if message_type == midiconstants.NOTE_ON:
            # if midi note belongs to reserved midi notes for cue changes, update cue
            if message[1] in (config.NEXT_CUE_MIDI_NOTE, config.PREVIOUS_CUE_MIDI_NOTE):
                self.update_cue(message[1])
            else:
                self.occupy_midi_channel(message, message_type)
        elif message_type == midiconstants.NOTE_OFF:
            self.release_midi_channel(message[1])

        # ignore all other midi messages

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
