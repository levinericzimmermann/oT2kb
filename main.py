if __name__ == "__main__":
    import PySimpleGUI as sg

    from ot2kb import cues
    from ot2kb import config
    from ot2kb import engines
    from ot2kb import io
    from ot2kb import gui

    # start performance mode
    # subprocess.run("etc/performance_on.sh", shell=True)

    # start jack
    # subprocess.run("qjackctl -a jack/patchbay-aml.xml -s &", shell=True)
    # time.sleep(0.5)

    engines = engines.initialise_engines()
    cues = cues.initialise_cues()

    ACTIVE_CUE = cues[0]

    def set_active_cue(nth_cue: int):
        globals()["ACTIVE_CUE"] = cues[nth_cue - 1]

    def get_active_cue():
        return globals()["ACTIVE_CUE"]

    window = gui.initialise_window(cues)
    midi_in = io.initialise_midi_in(window, get_active_cue, set_active_cue, engines)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == config.CUE_KEY:
            set_active_cue(values[config.CUE_KEY])

        elif event == "PANIC":
            [engine.panic() for engine in engines]

    # close program
    [engine.close() for engine in engines]
    midi_in.close_port()
    del midi_in
    window.close()

    # subprocess.run("etc/performance_off.sh", shell=True)
