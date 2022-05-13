import logging
import subprocess
import time

from . import base


class FaustEngine(base.Engine):
    def __init__(self, name: str, *args, **kwargs):
        faust_engine_command = [
            f"bin/{name}",
        ]
        # start faust binary file
        self._faust_engine_process = subprocess.Popen(faust_engine_command)

        # wait for faust process to start
        time.sleep(1)

        super().__init__(*args, **kwargs)
        logging.info(f"Used port for {name}: {self._port_name}.")

    def close(self):
        self._faust_engine_process.terminate()
        super().close()
