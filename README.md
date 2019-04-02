# mididings-push
Use a Push 1 controller to operate Mididings.

## Idea

[Mididings](http://das.nasophon.de/mididings/) is a tool to switch
between scenes of MIDI routing and preset configurations. This is
useful if you would like to use a single keyboard with multiple
hardware synthesizers.

This project enables you to switch Mididings scenes with a Ableton
Push 1 controller instead of using up- and down-arrows on a
PC-keyboard. It also provides you with feedback: The current scene is
highlighted and its name is shown in the display.

## Prerequisites

* A Linux based operating system.
* Python 2 for Mididings and Python 3 for the code generation.

## How it works

When switching a scene in Mididings the feedback to the controller is
plain MIDI events. Adding 64 Note-On or -Off events by hand for each
of the pads would be painstaking. So we simply use a programming
language to print the repetitive statements of a valid Mididings
configuration file.

### Adopt the generation template to your needs

Change the `generate.py` file. Take care of indention.

* Adapt the `print_config()` function to use your ports. Compare the
  port names of e.g. `aseqdump -l`.

* Change the scene patches in the `defined_scenes` list to your needs.

### Generate configuration

```
> make
python3 generate.py > config.py
```

### Start Mididings

```
> mididings -f config.py
...
switching to scene 1: ...
```
