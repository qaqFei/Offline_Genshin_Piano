from sys import argv
from os import _exit
from time import time
from json import dumps

if len(argv) < 3:
    print("YChartx_To_YChartx <input_file> <output_file>")
    _exit(0)

try:
    with open(argv[1],"r",encoding="utf-8") as f:
        ychart = f.read().split("\n")
    ychartx = {"meta":{
        "version":"1.0.0",
        "title":"Unknow",
        "create_time":time(),
        "from":"YChart",
        "author":"Unknow",
        "description":"Convert YChart to YChart JSON."
    },"data":[]}
    bpm = float(ychart[0].split(" ")[-1])
    del ychart[0]
    i = 0
    for line in ychart:
        if "d" in line:
            notes = [int(i) for i in line.replace("d","").replace(" ","").split(",")]
            for note in notes:
                ychartx["data"].append({"time":i * (60 / bpm),"note":note})
        i += 1
    with open(argv[2],"w",encoding="utf-8") as f:
        f.write(dumps(ychartx))
except StopAsyncIteration as e:
    print(f"error: {e}")