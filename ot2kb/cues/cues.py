import os
import json
import typing

import frozendict
import natsort

from ot2kb import config


class Cue(frozendict.frozendict):
    @staticmethod
    def parse_json(path: str):
        with open(path, "r") as f:
            data = json.load(f)

        data = {int(key): value for key, value in data.items()}
        return data


def _initialise_cue(path: str) -> Cue:
    data = Cue.parse_json(path)
    return Cue(data)


def initialise_cues() -> typing.Tuple[Cue, ...]:
    cues = []
    for path in natsort.natsorted(os.listdir(config.CUES_PATH)):
        cue = _initialise_cue(f"{config.CUES_PATH}/{path}")
        cues.append(cue)
    return tuple(cues)
