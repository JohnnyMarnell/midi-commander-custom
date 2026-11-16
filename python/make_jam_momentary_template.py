#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the "ten momentary switches" template, python/templates/Jam_Momentary.csv.

A deliberately dumb configuration: no banks, no modes, no preset navigation,
no latching, no state. Each of the ten switches sends one CC as it goes down
and the same CC as it comes up, 127 then 0, on one channel.

The eight lettered and numbered switches do that with an ordinary CC command
whose Toggle is N. The two bank switches do it because `Bank_Switch_Mode` is
`MIDI only`, which stops them changing bank at all, and `Momentary_Hold` on
their short press, which sends the list as the switch goes down and lets it go
as it comes up (firmware 1.42 or later).

Every bank holds the same ten commands, so the pedal behaves identically
whatever bank it is on and nothing a stray press does can change what a switch
sends. `Edit_Lock` keeps the two bank switches held together from opening the
on-pedal editor, which a momentary pair would otherwise reach under a foot.

    python3 python/make_jam_momentary_template.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lib.flashLayout import NUM_BANKS  # noqa: E402
from lib.templateMaker import full_range_pedals, global_settings, write_template  # noqa: E402
from make_demo_config import Demo  # noqa: E402

OUT = os.path.join(HERE, "templates", "Jam_Momentary.csv")

# One channel of its own, so no CC can collide with the rig's other surfaces.
CHANNEL = "3"

# The eight switches, laid out as on the pedal: 1 2 3 4 on top, A B C D below.
# The label is what the display shows, and the CC is what MIDI Learn will see.
SWITCHES = (
    ("1", "30"), ("2", "31"), ("3", "32"), ("4", "33"),
    ("A", "34"), ("B", "35"), ("C", "36"), ("D", "37"),
)

# The two the factory firmware keeps for navigation. Here they are switches.
BANK_DOWN_CC = "38"
BANK_UP_CC = "39"

# The expression jacks, left on the factory CC numbers.
EXP1_CC = "11"
EXP2_CC = "4"


def build():
    d = Demo()
    names = {}

    for bank in range(NUM_BANKS):
        names[bank] = ("JAM", "MOMENT")
        for btn, cc in SWITCHES:
            # d.cc defaults are on 127, off 0, Toggle N: momentary already.
            d.cc(bank, btn, cc, cc, ch=CHANNEL)

    # The bank switches, short press only: a long press list would claim the
    # hold that Momentary_Hold needs.
    for switch, cc in (("Down", BANK_DOWN_CC), ("Up", BANK_UP_CC)):
        d.bank_switch(switch, "Short", label=cc, CommandType="CC",
                      **{"Channel_(PC/CC/Note/PB)": CHANNEL,
                         "Number_(PC/CC/Note)": cc,
                         "OnValue_(CC/PB)": "127",
                         "OffValue_(CC)": "0",
                         "Toggle_(CC/PB/Note)": "N"})
        frame = d.bank_switch_frame
        mask = (frame["Switch"].astype(str) == switch) & (frame["Press"].astype(str) == "Short")
        frame.loc[mask, "Momentary_Hold"] = "Y"

    full_range_pedals(d)

    settings = global_settings("Jam Momentary", CHANNEL, EXP1_CC, EXP2_CC, extra=(
        ("Bank_Switch_Mode", "MIDI only"),   # the bank switches never change bank
        ("Global_Channel", CHANNEL),         # everything on one channel, pedals included
        ("Edit_Lock", "Y"),                  # no on-pedal editor under a foot
        ("Remember_State", "N"),             # nothing carried across a power cycle
        ("Boot_Banner", "Off"),
    ))
    return d, names, settings


def main() -> int:
    d, names, settings = build()
    return write_template(OUT, d, names, settings, os.path.basename(__file__))


if __name__ == "__main__":
    sys.exit(main())
