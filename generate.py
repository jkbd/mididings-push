#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2019 Jakob Dübel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Color definitions
color_off = 0x00
color_medium_gray = 0x02
color_red = 0x05
color_soft_red = 0x06
color_green = 0x11
color_medium_green = 0x12
color_dark_green = 0x13

color_blue = 0x42
color_azur = 0x43
color_darkazur = 0x44
color_lila = 0x45

defined_scenes = [
    # First row
    {
        'name': "Panic",
        'note': "Send all-notes-off and sustain-off to all ports",
        'color': (color_red, color_soft_red),
        'patch': """
              [
                  Panic(bypass=False) >> [ Output('synth1', channel=1), Output('synth2', channel=1) ],
              ],
"""
    },
    {
        'name': "No patch",
        'note': "No routing and no presets configured.",
        'patch': """
              [
                  Discard(),
              ],
"""
    },
    {
        'name': "(Key1 -> Bob) + (Key2 -> Don)",
        'note': "Routing without presets",
        'patch': """
              [                         
                  PortFilter('keys1') >> ~Filter(SYSEX) >> Output('synth1', channel=1),
                  PortFilter('keys2') >> ~Filter(SYSEX) >> Output('synth2', channel=3, volume=127),
              ],
"""
    },
    {
        'name': "(Key1 -> Don) + (Key2 -> Bob)",
        'note': "Another routing without presets",
        'patch': """
              [                         
                  PortFilter('keys1') >> ~Filter(SYSEX) >> Output('synth2', channel=3, volume=127),
                  PortFilter('keys2') >> ~Filter(SYSEX) >> Output('synth1', channel=1),
              ],
"""
    },
    {
        'name': "Key1 -> (Bob + Don)",
        'note': "One keyboard plays many synths",
        'patch': """
              [                         
                  PortFilter('keys1') >> ~Filter(SYSEX) >> Output('synth1', channel=1),
                  PortFilter('keys1') >> ~Filter(SYSEX) >> Output('synth2', channel=3, volume=127),
              ],
"""
    },
    {
        'name': "Key2 -> (Bob + Don)",
        'note': "One keyboard plays many synths with defined presets",
        'patch': """
              [                         
                  PortFilter('keys1') >> ~Filter(SYSEX) >> Output('synth1', channel=1, program=(1, 1)),
                  PortFilter('keys1') >> ~Filter(SYSEX) >> Output('synth2', channel=3, program=(3, 2), volume=127),
              ],
"""
    },
]


def print_header():
    print("""#!/usr/bin/env python2
# -*- coding: utf-8 -*-
""")


def print_imports():
    print("""
from mididings import *
#from mididings.extra.osc import OSCInterface
#from mididings.extra.osc import SendOSC
#import liblo
""")


def print_config():
    print("""
config(
    backend='alsa',
    start_delay=0.5,
    initial_scene=1,
    
    in_ports = [
        ('push1in', '.*Ableton.*MIDI 2.*'),
        ('keys1', '.*Key1.*'),
        ('keys2', '.*Key2.*'),
    ],
    out_ports = [
        ('push1out', '.*Ableton.*MIDI 2.*'),
        ('synth1', '.*Bob.*'),
        ('synth2', '.*Don.*'),
    ],
)""")


def print_hooks():
    print("""
    # The default ports are 56418 and [56419]
hook(OSCInterface())
""")

def push1_char_map(char):
        
    m = {
        'ö': 12,
        'ü': 13,
        'ß': 14,
        'ä': 16,
        # ' ': 32,
        # '!': 33,
        # '"': 34,
        # '#': 35,
        # '$': 36,
        # '%': 37,
        # '&': 38,
        # "'": 39,
        # '(': 40,
        # ')': 41,
        # '*': 42,
        # '+': 43,
        # ',': 44,
        # '-': 45,
        # '.': 46,
        # '/': 47,
    }
    # From `0` to `~`
    if ord(char) >= 32 and ord(char) <= 126:
        return ord(char)
    else:
        if char in m.keys():
            return m[char]
        else:
            return 27;
      
    
def push1_display(line, text):
    """Return the sysex for the display text"""
    if line in [1, 2, 3, 4]:
        line += 23
    else:
        line = 24 # TODO: Raise error

    head = [0xF0, 0x47, 0x7F, 0x15, line, 0x00, 0x45, 0x00]    
    tail = 0xF7

    # Pad and trim the msg string so it is 68 characters long
    msg = text.ljust(68, ' ')[:68]    
    
    hexstr = "["
    for c in head:
        hexstr += "0x{:02x}, ".format(c)
    for c in msg:
        hexstr += "0x{:02x}, ".format(push1_char_map(c))
    hexstr += "0x{:02x}".format(tail)
    hexstr += "]"
    return hexstr

# The name is displayed in the first row.
# `i` is the index of the scene
# `note` is displayed in the third line
def print_scene(i, scene):
    print("""
    {0}: Scene("{1}",
""".format(i, scene['name']))

    print(scene['patch'])
    print("""             
             init_patch=[
""")

    # Display lines
    sysex = push1_display(1, "Mididings    {:3d}.{:17s}".format(i, scene['name']))
    print("                 SysEx('push1out', {0}),".format(sysex))
    sysex = push1_display(2, "")
    print("                 SysEx('push1out', {0}),".format(sysex))    
    sysex = push1_display(3, " "*17 + scene['note'])
    print("                 SysEx('push1out', {0}),".format(sysex))
    sysex = push1_display(4, "")
    print("                 SysEx('push1out', {0}),".format(sysex))

    # Light up pads
    for n in range(1, len(defined_scenes)+1):
        if n == i:
            if 'color' in defined_scenes[n-1]:
                color = defined_scenes[n-1]['color'][0]
            else:
                color = color_green
        else:
            if 'color' in defined_scenes[n-1]:
                color = defined_scenes[n-1]['color'][1]
            else:
                color = color_medium_gray
        if color != color_off:
            print("                 NoteOn('push1out', 1, {0}, {1}),".format(n+35, color))
        else:
            print("                 NoteOff('push1out', 1, {0}, {1}),".format(n+35, color))
            
    print("""
             ]),
""")
    
def print_scenes():
    i = 1
        
    print("""
scenes = {""")

    for s in defined_scenes:
        if 'color' in s:
            if (s['color'][0] != color_off):
                print_scene(i, s)
        else:
            print_scene(i, s)
        i += 1    
    
    print("""
}    
""")


def print_run():
    print("""
run(
    scenes = scenes,
    control = PortFilter('push1in') >> Filter(NOTEON) >> [
""")
    for n in range(1, len(defined_scenes)+1):
        print("        KeyFilter(notes=[{0}]) >> SceneSwitch(number={1}),".format(n+35, n))
    print("""
    ],
    pre = ~Filter(PROGRAM),
    post = None
)
""")

if __name__ == "__main__":
    print_header()
    print_imports()
    print_config()
    #print_hooks()
    print_scenes()
    print_run()
