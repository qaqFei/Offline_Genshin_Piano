from sys import argv
from ctypes import windll

import mido

if len(argv) < 3:
    print("Fix_mid <Input_file> <Output_file>")
    windll.kernel32.ExitProcess(1)

def read_track(infile,*args,**kwargs):
    track = mido.MidiTrack();name,size = mido.midifiles.midifiles.read_chunk_header(infile)
    if name != b'MTrk':raise OSError('no MTrk header at start of track')
    start,last_status = infile.tell(),None
    while True:
        if infile.tell() - start == size:break
        delta = mido.midifiles.midifiles.read_variable_int(infile)
        try:status_byte = mido.midifiles.midifiles.read_byte(infile)
        except EOFError:break
        if status_byte < 0x80:
            if last_status is None:raise OSError('running status without last_status')
            peek_data,status_byte = [status_byte],last_status
        else:
            if status_byte != 0xff:last_status = status_byte
            peek_data = []
        if status_byte == 0xff:msg = mido.midifiles.midifiles.read_meta_message(infile,delta)
        elif status_byte in [0xf0,0xf7]:msg = mido.midifiles.midifiles.read_sysex(infile,delta,True)
        else:msg = mido.midifiles.midifiles.read_message(infile,status_byte,peek_data,delta,True)
        track.append(msg)
    return track

mido.midifiles.midifiles.read_track = read_track

try:
    mid_obj = mido.MidiFile(argv[1])
    mid_obj.save(argv[2])
except Exception as e:
    print(f"error: {e}")