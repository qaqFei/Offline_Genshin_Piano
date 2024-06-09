from sys import argv
from os import _exit,listdir
from os.path import exists,isfile

if len(argv)!=3:
    print("Js_To_YChart <input_directory> <output_directory>")
    _exit(0)

map_table={"Q":"1","W":"2","E":"3","R":"4","T":"5","Y":"6","U":"7",
           "A":"8","S":"9","D":"10","F":"11","G":"12","H":"13","J":"14",
           "Z":"15","X":"16","C":"17","V":"18","B":"19","N":"20","M":"21"}

map_table_2={"c4":"1","d4":"2","e4":"3","f4":"4","g4":"5","a4":"6","b4":"7",
             "c5":"8","d5":"9","e5":"10","f5":"11","g5":"12","a5":"13","b5":"14",
             "c6":"15","d6":"16","e6":"17","f6":"18","g6":"19","a6":"20","b6":"21",
             "1":"Q","2":"W","3":"E","4":"R","5":"T","6":"Y","7":"U",
             "8":"A","9":"S","10":"D","11":"F","12":"G","13":"H","14":"J",
             "15":"Z","16":"X","17":"C","18":"V","19":"B","20":"N","21":"M",}

def _Js_To_YChart(Input_FilePath,OutPut_FilePath):
    try:
        Read_Line=0
        #读取文件
        while True:
            Read_Line-=1
            Input_Stream=open(Input_FilePath,"r",encoding="utf-8")
            Input_Text=Input_Stream.read().split("\n")[Read_Line].split(";")
            Input_Stream.close()
            if Input_Text!=[""]:  #空行
                break
        #处理
        OutPut_Temp=""
        for i in Input_Text:
            if i=="":
                continue
            if i[0]=="t":
                try:
                    OutPut_Temp+=" "*int(int(i.replace("t","").replace("(","").replace(")",""))/10)
                except TypeError: #失败
                    continue
            elif i[1]=="(" and i[-1]==")":
                OutPut_Temp+=i.replace("()","")
        OutPut_Text=""
        for i in OutPut_Temp.split(" "):
            if i=="":
                OutPut_Text+="c\n"
            else:
                OutPut_Text+="d "+",".join([map_table[i2] for i2 in list(i)])+"\n"
        if len(OutPut_Text)==2:  #格式2
            _Js_To_YChart_2(Input_FilePath,OutPut_FilePath)
            return 0
    except SystemError as e:
        print("Js File Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
        return None
    try:
        OutPut_Stream=open(OutPut_FilePath,"w")
        OutPut_Stream.write("bpm 6000\n")
        OutPut_Stream.write(OutPut_Text)
        OutPut_Stream.close()
        print(f"导出YChart谱面:{OutPut_FilePath} 大小:{len(OutPut_Text)}字节")
    except Exception as e:
        print("Out Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
        return None

def _Js_To_YChart_2(Input_FilePath,OutPut_FilePath):
    try:
        Read_Line=0
        #读取文件
        while True:
            Read_Line-=1
            Input_Stream=open(Input_FilePath,"r",encoding="utf-8")
            Input_Text_=Input_Stream.read()
            Input_Text=Input_Text_.split("\n")[Read_Line].split(";")
            speedControl=float(Input_Text_.split("speedControl=")[1].split(";")[0])
            time1=float(Input_Text_.split("time=")[1].split(";")[0])/speedControl
            time2=float(Input_Text_.split("time1=")[1].split(";")[0])/speedControl
            time3=float(Input_Text_.split("time2=")[1].split(";")[0])/speedControl
            try:
                time4=float(Input_Text_.split("function t4() {sleep(")[1].split("/")[0])/speedControl
            except IndexError:  #方案2
                time4=float(Input_Text_.split("time3=")[1].split(";")[0])/speedControl
            Input_Stream.close()
            if Input_Text!=[""]:  #空行
                break
        OutPut_Temp=""
        for i in Input_Text:
            if i=="":
                continue
            else:
                if i.replace("()","") in map_table_2:
                    OutPut_Temp+=map_table_2[map_table_2[i.replace("()","")]]
                else:
                    if i.replace("()","") == "t1":
                        OutPut_Temp+=int(time1/10)*" "
                    if i.replace("()","") == "t2":
                        OutPut_Temp+=int(time2/10)*" "
                    if i.replace("()","") == "t3":
                        OutPut_Temp+=int(time3/10)*" "
                    if i.replace("()","") == "t4":
                        OutPut_Temp+=int(time4/10)*" "
        OutPut_Text=""
        for i in OutPut_Temp.split(" "):
            if i=="":
                OutPut_Text+="c\n"
            else:
                OutPut_Text+="d "+",".join([map_table[i2] for i2 in list(i)])+"\n"
    except Exception as e:
        print("Js File Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
        return None
    try:
        OutPut_Stream=open(OutPut_FilePath,"w")
        OutPut_Stream.write("bpm 6000\n")
        OutPut_Stream.write(OutPut_Text)
        OutPut_Stream.close()
        print(f"导出YChart谱面:{OutPut_FilePath} 大小:{len(OutPut_Text)}字节")
    except Exception as e:
        print("Out Error.",e.__repr__().split("(")[0]+" "+e.__str__(),sep="\n")
        return None

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
    if i[-3:]==".js" and exists(i):
        _Js_To_YChart(i,argv[2]+"\\"+i[0:-3].split("\\")[-1].split("/")[-1]+".ychart")