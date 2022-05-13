from ot2kb import config

from . import faust


class Tremolo(faust.FaustEngine):
    def __init__(self):
        super().__init__(
            "tremolo",
            port=config.engines.TREMOLO_PORT,
            port_name=config.engines.TREMOLO_PORT_NAME,
        )
