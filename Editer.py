#Run at python < 3.12
from tkinter import Tk,Toplevel,Canvas,Text,Label,Menu,Event
from tkinter.ttk import Entry,Button
from tkinter.messagebox import showinfo,showerror,askokcancel,askyesnocancel
from tkinter.filedialog import askopenfilename,asksaveasfilename
from json import loads,dumps
from ctypes import windll
from time import time,sleep
from math import pi,cos,ceil

from PIL import Image,ImageTk,ImageDraw,ImageFont,ImageFilter
Image.Image.putpixel
VERSION = "1.0.0"
NOTE_IMG = Image.open("editer_note.png")
FONT = ImageFont.truetype("./汉仪文黑-85W.ttf",size=NOTE_IMG.width/4)
Number = int|float
choose_call = {}
WheelAnimationTime = 0.2
WheelAnimationFps = 12
WheelAnimationGrX = int(WheelAnimationFps * WheelAnimationTime) + 1
z = 0.5
WheelAnimationGr = [z * cos(x / WheelAnimationGrX * pi) + z for x in range(0,WheelAnimationGrX)] ; del z
WheelAnimationGrSum = sum(WheelAnimationGr)
WheelAnimationGr = [x / WheelAnimationGrSum for x in WheelAnimationGr] ; del WheelAnimationGrSum
WheelAnimationStepTime = WheelAnimationTime / len(WheelAnimationGr)

class _cls:
    value:Number|None

def _get_note_img(note:int) -> Image.Image:
    img = NOTE_IMG.copy()
    draw_obj = ImageDraw.Draw(img)
    if note <= 7:
        draw_type = "down"
    elif note > 14:
        draw_type = "up"
    else:
        draw_type = "normal"
    draw_obj.text(
        (img.width/2,)*2,
        str({
            1:1,2:2,3:3,4:4,5:5,6:6,7:7,
            8:1,9:2,10:3,11:4,12:5,13:6,14:7,
            15:1,16:2,17:3,18:4,19:5,20:6,21:7
        }[note]),(99,174,167),
        FONT,anchor="mm" #mm = center
    )
    match draw_type:
        case "up":
            x,y = img.width/2, img.width*0.3
            r = img.width/20
            draw_obj.ellipse(
                (
                    x-r,y-r,x+r,y+r
                ),fill=(99,174,167)
            )
        case "down":
            x,y = img.width/2, img.width*0.685
            r = img.width/20
            draw_obj.ellipse(
                (
                    x-r,y-r,x+r,y+r
                ),fill=(99,174,167)
            )
        case "normal":
            pass
    return img.resize((int(canvas_size[0] / 22),)*2)

def choose_note() -> int|None:
    choose_ans_cls = _cls()
    choose_ans_cls.value = None
    choose_window = Toplevel(root)
    choose_window.resizable(False,False)
    choose_window.title("选择Note")
    choose_window.iconbitmap("Icon")
    choose_canvas_size = (int(root.winfo_screenwidth() * 0.25),int(root.winfo_screenwidth() * 0.25 / 7 * 3))
    choose_window.geometry(f"+{int(root.winfo_x()+root.winfo_width()/2-choose_canvas_size[0]/2)}+{int(root.winfo_y()+root.winfo_height()/2-choose_canvas_size[1]/2)}")
    choose_canvas = Canvas(choose_window,width=choose_canvas_size[0],height=choose_canvas_size[1],highlightthickness=0)
    choose_canvas.pack()
    choose_window.transient(root)
    root.attributes("-disabled",True)
    choose_window.focus_force()
    def _click(e):
        if e.x < 0 or e.y < 0 or e.x > choose_canvas_size[0] or e.y > choose_canvas_size[1]:
            return None
        choose_ans_cls.value = ceil(e.x / (choose_canvas_size[0] / 7)) + 7 * (ceil(e.y / (choose_canvas_size[1] / 3)) - 1)
    for i in range(1,22):
        line = ceil(i/7)
        choose_canvas.create_image(
            ({1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:1,9:2,10:3,11:4,12:5,13:6,14:7,15:1,16:2,17:3,18:4,19:5,20:6,21:7}[i] - 1) * choose_canvas_size[0] / 7,
            (line - 1) * choose_canvas_size[1] / 3,
            image = NOTES[i-1],anchor="nw",tag=f"note_{i}"
        )
        choose_canvas.tag_bind(f"note_{i}","<ButtonRelease-1>",_click)
    choose_window.protocol("WM_DELETE_WINDOW",lambda choose_ans_cls=choose_ans_cls:exec("choose_ans_cls.value = \"cancel\""))
    choose_window.bind("<Escape>",lambda e,choose_ans_cls=choose_ans_cls:exec("choose_ans_cls.value = \"cancel\""))
    while True:
        sleep(0.02)
        choose_window.update()
        if choose_ans_cls.value is not None:
            choose_canvas.destroy()
            choose_window.destroy()
            root.attributes("-disabled",False)
            root.focus_force()
            if choose_ans_cls.value == "cancel":
                return None
            else:
                return choose_ans_cls.value

