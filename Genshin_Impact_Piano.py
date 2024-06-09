from tkinter import TclError,Tk,Toplevel,Event,Label,Canvas,BooleanVar,filedialog as filedialog_,Menu as tkinter_Menu
from tkinter.ttk import Button,Progressbar,Entry,Scale,Checkbutton,LabelFrame
from tkinter.messagebox import showinfo as showinfo_,showwarning as showwarning_,showerror as showerror_,askyesno as askyesno_
from tkinter.colorchooser import askcolor #有
from os import system,chdir,listdir,startfile
from os.path import exists,dirname,isdir,isfile
from sys import argv,executable
from json import loads,dumps
from time import sleep,time
from threading import Thread
from ctypes import windll,c_uint64,WINFUNCTYPE,create_unicode_buffer,sizeof
from typing import NoReturn
from tempfile import mkdtemp
import gc

from pynput.keyboard import GlobalHotKeys
from PIL import Image,ImageTk,ImageDraw,ImageFilter
from pystray import MenuItem,Icon
from pydub import AudioSegment
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mido import MetaMessage,Message,MidiFile,MidiTrack,second2tick
from pygame import mixer

import PlaySound
import CreateAeroWindow
import MetronomeData
import NonlinearMoveWindow

#准备工作
chdir(dirname(argv[0]))
mixer.init()
temp_dirs = []
keybd_event = windll.user32.keybd_event
fullscreen = False
BreakYChartPlay = False
PlaySpeed = 1.0
CanvasBackgroundGaussianBlurRadius = 2.0
CanvasBackgroundWillSet = None
init_ellipse_effect_image_list_num = 16
PlayLoop = False
CanvasBackgroundGaussianBlurRadiusScaleMaxVar = 120
OpenMetronome = False
ShowEffect = True
MetronomeBpm = 90.0
MetronomeBpm_Scale_Min = 60.0
MetronomeBpm_Scale_Max = 960.0
PlaySpeed_Scale_Label_Text = "播放速度 (0.5 ~ 10.0)"
WindowTransparent_Scale_Label_Text = "窗口透明度 (25.0% ~ 100.0%)"
CanvasBackgroundGaussianBlurRadius_Scale_Label_Text = f"背景模糊半径(鼠标左键释放生效) (0px ~ {CanvasBackgroundGaussianBlurRadiusScaleMaxVar}px)"
MetronomeBpm_Scale_Label_Text = f"节拍器Bpm ({MetronomeBpm_Scale_Min}~{MetronomeBpm_Scale_Max})"
PlayViewColor = "#ff0000"
title_bar_act_color = "#0078d7"
title_bar_noact_color = "#FFFFFF"
window_width = None
window_height = None
window_x = None
window_y = None
imgCanvas_width = None
imgCanvas_height = None
imgCanvas_x = None
imgCanvas_y = None
screen_width = None
screen_height = None
Pydub_Music_List = [AudioSegment.from_wav(f".\\{i}.wav") for i in range(1,22)]

def never(*args,**kwargs) -> NoReturn:
    try:
        gui.destroy()
    except Exception:
        pass
    showerror_(message="NERVER FUNCTION CALLED")
    windll.kernel32.ExitProcess(1)

def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def use_admin() -> NoReturn|bool:
    if not is_admin():
        #重启
        result = windll.shell32.ShellExecuteW(None,"runas",executable,
                                              " ".join(argv),
                                              None,1)
        
        if result == 42:
            return windll.kernel32.ExitProcess(0)
        return False
    else:
        return True

#use_admin()

def hook_dropfiles(hwnd,callback):
    new,old="widget_id_new","widget_id_old"
    prototype = WINFUNCTYPE(*(c_uint64,)*5)
    def py_drop_func(hwnd,msg,wp,lp):
        if msg == 0x233:
            szFile = create_unicode_buffer(260)
            files = []
            for i in range(windll.shell32.DragQueryFileW(c_uint64(wp),-1,None,None)):
                windll.shell32.DragQueryFileW(c_uint64(wp),i,szFile,sizeof(szFile))
                files.append(szFile.value)
            Thread(target=callback,args=(files,)).start()
            windll.shell32.DragFinish(c_uint64(wp))
        return windll.user32.CallWindowProcW(*map(c_uint64,(globals()[old],hwnd,msg,wp,lp)))
    globals()[old] = None
    globals()[new] = prototype(py_drop_func)
    windll.shell32.DragAcceptFiles(hwnd,True)
    globals()[old] = windll.user32.GetWindowLongPtrA(hwnd,-4)
    windll.user32.SetWindowLongPtrA(hwnd,-4,globals()[new])

def init_sound_data():
    global soundlist
    soundlist = []
    for i in range(1,22):
        while True:
            try:
                with open(f"{i}.wav","rb") as f:
                    soundlist += [f.read()]
            except Exception as e:  #文件未复制完成/?
                sleep(0.1)
                continue
            break

def playsound(key:int):
    try:
        PlaySound.Play(soundlist[key-1])
    except IndexError: #正在重新加载音频
        return None

#适应缩放
windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = windll.shcore.GetScaleFactorForDevice(0)
Tk_Temp = Tk
Toplevel_Temp = Toplevel
class Tk(Tk_Temp):
    def __init__(self,**kw):
        super().__init__(**kw) #初始化
        self.tk.call("tk","scaling",ScaleFactor / 75) #设置缩放
        #self.bind("<Escape>",lambda x:self.iconify())  #绑定ESC键
class Toplevel(Toplevel_Temp):
    def __init__(self,**kw):
        super().__init__(**kw) #初始化
        self.tk.call("tk","scaling",ScaleFactor / 75) #设置缩放
        self.bind("<Escape>",lambda x:self.withdraw())  #绑定ESC键
del Tk_Temp,Toplevel_Temp

#"特殊"的Canvas  !!! : 任何操作的x和y 都要加上/减去 winfo_x()或winfo_y()
class Canvas_Img(Canvas):
    def winfo_x(self) -> int:
        return super().winfo_x() + int(window_width / 2 - Image_width/2)
    def winfo_y(self) -> int:
        return super().winfo_y() + int(window_height / 2 + window_height / 2 * 0.25 - Image_height / 2)
    def winfo_width(self) -> int:
        return Image_width
    def winfo_height(self) -> int:
        return Image_height

class get_value:
    def get(self,
            master:Tk = None,
            title = "离线原琴",
            text = "请输入:",
            buttontext = "确定",
            type = "str"):
        def cancel(self):
            self.window.destroy()
            master.attributes("-disabled",False)
            self.value = "cancel"
        def ok(self):
            self.value = self.entry.get()
        self.window = Toplevel()
        self.window.iconbitmap("Icon")
        self.window.protocol("WM_DELETE_WINDOW",lambda:cancel(self))
        self.window.resizable(0,0)
        self.window.title(title)
        if master != None:
            self.window.transient(master)
            self.window.grab_set()
            master.attributes("-disabled",True)
        self.label = Label(self.window,text=text,justify="left")
        self.entry = Entry(self.window)
        self.button = Button(self.window,text=buttontext,command=lambda:ok(self))
        self.label.pack(anchor="w")
        self.entry.pack()
        self.button.pack()
        self.value = None
        self.cancel = False
        while True:
            self.window.update()
            if self.value == "cancel":
                return None
            if self.value != None:
                if type == "str":
                    self.window.destroy()
                    master.attributes("-disabled",False)
                    return str(self.value)
                if type == "float":
                    try:
                        float(self.value)
                        self.window.destroy()
                        master.attributes("-disabled",False)
                        return float(self.value)
                    except ValueError:
                        showerror(message="无法转化为小数")
                        self.value = None
                if type == "int":
                    try:
                        int(self.value)
                        self.window.destroy()
                        master.attributes("-disabled",False)
                        return int(self.value)
                    except ValueError:
                        showerror(message="无法转化为整数")
                        self.value=None

class YChart_Type:
    def __init__(self,data:str) -> None:
        self._json_data = loads(data)
        self.version = self._json_data["meta"]["version"]
        self._init()
    def _init(self) -> None:
        match self.version:
            case "1.0.0" | "1.0.1":
                self.title = self._json_data["meta"]["title"]
                self.author = self._json_data["meta"]["author"]
                self.description = self._json_data["meta"]["description"]
                self.data:list = self._json_data["data"]
                self.data.sort(key=lambda x:x["time"])
            case _:
                raise Exception("Unknow version.")
    def __iter__(self):
        match self.version:
            case "1.0.0" | "1.0.1":
                return self.data.__iter__()
            case _:
                raise Exception("Unknow version.")

def ConfigureUpdate(e:Event):
    if e.widget == gui:
        global window_width,window_height
        global window_x,window_y
        if e.width != window_width:
            window_width = e.width
        if e.height != window_height:
            window_height = e.height
        if e.x != window_x:
            window_x = e.x
        if e.y != window_y:
            window_y = e.y
    elif e.widget == ImgCanvas:
        global imgCanvas_width,imgCanvas_height
        global imgCanvas_x,imgCanvas_y
        if (temp := e.widget.winfo_width()) != imgCanvas_width:
            imgCanvas_width = temp
        if (temp := e.widget.winfo_height()) != imgCanvas_height:
            imgCanvas_height = temp
        if (temp := e.widget.winfo_x()) != imgCanvas_x:
            imgCanvas_x = temp
        if (temp := e.widget.winfo_y()) != imgCanvas_y:
            imgCanvas_y = temp
        
gui=Tk()
gui.withdraw()
gui.bind("<Configure>",ConfigureUpdate)
screen_width = gui.winfo_screenwidth()
screen_height = gui.winfo_screenheight()

#loading_gui 加载中窗口
loading_gui=Toplevel()
loading_gui.overrideredirect(True)
loading_gui.config(cursor="watch")
loading_label = Label(loading_gui,text="加载中...",justify="left")
loading_label.pack()
loading_gui.update()

#debug
debug_ = True
debug_level = [1,2,3]  # 1=info 2=warn 3=error
debug_num = 0
#判断是否为exe模式
if not (argv[0][-4:len(argv[0])] == ".exe" or debug_ is False):
    system("")
class debug:
    def message(self,message_type="info",message="",level=None,start="",end=""):
        if debug_:
            global debug_num
            debug_num += 1
            log=f"{start}[{message_type} num={debug_num}]{message}{end}"
            if level in debug_level:
                print(log)
    def info(self,message):
        self.message(message_type="info",message=message,level=1)
    def warn(self,message):
        self.message(message_type="warn",message=message,level=2,start="\033[1;40;33m",end="\033[0m")
    def error(self,message):
        self.message(message_type="error",message=message,level=3,start="\033[1;40;31m",end="\033[0m")
debug = debug()

#定义映射表  1000+key=heigth 2000+key=width
map_table = {"1":"Q","2":"W","3":"E","4":"R","5":"T","6":"Y","7":"U",
             "8":"A","9":"S","10":"D","11":"F","12":"G","13":"H","14":"J",
             "15":"Z","16":"X","17":"C","18":"V","19":"B","20":"N","21":"M",

             "Q":"1","W":"2","E":"3","R":"4","T":"5","Y":"6","U":"7",
             "A":"8","S":"9","D":"10","F":"11","G":"12","H":"13","J":"14",
             "Z":"15","X":"16","C":"17","V":"18","B":"19","N":"20","M":"21",
             
             1:"Q",2:"W",3:"E",4:"R",5:"T",6:"Y",7:"U",
             8:"A",9:"S",10:"D",11:"F",12:"G",13:"H",14:"J",
             15:"Z",16:"X",17:"C",18:"V",19:"B",20:"N",21:"M",
             
             1000:0,
             1001:1,1002:1,1003:1,1004:1,1005:1,1006:1,1007:1,
             1008:2,1009:2,1010:2,1011:2,1012:2,1013:2,1014:2,
             1015:3,1016:3,1017:3,1018:3,1019:3,1020:3,1021:3,
             
             2000:0,
             2001:1,2002:2,2003:3,2004:4,2005:5,2006:6,2007:7,
             2008:1,2009:2,2010:3,2011:4,2012:5,2013:6,2014:7,
             2015:1,2016:2,2017:3,2018:4,2019:5,2020:6,2021:7}
notes_high = {84:1,86:2,88:3,89:4,91:5,93:6,95:7,
              72:8,74:9,76:10,77:11,79:12,81:13,83:14,
              60:15,62:16,64:17,65:18,67:19,69:20,71:21}
notes_high = {value:key for key,value in notes_high.items()}

Display_size_width = screen_width
Display_size_height = screen_height
Display_size_real = [Display_size_width,Display_size_height]
debug.info("DisplaySize:"+str(Display_size_width)+"x"+str(Display_size_height))

