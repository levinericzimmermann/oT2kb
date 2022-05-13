import subprocess
import time
import typing

from rtmidi import midiconstants

from ot2kb import config

from . import base


class SharedPianoteqEngine(base.Engine):
    def __init__(self, port: str = config.PIANOTEQ_PORT0, headless: bool = True):
        pianoteq_command = [
            "bin/pianoteq",
            # keyboard / velocity fxp
            # doesn't seem to work?
            # "--fxp",
            # "standard-velocity.mfxp",
            "--fxp",
            "oT2p.fxp",
            # set midimapping
            # "--midimapping",
            # "minimal",
            # increase performance
            "--multicore",
            "max",
        ]

        if headless:
            pianoteq_command.append("--headless")

        # start pianoteq
        self._pianoteq_process = subprocess.Popen(pianoteq_command)
        self._last_control_number = None
        self._is_closed = False

        # wait for pianoteq process to start
        time.sleep(1)

        super().__init__(port=port)

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    def spawn_child(self, control_number: int) -> "PianoteqEngineChild":
        return PianoteqEngineChild(self, control_number)

    def close(self):
        if not self.is_closed:
            self._pianoteq_process.terminate()
            super().close()
            self._is_closed = True


class PianoteqEngineChild(base.AbstractEngine):
    def __init__(self, parent: SharedPianoteqEngine, control_number: int):
        self._parent = parent
        self._control_number = control_number

    @property
    def control_number(self) -> int:
        return self._control_number

    @property
    def midi_out(self):
        return self._parent.midi_out

    def send_message(self, message: typing.List[int]):
        self._parent.send_message(message)

    def close(self):
        self._parent.close()

    def panic(self):
        self._parent.panic()

    def prepare(self):
        if self._parent._last_control_number != self.control_number:
            self.send_message(
                [
                    midiconstants.CONTROL_CHANGE,
                    self.control_number & 0x7F,
                    127 & 0x7F,
                ]
            )
            self._parent._last_control_number = self.control_number