def set_note_time(t:Number) -> Number|None:
    time_ans_cls = _cls()
    time_ans_cls.value = None
    def _click():
        try:
            time_ans_cls.value = float(settime_entry.get())
        except Exception as e:
            showerror("error",repr(e))
            return None
    settime_window = Toplevel(root)
    settime_window.withdraw()
    settime_window.resizable(False,False)
    settime_window.title("设置音符时间")
    settime_window.iconbitmap("Icon")
    settime_window.transient(root)
    root.attributes("-disabled",True)
    settime_window.focus_force()
    settime_label = Label(settime_window,text="请输入音符时间(秒): ")
    settime_entry = Entry(settime_window)
    settime_button = Button(settime_window,text="确定",command=_click)
    settime_label.grid(row=0,column=0)
    settime_entry.grid(row=0,column=1)
    settime_button.grid(row=1,column=1)
    settime_entry.insert(0,str(t))
    settime_window.update()
    settime_window.geometry(f"+{int(root.winfo_x()+root.winfo_width()/2-settime_window.winfo_width()/2)}+{int(root.winfo_y()+root.winfo_height()/2-settime_window.winfo_height()/2)}")
    settime_window.protocol("WM_DELETE_WINDOW",lambda time_ans_cls=time_ans_cls:exec("time_ans_cls.value = \"cancel\""))
    settime_window.bind("<Escape>",lambda e,time_ans_cls=time_ans_cls:exec("time_ans_cls.value = \"cancel\""))
    settime_window.deiconify()
    while True:
        sleep(0.02)
        settime_window.update()
        if time_ans_cls.value is not None:
            settime_label.destroy()
            settime_entry.destroy()
            settime_button.destroy()
            settime_window.destroy()
            root.attributes("-disabled",False)
            root.focus_force()
            if time_ans_cls.value == "cancel":
                return None
            else:
                return time_ans_cls.value

def note_click(e:Event,note_tag:str):
    for note in data["data"]:
        hash_var = hash((note["time"],note["note"]))
        if f"{hash_var}_note" == note_tag:
            index = data["data"].index(note)
    user_note = choose_note()
    if user_note is None:
        return None
    if data["data"][index]["note"] == user_note:
        return None
    askokcancel_tempstring = data["data"][index]["note"]
    if askokcancel("确认",f"是否将Note{askokcancel_tempstring}更改为Note{user_note}?"):
        data["data"][index]["note"] = user_note
        root.title(f"*Editer Version {VERSION}")
        render()

def del_note(menu:Menu,note_tag:str):
    menu.destroy()
    if askokcancel("确认",f"是否删除这个Note?"):
        for note in data["data"]:
            hash_var = hash((note["time"],note["note"]))
            if f"{hash_var}_note" == note_tag:
                index = data["data"].index(note)
                del data["data"][index]
                root.title(f"*Editer Version {VERSION}")
                render()
                return None

def change_notetime(menu:Menu,note_tag:str):
    menu.destroy()
    for note in data["data"]:
        hash_var = hash((note["time"],note["note"]))
        if f"{hash_var}_note" == note_tag:
            index = data["data"].index(note)
            break
    user_time = set_note_time(data["data"][index]["time"])
    if user_time is None:
        return None
    if data["data"][index]["time"] == user_time:
        return None
    if askokcancel("确认",f"是否更改Note时间为{user_time}s?"):
        data["data"][index]["time"] = user_time
        root.title(f"*Editer Version {VERSION}")
        render()