#检测options.json是否存在
debug.info("loading options.json")
if exists("options.json"):
    #读取options.json
    with open("options.json","r",encoding="utf-8") as options_:
        try:
            options = options_.read()
        except UnicodeDecodeError:
            debug.error("options.json decode error")
    #解析
    try:
        #加载成字典
        options = loads(options)


        if "Display_size_width" in options:
            try:
                var_type = type(options["Display_size_width"])
                if var_type == float:
                    options["Display_size_width"] = int(options["Display_size_width"])
                elif var_type == str:
                    options["Display_size_width"] = int(float(options["Display_size_width"]))
                elif var_type == int:
                    pass
                else:
                    raise TypeError
                del var_type

                Display_size_width = options["Display_size_width"]
            except Exception as e:
                debug.error(f"options.json:Display_size_width is error: {e.__repr__()}")
        else:
            debug.info("options.json:Display_size_width is not exists.")



        if "Display_size_height" in options:
            try:
                var_type = type(options["Display_size_height"])
                if var_type == float:
                    options["Display_size_height"] = int(options["Display_size_height"])
                elif var_type == str:
                    options["Display_size_height"] = int(float(options["Display_size_height"]))
                elif var_type == int:
                    pass
                else:
                    raise TypeError
                del var_type

                Display_size_height = options["Display_size_height"]
            except Exception as e:
                debug.error(f"options.json:Display_size_height is error: {e.__repr__()}")
        else:
            debug.info("options.json:Display_size_height is not exists.")



        if "map_table" in options:
            try:
                var_type = type(options["map_table"])
                if var_type == dict:
                    pass
                else:
                    raise TypeError
                del var_type

                map_table_ = options["map_table"]

                map_table_temp = {}
                for i in map_table_:
                    map_table_temp.update({map_table[i]:map_table_[i]})       #过几天 我可能也不知道原理了 哈哈哈 -- 2023/11/19 15:58:31
                    map_table_temp.update({map_table_[i]:map_table[i]})       #过几天 我可能也不知道原理了 哈哈哈 -- 2023/11/19 15:58:31
                    map_table_temp.update({int(map_table[i]):map_table_[i]})  #过几天 我可能也不知道原理了 哈哈哈 -- 2023/11/19 15:58:31
                    debug.info(f"键位{map_table_[i]}映射到{i}")
                map_table.update(map_table_temp)
                del map_table_,map_table_temp
            except Exception as e:
                debug.error(f"options.json:map_table is error: {e.__repr__()}")
        else:
            debug.info("options.json:map_table is not exists.")



        if "CanvasBackgroundGaussianBlurRadius" in options:
            try:
                var_type = type(options["CanvasBackgroundGaussianBlurRadius"])
                if var_type == str:
                    options["CanvasBackgroundGaussianBlurRadius"] = float(options["CanvasBackgroundGaussianBlurRadius"])
                elif var_type == int:
                    pass
                elif var_type == float:
                    pass
                else:
                    raise TypeError
                del var_type

                CanvasBackgroundGaussianBlurRadius = options["CanvasBackgroundGaussianBlurRadius"]
            except Exception as e:
                debug.error(f"options.json:CanvasBackgroundGaussianBlurRadius is error: {e.__repr__()}")
        else:
            debug.info("options.json:CanvasBackgroundGaussianBlurRadius is not exists.")



        if "CanvasBackgroundWillSetPath" in options:
            try:
                var_type = type(options["CanvasBackgroundWillSetPath"])
                if var_type == str:
                    pass
                else:
                    raise TypeError
                del var_type

                CanvasBackgroundWillSet = options["CanvasBackgroundWillSetPath"]

                if not exists(CanvasBackgroundWillSet) or not isfile(CanvasBackgroundWillSet):
                    raise FileNotFoundError

            except Exception as e:
                debug.error(f"options.json:CanvasBackgroundWillSetPath is error: {e.__repr__()}")
        else:
            debug.info("options.json:CanvasBackgroundWillSetPath is not exists.")
        
        if "OpenMetronome" in options:
            try:
                var_type = type(options["OpenMetronome"])
                if var_type == int:
                    options["OpenMetronome"] = bool(options["OpenMetronome"])
                elif var_type == str:
                    match options["OpenMetronome"].lower():
                        case "true" | "1":
                            options["OpenMetronome"] = True
                        case "false" | "0":
                            options["OpenMetronome"] = False
                        case _:
                            raise TypeError
                elif var_type == bool:
                    pass
                else:
                    raise TypeError
                del var_type

                OpenMetronome = options["OpenMetronome"]
            except Exception as e:
                debug.error(f"options.json:OpenMetronome is error: {e.__repr__()}")
        else:
            debug.info("options.json:OpenMetronome is not exists.")
        
        if "MetronomeBpm" in options:
            try:
                var_type = type(options["MetronomeBpm"])
                if var_type == str:
                    options["MetronomeBpm"] = float(options["MetronomeBpm"])
                elif var_type == float:
                    pass
                elif var_type == int:
                    pass
                else:
                    raise TypeError
                del var_type

                if not (30 <= options["MetronomeBpm"] <= 1920):
                    raise ValueError

                MetronomeBpm = options["MetronomeBpm"]
            except Exception as e:
                debug.error(f"options.json:MetronomeBpm is error: {e.__repr__()}")
        else:
            debug.info("options.json:MetronomeBpm is not exists.")

    except Exception:
        debug.error("options.json is error or load error.")

def showinfo(message=""):
    return showinfo_(title="消息",message=message)
def showwarning(message=""):
    return showwarning_(title="警告",message=message)
def showerror(message=""):
    return showerror_(title="错误",message=message)
def askyesno(message=""):
    return askyesno_(title="选择",message=message)
class filedialog:
    def askopenfilename(title:str="",filetypes:str|list=""):
        if filetypes != "":
            filetypes += [("所有文件",".*")]
        return filedialog_.askopenfilename(title=title,filetypes=filetypes)
    def asksaveasfilename(title:str="",filetypes:str|list=""):
        return filedialog_.asksaveasfilename(title=title,filetypes=filetypes)

#设置是否要更改gui_daochuhexian的大小
gui_daochuhexian_Setting = False
#默认播放模式为0
playsound_mode = 0

init_sound_data()

#定义获取临时窗口的函数
def get_toplevel(title="离线原琴",
                 resizable_ff=True,
                 withdraw=False,
                 protocol_WM_DELETE_WINDOW=None,
                 transient=None,
                 cursor=None
                 ) -> Toplevel:
    debug.info("创建窗口")
    get_toplevel_ = Toplevel()
    if withdraw:
        debug.info("隐藏窗口")
        get_toplevel_.withdraw()
    debug.info(f"设置窗口标题:{title}")
    get_toplevel_.title(title)
    debug.info("设置窗口图标")
    get_toplevel_.iconbitmap("Icon")
    if resizable_ff:
        debug.info("锁定窗口大小")
        get_toplevel_.resizable(0,0)
    if protocol_WM_DELETE_WINDOW != None:
        debug.info("绑定窗口关闭事件")
        if protocol_WM_DELETE_WINDOW == "withdraw":
            get_toplevel_.protocol("WM_DELETE_WINDOW",get_toplevel_.withdraw)
        elif protocol_WM_DELETE_WINDOW == "deiconify":
            get_toplevel_.protocol("WM_DELETE_WINDOW",get_toplevel_.deiconify)
        else:
            get_toplevel_.protocol("WM_DELETE_WINDOW",protocol_WM_DELETE_WINDOW)
    if transient != None:
        debug.info("绑定父窗口")
        get_toplevel_.transient(transient)
    if cursor != None:
        debug.info(f"更改窗口鼠标样式:{cursor}")
        get_toplevel_.config(cursor=cursor)
    if withdraw == False:
        debug.info(f"重新显示窗口:{get_toplevel_.winfo_name()} (用于父窗口隐藏的情况)")
        get_toplevel_.deiconify()
    return get_toplevel_

#YChart[0]用于判断是否打开了原琴谱面文件  YChart[1]用于存放原琴谱面文件的内容
YChart = [False,""]

#用于判断是否在录制原琴谱面
Recording = False

#用于判断是否需要继续播放
JiXuBoFan_keyboard = True
JiXuBoFan_ychart = True
JiXuBoFan_click = True

#鼠标特效列表
effect_down = []

#特效坐标偏移
effect_offset = [[0.01,0,0.135,0.135],[0.02,0.02,0.13,0.13],[0.025,0.02,0.125,0.13],[0.03,0.02,0.115,0.13],[0.0385,0.02,0.105,0.13],[0.043,0.02,0.085,0.13],[0.053,0.02,0.078,0.13],
                 [0.01,0.02,0.135,0.124],[0.02,0.02,0.13,0.124],[0.025,0.02,0.125,0.124],[0.03,0.02,0.115,0.124],[0.0385,0.02,0.105,0.124],[0.043,0.02,0.085,0.124],[0.053,0.03,0.078,0.124],
                 [0.01,0.05,0.135,0.085],[0.02,0.05,0.13,0.085],[0.025,0.05,0.125,0.085],[0.03,0.05,0.115,0.085],[0.0385,0.05,0.105,0.085],[0.043,0.05,0.085,0.085],[0.053,0.05,0.078,0.085]]

