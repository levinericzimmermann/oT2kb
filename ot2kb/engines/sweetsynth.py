from ot2kb import config

from . import faust


class Sweetsynth(faust.FaustEngine):
    def __init__(self):
        super().__init__(
            "sweetsynth",
            port=config.engines.SWEETSYNTH_PORT,
            port_name=config.engines.SWEETSYNTH_PORT_NAME,
        )
