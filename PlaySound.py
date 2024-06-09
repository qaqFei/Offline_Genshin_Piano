from win32comext.directsound.directsound import DirectSoundCreate,DSBUFFERDESC,IID_IDirectSoundNotify
from struct import unpack
from pywintypes import WAVEFORMATEX
from win32event import CreateEvent,WaitForSingleObject
from functools import cache

@cache
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
    return datalength,wfx

def Play(data:bytes):
    "Play a wav file."
    hdr=data[0:44]

    sdesc=DSBUFFERDESC()
    sdesc.dwBufferBytes,sdesc.lpwfxFormat=_wav_header_unpack(hdr)
    sdesc.dwFlags=16640

    DirectSound=DirectSoundCreate(None,None)
    DirectSound.SetCooperativeLevel(None,2)
    event=CreateEvent(None,0,0,None)

    buffer=DirectSound.CreateSoundBuffer(sdesc,None)
    buffer.QueryInterface(IID_IDirectSoundNotify).SetNotificationPositions((-1,event))
    buffer.Update(0,data[44:])
    buffer.Play(0)
    WaitForSingleObject(event,-1)

    del data,hdr,DirectSound,sdesc,buffer,event