from ot2kb import config

from . import faust


class Multiguitar(faust.FaustEngine):
    def __init__(self):
        super().__init__(
            "multiguitar",
            port=config.engines.MULTIGUITAR_PORT,
            port_name=config.engines.MULTIGUITAR_PORT_NAME,
        )
