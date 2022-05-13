import abc
import time
import typing

from rtmidi import midiutil
from rtmidi import midiconstants

from ot2kb import config


class AbstractEngine(abc.ABC):
    @property
    @abc.abstractmethod
    def midi_out(self):
        raise NotImplementedError

    @abc.abstractmethod
    def send_message(self, message: typing.List[int]):
        raise NotImplementedError

    @abc.abstractmethod
    def panic(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError

    def prepare(self):
        # potential preperations
        pass


class Engine(AbstractEngine):
    def __init__(
        self, port: typing.Optional[str] = None, port_name: typing.Optional[str] = None
    ):
        if port or port_name:
            use_virtual = False
        else:
            use_virtual = True

        midi_out, port_name = midiutil.open_midioutput(
            api=config.API, use_virtual=use_virtual, port=port, port_name=port_name
        )
        self._midi_out = midi_out
        self._port_name = port_name

    @property
    def midi_out(self):
        return self._midi_out

    def send_message(self, message: typing.List[int]):
        self._midi_out.send_message(message)

    def panic(self):
        for channel in range(16):
            self._midi_out.send_message(
                [midiconstants.CONTROL_CHANGE | channel, midiconstants.ALL_SOUND_OFF, 0]
            )
            self._midi_out.send_message(
                [
                    midiconstants.CONTROL_CHANGE | channel,
                    midiconstants.RESET_ALL_CONTROLLERS,
                    0,
                ]
            )
            time.sleep(0.05)

        time.sleep(0.1)

    def close(self):
        self._midi_out.close_port()
        del self._midi_out
        del self
