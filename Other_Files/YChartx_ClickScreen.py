from os import _exit
from sys import argv
from time import time,sleep
from json import loads
from math import ceil

import pyautogui

if len(argv)!=2:
    print("YChartx_ClickScreen <input_ychartx>")
    _exit(1)

try:
    with open(argv[1],"r") as f:
        ychartx=loads(f.read())
except Exception as e:
    print(f"Read File Error. {e}")

pyautogui.PAUSE = 0.0125
sp = [375,532]
x_tonext_length = 90
y_tonext_length = 90

def ClickScreen(key):
    x = key % 7
    if x == 0:
        x = 7
    y = ceil(key / 7)
    x,y = x-1,y-1
    pos = sp.copy()
    pos[0] += x * x_tonext_length
    pos[1] += y * y_tonext_length
    pyautogui.click(*pos,button="left")

try:
    match ychartx["meta"]["version"]:
        case "1.0.0" | "1.0.1":
            ychartx:dict[dict[str,str|int|float]|list[dict[str,int|float]]]
            ychartx["data"].sort(key=lambda x:x["time"])
            print(f"标题: {ychartx["meta"]["title"]}")
            print(f"作者: {ychartx["meta"]["author"]}")
            print(f"描述: {ychartx["meta"]["description"]}")
            for note_index in range(len(ychartx["data"])):
                st = time()
                this_note = ychartx["data"][note_index]
                try:
                    next_note = ychartx["data"][note_index+1]
                except IndexError:
                    next_note = {"time":this_note["time"]}
                ClickScreen(this_note["note"])
                sleept = (next_note["time"] - this_note["time"]) / 1
                sleep(sleept - min(time() - st,sleept))
        case _:
            raise Exception("Unknow ychartx version.")
    sleep(3)
except (Exception,KeyboardInterrupt) as e:
    print(f"error: {e}")