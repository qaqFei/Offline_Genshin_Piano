from tkinter import Tk,Toplevel
from time import time,sleep
from math import cos,pi

AnimationTime = 0.75
AnimationFps = 120
AnimationGrX = int(AnimationFps * AnimationTime) + 1
z = 0.5
AnimationGr = [z * cos(x / AnimationGrX * pi) + z for x in range(0,AnimationGrX)] ; del z
AnimationGrSum = sum(AnimationGr)
AnimationGr = [x / AnimationGrSum for x in AnimationGr] ; del AnimationGrSum
AnimationStepTime = AnimationTime / len(AnimationGr)

def Move(Window:Tk|Toplevel,dx:int|float,dy:int|float):
    Window.update()
    x,y = Window.winfo_x(),Window.winfo_y()
    for step in AnimationGr:
        st = time()
        x,y = x + dx * step,y + dy * step
        Window.geometry(f"+{int(x)}+{int(y)}")
        sleep(AnimationStepTime - min(time() - st,AnimationStepTime))
