from sys import argv
from os import _exit
from json import loads,dumps

if len(argv) < 3:
    print("convert_to_phigros_chart <input_file> <output_file>")
    _exit(0)

try:
    with open(argv[1],"r",encoding="utf-8") as f:
        ychartx = loads(f.read())
    match ychartx["meta"]["version"]:
        case "1.0.0" | "1.0.1":
            speed = 2.0
            data = {
                "formatVersion":3,
                "offset":0.0,
                "judgeLineList":[{
                    "bpm":120,
                    "notesAbove":[],
                    "notesBelow":[],
                    "speedEvents":[{
                        "startTime":0.0,
                        "endTime":9999999.0,
                        "value":speed
                    }],
                    "judgeLineMoveEvents":[
                        {
                            "startTime": -999999.0,
                            "endTime": 0.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.5,
                            "end2": 0.5
                        },
                        {
                            "startTime": 0.0,
                            "endTime": 4.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.5,
                            "end2": 0.48154625
                        },
                        {
                            "startTime": 4.0,
                            "endTime": 8.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.48154625,
                            "end2": 0.4636775
                        },
                        {
                            "startTime": 8.0,
                            "endTime": 12.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.4636775,
                            "end2": 0.44639376
                        },
                        {
                            "startTime": 12.0,
                            "endTime": 16.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.44639376,
                            "end2": 0.429695
                        },
                        {
                            "startTime": 16.0,
                            "endTime": 20.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.429695,
                            "end2": 0.41358125
                        },
                        {
                            "startTime": 20.0,
                            "endTime": 24.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.41358125,
                            "end2": 0.39805248
                        },
                        {
                            "startTime": 24.0,
                            "endTime": 28.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.39805248,
                            "end2": 0.38310874
                        },
                        {
                            "startTime": 28.0,
                            "endTime": 32.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.38310874,
                            "end2": 0.36875
                        },
                        {
                            "startTime": 32.0,
                            "endTime": 36.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.36875,
                            "end2": 0.35498375
                        },
                        {
                            "startTime": 36.0,
                            "endTime": 40.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.35498375,
                            "end2": 0.34180248
                        },
                        {
                            "startTime": 40.0,
                            "endTime": 44.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.34180248,
                            "end2": 0.32920626
                        },
                        {
                            "startTime": 44.0,
                            "endTime": 48.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.32920626,
                            "end2": 0.317195
                        },
                        {
                            "startTime": 48.0,
                            "endTime": 52.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.317195,
                            "end2": 0.30576876
                        },
                        {
                            "startTime": 52.0,
                            "endTime": 56.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.30576876,
                            "end2": 0.2949275
                        },
                        {
                            "startTime": 56.0,
                            "endTime": 60.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.2949275,
                            "end2": 0.28467125
                        },
                        {
                            "startTime": 60.0,
                            "endTime": 64.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.28467125,
                            "end2": 0.275
                        },
                        {
                            "startTime": 64.0,
                            "endTime": 68.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.275,
                            "end2": 0.26592126
                        },
                        {
                            "startTime": 68.0,
                            "endTime": 72.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.26592126,
                            "end2": 0.25742748
                        },
                        {
                            "startTime": 72.0,
                            "endTime": 76.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.25742748,
                            "end2": 0.24951875
                        },
                        {
                            "startTime": 76.0,
                            "endTime": 80.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.24951875,
                            "end2": 0.24219501
                        },
                        {
                            "startTime": 80.0,
                            "endTime": 84.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.24219501,
                            "end2": 0.23545624
                        },
                        {
                            "startTime": 84.0,
                            "endTime": 88.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.23545624,
                            "end2": 0.2293025
                        },
                        {
                            "startTime": 88.0,
                            "endTime": 92.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.2293025,
                            "end2": 0.22373377
                        },
                        {
                            "startTime": 92.0,
                            "endTime": 96.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.22373377,
                            "end2": 0.21875
                        },
                        {
                            "startTime": 96.0,
                            "endTime": 100.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.21875,
                            "end2": 0.21435875
                        },
                        {
                            "startTime": 100.0,
                            "endTime": 104.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.21435875,
                            "end2": 0.21055251
                        },
                        {
                            "startTime": 104.0,
                            "endTime": 108.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.21055251,
                            "end2": 0.20733126
                        },
                        {
                            "startTime": 108.0,
                            "endTime": 112.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.20733126,
                            "end2": 0.20469502
                        },
                        {
                            "startTime": 112.0,
                            "endTime": 116.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.20469502,
                            "end2": 0.20264375
                        },
                        {
                            "startTime": 116.0,
                            "endTime": 120.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.20264375,
                            "end2": 0.2011775
                        },
                        {
                            "startTime": 120.0,
                            "endTime": 124.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.2011775,
                            "end2": 0.20029624
                        },
                        {
                            "startTime": 124.0,
                            "endTime": 128.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.20029624,
                            "end2": 0.2
                        },
                        {
                            "startTime": 128.0,
                            "endTime": 160.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.2,
                            "end2": 0.2
                        },
                        {
                            "startTime": 160.0,
                            "endTime": 9999999.0,
                            "start": 0.5,
                            "end": 0.5,
                            "start2": 0.2,
                            "end2": 0.2
                        }],
                    "judgeLineRotateEvents":[{
                        "startTime": -999999.0,
                        "endTime": 9999999.0,
                        "start": 0.0,
                        "end": 0.0
                    }],
                    "judgeLineDisappearEvents":[{
                        "startTime": -999999.0,
                        "endTime": 9999999.0,
                        "start": 1.0,
                        "end": 1.0
                    }]
                }]
            }
            T = 1.875 / 120.0
            X = 1 / 0.05625
            X *= 0.8
            ychartx["data"].sort(key=lambda x:x["time"])
            for note in ychartx["data"]:
                phigros_time = note["time"] / T
                phigros_floor_position = speed / 120 * 1.875 * phigros_time
                phigros_positionX = note["note"] / 21 * X
                if phigros_positionX > X / 2:
                    phigros_positionX %= X / 2
                    phigros_positionX *= -1
                data["judgeLineList"][0]["notesAbove"].append({
                    "time":phigros_time,
                    "floorPosition":phigros_floor_position,
                    "type":1,
                    "holdTime":0.0,
                    "speed":speed,
                    "positionX":phigros_positionX
                })
            with open(argv[2],"w") as f:
                f.write(dumps(data))
        case _:
            raise Exception("Unknow ychartx version.")
except (ImportError,KeyboardInterrupt) as e:
    print(f"error: {e}")