def note_menu(e:Event,note_tag:str):
    this_menu = Menu(main_canvas,tearoff=0,activebackground="#90C8F6",activeforeground="black")
    this_menu.add_command(label="删除",command=lambda note_tag=note_tag:del_note(this_menu,note_tag))
    this_menu.add_command(label="更改Note时间",command=lambda note_tag=note_tag:change_notetime(this_menu,note_tag))
    this_menu.post(e.x_root,e.y_root)

def render() -> float:
    start_time = time()
    main_canvas.delete("render-item")
    for note in data["data"]:
        note:dict[str,int|float]
        x = note["note"] / 21 * (canvas_size[0] * 0.875) + canvas_size[0] / 16
        y = note["time"] * view_size * -1 + canvas_size[1] + view_dy
        if -canvas_size[1] * 0.125 < y < canvas_size[1] * 1.125:
            hash_var = hash((note["time"],note["note"]))
            this_note_hash_tag = f"{hash_var}_note"
            main_canvas.create_image(
                x,y,image=NOTES[note["note"]-1],
                anchor="center",tags=["render-item",this_note_hash_tag]
            )
            main_canvas.tag_bind(this_note_hash_tag,"<Double-Button-1>",eval(f"lambda e,note_tag=\"{this_note_hash_tag}\":note_click(e,note_tag)"))
            main_canvas.tag_bind(this_note_hash_tag,"<Button-3>",eval(f"lambda e,note_tag=\"{this_note_hash_tag}\":note_menu(e,note_tag)"))
    draw_line_x = 64
    for i in range(draw_line_x):
        i /= draw_line_x
        y = i * canvas_size[1]
        this_time = (((1.0 - i) * canvas_size[1]) + view_dy) / view_size
        main_canvas.create_line(
            0,y,canvas_size[0]*0.01,y,
            fill="black",tag="render-item"
        )
        main_canvas.create_text(
            canvas_size[0]*0.01,y,fill="black",
            text=f"{this_time:.3f}s",anchor="w",
            tag="render-item"
        )
    for i in range(22):
        x = i / 21 * (canvas_size[0] * 0.875) + canvas_size[0] / 16 + NOTES[0].width() / 2 - NOTE_LINE.width()
        main_canvas.create_image(
            x,0,image=NOTE_LINE,
            anchor="nw",tags=["render-item","note-line"]
        )
    main_canvas.update()
    return time() - start_time

def copy_data_to_meta_widgets():
    edit_meta_version_entry.configure(state="normal")
    edit_meta_version_entry.delete(0,"end")
    edit_meta_version_entry.configure(state="disabled")
    edit_meta_title_entry.delete(0,"end")
    edit_meta_from_entry.delete(0,"end")
    edit_meta_author_entry.delete(0,"end")
    edit_meta_description_text.delete(0.0,"end")
    edit_meta_version_entry.configure(state="normal")
    edit_meta_version_entry.insert(0,data["meta"]["version"])
    edit_meta_version_entry.configure(state="disabled")
    edit_meta_title_entry.insert(0,data["meta"]["title"])
    edit_meta_from_entry.insert(0,data["meta"]["from"])
    edit_meta_author_entry.insert(0,data["meta"]["author"])
    edit_meta_description_text.insert(0.0,data["meta"]["description"])

def copy_meta_widgets_to_data():
    data["meta"]["title"] = edit_meta_title_entry.get()
    data["meta"]["from"] = edit_meta_from_entry.get()
    data["meta"]["author"] = edit_meta_author_entry.get()
    data["meta"]["description"] = edit_meta_description_text.get(0.0,"end")
    root.title(f"*Editer Version {VERSION}")

def editer_open():
    global data_bak,data,save_fp,view_dy
    fp = askopenfilename(title="选择谱面文件")
    if fp == "":
        return None
    try:
        data_bak = data
        with open(fp,"r",encoding="utf-8") as f:
            data = loads(f.read())
            root.title(f"*Editer Version {VERSION}")
        if data["meta"]["version"] != VERSION:
            showerror(title="版本错误",message="该谱面文件不是所支持的版本")
            data = data_bak
    except Exception as e:
        showerror(title="error",message=repr(e))
    save_fp = None
    view_dy = 0.0
    render()
    copy_data_to_meta_widgets()

