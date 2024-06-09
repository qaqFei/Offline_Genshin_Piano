from tkinter import Tk
from ctypes import POINTER,sizeof,windll,pointer,Structure,c_ulong
from sys import getwindowsversion
from win32api import GetWindowLong,SetWindowLong,RGB
from win32con import GWL_EXSTYLE,WS_EX_LAYERED,LWA_COLORKEY

windowsversion=getwindowsversion()

class ACCENT_POLICY(Structure):
    _fields_ = [
        ('AccentState',   c_ulong),
        ('AccentFlags',   c_ulong),
        ('GradientColor', c_ulong),
        ('AnimationId',   c_ulong),
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ('Attribute',  c_ulong),
        ('Data',       POINTER(ACCENT_POLICY)),
        ('SizeOfData', c_ulong),
    ]

def _setAeroEffect(hwnd):
    accentPolicy = ACCENT_POLICY()
    winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
    winCompAttrData.Attribute = 19
    winCompAttrData.SizeOfData = sizeof(accentPolicy)
    winCompAttrData.Data = pointer(accentPolicy)
    accentPolicy.AccentState = 3
    windll.user32.SetWindowCompositionAttribute(hwnd,pointer(winCompAttrData))

def CreateAeroWindow(width:int|None=None,height:int|None=None,
                     x:int=0,y:int=0,
                     fullscreen:bool=False,
                     bar=True,resizable:tuple=(True,True),
                     transient:Tk|None=None,
                     title:str="",tk=Tk) -> Tk:
    '''
    >>> AeroWindow = CreateAeroWindow(100,100)
    >>> AeroWindow.deiconify()
    >>> AeroWindow.mainloop()
    '''
    Aero=tk()
    Aero.geometry(f"+{int(Aero.winfo_screenwidth()*1.5)}+{int(Aero.winfo_screenheight()*1.5)}")
    Aero.resizable(*resizable)
    if transient is not None:
        try:
            Aero.transient(transient)
        except AttributeError:
            pass
    Aero.title("")
    if windowsversion.build >= 21380:  #w11
        Aero.title(title)
    bg="000001"
    Aero["bg"]=f"#{bg}"
    Aero.withdraw()

    exStyle=GetWindowLong(int(Aero.frame(),16), GWL_EXSTYLE)
    exStyle|=WS_EX_LAYERED
    SetWindowLong(int(Aero.frame(),16),GWL_EXSTYLE,exStyle)
    windll.user32.SetLayeredWindowAttributes(int(Aero.frame(),16),RGB(int(f"0x{bg[0:2]}",16),int(f"0x{bg[2:4]}",16),int(f"0x{bg[4:6]}",16)),0,LWA_COLORKEY)

    if width is not None and height is not None:
        Aero.geometry(f"{width}x{height}")
    
    Aero.geometry(f"+{x}+{y}")

    if fullscreen:
        Aero.attributes("-fullscreen",True)
    else:
        if not bar:
            Aero.overrideredirect(True)

    Aero.update()
    _setAeroEffect(int(Aero.frame(),16))

    Aero.attributes("-transparentcolor",f"#{bg}")

    return Aero