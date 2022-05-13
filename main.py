if __name__ == "__main__":
    import operator
    import logging
    import subprocess
    import time

    import PySimpleGUI as sg

    from ot2kb import cues
    from ot2kb import config
    from ot2kb import engines
    from ot2kb import io
    from ot2kb import gui

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    # start performance mode
    # subprocess.run("etc/performance_on.sh", shell=True)

    # start jack
    # subprocess.run("qjackctl -a ot2kb/etc/ot2kb.xml -s &", shell=True)
    time.sleep(0.5)

    ENGINES = engines.initialise_engines()
    CUES = cues.initialise_cues()

    def set_active_cue(nth_cue: int):
        active_cue = CUES[nth_cue - 1]
        used_engines = map(operator.itemgetter(2), active_cue.values())
        engine_indices = set(used_engines)
        [ENGINES[index].prepare() for index in engine_indices]
        globals()["ACTIVE_CUE"] = active_cue

    def get_active_cue():
        return globals()["ACTIVE_CUE"]

    set_active_cue(1)

    window = gui.initialise_window(CUES)
    midi_in = io.initialise_midi_in(window, get_active_cue, set_active_cue, ENGINES)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == config.CUE_KEY:
            set_active_cue(values[config.CUE_KEY])

        elif event == "PANIC":
            [engine.panic() for engine in ENGINES]

    # close program
    [engine.close() for engine in ENGINES]
    midi_in.close_port()
    del midi_in
    window.close()

    # subprocess.run("etc/performance_off.sh", shell=True)
