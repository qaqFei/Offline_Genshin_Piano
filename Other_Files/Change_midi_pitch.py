from sys import argv
from ctypes import windll

from mido import MidiFile,Message

if len(argv) < 4:
    print("Change_midi_pitch <Input_file> <Output_file> <dpitch>")
    windll.kernel32.ExitProcess(1)

try:
    dpitch = int(argv[3])
    mid_obj = MidiFile(argv[1])
    for track in mid_obj.tracks:
        for msg in track:
            try:
                if type(msg) == Message:
                    msg.note += dpitch
            except AttributeError:
                pass
    mid_obj.save(argv[2])
except Exception as e:
    print(f"error: {e}")