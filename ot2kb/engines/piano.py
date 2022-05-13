import subprocess

from ot2kb import config

from . import base


class Pianoteq(base.Engine):
    def __init__(self, headless: bool = True):
        super().__init__(port=config.PIANOTEQ_PORT)
        pianoteq_command = [
            "bin/pianoteq",
            # keyboard / velocity fxp
            "--fxp",
            "standard-velocity.mfxp",
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

    def close(self):
        self._pianoteq_process.terminate()
        super().close()