#定义??类
class FunctionsClass:
    #防止重复
    effect_mouse_last_key = None
    set_volume_last_value = None
    last_window_size = None
    effect_num = 0

    #窗口进入动画
    def WindowInAnimation():
        gui.attributes("-disabled",True)
        gui.update()
        gui_begin_pos = [
            int(screen_width / 2 - window_width / 2),
            int(screen_height / 2 - window_height / 2 + screen_height)
        ]
        gui.geometry(f"+{gui_begin_pos[0]}+{gui_begin_pos[1]}")
        gui.deiconify()
        NonlinearMoveWindow.Move(gui,-gui_begin_pos[0] + screen_width / 2 - window_width / 2,-gui_begin_pos[1] + screen_height / 2 - window_height / 2)
        gui.attributes("-disabled",False)
    
    #窗口退出动画
    def WindowOutAnimation():
        gui.attributes("-disabled",True)
        gui.update()
        gui_begin_pos = [
            gui.winfo_x(),
            gui.winfo_y()
        ]
        target_pos = [
            screen_width / 2 - window_width / 2,-window_height*1.2
        ]
        NonlinearMoveWindow.Move(gui,target_pos[0]-gui_begin_pos[0],target_pos[1]-gui_begin_pos[1])
        gui.withdraw()
        gui.update()
        gui.after(500,lambda:gui.geometry(f"+{gui_begin_pos[0]}+{gui_begin_pos[1]}"))
        gui.attributes("-disabled",False)

    #谱面编辑器
    def Editer():
        system("start ./Editer.exe")

    #emm... -> xxx.bind("<xxx>",_GetBindCommand(func))
    def _GetBindCommand(func):
        return lambda e:func()

    #分割列表
    def split_list(music_list,length):
        reslut = [[]]
        for i in music_list:
            if len(reslut[-1]) < length:
                reslut[-1].append(i)
            else:
                reslut.append([i])
        return reslut

    #添加文件后缀名
    def Add_Extension(Path:str,Extension:str) -> str:
        if not Path.endswith(f".{Extension}"):
            return f"{Path}.{Extension}"
        return Path
    
    #获取唯一的特效id
    def GetEffectId():
        FunctionsClass.effect_num += 1
        return FunctionsClass.effect_num

    #特效
    def effect(key,thread=True):
        if not ShowEffect:
            return None
        if not thread:
            Thread(target=lambda:FunctionsClass.effect(key)).start()
            return None
        effect_id = FunctionsClass.GetEffectId()
        effect_time = 0.4
        effect_AllStartTime = time()
        effect_canvas_name = ImgCanvas.winfo_name()
        Canvas_width = imgCanvas_width
        Canvas_height = imgCanvas_height
        size = Canvas_width / 7 * 0.85
        x1 = Canvas_width / 7 * (map_table[2000 + key] - 1) + (Canvas_width / 7 * effect_offset[key - 1][0] * 2)
        y1 = Canvas_height / 3 * (map_table[1000 + key] - 1) + (Canvas_height / 3 * effect_offset[key - 1][1] * 2)
        x2,y2 = x1 + size,y1 + size
        while True:
            try:
                effect_down = ImgCanvas.create_image(imgCanvas_x+x1,
                                                    imgCanvas_y+y1,
                                                    anchor="nw",
                                                    image=effect_image,
                                                    tag=f"EffectImage_{effect_id}")
            except Exception as e:
                debug.error(e.__repr__());continue
            break
        for i in range(init_ellipse_effect_image_list_num):
            effect_StartTime = time()

            if i == int(init_ellipse_effect_image_list_num / 2):
                ImgCanvas.delete(effect_down)
            while True:
                try:
                    effect = ImgCanvas.create_image(imgCanvas_x + (x1 + x2) / 2,
                                                    imgCanvas_y + (y1 + y2) / 2,
                                                    image = ellipse_effect_image_list[i],
                                                    tag=f"EffectImage_{effect_id}")
                except Exception as e:
                    debug.error(e.__repr__());continue
                break
            #防止卡顿 (以下的 i!=0:不是第一次 i==max:最后一次)
            if i != 0:
                ImgCanvas.delete(last_effect)
            last_effect = effect
            if i == init_ellipse_effect_image_list_num - 1:
                ImgCanvas.delete(last_effect)
            if time() - effect_AllStartTime > effect_time * 1.75: #特效超时
                debug.warn(f"Effect_{effect_id}: Timeout!")
                ImgCanvas.delete(f"EffectImage_{effect_id}")
                return None
            if i % 4 == 0:
                if ImgCanvas.winfo_name() != effect_canvas_name:
                    debug.info(f"Effect_{effect_id}: The canvas is different!")
                    ImgCanvas.delete(f"EffectImage_{effect_id}")
                    return None
            sleep(effect_time / init_ellipse_effect_image_list_num - min(time() - effect_StartTime,effect_time / init_ellipse_effect_image_list_num))

    #特效_鼠标
    def effect_mouse(event,thread=False,key=None):
        if thread:  #不加的话 会2次 :(
            #修正
            event.x -= imgCanvas_x
            event.y -= imgCanvas_y
        if event.type.__str__() != "6":  #离开组件/其他
            try:
                ImgCanvas.moveto(effect_image_mouse_list_CanvasId[FunctionsClass.effect_mouse_last_key-1],window_width,window_height)
            except TypeError:  #TypeError: unsupported operand type(s) for -: 'NoneType' and 'int' 鼠标在图片外移动 忽略
                return 0
            FunctionsClass.effect_mouse_last_key = None
            return 0
        if (event.x - imgCanvas_x<0
            or event.y-imgCanvas_y<0
            or event.x-imgCanvas_x>imgCanvas_width
            or event.y-imgCanvas_y>imgCanvas_height) and (not thread):   #超出范围  #过程中修正了坐标
            class event:  #伪造一个离开的event
                class type:
                    def __str__(self):
                        return "8"
                type = type()
                x,y=0,0
            FunctionsClass.effect_mouse(event())
            return 0
        if not thread:
            Thread(target=lambda:FunctionsClass.effect_mouse(event,True)).start()
            return 0
        if key == None:
            for i in [0,1,2,3,4,5,6]:
                if imgCanvas_width / 7 * i < event.x < imgCanvas_width / 7 * (i + 1):  #第i+1列
                    if event.y < imgCanvas_height / 3 * 1:  #第1行
                        Thread(target=lambda:FunctionsClass.effect_mouse(event,True,i+1)).start()
                        return 0
                    if event.y < imgCanvas_height / 3 * 2:  #第2行
                        Thread(target=lambda:FunctionsClass.effect_mouse(event,True,i+8)).start()
                        return 0
                    if event.y < imgCanvas_height / 3 * 3:  #第3行
                        Thread(target=lambda:FunctionsClass.effect_mouse(event,True,i+15)).start()
                        return 0
            FunctionsClass.effect_mouse_last_key = None
            return 1
        if FunctionsClass.effect_mouse_last_key == key:
            return 0
        else:
            if FunctionsClass.effect_mouse_last_key != None:
                class event:  #伪造一个离开的event
                    class type:
                        def __str__(self):
                            return "8"
                    type = type()
                    x,y=0,0
                FunctionsClass.effect_mouse(event())
            FunctionsClass.effect_mouse_last_key=key
            Canvas_width = imgCanvas_width
            Canvas_height = imgCanvas_height
            x1 = Canvas_width / 7 * (map_table[2000 + key] - 1) - Canvas_width / 7 * 0.025
            y1 = Canvas_height / 3 * (map_table[1000 + key] - 1) - Canvas_height /3 * 0.025
            ImgCanvas.moveto(effect_image_mouse_list_CanvasId[key - 1],
                             imgCanvas_x + x1,
                             imgCanvas_y + y1)
            
    #定义模拟键盘输入的函数
    def keyInput(key):
        keybd_event(ord(key),0,0,0)
        keybd_event(ord(key),0,2,0)

    #测试是否打开YChart -> False | True
    def isOpenYChart(tips=True) -> bool:
        if YChart[0] == False:
            if tips:
                showerror(message="未打开谱面")
            return False
        return True
    
    #定义关闭程序的函数
    def close(thread:bool=False):
        if not thread:
            Thread(target=FunctionsClass.close,args=(True,)).start()
            return None
        global Recording
        try:
            icon.stop()
        except Exception:
            pass
        FunctionsClass.WindowOutAnimation()
        if Recording == True:
            Recording = False
            sleep(0.4)  #等待时间,用于等待保存
        debug.info("退出...")
        windll.kernel32.ExitProcess(0)
    
    #定义重启程序的函数
    def reopen():
        try:
            icon.stop()
        except Exception:
            pass
        startfile(argv[0])
        gui.title("离线原琴 ") #1 " "
        while True:
            if gui.title() == "离线原琴  ": #2 " "
                break
            gui.update()
            sleep(0.1)
        FunctionsClass.close()

    #定义获取文件夹中的全部文件
    def GetAllFile(Path):
        File_List = []
        debug.info("初始化File_List变量")
        #循环遍历
        for i in listdir(Path):
            #是目录 -- 递归
            if isdir(Path + "\\" + i):
                debug.info(i + "是目录")
                File_List+=FunctionsClass.GetAllFile(Path + "\\" + i)
            else:
                debug.info(i + "是文件")
                File_List+=[Path + "\\" + i]
        return File_List #Format code at this. Please continue.

    #定义数字转键盘按键的函数
    def Num_To_JianPan(Num):
        try:
            return map_table[Num]
        except KeyError:
            return ""

    #定义打开YChart的函数_主体
    def OpenYChart_(filepath):
        if filepath=="":
            debug.info("文件路径为空")
            return 1
        global YChart
        YChart=[False,""]
        if filepath=="":
            debug.info("文件路径为空")
            return 1
        debug.info("尝试打开文件...")
        try:
            f=open(filepath,"r",encoding="utf-8")
        except FileNotFoundError:
            showerror(message="文件不存在!")
            return 1
        #读取数据
        try:
            debug.info("读取数据...")
            YChart[1]=f.read()
        except UnicodeDecodeError:
            showerror(message="编码错误!")
            debug.error("编码错误!")
        f.close()
        debug.info("关闭文件流...")
        #YChart[0]更改为True,表示有数据,打开了文件
        YChart[0]=True

    #定义打开YChart的函数
    def OpenYChart():
        debug.info("打开YChart")
        return FunctionsClass.OpenYChart_(filedialog.askopenfilename(title="打开谱面文件",filetypes=[("原琴谱面文件",".ychartx")]))
    
    #定义播放谱面的函数
    def PlayChart(thread=True):
        if not FunctionsClass.isOpenYChart():
            return 1
        if thread:
            Thread(target=FunctionsClass.PlayChart_).start()
        else:
            FunctionsClass.PlayChart_()
    
    #定义播放谱面的函数_主体
    def PlayChart_(looping:bool=False):
        global BreakYChartPlay

        BreakYChartPlay = False
        
        try:
            obj = YChart_Type(YChart[1])
        except Exception as e:
            showerror(message=f"谱面解析错误:\n{e.__repr__()}")
            return 1
        match obj.version:
            case "1.0.0" | "1.0.1":
                if not looping:
                    showinfo(f"谱面版本: {obj.version}\n标题: {obj.title}\n作者: {obj.author}\n描述: {obj.description}")
                index = -1
                for i in obj:
                    index += 1
                    if index != 0:
                        sleep((i["time"] - obj.data[index - 1]["time"]) / PlaySpeed)
                    else:
                        sleep(i["time"] / PlaySpeed)
                    if BreakYChartPlay:
                        debug.info("Play Breaked.")
                        return None
                    PlayButtonSound.PlayByIntKey(key=i["note"],type="ychart")
            case _:
                never()
        
        if PlayLoop:
            debug.info("[PlayYChart]Play again.")
            Thread(target=FunctionsClass.PlayChart_,args=(True,)).start()
    
    #以midi方式播放谱面文件
    def PlayChart_ByMidi(thread=True):
        if not FunctionsClass.isOpenYChart():
            return 1
        if thread:
            Thread(target=FunctionsClass.PlayChart_ByMidi_).start()
        else:
            FunctionsClass.PlayChart_ByMidi_()

    #以midi方式播放谱面文件_主体
    def PlayChart_ByMidi_(looping:bool=False):
        global BreakYChartPlay

        if not FunctionsClass.isOpenYChart():
            return 1
        
        BreakYChartPlay = False

        try:
            obj = YChart_Type(YChart[1])
        except Exception as e:
            showerror(message=f"谱面解析错误:\n{e.__repr__()}")
            return 1
        
        match obj.version:
            case "1.0.0" | "1.0.1":
                if not looping:
                    showinfo(f"谱面版本: {obj.version}\n标题: {obj.title}\n作者: {obj.author}\n描述: {obj.description}")
                mid_filedir = mkdtemp()
                temp_dirs.append(mid_filedir)
                mid_obj = MidiFile()
                main_track = MidiTrack()
                main_track_tempo = 120000
                main_track.append(
                    MetaMessage("set_tempo",tempo=main_track_tempo,time=0)
                )
                for index,note in enumerate(obj.data):
                    if index != 0:
                        t = note["time"] - obj.data[index-1]["time"]
                    else:
                        t = note["time"]
                    main_track.append(
                        Message("note_on",note=notes_high[note["note"]] if obj.version == "1.0.0" else note["real_note"],velocity=127,time=second2tick(t,480,main_track_tempo))
                    )
                main_track.append(
                    Message("note_off",note=notes_high[note["note"]] if obj.version == "1.0.0" else note["real_note"],time=second2tick(1.5,480,main_track_tempo))
                )
                mid_obj.tracks.append(main_track)
                mid_obj.save(f"{mid_filedir}/file.mid")
                mixer.music.load(f"{mid_filedir}/file.mid")
                mixer.music.play()
                play_time = 0.0
                play_effected_notes = []
                while mixer.music.get_busy():
                    sleep(0.01)
                    play_time = mixer.music.get_pos() / 1000
                    for note in obj.data:
                        if note["time"] <= play_time and note not in play_effected_notes:
                            play_effected_notes.append(note)
                            FunctionsClass.effect(note["note"],False)
                    if BreakYChartPlay:
                        mixer.music.stop()
                        debug.info("Play Breaked.")
                        return None
            case _:
                never()

        if PlayLoop:
            debug.info("[PlayChart_ByMidi]Play again.")
            Thread(target=FunctionsClass.PlayChart_ByMidi_,args=(True,)).start()
    
    #定义播放谱面的函数 -- 拥有路径
    def BoFanYChart_HavePath(Path):
        global BoFanYChart_HavePath_Finish
        BoFanYChart_HavePath_Finish=False
        FunctionsClass.OpenYChart_(Path)
        FunctionsClass.PlayChart(thread=False)
        debug.info("[播放谱面]播放完成:"+Path)
        BoFanYChart_HavePath_Finish=True
    
    #定义录制YChart的函数
    def RecordYChart():
        global Recording,Record_Data
        if Recording == True:
            showinfo(message="正在录制")
            return None
        RecordingYChart_Path = filedialog.asksaveasfilename(title="请选择录制YChart路径",filetypes=[("原琴谱面文件",".ychartx")])
        #如果路径为空
        if RecordingYChart_Path == "":
            return None
        RecordingYChart_Path = FunctionsClass.Add_Extension(RecordingYChart_Path,"ychartx")
        Record_Data = {
            "meta":{
                "version":"1.0.0",
                "title":"Unknow",
                "create_time":time(),
                "from":"record",
                "author":"Unknow",
                "description":"Unknow"
            },
            "data":[]
        }
        Recording = True
        showinfo(message="开始录制")
        #开启录制线程
        Thread(target=FunctionsClass.RecordYChart_,args=(RecordingYChart_Path,)).start()
        debug.info("[录制谱面]开始录制")
    
    #定义录制YChart的函数_主体
    def RecordYChart_(path:str):
        while True:
            sleep(0.01)
            #如果停止 --> 写入
            if not Recording:
                with open(path,"w",encoding="utf-8") as f:
                    f.write(dumps(Record_Data))
    
    #定义停止录制的函数
    def RecordYChart_Stop():
        global Recording
        #如果未开始录制
        if not Recording:
            showerror(message="未开始录制")
            return 1
        #有正在录制
        Recording = False
        showinfo(message="已停止录制")

    #系统托盘调用的函数 -- 返回GUI界面
    def backgui():
        FunctionsClass.WindowInAnimation()
        gui.deiconify()
        gui.update()
        #尝试关闭系统托盘
        try:
            icon.stop()
        except Exception:
            pass

    #定义隐藏至系统托盘的函数
    def To_System_Tray(thread:bool=False):
        if not thread:
            Thread(target=FunctionsClass.To_System_Tray,args=(True,)).start()
            return None
        FunctionsClass.WindowOutAnimation()
        #创建菜单项
        Menu_=()
        for i in Menu_All_:
            if not i=={"label":None,"command":None}:  #不是分割线
                if i=={"label":"隐藏至系统托盘","command":FunctionsClass.To_System_Tray}:  #是隐藏至系统托盘
                    Menu_+=(MenuItem("返回GUI界面",FunctionsClass.backgui),)
                else:
                    Menu_+=(MenuItem(i["label"],i["command"]),)
        def Temp_Function():
            global icon
            icon = Icon("name",Image.open("Icon"),
                        "离线原琴\nBy Bilibili qaq_fei\nqaq_fei@163.com",
                        Menu_)
            icon.run()
        Thread(target=Temp_Function).start()
    
    #定义通过谱面导出音频的函数_主体
    def OutPutWav_(OutPut_FilePath,show_gui=True):
        if not FunctionsClass.isOpenYChart():
            return 1
        if OutPut_FilePath=="":
            return 1
        OutPut_FilePath=FunctionsClass.Add_Extension(OutPut_FilePath,"wav")
        showinfo(message="点击确定开始生成")
        #定义进度条进度变量
        global Process_Value,Process_Widget,Process_Done,UserIsCancel
        Process_Value = 0.0
        def Temp_Function(OutPut_FilePath_,show_gui=show_gui):
            global Process_Value,Process_Widget,Process_Done,UserIsCancel

            #叠加音符声音
            try:
                obj = YChart_Type(YChart[1])
            except Exception as e:
                showerror(message=f"谱面解析错误:\n{e.__repr__()}")
                return 1
            
            match obj.version:
                case "1.0.0" | "1.0.1":
                    target_wav = AudioSegment.silent(duration=obj.data[-1]["time"] * 1000 + Pydub_Music_List[obj.data[-1]["note"] - 1].duration_seconds * 1000)
                    wavs = []
                    split_length = int(obj.data[-1]["time"] / 3)
                    if split_length == 0:
                        split_length = 1
                    for i in FunctionsClass.split_list(obj.data,split_length):
                        duration = i[-1]["time"] - i[0]["time"] + Pydub_Music_List[i[-1]["note"]-1].duration_seconds
                        duration *= 1000
                        wav_temp = AudioSegment.silent(duration=duration)
                        for j in i:
                            this_time = j["time"] - i[0]["time"]
                            wav_temp = wav_temp.overlay(Pydub_Music_List[j["note"]-1],this_time*1000) #why no add -1 ?
                        wavs.append({"obj":wav_temp,"time":i[0]["time"]})
                        Process_Value += 1 / (len(obj.data) / split_length) * 0.5 * 100
                    for i in wavs:
                        target_wav = target_wav.overlay(i["obj"],i["time"]*1000)
                        Process_Value += 1 / len(wavs) * 0.5 * 100
                    target_wav.export(OutPut_FilePath_,format="wav")
                case _:
                    never()
            Process_Done = True
        return lambda:Temp_Function(OutPut_FilePath)

    #定义通过谱面导出音频的函数
    def OutPutWav():
        global Process_Value,Process_Widget,Process_Done,UserIsCancel
        UserIsCancel=False
        Temp_Function=FunctionsClass.OutPutWav_(filedialog.asksaveasfilename(title="选择保存音频文件的路径",filetypes=[("wav音频",".wav")]))
        if Temp_Function == 1:
            return 1
        #创建进度条窗口
        Process_Done = False
        gui_jingdutiao = get_toplevel(title="Progressbar",
                                      resizable_ff=True,
                                      protocol_WM_DELETE_WINDOW=lambda:exec("global UserIsCancel ; UserIsCancel=True"),
                                      transient=gui,
                                      cursor="watch")
        gui.grab_set()
        gui.attributes("-disabled",True)
        Process_Widget = Progressbar(gui_jingdutiao,length=int(Display_size_width*0.35),maximum=100,value=0)
        Process_Widget.pack()
        Process_Widget.update()
        Thread(target=Temp_Function).start()
        while True:
            if Process_Value == "UserCancel":
                gui_jingdutiao.destroy()
                gui.attributes("-disabled",False)
                showinfo(message="已取消")
                break
            if Process_Done is False:
                if Process_Value > 100:
                    debug.warn("进度精度引发数值错误(>100),修正为100")
                    Process_Value = 100.0
                Process_Widget["value"] = Process_Value
                gui_jingdutiao.title("Progressbar("+str(Process_Value)+"%)")
                Process_Widget.update()
            else:
                debug.info("生成完毕,结束循环")
                gui_jingdutiao.destroy()
                gui.attributes("-disabled",False)
                showinfo(message="生成完成")
                break
    
    #定义通过谱面模拟键盘的函数
    def MoNiJianPan():
        global JiXuBoFan_keyboard
        #如果未打开谱面
        if not FunctionsClass.isOpenYChart():
            #中断函数
            debug.info("中断函数")
            return 1
        #提示
        if not askyesno(message="确定要继续吗?"):
            return 0
        showinfo(message="点击确定开始")
        if askyesno(message="是否需要离线原琴继续发出声音?"):
            JiXuBoFan_keyboard=True
        else:
            JiXuBoFan_keyboard=False
        def Temp_Function():
            global JiXuBoFan_keyboard
            global BreakYChartPlay

            BreakYChartPlay = False
            
            try:
                obj = YChart_Type(YChart[1])
            except Exception as e:
                showerror(message=f"谱面解析错误:\n{e.__repr__()}")
                return 1
            while True:
                match obj.version:
                    case "1.0.0" | "1.0.1":
                        index = -1
                        for i in obj:
                            index += 1
                            if index != 0:
                                sleep((i["time"] - obj.data[index - 1]["time"]) / PlaySpeed)
                            else:
                                sleep(i["time"] / PlaySpeed)
                            if BreakYChartPlay:
                                debug.info("Play Breaked.")
                                return None
                            FunctionsClass.keyInput(map_table[i["note"]])
                    case _:
                        never()
                if PlayLoop:
                    debug.info("[AnalogKeyboardInput]Play again.")
                else:
                    break
            debug.info("[AnalogKeyboardInput]Done.")
            JiXuBoFan_keyboard=True
        Thread(target=Temp_Function).start()
    
    #定义暂停/继续播放的类
    class ChangeBoFan:
        class keyboard:
            #暂停
            def stop():
                debug.info("声明全局变量:JiXuBoFan_keyboard")
                global JiXuBoFan_keyboard
                JiXuBoFan_keyboard=False
                debug.info("将JiXuBoFan_keyboard修改为False")
                showinfo(message="已禁用播放")
            #继续
            def go():
                debug.info("声明全局变量:JiXuBoFan_keyboard")
                global JiXuBoFan_keyboard
                JiXuBoFan_keyboard=True
                debug.info("将JiXuBoFan_keyboard修改为True")
                showinfo(message="已启用播放")
        class ychart:
            #暂停
            def stop():
                debug.info("声明全局变量:JiXuBoFan_ychart")
                global JiXuBoFan_ychart
                JiXuBoFan_ychart=False
                debug.info("将JiXuBoFan_ychart修改为False")
                showinfo(message="已禁用播放")
            #继续
            def go():
                debug.info("声明全局变量:JiXuBoFan_ychart")
                global JiXuBoFan_ychart
                JiXuBoFan_ychart=True
                debug.info("将JiXuBoFan_ychart修改为True")
                showinfo(message="已启用播放")
        class click:
            #暂停
            def stop():
                debug.info("声明全局变量:JiXuBoFan_click")
                global JiXuBoFan_click
                JiXuBoFan_click=False
                debug.info("将JiXuBoFan_click修改为False")
                showinfo(message="已禁用播放")
            #继续
            def go():
                debug.info("声明全局变量:JiXuBoFan_click")
                global JiXuBoFan_click
                JiXuBoFan_click=True
                debug.info("将JiXuBoFan_click修改为True")
                showinfo(message="已启用播放")
    
    #定义导出键盘谱的函数
    def OutPutJianPanPu():
        #如果未打开谱面
        if not FunctionsClass.isOpenYChart():
            #中断函数
            debug.info("中断函数")
            return 1
        OutPutJianPanPu_Path=filedialog.asksaveasfilename(title="请选择导出键盘谱的路径",filetypes=[("文本文件",".txt")])
        #判断是否为空
        if OutPutJianPanPu_Path=="":
            debug.info("文件路径为空")
            #中断函数
            debug.info("中断函数")
            return 0
        #添加后缀名
        debug.info("添加文件后缀名...")
        OutPutJianPanPu_Path=FunctionsClass.Add_Extension(OutPutJianPanPu_Path,"txt")
        #解析并导出
        debug.info("打开文件流")
        OutPutJianPanPu_Stream=open(OutPutJianPanPu_Path,"w")  #打开文件流
        debug.info("获取谱面数据...")
        OutPutJianPanPu_Text=YChart[1].split("\n")
        debug.info("删除第一项(bpm)...")
        del OutPutJianPanPu_Text[0]
        #计算进度条最小单位
        debug.info("按行数循环...")
        for i in OutPutJianPanPu_Text:
            if i=="" or i=="c":
                OutPutJianPanPu_Stream.write(" ")  #空
                continue
            if i[0]=="d":
                write_list=i.replace("d","").replace(" ","").split(",")
                write_list=[map_table[i] for i in write_list]
                OutPutJianPanPu_Stream.write("("+"".join(write_list)+")")
        #关闭文件流
        debug.info("关闭文件流...")
        OutPutJianPanPu_Stream.close()
        #提示
        showinfo(message="生成完成")
    
    #定义文件拖放到窗口的函数
    def TuoFan_File(files):
        #showerror(message="本版本已禁用此功能!")
        #debug.info("中断函数")
        #return 1
        def Temp_Function(files):
            global BoFanYChart_HavePath_Finish
            files_temp=[]
            #判断是否为文件夹
            for i in files:
                if isdir(i):
                    try:
                        files_temp+=FunctionsClass.GetAllFile(i)
                    except PermissionError as ErrorText:
                        debug.error("PermissionError:"+str(ErrorText))
                        showerror(message=ErrorText)
                else:
                    debug.info(f"{i}为文件")
                    files_temp+=[i]
            #替换
            files=files_temp
            #判断后缀名
            debug.info("判断后缀名...")
            for i in files:
                i:str
                if not i.endswith(".ychartx"):
                    files[files.index(i)]=None
            debug.info(str(files))
            #播放
            debug.info("播放...")
            #如果为空
            if files==[]:
                debug.info("列表为空")
                debug.info("中断函数")
                return 1
            if len(files)!=1:
                showinfo(message="即将开始播放\n播放完成后会弹出提示播放下一首\n播放列表:\n"+files.__repr__())
            for i in files:
                if i==None:
                    debug.info(str(i)+",跳过本次循环")
                    continue
                showinfo(message="播放YChart:\n"+i)
                debug.info("开始播放")
                Thread(target=lambda:FunctionsClass.BoFanYChart_HavePath(i)).start()
                #循环判断是否执行完毕
                debug.info("循环判断是否执行完毕...")
                while True:
                    sleep(0.05)
                    if BoFanYChart_HavePath_Finish:
                        debug.info("播放完毕:"+i)
                        break
        Thread(target=lambda:Temp_Function(files)).start()
        '''
        Fatal Python error: 
        PyEval_RestoreThread: the function must be called with the GIL held, 
        but the GIL is released (the current Python thread state is NULL)
        Python runtime state: initialized     2023.9.26 21:12 Fix!!!
        '''

    #键盘谱转YChart_1主体
    def Text_To_YChart_1_(input_text:str,
                          map_table_:dict={"Q":"1","W":"2","E":"3","R":"4","T":"5","Y":"6","U":"7",
                                          "A":"8","S":"9","D":"10","F":"11","G":"12","H":"13","J":"14",
                                          "Z":"15","X":"16","C":"17","V":"18","B":"19","N":"20","M":"21"}
                          ) -> tuple[list[dict[str,str|float]],float] | tuple[None,None] | tuple[str,None]:  #return (str,float) Dnoe. | return (None,None) Error. | return (str,None) User is cancel.
        try:
            bpm=get_value().get(master=gui,title="请输入谱面单个字符的时长(秒)",text="请输入谱面单个字符的时长(秒):",type="float")
            if bpm==None:
                debug.info("中断函数")
                return ("User is cancel.",None)
            bpm=60/bpm
            debug.info("替换字符...")
            input_text=input_text.replace("/"," ").replace("\\"," ").replace("\n","")
            output_text_list=[]
            input_text_temp=""
            is_in_tuple=False
            debug.info("遍历字符...")
            for i in input_text:
                try:
                    if i==" ":
                        #debug.info("[键盘谱转YChart]添加:c")
                        output_text_list+=["c\n"]
                    if is_in_tuple:
                        if i==")":
                            #debug.info("[键盘谱转YChart]结束和弦")
                            is_in_tuple=False
                            input_text_temp+="\n"
                            output_text_list+=[input_text_temp]
                            input_text_temp=""
                            continue
                        if len(input_text_temp)==0:
                            #debug.info("[键盘谱转YChart]添加:d "+str(map_table_[i]))
                            input_text_temp+="d "+str(map_table_[i])
                        else:
                            #debug.info("[键盘谱转YChart]添加:,"+str(map_table_[i]))
                            input_text_temp+=","+str(map_table_[i])
                        continue
                    if i=="(":
                        #debug.info("[键盘谱转YChart]开启和弦")
                        is_in_tuple=True
                        continue
                    for i2 in map_table_:
                        if i2==i:
                            #debug.info(f"[键盘谱转YChart]添加:d {map_table_[i2]}\n")
                            output_text_list+=[f"d {map_table_[i2]}\n"]
                except KeyError: #谱面里有奇怪的东西
                    continue
        except Exception:
            return (None,None)
        output_data = []  #不想改了 直接转格式(ychart -> ychartx)  管他...
        t = 0.0
        for line in output_text_list:
            line = line.replace("\n","")
            if "d" in line:
                for note in line.replace("d","").replace(" ","").split(","):
                    output_data.append({
                        "time":t,"note":int(note)
                    })
            t += 60 / bpm
        return (output_data,bpm)

    #键盘谱转YChart_1
    def Text_To_YChart_1():
        showinfo(message="支持的键盘谱格式示例(如谱面中含有回车将会去除 如谱面中含有\"/\"或\"\\\"将会修改为空格):\n(VAW) E /T Q /W (BSE) /T Q /(NDW) E /T Y /W (AGE) /H Q /(VAW) E /T Q /W (BSE) /T Q /(NDW) E /T Y /W (AGE) /H Q /(VS) D /G A /S (BD) /G A /(NS) D /G H /S (AD) /N A /(VS) D /G A /S (BD) /G A /(NS) D /G H /S (AD) /D G /(VAH)  /Q W /  (BSJ) /G F /(ND) G /J Q /  (BA) /Q J /(VAH)  /Q   /J (BSG) /  G /(ND)  /     /  (ZB) /D G /(VAH)  /Q W /  (BSJ) /G F /(ND) G /J Q /  (BA) /Q J /(VAH)  /Q   /J (BSG) /G G /(NDH)  /    /  (ZB) /H J /(VQ) A /(AF) J /H (BSJ) /Q  /N (DJ) /(DH) J /Q (BAJ) /G H /(VG) (ZA) /(NA) H /G (XBA) /S D /N  /  (AD) / (ZB) /H J /(VQ) A /(AF) J /H (BSJ) /Q  / N (DJ) /(DH) J /Q (BAW) /E R /  Q /Q E /W Q /Q  /    /    /    /E TE /(ZVW) (AQ) /(AFH)Q (AFW)/ (XB) /(SGE) TE /(CNW) (DQ) /(DH)Q (CNQ)/ (ZB) /(AGE) (BT)E /(ZVW) A /(AFE)T (AFT)/ Y(XB) /(SGT)R(BE) /(CN) (DW)E/(DT)YE(CNW)/E (ZB) /(AGE) (BT)E /(ZVW) (AQ) /(AFH)Q (AFW)/ (XB) /(SGE) TE /(CNW) (DQ) /(DH)Q (CNQ)/ (ZB) /(AGQ)J(BH)J /(ZVH) A /(AFW) (ZV)/J (XBH) /(SGJ) (BJ) /(ZVN) Q /(XBM)  /(CNA)  /XCNA  /(VS) D /G A /S (BD) /G A /(NS) D /G A /S (AD) /G A /(VS) D /G A /S (BD) /G A /(NS) D /G A /S D / QW/(VE) (AW)Q /(AFQ) HJ /Q (BSJ)H /(SG) (BD)G /(NH) (DJ)Q /(DJ)GGH /G (BA) /(AD)D(BF)G /(VH) (AJ)Q /(AFJ) QW /E (BSW)Q /(SJ) (BG)G /N QW /(ADE) W(ADE)/TY(NE)W /(BAE) QW /(VE) (AW)Q /(AFQ) HJ /Q (BSJ)H /(SG) (BG)G /(NH) (DJ)Q /(DJ)GGH / G(BA) /(AH) BG /V (AH) /(AF)Q  /W (BS)E /S (BW) /NQ  /(AD) (AD) /QW(NE) /(BAT) E /(VY) A /(AFT) R /E (BS) /(SW)E(BR) /NE(DW)Q /(DH)WER / E(BAW)Q /AH(BJ)Q /VJ(AH)G /(AF) G /H (BS)Q /S (BJ) /NG  /(AD) (ADH) /  N /(BA) B /(VY) A /(AFT) R /E (BS) /(SW)E(BR) /N D /(DE)WE / (BA) /A B /V A /(AF) R /E (BSW) /(SQ) (BQ) /(ZVBA)  /(BA)  (BA)/ (BA)(ZV)/(BA) (ZV) /(ZVBS)  /(BS)  (BS)/ (BS)(ZV)/(BD) (ZV) /(XBG) GG /(BSG)GG(XBG) /HH(XBH)H /(BSQ)QQQ /(XBW)WWW /(BSE)EE(XBE) /TT(XBT)T /E TE /(ZVW) (AQ) /(AFH)Q (AFW)/ (XB) /(SGE) TE /(CNW) (DQ) /(DH)Q (CNQ)/ (ZB) /(AGE) (BT)E /(ZVW) A /(AFE)T (AFT)/ Y(XB) /(SGT)R(BE) /(CN) (DW)E/(DT)YE(CNW)/E (ZB) /(AGE) (BT)E /(ZVW) (AQ) /(AFH)Q (AFW)/ (XB) /(SGE) TE /(CNW) (DQ) /(DH)Q (CNQ)/ (ZB) /(AGQ)J(BH)J /(ZVH) A /(AFW) (ZV)/J (XBG) /(SD) (BJ) /(ZVN) Q /(XBMQ)  /(CNA)  /XCNA  /(ZV) (AT) /(AFE)WQ(ZVW) /W (XBG) /(XD)S(BA)S /(CNS) (DT) /(DE)WQ(CNW) /W (ZBG) /(ZD)S(BA)S /(ZVS) (AT) /(AFE)WQ(ZVW) /W (XBG) /(XD)S(BA)S /(CNS) (DY) /(DT)RE(CNT) /T (ZBH) /(ZG)F(BD)G /(ZVG) (AT) /(AFE)WQ(ZVW) /W (XBG) /(XD)S(BA)S /(CNS) (DT) /(DE)WQ(CNW) /W (ZBG) /(ZD)S(BA)S /(ZVS) (AT) /(AFE)WQ(ZVW) /W (XBW) /(XE) (BR) /(XB) (BSW) /(BS) (BS) /(BS) (XB) /(XB) (XB) /(VAW) E /T Q /W (BSE) /T Q /(NDW) E /T Y /W (AGE) /H Q /(VAW) E /T Q /W (BSE) /T Q /(NDW) E /T Y /W (AGE) /D G /(VAH)  /Q W /  (BSJ) /G F /(ND) G /J Q /  (BA) /Q J /(VAH)  /Q   /J (BSG) /  G /(NS) S /S S /S (ZBS) /D G /(VAH)  /Q W /  (BSJ) /G F /(ND) G /J Q /  (BA) /Q J /(VAH)  /Q   /J (BSG) /G H /     /     /     /E TE /(ZVW) (AQ) /(AFH)Q (AFW)/ (XB) /(SGE) TE /(CNW) (DQ) /(DH)Q (CNQ)/ (ZB) /(AGE) (BT)E /(ZVW) A /(AFE)T (AFT)/ Y(XB) /(SGT)R(BE) /(CN) (DW)E/(DT)YE(CNW)/E (ZB) /(AGE) (BT)E /(ZVW) (AQ) /(AFH)Q (AFW)/ (XB) /(SGE) TE /(CNW) (DQ) /(DH)Q (CNQ)/ (ZB) /(AGQ)J(BH)J /(ZVH) A /(AFW) (ZV)/J (XBG) /(SD) (BJ) /(ZVN) Q /(XBM)  /(CNA)  /XCNA  /(ZVH) A /(AFH)HQ(ZV) /W (XB) /(SGE) (BQ) /(CNQ) D /(DHE)WQ(CN) /W (AG) /(AGT) (BE) /(ZVE) A /(AFQ) G(ZV)/H (XB) /(SG) (BF) /(CNG) D /(DH) (CN)/  (ZB) /(AG) B /(ZVH) A /(AFH)HQ(ZV) /W (XB) /(SGE) (BQ) /(CNQ) D /(DHE)WQ(CN) /W (AG) /(AGT) B /(ZVY) A /(AF) E(ZV)/W (XB) /(SG) (BQ)W/(CNE) D /(DH) W(CNQ)/Q (ZB) /(AG) B /(VAW) E /T Q /W (BSE) /T Q /(NDW) E /T Y /W (AGE) /H Q /(VAW) E /T Q /W (BSE) /T Q /(NDW) E /T Q /W (AGE) /T Q /W E /T Q /    /    /")
        input_path=filedialog.askopenfilename(title="打开键盘谱",filetypes=[("原琴键盘谱文件",".txt")])
        if input_path=="":
            return 1
        try:
            f=open(input_path,"r",encoding="utf-8")
        except FileNotFoundError:
            showerror(message="文件不存在!")
            return 1
        try:
            input_text=f.read()
        except UnicodeDecodeError:
            showerror(message="编码错误!")
            return 1
        f.close()
        output_path=filedialog.asksaveasfilename(title="请选择导出YChart路径",filetypes=[("原琴谱面文件",".ychartx")])
        if output_path=="":
            return 1
        output_path=FunctionsClass.Add_Extension(output_path,"ychartx")

        output_data,bpm=FunctionsClass.Text_To_YChart_1_(input_text)
        if (output_data,bpm) == (None,None):
            showerror(message="转化失败")
            return 1
        elif (output_data,bpm) == ("User is exit.",None):
            return 0  #取消了
        #写入
        output = {
            "meta":{
                "version":"1.0.0",
                "title":"Unknow",
                "create_time":time(),
                "from":"txt",
                "author":"Unknow",
                "description": "Convert txt to YChart JSON."
            },
            "data":output_data
        }
        f=open(output_path,"w")
        f.write(dumps(output))
        f.close()
        showinfo(message="转化成功")

    #键盘谱转YChart_2主体
    def Text_To_YChart_2_(input_text:str,
                          map_table_:dict={"Q":"1","W":"2","E":"3","R":"4","T":"5","Y":"6","U":"7",
                                           "A":"8","S":"9","D":"10","F":"11","G":"12","H":"13","J":"14",
                                           "Z":"15","X":"16","C":"17","V":"18","B":"19","N":"20","M":"21"}
                          ) -> tuple[str,float] | tuple[None,None] | tuple[str,None]:  #return (str,float) Dnoe. | return (None,None) Error. | return (str,None) User is exit.
        try:
            bpm=get_value().get(master=gui,title="请输入谱面\"按键精灵速度\"",text="请输入谱面\"按键精灵速度\" By BiliBili @呱呱能有什么坏心思:",type="float")
            if bpm==None:
                debug.info("中断函数")
                return ("User is exit.",None)
            bpm=(1/(bpm/1000))*60  #/1000=毫秒->秒  1/=每秒  *60=bpm  
            debug.info("替换字符...")
            input_text=input_text.replace(" ","").replace("\n","").replace("|","").replace("="," "*1).replace("-"," "*2).replace("+"," "*4)  #替换字符
            input_text=input_text.split(" ")  #分割
            output_text_list=[]
            for i in input_text:
                if i=="":
                    output_text_list+="c\n"
                else:
                    try:
                        output_text_list+="d "+",".join([map_table_[i2] for i2 in list(i)])+"\n"  # ",".join([map_table_[i2] for i2 in list(i)])  emm... "ABC" -> ["A","B","C"] -> ["8","19","17"] -> 8,19,17 -> "d 8,19,17\n"
                    except KeyError: #谱面里有奇怪的东西
                        continue
        except Exception:
            return (None,None)
        return (output_text_list,bpm)

    #键盘谱转YChart_2
    def Text_To_YChart_2():
        showinfo(message="支持的键盘谱格式示例(出处:BiliBili @呱呱能有什么坏心思 如谱面中含有回车或\"|\"和空格将会去除):\nXS++XS++XS+X+SW--X==N==XNS--XH--XN--X--XNS--XG--XN--X--VAF--VQ--VA--V--VAF--FQ--VA--V--XB--BS--BS--B--BSH--B--BSW--B--XN--XN--XN--XS==H==XNSQ--XNSW--XNSR-=T=XSY==S==XH--XF--NSG--XH--XH--XQ--NSW--XH--VG--VH--AF--VS--V--VH==H==AFH--VH--BSG--BH--SF--BS--B-=G=BH==H==SH--BH--XNG--XH--NSF==X====X==NASG--XH==X==AF-S-N-X-XNSH--XF--NSG--SH==X==SH--XQ--SHW--XH--VNAG--FH--AF==V==NS==Z==V--VH==H==AFH--VH--BNSG--BH--SF--BS==X==B-=G=BSH==H==SH--BH--XNG--XH--NSF==X====B==NASG--AH==X==AF-S-NGH-X-XHW--XFW--NSGR--XHR==W==XH--XAW--NS--XHQ--VGW--VHW--AFR--VWR==W==V--VHW==H==AH--VHQ--BGW--BHW--SF--BW--BR--BH==H==SHW--BHQ--XGW--XHW--NFQ--XW--XG--XH--NFR--XS--XAW--NSW--XFR--NHFR==W==X--NFW--X--NFQ--VAW--SW--VFR--AGR==W==V--AFW==G==V==F==SQ==A==BW--SGW--BF--AW==S==BFR==G==A--BSFW==G==AQ==F==XNSW--NSW--XAQ--NSW--NX--S--XHQW--S--XH--XFW--NSGR--XHY--XHT--XQR--NSW--XHR--VGW--VHR--AFT--VSY--V--VH==H==AFH--VH--BSGQ--BHW--SFR--BSY--BT--BHR==H==SHW--BHR--XNGW--XHR--NSTF==X==Y==X==NASG--XHQ==X==AFT-SR-NW-X-XNSH--XFW--NSGR--SHY==X==SHT--XQR--SHW--XHR--VNAGW--FHR--AFT==V==NSY==Z==VQ--VH==H==AFHY-T-VHR--BNSGT--BHT--SFT--BSR==X==BW-=T=BSHY==H==SHT--BHR--XNGT--XHT--NSFR==X==SW==B==NASG--AH==X==AF-S-NGH-X-XS--XF--XNSG--NH==X==NSG--XF--NS==X==VG==Z==VNA--VS--ZVNAF==V==G==V==NA--FH--ZVNAG==V==BF==X=G=BSH--BG--BF==X=G=SH==B==XG--BF--BS==X==A--XNS--SF--VASG==X==H==B==AFG--ZF--BAS==Z==AF==NA=V=XNH==Q==SW==H==XN==A=S=XNG==SH==XH==Q==SW==HR==XN==A=S=XF==G==VFH==Q==FW==R==AF==T=Y=VT==AFR==VW==H==VG==H==VAFQ=W=Q==GQ=H=XG==BSG=F=S==SF=G=H==BSF=G=NS==A=S=F==SG=F=S==BSF=G=H==BQ=W=R==BQ==H==VG=F=S==VA=S=F==VS=F=G==NSF=G=H==ZBAQ==S==AFW==H==NAHR==AQ=T=WY==N==XN==T=R=XSFW--")
        input_path=filedialog.askopenfilename(title="打开键盘谱",filetypes=[("原琴键盘谱文件",".txt")])
        #如果为空
        if input_path=="":
            debug.info("文件路径为空")
            #中断函数
            debug.info("中断函数")
            return 1
        #尝试打开文件
        debug.info("尝试打开文件...")
        try:
            f=open(input_path,"r",encoding="utf-8")
        except FileNotFoundError:  #文件不存在
            showerror(message="文件不存在!")
            #中断函数
            debug.info("中断函数")
            return 1
        #读取数据
        try:
            debug.info("读取数据...")
            input_text=f.read()
        except UnicodeDecodeError:
            showerror(message="编码错误!")
            debug.error("编码错误!")
            debug.error("中断函数")
            return 1
        #关闭文件流
        debug.info("关闭文件流...")
        f.close()
        output_path=filedialog.asksaveasfilename(title="请选择导出YChart路径",filetypes=[("原琴谱面文件",".ychartx")])
        #如果路径为空
        if output_path=="":
            debug.info("文件路径为空")
            #中断函数
            debug.info("中断函数")
            return 1
        #添加后缀名
        debug.info("添加文件后缀名...")
        output_path=FunctionsClass.Add_Extension(output_path,"ychart")
        #转化
        output_text_list,bpm=FunctionsClass.Text_To_YChart_2_(input_text)
        if (output_text_list,bpm)==(None,None):
            showerror(message="转化失败")
            return 1
        elif (output_text_list,bpm)==("User is exit.",None):
            return 0  #取消了
        #写入
        f=open(output_path,"w")
        f.write(f"bpm {bpm}\n")
        for i in output_text_list:
            f.write(i)
        f.close()
        showinfo(message="转化成功")
    
    #YChart转自动点击脚本 MuMu12
    def YChart_To_Auto_MuMu12(thread=False):
        #判断是否打开YChart
        if not YChart[0]:
            showerror(message="未打开谱面")
            debug.info("中断函数")
            return 1
        if not thread:
            Thread(target=lambda:FunctionsClass.YChart_To_Auto_MuMu12(True)).start()
            return 0
        output_filepath=filedialog.asksaveasfilename(title="请选择导出mmor文件路径",filetypes=[("MuMu12脚本文件",".mmor")])
        #如果路径为空
        if output_filepath=="":
            debug.info("文件路径为空")
            #中断函数
            debug.info("中断函数")
            return 1
        output_filepath=FunctionsClass.Add_Extension(output_filepath,"mmor")
        f=open(output_filepath,"w",encoding="utf-8")
        try:
            f.write(FunctionsClass.YChart_To_Auto_MuMu12_())
        except Exception:
            f.close()
            return 1
        f.close()
        showinfo(message="转化完成")
    
    #YChart转自动点击脚本 MuMu12_主体
    def YChart_To_Auto_MuMu12_():
        code = {"actions":[],
                "info":{}}
        try:
            obj = YChart_Type(YChart[1])
            #解析谱面
            pos_list=[(0.264583,0.314352),
                      (0.26224,0.503704),
                      (0.259375,0.688426),
                      (0.263802,0.894907),
                      (0.259896,1.08519),
                      (0.261979,1.2787),
                      (0.263281,1.46944),
                      (0.176302,0.3125),
                      (0.177865,0.501852),
                      (0.176042,0.694444),
                      (0.176042,0.893056),
                      (0.177083,1.07824),
                      (0.176563,1.2838),
                      (0.173177,1.46944),
                      (0.0908854,0.310648),
                      (0.0895833,0.506019),
                      (0.0882813,0.700463),
                      (0.0880208,0.89537),
                      (0.0888021,1.08056),
                      (0.0903646,1.27361),
                      (0.0888021,1.46574)]
            
            match obj.version:
                case "1.0.0" | "1.0.1":
                    code["actions"] += [{"data":r"{\"cmd\":\"detect_app\",\"params\":{\"app\":\"原神\",\"package\":\"com.miHoYo.ys.mi\"}}",
                                        "extra1":"",
                                        "extra2":"",
                                        "timing":0,
                                        "type":"vcontrol"}]
                    code["info"].update({"create_time":int(time()*1000),
                                        "package_name":"com.miHoYo.ys",
                                        "resolution_x":Display_size_real[0],
                                        "resolution_y":Display_size_real[1],
                                        "total_running_time":obj.data[-1]["time"]*1000+1000})
                    note=0
                    index = -1
                    for i in obj:
                        note += 1
                        index += 1
                        if index != 0:
                            timing = (i["time"] - obj.data[index-1]["time"]) * 1000
                        else:
                            timing = i["time"] * 1000
                        code["actions"] += [{"data":"press_rel:"+str(pos_list[i["note"]-1]).replace(" ",""),
                                            "extra1":str(note),
                                            "extra2":"",
                                            "timing":timing,
                                            "type":"touch"},
                                            {"data":"release",
                                            "extra1":str(note),
                                            "extra2":"",
                                            "timing":1,
                                            "type":"touch"}]
                    code["actions"] += [{"data":"reset",
                                        "extra1":"",
                                        "extra2":"",
                                        "timing":100,
                                        "type":"touch"}]
                case _:
                    never()
        except Exception as e:
            showerror(message=f"谱面解析错误:\n{e.__repr__()}")
            raise e
        return dumps(code)
    
    #修改窗口大小
    def SetWindowSize(width=None):
        if width is None:
            width=get_value().get(master=gui,title="请输入窗口宽度",text="请输入窗口宽度:",type="int")
            if width is None:
                return 0
            if width<15:
                showerror(message="窗口宽度不能小于15")
                return 1
        gui.geometry(f"{width}x{int(width/16*9)}")
        gui.update()
        init_image()
        init_down_effect_image()
        init_mouse_effect_image()
        gui.deiconify()
    
    #定义修改音频的函数 type=1~3
    def Change_Audio(type:int):
        if not askyesno(message="确定要修改吗?"):
            return 0
        system(f"start Change_Audio.exe {type}")
    
    #全屏/取消全屏
    def set_fullscreen(full=True):
        if full:
            gui.attributes("-fullscreen",True)
            FunctionsClass.SetWindowSize(screen_width)
        else:
            gui.attributes("-fullscreen",False)
            FunctionsClass.SetWindowSize(int(Display_size_width*0.75))
    
    #绑定事件用的 f11/esc
    def set_fullscreen_(from_:str):
        global fullscreen
        if from_=="f11":
            fullscreen=not fullscreen
            FunctionsClass.set_fullscreen(fullscreen)
        elif from_=="esc":
            if not fullscreen:
                return None
            else:
                fullscreen=not fullscreen
                FunctionsClass.set_fullscreen(fullscreen)
    
    #设置播放速度
    def SetPlaySpeed(v):
        global PlaySpeed
        PlaySpeed=round(float(v),2)
        PlaySpeed_Scale_Label["text"] = PlaySpeed_Scale_Label_Text+f"(目前为{PlaySpeed:.2f}): "
    
    #节拍器Bpm
    def SetMetronomeBpm(v):
        global MetronomeBpm
        MetronomeBpm=round(float(v),1)
        MetronomeBpm_Scale_Label["text"] = MetronomeBpm_Scale_Label_Text+f"(目前为{MetronomeBpm}): "
    
    #显示设置的窗口
    def DisplaySettingWindow():
        global SettingWindow
        global SettingLabelFrameBlock_1
        global PlaySpeed_Scale,PlaySpeed_Scale_Label
        global WindowTransparent_Scale,WindowTransparent_Scale_Label
        global BreakYChartPlay,BreakYChartPlayButton
        global ChangeCanvasBackgroundButton
        global CanvasBackgroundGaussianBlurRadius_Scale,CanvasBackgroundGaussianBlurRadius_Scale_Label
        global PlayLoopCheckButtonVar,PlayLoopCheckButton,ReLoadCanvasButton
        global ReStartToAdminButton
        global MetronomeCheckButtonVar,MetronomeCheckButton
        global MetronomeBpm_Scale,MetronomeBpm_Scale_Label
        global ShowEffectCheckButtonVar,ShowEffectCheckButton

        try:
            PlaySpeed_Scale.destroy()
            PlaySpeed_Scale_Label.destroy()
            WindowTransparent_Scale.destroy()
            WindowTransparent_Scale_Label.destroy()
            BreakYChartPlayButton.destroy()
            ChangeCanvasBackgroundButton.destroy()
            CanvasBackgroundGaussianBlurRadius_Scale.destroy()
            CanvasBackgroundGaussianBlurRadius_Scale_Label.destroy()
            PlayLoopCheckButton.destroy()
            ReLoadCanvasButton.destroy()
            ReStartToAdminButton.destroy()
            MetronomeCheckButton.destroy()
            MetronomeBpm_Scale.destroy()
            MetronomeBpm_Scale_Label.destroy()
            ShowEffectCheckButton.destroy()
            SettingLabelFrameBlock_1.destroy()
            SettingWindow.destroy()
        except (NameError,TclError):
            pass

        SettingWindow = CreateAeroWindow.CreateAeroWindow(tk=Toplevel,resizable=(False,False))
        SettingWindow.iconbitmap("Icon")
        SettingWindow.deiconify()

        SettingLabelFrameBlock_1 = LabelFrame(SettingWindow,text="离线原琴 -- 设置 -- Block_1")

        PlaySpeed_Scale = Scale(SettingLabelFrameBlock_1,from_=0.5,to=10.0,command=FunctionsClass.SetPlaySpeed)  #播放速度条
        PlaySpeed_Scale_Label = Label(SettingLabelFrameBlock_1,text=PlaySpeed_Scale_Label_Text+"(目前为1.00): ")

        WindowTransparent_Scale = Scale(SettingLabelFrameBlock_1,from_=0.25,to=1.0,command=lambda v:gui.attributes("-alpha",float(v)))
        WindowTransparent_Scale_Label = Label(SettingLabelFrameBlock_1,text=WindowTransparent_Scale_Label_Text+":")

        CanvasBackgroundGaussianBlurRadius_Scale = Scale(SettingLabelFrameBlock_1,from_=0,to=CanvasBackgroundGaussianBlurRadiusScaleMaxVar)
        CanvasBackgroundGaussianBlurRadius_Scale_Label = Label(SettingLabelFrameBlock_1,text=CanvasBackgroundGaussianBlurRadius_Scale_Label_Text+":")

        BreakYChartPlayButton=Button(SettingLabelFrameBlock_1,text="停止所有正在播放的谱面",command=lambda:exec("global BreakYChartPlay ; BreakYChartPlay = not BreakYChartPlay ; debug.info(\"BreakYChartPlay.\")"))
        ChangeCanvasBackgroundButton = Button(SettingLabelFrameBlock_1,text="修改窗口背景",command=FunctionsClass.ChangeCanvasBackground)

        PlayLoopCheckButtonVar = BooleanVar(SettingLabelFrameBlock_1,value=PlayLoop)
        PlayLoopCheckButton = Checkbutton(SettingLabelFrameBlock_1,text="循环播放 tips:包括所有",onvalue=True,offvalue=False,variable=PlayLoopCheckButtonVar,command=lambda:exec("global PlayLoop ; PlayLoop = PlayLoopCheckButtonVar.get() ; debug.info(f\"PlayLoop:{PlayLoop}\")"))

        ReStartToAdminButton = Button(SettingLabelFrameBlock_1,text="以管理员身份重新启动",command=lambda:Thread(target={
            True:lambda:(
                    ReStartToAdminButton.config(text="目前已是管理员身份",state="disabled"),
                    ReStartToAdminButton.update(),
                    sleep(0.5),
                    ReStartToAdminButton.config(text="以管理员身份重新启动",state="normal"),
                    ReStartToAdminButton.update()
                ),
            False:lambda:None
        }[use_admin()]).start())

        ReLoadCanvasButton = Button(SettingLabelFrameBlock_1,text="重新加载窗口",command=lambda:(
            ReLoadCanvasButton.config(text="重新加载窗口ing...",state="disabled"),
            ReLoadCanvasButton.update(),
            gui.iconify(),
            init_image(),
            init_down_effect_image(),
            init_mouse_effect_image(),
            gui.deiconify(),
            ReLoadCanvasButton.config(text="重新加载窗口",state="normal"),
            ReLoadCanvasButton.update(),
        ))

        MetronomeCheckButtonVar = BooleanVar(SettingLabelFrameBlock_1,value=OpenMetronome)
        MetronomeCheckButton = Checkbutton(SettingLabelFrameBlock_1,text="启用节拍器",onvalue=True,offvalue=False,variable=MetronomeCheckButtonVar,command=lambda:exec("global OpenMetronome ; OpenMetronome = MetronomeCheckButtonVar.get() ; debug.info(f\"OpenMetronome:{OpenMetronome}\")"))

        MetronomeBpm_Scale = Scale(SettingLabelFrameBlock_1,from_=MetronomeBpm_Scale_Min,to=MetronomeBpm_Scale_Max,command=FunctionsClass.SetMetronomeBpm)
        MetronomeBpm_Scale_Label = Label(SettingLabelFrameBlock_1,text=MetronomeBpm_Scale_Label_Text+f"(目前为{MetronomeBpm}): ")

        ShowEffectCheckButtonVar = BooleanVar(SettingLabelFrameBlock_1,value=ShowEffect)
        ShowEffectCheckButton = Checkbutton(SettingLabelFrameBlock_1,text="启用点击动画",onvalue=True,offvalue=False,variable=ShowEffectCheckButtonVar,command=lambda:exec("global ShowEffect ; ShowEffect = ShowEffectCheckButtonVar.get() ; debug.info(f\"ShowEffect:{ShowEffect}\")"))

        PlaySpeed_Scale.set(PlaySpeed)
        WindowTransparent_Scale.set(gui.attributes("-alpha"))
        CanvasBackgroundGaussianBlurRadius_Scale.set(CanvasBackgroundGaussianBlurRadius)
        MetronomeBpm_Scale.set(MetronomeBpm)

        CanvasBackgroundGaussianBlurRadius_Scale.bind("<ButtonRelease-1>",lambda e:(
                    int(float(e.widget.get())) != CanvasBackgroundGaussianBlurRadius  #40 -> 40.4 (No!) 40 -> 41 (Yes!)
                    and (
                        exec("global CanvasBackgroundGaussianBlurRadius ; CanvasBackgroundGaussianBlurRadius = float(e.widget.get())"),
                        FunctionsClass.LoadCanvasBackground()
                    )
                ))

        PlaySpeed_Scale_Label.grid(row=0,column=0,sticky="nw")
        PlaySpeed_Scale.grid(row=0,column=1,sticky="nw")
        WindowTransparent_Scale_Label.grid(row=1,column=0,sticky="nw")
        WindowTransparent_Scale.grid(row=1,column=1,sticky="nw")
        BreakYChartPlayButton.grid(row=2,column=0,sticky="nw")
        ChangeCanvasBackgroundButton.grid(row=3,column=0,sticky="nw")
        CanvasBackgroundGaussianBlurRadius_Scale_Label.grid(row=4,column=0,sticky="nw")
        CanvasBackgroundGaussianBlurRadius_Scale.grid(row=4,column=1,sticky="nw")
        PlayLoopCheckButton.grid(row=5,column=0,sticky="nw")
        ReLoadCanvasButton.grid(row=6,column=0,sticky="nw")
        ReStartToAdminButton.grid(row=7,column=0,sticky="nw")
        MetronomeCheckButton.grid(row=8,column=0,sticky="nw")
        MetronomeBpm_Scale_Label.grid(row=9,column=0,sticky="nw")
        MetronomeBpm_Scale.grid(row=9,column=1,sticky="nw")
        ShowEffectCheckButton.grid(row=10,column=0,sticky="nw")

        SettingLabelFrameBlock_1.pack(padx=15,pady=25)
    
    #修改背景
    def ChangeCanvasBackground(ImageFilePath=None):
        global BackgroundImage
        
        if ImageFilePath is None:
            ImageFilePath = filedialog.askopenfilename(title="请选择背景图片",filetypes=[("图片文件","*.png *.jpg *.jpeg *.bmp *.gif")])
            if ImageFilePath == "":
                return None
        
        try:
            BackgroundImage = Image.open(ImageFilePath)
        except Exception as e:
            debug.error(message=f"ChangeCanvasBackground LoadImage Error: {e.__repr__()}")
        FunctionsClass.LoadCanvasBackground()
    
    #加载背景
    def LoadCanvasBackground():
        global BackgroundImageTk

        try:
            BackgroundImage
        except NameError:  #No have Background
            return None
        
        CanvasWidth = Canvas.winfo_width(ImgCanvas)
        CanvasHeight = Canvas.winfo_height(ImgCanvas)

        BackgroundImageTk = ImageTk.PhotoImage(
            BackgroundImage.resize(
                    (
                        CanvasWidth,
                        int(CanvasWidth * (BackgroundImage.height / BackgroundImage.width))
                    )
                ).filter(ImageFilter.GaussianBlur(radius=CanvasBackgroundGaussianBlurRadius))
        )

        ImgCanvas.update()
        ImgCanvas.delete("Background")
        ImgCanvas.create_image(CanvasWidth / 2,CanvasHeight / 2,image=BackgroundImageTk,tag="Background")
        ImgCanvas.lower("Background")
    
    #节拍器
    def MetronomeMain():
        while True:
            sleep(60 / MetronomeBpm)
            if OpenMetronome:
                Thread(target=PlaySound.Play,args=(MetronomeData.MetronomeData,)).start()

