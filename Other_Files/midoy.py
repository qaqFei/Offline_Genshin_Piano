from sys import argv
from ctypes import windll
from json import dumps
from time import time

from mido import *

if len(argv) < 3:
    print("midoy <input> <output>")
    windll.kernel32.ExitProcess(1)

notes = {84:1,86:2,88:3,89:4,91:5,93:6,95:7,
         72:8,74:9,76:10,77:11,79:12,81:13,83:14,
         60:15,62:16,64:17,65:18,67:19,69:20,71:21}
notes_keys = list(notes.keys())
notes_values = list(notes.values())

def MidiNote_ToYChartNote(note:int) -> int:
    notes_qz = []
    can_out_range = 0
    for n in notes:
        notes_qz.append(abs(n-note))
    reslut = notes_values[notes_qz.index(min(notes_qz))]
    if reslut == 1:
        if note < notes_keys[0]-can_out_range:
            return None
    elif reslut == 21:
        if note > notes_keys[-1]+can_out_range:
            return None
    return reslut

try:
    #mid_obj = MidiFile(argv[1])   #ychartx v1.0.0
    #output_tracks = []
    #for midi_track in mid_obj.tracks:
    #    midi_track:MidiTrack
    #    this_track = {"name":None,"data":[]}
    #    this_track_notes = {}
    #    this_track_notes_nooff = []
    #    msg_time = 0.0
    #    for midi_msg in midi_track:
    #        midi_msg:Message|MetaMessage
    #        midi_dict_msg = midi_msg.dict()
    #        msg_time += midi_dict_msg["time"]
    #        if type(midi_msg) == MetaMessage:
    #            if midi_dict_msg["type"] == "set_tempo":
    #                midi_track_tempo = midi_dict_msg["tempo"]
    #        elif type(midi_msg) == Message:
    #            if midi_dict_msg["type"] == "note_on":
    #                this_note = MidiNote_ToYChartNote(midi_dict_msg["note"])
    #                if this_note is not None:
    #                    this_track_notes.update({this_note:msg_time})
    #                    this_track_notes_nooff.append([this_note,msg_time])
    #            elif midi_dict_msg["type"] == "note_off":
    #                this_note = MidiNote_ToYChartNote(midi_dict_msg["note"])
    #                if this_note is not None:
    #                    if this_note in this_track_notes:
    #                        on_time = this_track_notes[this_note]
    #                        this_track_notes_nooff.remove([this_note,on_time])
    #                        del this_track_notes[this_note]
    #                    this_track["data"].append({"time":tick2second(msg_time,mid_obj.ticks_per_beat,midi_track_tempo),"note":this_note})
    #    for note in this_track_notes_nooff:
    #        this_track["data"].append({"time":tick2second(note[1],mid_obj.ticks_per_beat,midi_track_tempo),"note":note[0]})
    #    output_tracks.append(this_track)
    #output = {"meta":{
    #    "version":"1.0.0",
    #    "title":"Unknow",
    #    "create_time":time(),
    #    "from":"MIDI",
    #    "author":"Unknow",
    #    "description":"Convert MIDI to YChart JSON."
    #},"data":[]}
    #for track in output_tracks:
    #    for note in track["data"]:
    #        if note not in output["data"] or True:
    #            output["data"].append(note)
    #with open(argv[2],"w",encoding="utf-8") as f:
    #    f.write(dumps(output))


    mid_obj = MidiFile(argv[1],clip=True)   #ychartx v1.0.1
    output_tracks = []
    for midi_track in mid_obj.tracks:
        midi_track:MidiTrack
        this_track = {"name":None,"data":[]}
        this_track_notes = {}
        this_track_notes_nooff = []
        msg_time = 0.0
        for midi_msg in midi_track:
            midi_msg:Message|MetaMessage
            midi_dict_msg = midi_msg.dict()
            msg_time += midi_dict_msg["time"]
            if type(midi_msg) == MetaMessage:
                if midi_dict_msg["type"] == "set_tempo":
                    midi_track_tempo = midi_dict_msg["tempo"]
            elif type(midi_msg) == Message:
                if midi_dict_msg["type"] == "note_on":
                    this_note = MidiNote_ToYChartNote(midi_dict_msg["note"])
                    if this_note is not None:
                        this_track_notes.update({(this_note,midi_dict_msg["note"]):msg_time})
                        this_track_notes_nooff.append([[this_note,midi_dict_msg["note"]],msg_time])
                elif midi_dict_msg["type"] == "note_off":
                    this_note = MidiNote_ToYChartNote(midi_dict_msg["note"])
                    if this_note is not None:
                        if this_note in this_track_notes: # (?,?)
                            on_time = this_track_notes[this_note]
                            this_track_notes_nooff.remove([list(this_note),on_time])
                            del this_track_notes[this_note]
                        try:
                            this_track["data"].append({"time":tick2second(msg_time,mid_obj.ticks_per_beat,midi_track_tempo),"note":note[0][0],"real_note":note[0][1]})
                        except NameError:
                            pass
        for note in this_track_notes_nooff:
            this_track["data"].append({"time":tick2second(note[1],mid_obj.ticks_per_beat,midi_track_tempo),"note":note[0][0],"real_note":note[0][1]})
        output_tracks.append(this_track)
    output = {"meta":{
        "version":"1.0.1",
        "title":"Unknow",
        "create_time":time(),
        "from":"MIDI",
        "author":"Unknow",
        "description":"Convert MIDI to YChart JSON."
    },"data":[]}
    for track in output_tracks:
        for note in track["data"]:
            if note not in output["data"] or True:
                output["data"].append(note)
    with open(argv[2],"w",encoding="utf-8") as f:
        f.write(dumps(output))
except DeprecationWarning as e:
    print(f"error: {e}")
    windll.kernel32.ExitProcess(1)