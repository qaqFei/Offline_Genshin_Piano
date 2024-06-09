from os import _exit
from sys import argv
from time import sleep
from threading import Thread
from json import loads
from win32comext.directsound.directsound import DirectSoundCreate,DSBUFFERDESC,IID_IDirectSoundNotify
from struct import unpack,calcsize
from pywintypes import WAVEFORMATEX
from win32event import CreateEvent,WaitForSingleObject

if len(argv)!=2:
    print("Play_YChartx <input_ychartx>")
    _exit(1)

try:
    with open(argv[1],"r") as f:
        ychartx=loads(f.read())
except Exception as e:
    print(f"Read File Error. {e}")

def _wav_header_unpack(data):
    (riff,
     riffsize,
     wave,
     fmt,
     fmtsize,
     format,
     nchannels,
     samplespersecond,
     datarate,
     blockalign,
     bitspersample,
     data,
     datalength
     )=unpack("<4sl4s4slhhllhh4sl",data)
    wfx=WAVEFORMATEX()
    wfx.wFormatTag=format
    wfx.nChannels=nchannels
    wfx.nSamplesPerSec=samplespersecond
    wfx.nAvgBytesPerSec=datarate
    wfx.nBlockAlign=blockalign
    wfx.wBitsPerSample=bitspersample
    return wfx,datalength
def Play(data:bytes):
    "Play a wav file."
    headsize=calcsize("<4sl4s4slhhllhh4sl")
    hdr=data[0:headsize]
    wfx,size=_wav_header_unpack(hdr)
    d=DirectSoundCreate(None,None)
    d.SetCooperativeLevel(None,2)
    sdesc=DSBUFFERDESC()
    sdesc.dwFlags=16640
    sdesc.dwBufferBytes=size
    sdesc.lpwfxFormat=wfx
    buffer=d.CreateSoundBuffer(sdesc,None)
    event=CreateEvent(None,0,0,None)
    notify=buffer.QueryInterface(IID_IDirectSoundNotify)
    notify.SetNotificationPositions((-1,event))
    buffer.Update(0,data[headsize:])
    buffer.Play(0)
    WaitForSingleObject(event,-1)
    del buffer

try:
    Sounds=[open(f"./{n}.wav","rb").read() for n in range(1,22)]
except FileNotFoundError:
    Sounds=[open(f"./../{n}.wav","rb").read() for n in range(1,22)]

try:
    match ychartx["meta"]["version"]:
        case "1.0.0":
            ychartx:dict[dict[str,str|int|float]|list[dict[str,int|float]]]
            ychartx["data"].sort(key=lambda x:x["time"])
            print(f"标题: {ychartx["meta"]["title"]}")
            print(f"作者: {ychartx["meta"]["author"]}")
            print(f"描述: {ychartx["meta"]["description"]}")
            for note_index in range(len(ychartx["data"])):
                this_note = ychartx["data"][note_index]
                try:
                    next_note = ychartx["data"][note_index+1]
                except IndexError:
                    next_note = {"time":this_note["time"]}
                Thread(target=Play,args=(Sounds[this_note["note"]-1],),daemon=True).start()
                sleep(next_note["time"] - this_note["time"])
        case _:
            raise Exception("Unknow ychartx version.")
    sleep(3)
except (Exception,KeyboardInterrupt) as e:
    print(f"error: {e}")