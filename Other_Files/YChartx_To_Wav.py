from sys import argv
from os import _exit
from json import loads

from pydub import AudioSegment

if len(argv) < 3:
    print("YChartx_To_Wav <input_file> <output_file> <note_speed>")
    _exit(0)

SPEED = 1.0
if len(argv) >= 4:
    SPEED = float(argv[3])
try:
    Pydub_Music_List:list[AudioSegment] = [AudioSegment.from_wav(f".\\{i}.wav") for i in range(1,22)]
except FileNotFoundError:
    Pydub_Music_List:list[AudioSegment] = [AudioSegment.from_wav(f".\\..\\{i}.wav") for i in range(1,22)]
for i in range(len(Pydub_Music_List)):
    Pydub_Music_List[i] = Pydub_Music_List[i]._spawn(Pydub_Music_List[i].raw_data,overrides={
         "frame_rate": int(Pydub_Music_List[i].frame_rate * SPEED)
      }).set_frame_rate(Pydub_Music_List[i].frame_rate)

def split_list(music_list,length):
    reslut = [[]]
    for i in music_list:
        if len(reslut[-1]) < length:
            reslut[-1].append(i)
        else:
            reslut.append([i])
    return reslut

try:
    with open(argv[1],"r",encoding="utf-8") as f:
        ychartx = loads(f.read())
    match ychartx["meta"]["version"]:
        case "1.0.0" | "1.0.1":
            process_1 = 0.0
            process_2 = 0.0
            ychartx:dict[dict[str,str|int|float]|list[dict[str,int|float]]]
            ychartx["data"].sort(key=lambda x:x["time"])
            target_wav = AudioSegment.silent(duration=ychartx["data"][-1]["time"] * 1000 + Pydub_Music_List[ychartx["data"][-1]["note"]-1].duration_seconds * 1000)
            wavs = []
            split_length = int(ychartx["data"][-1]["time"]/3)
            if split_length == 0:
                split_length = 1
            for i in split_list(ychartx["data"],split_length):
                duration = i[-1]["time"] - i[0]["time"] + Pydub_Music_List[i[-1]["note"]-1].duration_seconds
                duration *= 1000
                wav_temp = AudioSegment.silent(duration=duration)
                for j in i:
                    this_time = j["time"] - i[0]["time"]
                    wav_temp = wav_temp.overlay(Pydub_Music_List[j["note"]-1],this_time*1000)
                wavs.append({"obj":wav_temp,"time":i[0]["time"]})
                process_1 += 1 / (len(ychartx["data"]) / split_length)
                print(f"\rprocess_1: {process_1:.2%}  ",end="")
            for i in wavs:
                target_wav = target_wav.overlay(i["obj"],i["time"]*1000)
                process_2 += 1 / len(wavs)
                print(f"\rprocess_2: {process_2:.2%}  ",end="")
            target_wav.export(argv[2],format="wav")
            print(f"\rfile: {argv[1]} process: done",end="")
        case _:
            raise Exception("Unknow ychartx version.")
except (ImportError,KeyboardInterrupt) as e:
    print(f"error: {e}")