class PlayButtonSound:
    def PlayByIntKey(key:int,type:None|str=None):
        debug.info(f"[按键点击]按下\"{map_table[key]}\"")
        #调用特效
        Thread(target=lambda:FunctionsClass.effect(key)).start()
        #判断是否需要播放
        if type=="keyboard":
            if JiXuBoFan_keyboard:
                Thread(target=lambda:playsound(key)).start()
        elif type=="ychart":
            if JiXuBoFan_ychart:
                Thread(target=lambda:playsound(key)).start()
        elif type=="click":
            if JiXuBoFan_click:
                Thread(target=lambda:playsound(key)).start()
        else:
            Thread(target=lambda:playsound(key)).start()
        if Recording:
            Record_Data["data"].append({
                "time":time() - Record_Data["meta"]["create_time"],
                "note":key
            })
    #定义点击函数
    def Click(event):
        #修正
        event.x -= imgCanvas_x
        event.y -= imgCanvas_y
        #打印点击位置
        debug.info(f"[按键点击]鼠标点击了 x={event.x} y={event.y}")
        #判断是否超出范围
        if event.x<0 or event.y<0 or event.x>imgCanvas_width or event.y>imgCanvas_height:
            debug.info("[按键点击]超出范围")
            return 0
        #判断点击的按键
        for i in [0,1,2,3,4,5,6]:
            if imgCanvas_width/7*i < event.x < imgCanvas_width/7*(i+1):  #第i+1列
                if event.y < imgCanvas_height/3*1:  #第1行
                    PlayButtonSound.PlayByIntKey(key=i+1,type="click")
                    return 0
                if event.y < imgCanvas_height/3*2:  #第2行
                    PlayButtonSound.PlayByIntKey(key=i+8,type="click")
                    return 0
                if event.y < imgCanvas_height/3*3:  #第3行
                    PlayButtonSound.PlayByIntKey(key=i+15,type="click")
                    return 0

