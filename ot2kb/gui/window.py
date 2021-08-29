import typing

import PySimpleGUI as sg

from ot2kb import config


def initialise_window(cues: typing.Tuple):
    sg.theme(config.THEME)

    layout = [
        [
            sg.Text("oT (2) keyboard patch", font=(config.DEFAULT_FONT, 35)),
            sg.Button(
                button_text="PANIC",
                pad=(90, None),
                font=(config.DEFAULT_FONT, config.ELEMENT_FONT_SIZE),
            ),
        ],
        [
            sg.Text(
                "current cue:", font=(config.DEFAULT_FONT, config.ELEMENT_FONT_SIZE)
            ),
            sg.Spin(
                list(range(1, len(cues) + 1)),
                initial_value=1,
                font=(config.DEFAULT_FONT, config.ELEMENT_FONT_SIZE),
                size=(8, None),
                enable_events=True,
                key=config.CUE_KEY,
            ),
        ],
        [
            sg.Text("volume:", font=(config.DEFAULT_FONT, config.ELEMENT_FONT_SIZE)),
            sg.Slider(
                (0, 1),
                default_value=0.75,
                resolution=0.01,
                orientation="horizontal",
                size=(84, 35),
                enable_events=True,
                key=config.VOLUME_KEY,
            ),
        ],
        [
            sg.Text(
                "last received midi message:",
                font=(config.DEFAULT_FONT, config.ELEMENT_FONT_SIZE),
            ),
            sg.Text(
                "",
                font=(config.DEFAULT_FONT, config.ELEMENT_FONT_SIZE),
                key=config.MIDI_RECEIVE_KEY,
                background_color="white",
                text_color="black",
                size=(27, 1),
            ),
        ],
    ]

    # Create the window
    window = sg.Window(
        "oT(2)keyboard",
        layout,
        # size=(900, 700),
    )
    return window
