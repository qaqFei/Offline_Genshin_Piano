from sys import argv
from time import sleep
from os import _exit,listdir
from os.path import exists,isfile
from mcpi import minecraft
from json import loads

if len(argv)!=2 and len(argv)!=3:
    print("Play_YChart <input_directory> [Speed]")
    _exit(0)

speed=1.0
mc = minecraft.Minecraft.create()
class _pos:
    x:int|float ; y:int|float ; z:int|float
    def __init__(self,x:int|float,y:int|float,z:int|float) -> None:
        self.x = x ; self.y = y ; self.z = z
if exists("Minecraft_Play_YChart_Config.json"):
    with open("Minecraft_Play_YChart_Config.json","r") as f:
        Config = loads(f.read())
        worldspawn = _pos(*Config["worldspawn"])
        pos = _pos(*Config["pos"])
else:
    worldspawn = _pos(*[float(i) for i in input("worldspawn: ").split(",")])
    pos = _pos(*[float(i) for i in input("pos: ").split(",")])
pos.x -= worldspawn.x ; pos.y -= worldspawn.y ; pos.z -= worldspawn.z
if not input(f"tilepos:{pos.x},{pos.y},{pos.z} continue(y/n)?").lower() == "y":
    raise SystemExit

if len(argv)==3:
    speed=float(argv[2])

if not exists(argv[1]):
    print(f"{argv[1]} is not exists.")
    _exit(1)

def get_allfile(path):
    file_list=[]
    if isfile(path):
        return [path]
    for i in listdir(path):
        if isfile(path+"\\"+i):
            file_list+=[path+"\\"+i]
        else:
            file_list+=get_allfile(path+"\\"+i+"\\")
    return file_list

ychart_file_list=get_allfile(argv[1])
for i in ychart_file_list:
    try:
        try:
            f=open(i,"r",encoding="utf-8")
            ychart_text=f.read().split("\n")
            f.close()
        except Exception as e:
            print("Read File Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
            continue
        try:
            bpm=float(ychart_text[0].replace("bpm","").replace(" ",""))
            del ychart_text[0]
        except Exception as e:
            print("Get Bpm Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
            continue
        print(f"File:{i} Time:{len(ychart_text)*(60/bpm)}s Speed:{speed}x")
        try:
            for i in ychart_text:
                sleep(60/speed/bpm)
                if i=="":
                    continue
                if i=="c":
                    continue
                if i[0]=="d":
                    for i2 in i.replace("d","").replace(" ","").split(","):
                        i2 = int(i2)
                        x,y,z = pos.x,pos.y,pos.z
                        x += {1:2,2:4,3:6,4:8,5:10,6:12,7:14,
                            8:2,9:4,10:6,11:8,12:10,13:12,14:14,
                            15:2,16:4,17:6,18:8,19:10,20:12,21:14}[i2]
                        z += {1:2,2:2,3:2,4:2,5:2,6:2,7:2,
                              8:4,9:4,10:4,11:4,12:4,13:4,14:4,
                              15:6,16:6,17:6,18:6,19:6,20:6,21:6,}[i2]
                        mc.setBlock(x,y,z,152) #redstone block
                        mc.setBlock(x,y,z,0) #air
        except Exception as e:
            print("YChart File Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
            continue
    except KeyboardInterrupt:
        print("exit.")
        _exit(1)