debug.info("加载按键监听...")
GlobalHotKeys_Keys={}
for i in range(1,22):
    GlobalHotKeys_Keys.update({map_table[i].lower():eval(f"lambda:PlayButtonSound.PlayByIntKey(key={i},type=\"keyboard\")")})
GlobalHotKeys(GlobalHotKeys_Keys).start()
debug.info("按键监听加载成功")

debug.info("加载窗口...")
gui.iconbitmap("Icon")
gui.geometry(f"{int(Display_size_width*0.75)}x{int(Display_size_width*0.75/16*9)}")
gui.resizable(False,False)
gui.protocol("WM_DELETE_WINDOW",FunctionsClass.close)
windll.gdi32.AddFontResourceW("./font.ttf")
gui.bind("<KeyRelease-F11>",lambda x:FunctionsClass.set_fullscreen_("f11"))
gui.bind("<Escape>",lambda x:FunctionsClass.set_fullscreen_("esc"))
gui.update()
window_width = gui.winfo_width()
window_height = gui.winfo_height()
window_x = gui.winfo_x()
window_y = gui.winfo_y()
while True:
    #加载图片
    try:
        def init_image():
            global Img,Photo,ImgCanvas
            global Image_width,Image_height
            global Image_width_,Image_height_
            global imgCanvas_width,imgCanvas_height
            global imgCanvas_x,imgCanvas_y
            
            try:
                ImgCanvasBak = ImgCanvas
            except NameError:
                pass

            debug.info("加载图片...")
            try:
                Img=Image.open("Image")
            except Exception:
                showerror(message="图片文件加载失败!请使用Change_Audio.exe进行恢复!")
                FunctionsClass.close()
            Image_width,Image_height=Img.size
            Image_width_,Image_height_=Image_width,Image_height #做个备份 分割图片是要用
            Photo=ImageTk.PhotoImage(Img.resize((int(window_width*0.65),int(window_width*0.65*(Image_height/Image_width)))),master=gui)
            Image_width,Image_height=int(window_width*0.65),int(window_width*0.65*(Image_height/Image_width))
            ImgCanvas=Canvas_Img(gui,
                                 width=window_width,
                                 height=window_height)
            ImgCanvas.config(highlightthickness=0)

            #显示
            ImgCanvas.place(x=0,y=0)
            imgCanvas_width = ImgCanvas.winfo_width()
            imgCanvas_height = ImgCanvas.winfo_height()
            imgCanvas_x = ImgCanvas.winfo_x()
            imgCanvas_y = ImgCanvas.winfo_y()
            ImgCanvas.update()
            ImgCanvas.create_image(imgCanvas_x,imgCanvas_y,anchor="nw",image=Photo,tag="Image")
            FunctionsClass.LoadCanvasBackground()
            try:
                init_ellipse_effect_image()  #定义在下面
            except NameError:
                pass

            debug.info(f"绑定图片组件({ImgCanvas})事件...")
            ImgCanvas.bind("<Button-1>",PlayButtonSound.Click)
            ImgCanvas.bind("<Motion>",FunctionsClass.effect_mouse)
            ImgCanvas.bind("<Leave>",FunctionsClass.effect_mouse)
            ImgCanvas.bind("<Configure>",ConfigureUpdate)

            try:
                ImgCanvasBak.destroy()
            except NameError:
                pass
        init_image()
        #加载文件监听
        class Img_Handler(FileSystemEventHandler):
            def on_any_event(self,event):
                if not (True in [".\\Image"==eval(f"event.{i}") for i in dir(event)]):  #不是Image
                    return 0
                if event.event_type=="deleted": #删除
                    return 0
                sleep(0.2) #防止未复制完成
                if exists(".\\Image") and (not event.is_directory):
                    init_sound_data()
                    init_image()
                    init_mouse_effect_image()
                    debug.info("刷新图片成功!")
        event_handler=Img_Handler()
        Observer_=Observer()
        Observer_.schedule(event_handler,path=".\\",recursive=False)
        Observer_.start()
    except ValueError as ErrorText:
        ImgCanvas=Canvas_Img()  #防止报错
        debug.error("显示器分辨率过低,无法显示窗口!\nErrorText:"+str(ErrorText))
        debug.info("隐藏窗口...")
        gui.withdraw()
        showerror(message="显示器分辨率过低,无法显示窗口!")
        try:
            debug.info("尝试关闭Img(.\\Image)文件流")
            Img.close()
        except Exception:
            debug.info("关闭Img(.\\Image)文件流失败")
        if not askyesno(message="是否要在后台运行离线原琴?"):
            debug.info("选择为no,退出程序...")
            FunctionsClass.close()
        showinfo(message="离线原琴将隐藏至系统托盘")
        def Error_To_System_Tray():
            debug.info("定义系统托盘菜单列表...")
            Menu_=(MenuItem('重启至GUI界面',FunctionsClass.reopen),MenuItem('退出',lambda:windll.kernel32.ExitProcess(0)))
            debug.info("系统托盘菜单列表:"+str(Menu_))
            icon=Icon("name",Image.open("Icon"),
                    "离线原琴\nBy Bilibili qaq_fei\nqaq_fei@163.com",
                    Menu_)
            debug.info("创建系统托盘...")
            gui.withdraw()
            Thread(target=icon.run).start()
    break