def editer_save():
    global save_fp
    if save_fp is None:
        fp = asksaveasfilename(title="另存为",defaultextension=".ychartx")
        if fp == "":
            return None
        with open(fp,"w",encoding="utf-8") as f:
            f.write(dumps(data))
            root.title(f"Editer Version {VERSION}")
        save_fp = fp
    else:
        try:
            with open(save_fp,"w",encoding="utf-8") as f:
                f.write(dumps(data))
                root.title(f"Editer Version {VERSION}")
        except Exception as e:
            showerror(title="error",message=repr(e))
            save_fp = None
            editer_save()

def editer_other_save():
    global save_fp
    fp_bak = save_fp
    save_fp = None
    editer_save()
    if save_fp is None:
        save_fp = fp_bak

def mouse_wheel(e:Event):
    global view_dy
    d = {True:-1,False:1}[e.delta < 0]
    for step in WheelAnimationGr:
        view_dy += d * canvas_size[1] / 16 * step
        render()

def exitedit():
    if root.title()[0] == "*":
        user_input = askyesnocancel("选择","是否保存?")
        if user_input is None:
            return None
        elif user_input is True:
            editer_save()
            if save_fp is None:
                return None
    root.quit()

def change_viewsize(e:Event):
    global view_size
    match e.keysym:
        case "minus":
            view_size *= 0.99
        case "equal":
            view_size *= 1.01
    if view_size <= canvas_size[1] * (1 / 60):
        showinfo("啊?","这个大小够用了吧 别再缩小了~")
        view_size = canvas_size[1] * (1 / 60)
    elif view_size >= canvas_size[1] * 10:
        showinfo("啊?","这个大小够用了吧 别再放大了~")
        view_size = canvas_size[1] * 10
    render()

def set_last_canvas_menu_post_mouse_click_event_pos(e):
    global last_canvas_menu_post_mouse_click_event_pos
    last_canvas_menu_post_mouse_click_event_pos = e.x,e.y

def add_note():
    this_note_time = (canvas_size[1] - last_canvas_menu_post_mouse_click_event_pos[1] + view_dy) / view_size
    if this_note_time < 0:
        showerror("...","时间不可以小于0")
        return None
    user_note = -1
    for i in range(22):
        note_x = i / 21 * (canvas_size[0] * 0.875) + canvas_size[0] / 16 + NOTES[0].width() / 2 - NOTE_LINE.width() / 2
        if last_canvas_menu_post_mouse_click_event_pos[0] < note_x:
            user_note = i #y?
            break
    if user_note not in [i for i in range(1,22)]:
        showerror("...","你点到其他地方惹")
        return None
    data["data"].append({"time":this_note_time,"note":user_note})
    root.title(f"*Editer Version {VERSION}")
    render()

windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = windll.shcore.GetScaleFactorForDevice(0)
root = Tk()
root.withdraw()
root.tk.call("tk","scaling",ScaleFactor / 75)
root.resizable(False,False)
root.title(f"Editer Version {VERSION}")
root.iconbitmap("Icon")
root.bind("<Control-s>",lambda e:editer_save())
root.bind("<Control-Shift-S>",lambda e:editer_other_save())
root.bind("<Control-o>",lambda e:editer_open())
root.bind("<MouseWheel>",mouse_wheel)
root.bind("<Control-equal>",change_viewsize)
root.bind("<Control-minus>",change_viewsize)
root.bind("<Triple-Control-d>",lambda e:exec(f"global view_size ; view_size = {canvas_size[1] / 2} ; render()"))
root.protocol("WM_DELETE_WINDOW",exitedit)
edit_meta_window = Toplevel(root)
edit_meta_window.tk.call("tk","scaling",ScaleFactor / 75)
edit_meta_window.resizable(False,False)
edit_meta_window.title(f"Editer Version {VERSION} - 编辑元数据")
edit_meta_window.iconbitmap("Icon")
edit_meta_window.protocol("WM_DELETE_WINDOW",edit_meta_window.withdraw)
edit_meta_window.bind("<Key>",lambda e:copy_meta_widgets_to_data())
edit_meta_version_label = Label(edit_meta_window,text="谱面版本: ")
edit_meta_version_entry = Entry(edit_meta_window,state="disabled")
edit_meta_title_label = Label(edit_meta_window,text="标题: ")
edit_meta_title_entry = Entry(edit_meta_window)
edit_meta_from_label = Label(edit_meta_window,text="来源: ")
edit_meta_from_entry = Entry(edit_meta_window)
edit_meta_author_label = Label(edit_meta_window,text="作者: ")
edit_meta_author_entry = Entry(edit_meta_window)
edit_meta_description_label = Label(edit_meta_window,text="描述: ")
edit_meta_description_text = Text(edit_meta_window)
edit_meta_version_label.grid(row=0,column=0,sticky="w")
edit_meta_version_entry.grid(row=0,column=1,sticky="w")
edit_meta_title_label.grid(row=1,column=0,sticky="w")
edit_meta_title_entry.grid(row=1,column=1,sticky="w")
edit_meta_from_label.grid(row=2,column=0,sticky="w")
edit_meta_from_entry.grid(row=2,column=1,sticky="w")
edit_meta_author_label.grid(row=3,column=0,sticky="w")
edit_meta_author_entry.grid(row=3,column=1,sticky="w")
edit_meta_description_label.grid(row=4,column=0,sticky="w")
edit_meta_description_text.grid(row=4,column=1,sticky="w")
edit_meta_window.withdraw()
canvas_size = [int(root.winfo_screenwidth() * 0.75),int(root.winfo_screenheight() * 0.75)]
NOTES = [ImageTk.PhotoImage(_get_note_img(i)) for i in range(1,22)]
NOTE_LINE = ImageTk.PhotoImage(Image.new("RGBA",(int(canvas_size[0]/350),canvas_size[1]),"#0078d788"))
BACKGROUND = ImageTk.PhotoImage(
    Image.open("./editer_background.jpg").resize(
        (
            {
                True:(
                    canvas_size[0],
                    int(canvas_size[0]/16*9)
                ),
                False:(
                    int(canvas_size[1]/9*16),
                    canvas_size[1]
                )
            }[max(canvas_size) == canvas_size[0]]
        )
    ).filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.GaussianBlur(sum(canvas_size)/512))
)
main_canvas = Canvas(root,width=canvas_size[0],height=canvas_size[1],highlightthickness=0)
main_canvas.create_image(
    canvas_size[0] / 2,canvas_size[1] / 2,
    image = BACKGROUND,anchor = "center",tag="bg"
)
main_canvas.pack()
save_fp = None
view_size = canvas_size[1] / 2 # view_size px / s
view_dy = 0.0
last_canvas_menu_post_mouse_click_event_pos = None
menu_root = Menu(root)
menu_file = Menu(menu_root,tearoff=False,activebackground="#90C8F6",activeforeground="black")
menu_edit = Menu(menu_root,tearoff=False,activebackground="#90C8F6",activeforeground="black")
menu_file.add_command(label="打开",command=editer_open,accelerator="Ctrl+O")
menu_file.add_command(label="保存",command=editer_save,accelerator="Ctrl+S")
menu_file.add_command(label="另存为",command=editer_other_save,accelerator="Ctrl+Shift+S")
menu_edit.add_command(label="编辑元数据",command=edit_meta_window.deiconify)
menu_root.add_cascade(label="文件",menu=menu_file)
menu_root.add_cascade(label="编辑",menu=menu_edit)
root.configure(menu=menu_root)
canvas_menu = Menu(main_canvas,tearoff=False,activebackground="#90C8F6",activeforeground="black")
canvas_menu.add_command(label="编辑元数据",command=edit_meta_window.deiconify)
canvas_menu.add_command(label="在此处添加Note",command=add_note)
main_canvas.tag_bind("bg","<Button-3>",lambda e:(set_last_canvas_menu_post_mouse_click_event_pos(e),canvas_menu.post(e.x_root,e.y_root)))
main_canvas.tag_bind("note-line","<Button-3>",lambda e:(set_last_canvas_menu_post_mouse_click_event_pos(e),canvas_menu.post(e.x_root,e.y_root)))
data = {
    "meta":{
        "version":VERSION,
        "title":"Unknow",
        "create_time":time(),
        "from":"editer",
        "author":"Unknow",
        "description":"Unknow"
    },
    "data":[]
}
render()
copy_data_to_meta_widgets()
root.geometry(f"+{int(root.winfo_screenwidth()/2-canvas_size[0]/2)}+{int(root.winfo_screenheight()/2-canvas_size[1]/2)}")
root.deiconify()
root.mainloop()