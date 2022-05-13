# oT2kb

Keyboard patch for [ohne Titel (2)](https://github.com/levinericzimmermann/ot2).


## tech setup

### internal mapping from engine indices to engines

This mapping is defined in `ot2kb/io/__init__.py`.

- 0: piano, -> for chords
- 1: tremolo, -> for tremolo AND right hand cengkok
- 2: bell, -> for the-third-way
- 3: multiguitar, -> for left hand cengkok AND left hand river
- 4: oT2-river-left-hand, -> for river left hand
- 5: oT2-river-right-hand, -> for river right hand
- 6: fm-synth -> for river right hand

### pianoteq patch midi mapping: cc to engine

This data is saved in midi mapping file "oT2_mapping.ptm" (in ot2kb/etc) and in "ot2kb/config/engines.py".

- 1 -> piano (for chords)
- 2 -> bells (for the-third-way)
- 3 -> oT2-river-left-hand
- 4 -> oT2-river-right-hand