debug.info("定义窗口顶部菜单...")
Menu_All=tkinter_Menu(gui)
debug.info("定义窗口顶部菜单的子菜单...")
Menu=tkinter_Menu(gui,tearoff=False,activebackground="#90C8F6",activeforeground="black")
Menu_Change_Audio=tkinter_Menu(gui,tearoff=False,activebackground="#90C8F6",activeforeground="black")
debug.info("将子菜单添加到父菜单...")
Menu_All.add_cascade(label="选项",menu=Menu)
Menu_All.add_cascade(label="修改资源",menu=Menu_Change_Audio)

Menu_All_=[{"label":"打开谱面文件","command":FunctionsClass.OpenYChart,"accelerator":"Ctrl+O|<Control-o>"},
           {"label":"播放谱面文件","command":FunctionsClass.PlayChart,"accelerator":"Ctrl+P|<Control-p>"},
           {"label":"以midi方式播放谱面文件","command":FunctionsClass.PlayChart_ByMidi,"accelerator":"Ctrl+Shift+P|<Control-P>"}, #Shift + p -> P
           {"label":"通过谱面文件导出音频","command":FunctionsClass.OutPutWav},
           {"label":"通过谱面文件模拟键盘","command":FunctionsClass.MoNiJianPan},
           {"label":"通过谱面文件生成键盘谱","command":FunctionsClass.OutPutJianPanPu},
           {"label":None,"command":None},
           {"label":"键盘谱转YChart Type: 含 空格 (  ) 字母","command":FunctionsClass.Text_To_YChart_1},
           {"label":"键盘谱转YChart Type: 含 字母 + - =","command":FunctionsClass.Text_To_YChart_2},
           {"label":None,"command":None},
           {"label":"YChart转自动点击脚本 MuMu12","command":FunctionsClass.YChart_To_Auto_MuMu12},
           {"label":None,"command":None},
           {"label":"录制谱面文件","command":FunctionsClass.RecordYChart},
           {"label":"停止录制谱面文件","command":FunctionsClass.RecordYChart_Stop},
           {"label":None,"command":None},
           {"label":"启用播放_键盘","command":FunctionsClass.ChangeBoFan.keyboard.go},
           {"label":"禁用播放_键盘","command":FunctionsClass.ChangeBoFan.keyboard.stop},
           {"label":"启用播放_点击","command":FunctionsClass.ChangeBoFan.click.go},
           {"label":"禁用播放_点击","command":FunctionsClass.ChangeBoFan.click.stop},
           {"label":"启用播放_谱面播放","command":FunctionsClass.ChangeBoFan.ychart.go},
           {"label":"禁用播放_谱面播放","command":FunctionsClass.ChangeBoFan.ychart.stop},
           {"label":None,"command":None},
           {"label":"设置窗口置顶","command":lambda:(gui.attributes("-topmost",True),showinfo(message="设置窗口置顶成功"))},  #lambda : (func,func,......)  通过元组调用多函数 ... [] () {} print(func,func,...) 都行
           {"label":"取消窗口置顶","command":lambda:(gui.attributes("-topmost",False),showinfo(message="取消窗口置顶成功"))},
           {"label":"设置窗口大小","command":FunctionsClass.SetWindowSize},
           {"label":None,"command":None},
           {"label":"隐藏至系统托盘","command":FunctionsClass.To_System_Tray},
           {"label":"设置","command":FunctionsClass.DisplaySettingWindow,"accelerator":"Ctrl+T|<Control-t>"},
           {"label":"重启","command":FunctionsClass.reopen},
           {"label":"退出","command":FunctionsClass.close},
           {"label":None,"command":None}]

