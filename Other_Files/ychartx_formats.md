# YChartx 各版本格式


写在前面:
1. 所有版本都遵循JSON格式
2. 在所有YChartx谱面中 不应在 同一时间内 存在 2个或多个 相同note
3. 每个YChartx谱面中 必须存在```meta```-```version```

目录
- [YChartx 各版本格式](#ychartx-各版本格式)
  - [YChartx 1.0.0版本](#ychartx-100版本)
  - [YChartx 1.0.1版本](#ychartx-101版本)
  
## YChartx 1.0.0版本
更新时间: 2024.3.13
```json
{
    "meta":{ //元数据 type = dict
        "version":"1.0.0", //版本号 type = str
        "title":"This is a ychartx", //标题 type = str
        "create_time":0.0, //创建时间的时间戳 type = int|float
        "from":"MIDI", //来源 type = str
        "author":"Your Name", //作者 type = str
        "description":"This is a description" //描述 type = str
    },
    "data":[ //谱面数据 type = list[dict]
        { //单个note
            "time":0.2, //note播放的时间 单位 = 秒 type = int|float
            "note":1 //note编号 range = 1~21 type = int
        },
        {
            "time":0.1, // 如上
            "note":2 // 2号note 如上
        }, //...
    ]
}
```
大致播放行为:
```
打印 meta 数据
对 data 中的每个 note 进行排序, key 为 time 属性
计算出每个 note 和 下一个note 的时间差
开始播放:
    start
    sleep 0.1 s
    play note 2
    sleep 0.1 s
    play note 1
    end
```
tips: 
1. ```data```中的每个```note```不必保持顺序

## YChartx 1.0.1版本
更新时间: 2024.4.14
```json
{
    "meta":{ //元数据 type = dict
        "version":"1.0.1", //版本号 type = str
        "title":"This is a ychartx", //标题 type = str
        "create_time":0.0, //创建时间的时间戳 type = int|float
        "from":"MIDI", //来源 type = str
        "author":"Your Name", //作者 type = str
        "description":"This is a description" //描述 type = str
    },
    "data":[ //谱面数据 type = list[dict]
        { //单个note
            "time":0.2, //note播放的时间 单位 = 秒 type = int|float
            "note":1, //note编号 range = 1~21 type = int
            "real_note":85 //由于某些方式转化的ychart有可能导致音乐失真 所以这里记录真实音高
        },
        {
            "time":0.1, // 如上
            "note":2, // 2号note 如上
            "real_note":87 // 如上
        }, //...
    ]
}