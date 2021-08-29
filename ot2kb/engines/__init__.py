def initialise_engines() -> tuple:
    from . import pianoteq

    return (pianoteq.Pianoteq(),)