#添加选项
for i in Menu_All_:
    if "accelerator" in i:
        Menu.add_command(label=i["label"],command=i["command"],accelerator=i["accelerator"].split("|")[0])
        gui.bind(i["accelerator"].split("|")[1],FunctionsClass._GetBindCommand(i["command"]))
    else:
        if i=={"label":None,"command":None}:  #添加分割
            Menu.add_separator()
        else:
            Menu.add_command(label=i["label"],command=i["command"])

Menu_Change_Audio.add_command(label="风物之诗琴",command=lambda:FunctionsClass.Change_Audio(type=1))
Menu_Change_Audio.add_command(label="老旧的诗琴",command=lambda:FunctionsClass.Change_Audio(type=2))
Menu_Change_Audio.add_command(label="镜花之琴",command=lambda:FunctionsClass.Change_Audio(type=3))
gui.bind("<Control-e>",FunctionsClass._GetBindCommand(FunctionsClass.Editer))

debug.info("添加菜单到窗口...")
gui.config(menu=Menu_All)
debug.info("添加菜单到窗口成功")

gui.update()
debug.info("窗口大小:"+str(window_width)+"x"+str(window_height))

#提前加载其他GUI界面
pass

#加载文件拖放功能
hook_dropfiles(gui.winfo_id(),FunctionsClass.TuoFan_File)

