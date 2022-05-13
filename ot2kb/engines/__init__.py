def initialise_engines() -> tuple:
    from ot2kb import config

    from . import multiguitar
    from . import pianoteq
    from . import tremolo
    from . import sweetsynth

    shared_pianoteq_engine0 = pianoteq.SharedPianoteqEngine(headless=False)
    shared_pianoteq_engine1 = pianoteq.SharedPianoteqEngine(
        headless=False, port=config.PIANOTEQ_PORT1
    )

    piano = shared_pianoteq_engine0.spawn_child(
        config.engines.PIANOTEQ_INSTRUMENT_TO_MIDI_CONTROL_NUMBER["piano-chords"]
    )
    bells = shared_pianoteq_engine0.spawn_child(
        config.engines.PIANOTEQ_INSTRUMENT_TO_MIDI_CONTROL_NUMBER["bells"]
    )
    left_hand_river = shared_pianoteq_engine0.spawn_child(
        config.engines.PIANOTEQ_INSTRUMENT_TO_MIDI_CONTROL_NUMBER["river-left-hand"]
    )
    right_hand_river = shared_pianoteq_engine1.spawn_child(
        config.engines.PIANOTEQ_INSTRUMENT_TO_MIDI_CONTROL_NUMBER["river-right-hand"]
    )

    return (
        piano,
        tremolo.Tremolo(),
        bells,
        multiguitar.Multiguitar(),
        left_hand_river,
        right_hand_river,
        sweetsynth.Sweetsynth(),
    )
