from sys import argv
from os import _exit
from json import loads

from mido import MidiFile,MidiTrack,MetaMessage,Message,second2tick

if len(argv) < 3:
    print("YChartx_To_Midi <input_file> <output_file>")
    _exit(0)

notes = {84:1,86:2,88:3,89:4,91:5,93:6,95:7,
         72:8,74:9,76:10,77:11,79:12,81:13,83:14,
         60:15,62:16,64:17,65:18,67:19,69:20,71:21}
notes = {value:key for key,value in notes.items()}

try:
    with open(argv[1],"r",encoding="utf-8") as f:
        ychartx = loads(f.read())
    match ychartx["meta"]["version"]:
        case "1.0.0" | "1.0.1":
            ychartx["data"].sort(key=lambda x:x["time"])
            mid_obj = MidiFile()
            main_track = MidiTrack()
            main_track_tempo = 120000
            main_track.append(
                MetaMessage("set_tempo",tempo=main_track_tempo,time=0)
            )
            for index,note in enumerate(ychartx["data"]):
                if index != 0:
                    t = note["time"] - ychartx["data"][index-1]["time"]
                else:
                    t = note["time"]
                main_track.append(
                    Message("note_on",note=notes[note["note"]] if ychartx["meta"]["version"] == "1.0.0" else note["real_note"],velocity=127,time=second2tick(t,480,main_track_tempo))
                )
            main_track.append(
                Message("note_off",note=notes[note["note"]] if ychartx["meta"]["version"] == "1.0.0" else note["real_note"],time=second2tick(1.5,480,main_track_tempo))
            )
            mid_obj.tracks.append(main_track)
            mid_obj.save(argv[2])
        case _:
            raise Exception("Unknow ychartx version.")
except (Exception,KeyboardInterrupt) as e:
    print(f"error: {e}")