#特效图片1
def init_down_effect_image():
    global effect_image

    Canvas_width = imgCanvas_width
    Canvas_height = imgCanvas_height

    x1 = Canvas_width / 7 * effect_offset[1][0]
    y1 = Canvas_height / 3 * effect_offset[1][1]
    x2 = Canvas_width / 7 - (Canvas_width / 7 * effect_offset[1][2])
    y2 = Canvas_height / 3 - (Canvas_height / 3 * effect_offset[1][3])

    effect_image_mask = Image.new("RGBA",(int(x2 - x1 + 2),int(y2 - y1 + 2)),"#00000000")
    effect_image_mask_draw:ImageDraw.ImageDraw
    effect_image_mask_draw = ImageDraw.Draw(effect_image_mask)
    effect_image_mask_draw.ellipse((0,0,int(x2 - x1 + 2),int(y2 - y1 + 2)),fill="#000000FF")

    effect_image_ = Image.new('RGBA',(int(x2 - x1 + 2),int(y2 - y1 + 2)),"#DDFFFF77")

    effect_image = Image.new("RGBA",(int(x2 - x1 + 2),int(y2 - y1 + 2)),"#000000FF")
    effect_image.paste(effect_image_,(0,0,int(x2 - x1 + 2),int(y2 - y1 + 2)),effect_image_mask)

    for x in range(effect_image.width): #Delete black
        for y in range(effect_image.height):
            data = effect_image.getpixel((x,y))
            if data[0:-1] == (0,0,0):
                effect_image.putpixel((x,y),(0,0,0,0))

    effect_image = ImageTk.PhotoImage(effect_image)

init_down_effect_image()


#特效图片2
def init_mouse_effect_image():
    global effect_image_mouse_list,effect_image_mouse_list_CanvasId
    Canvas_width=imgCanvas_width
    Canvas_height=imgCanvas_height
    effect_image_mouse_=Image.open("Image")
    effect_image_mouse_list=[]
    for i in range(1,22):
        box=(int((map_table[2000+i]-1)*Image_width_/7),  #加"_"的是原始的
            int((map_table[1000+i]-1)*Image_height_/3),
            int(map_table[2000+i]*Image_width_/7),
            int(map_table[1000+i]*Image_height_/3))
        effect_image_mouse_temp=effect_image_mouse_.crop(box)
        effect_image_mouse_temp=effect_image_mouse_temp.resize((int(Image_width/7*1.05),int(Image_height/3*1.05)))
        effect_image_mouse_list+=[ImageTk.PhotoImage(effect_image_mouse_temp)]
    effect_image_mouse_list_CanvasId_Temp=[]
    for key in range(1,22):  #提前生成 减少性能开销
        x1=Canvas_width/7*(map_table[2000+key]-1)-Canvas_width/7*0.025
        y1=Canvas_height/3*(map_table[1000+key]-1)-Canvas_height/3*0.025
        effect_image_mouse_list_CanvasId_Temp+=[ImgCanvas.create_image(imgCanvas_x+x1,
                                               imgCanvas_y+y1,
                                               anchor="nw",
                                               image=effect_image_mouse_list[key-1],tag="effect_mouse")]
        ImgCanvas.moveto(effect_image_mouse_list_CanvasId_Temp[-1],window_width,window_height)  #移走
    effect_image_mouse_list_CanvasId=effect_image_mouse_list_CanvasId_Temp

init_mouse_effect_image()


#特效图片3
def init_ellipse_effect_image():
    global ellipse_effect_image_list

    imgplussizex = 4  #抗锯齿
    key = 1
    Canvas_width=imgCanvas_width
    Canvas_height=imgCanvas_height
    size=Canvas_width / 7 * 0.85
    x1=Canvas_width/7 * effect_offset[key-1][0] * 2
    y1=Canvas_height/3 * effect_offset[key-1][1] * 2
    x2,y2=x1+size,y1+size
    img_size = int(size * 2) * imgplussizex
    ellipse_effect_image_list = []

    for n in range(init_ellipse_effect_image_list_num):
        debug.info(f"Loading ellipse_effect_image {n + 1}")
        alpha = 255 - int(n / init_ellipse_effect_image_list_num * 255)
        effect_img = Image.new("RGBA",(img_size,img_size),(0,0,0,0))
        effect_img_draw = ImageDraw.Draw(effect_img)
        effect_img_draw.ellipse([img_size / 4 + x1 * imgplussizex,
                                 img_size / 4 + y1 * imgplussizex,
                                 img_size / 4 + x2 * imgplussizex,
                                 img_size / 4 + y2 * imgplussizex],
                                 outline=(0x22,0xAA,0xFF,alpha),
                                 width=int(Canvas_width/175) * imgplussizex)
        x1 -= Canvas_width / 625
        y1 -= Canvas_width / 625
        x2 += Canvas_width / 625
        y2 += Canvas_width / 625
        
        ellipse_effect_image_list.append(ImageTk.PhotoImage(effect_img.resize((int(img_size / imgplussizex),)*2)))

init_ellipse_effect_image()

if CanvasBackgroundWillSet is not None:
    FunctionsClass.ChangeCanvasBackground(CanvasBackgroundWillSet)

def _update():
    while True:
        sleep(2.5)
        gui.update()
        gc.collect()

Thread(target=_update,daemon=True).start()

loading_label["text"]="加载完成!"
loading_label.update()
sleep(0.1)
loading_gui.destroy()
if (oth_window := windll.user32.FindWindowW(None,"离线原琴 ")) != 0: #1 " " important!
    windll.user32.SetWindowTextW(oth_window,"离线原琴  ") #2 " " important!
gui.title("离线原琴") #important!


#尝试执行options中的代码
try:
    for i in options["init_code"]:
        debug.warn(f"执行options.json中的代码: {i}")
        exec(i)
except BaseException:
    pass

def ConsoleCommand_Load(argv:list):
    if len(argv)==1:
        return None
    if len(argv)==2: #如: ["***.exe","***"]
        if exists(argv[1]) and isfile(argv[1]): #判断文件是否存在+是不是文件
            showinfo(message=f"点击确定播放YChart:{argv[1]}")
            FunctionsClass.OpenYChart_(argv[1])
            FunctionsClass.PlayChart()
    else:
        def _ConsoleCommand_Test_Many_YCharts(argv:list):
            for i in argv[1:]: #除了1 循环 判断是否全部YChart 是:播放 不是:return -1
                if not (exists(i) or isfile(i)):
                    return -1
            FunctionsClass.TuoFan_File(argv[1:]) #借助拖放文件的函数
        _ConsoleCommand_Test_Many_YCharts(argv)

Thread(target=lambda:ConsoleCommand_Load(argv)).start()

try:
    Error_To_System_Tray()
except NameError:
    pass

Thread(target=FunctionsClass.MetronomeMain,daemon=True).start()
Thread(target=FunctionsClass.WindowInAnimation,daemon=True).start()
gui.mainloop()   #进入主循环

'''
options.json: json,设置
            Display_size_width和Display_size_height: 属性类型为int 可设置虚假的分辨率 用于调整窗口大小 图片显示倍数
            init_code: 属性类型为list[str] emm... 为了方便? emm...  可能有危险?
            map_table: 属性类型为dict[str,str] 可设置按键映射 但不会改变图片的文字显示 如:{"Q":"1"} 即将1映射到Q
            CanvasBackgroundGaussianBlurRadius: 属性类型为int 背景模糊半径
            CanvasBackgroundWillSetPath: 属性类型为str 在启动时设置背景图
            OpenMetronome: 属性类型为bool 是否开启节拍器
            MetronomeBpm: 属性类型为int|float 节拍器速度
'''
