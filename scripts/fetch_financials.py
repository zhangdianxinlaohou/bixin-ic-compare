"""Fetch A-share analog semiconductor company data from Eastmoney.

The generated data.js is static. This script is only needed when refreshing
the dataset from public financial-report endpoints.
"""

from __future__ import annotations

import json
import math
import statistics
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data.js"
API = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
START_DATE = "2021-03-31"
END_DATE = "2026-09-30"
FINMIND_API = "https://api.finmindtrade.com/api/v4/data"
YAHOO_FX_API = (
    "https://query1.finance.yahoo.com/v8/finance/chart/TWDCNY=X"
    "?range=6y&interval=1d"
)


COMPANIES = [
    {
        "id": "sheng-bang",
        "code": "300661",
        "secucode": "300661.SZ",
        "name": "圣邦股份",
        "mark": "圣邦",
        "market": "创业板",
        "category": "信号链 / 通用模拟",
        "location": "北京",
        "products": ["信号链", "电源管理", "车规模拟", "ADC / DAC", "放大器", "比较器"],
        "description": "国内通用模拟 IC 龙头，信号链与电源管理产品料号覆盖广泛。",
    },
    {
        "id": "si-rui-pu",
        "code": "688536",
        "secucode": "688536.SH",
        "name": "思瑞浦",
        "mark": "思瑞",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "苏州",
        "products": ["信号链", "电源管理", "接口芯片", "隔离器件", "车规模拟", "嵌入式"],
        "description": "信号链模拟芯片起家，持续拓展电源、接口与车规产品。",
    },
    {
        "id": "na-xin-wei",
        "code": "688052",
        "secucode": "688052.SH",
        "name": "纳芯微",
        "mark": "纳芯",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "苏州",
        "products": ["数字隔离", "传感器", "信号调理", "车规模拟", "电源管理", "磁传感"],
        "description": "聚焦隔离、传感器与车规模拟，产品和汽车电子场景结合紧密。",
    },
    {
        "id": "ai-wei",
        "code": "688798",
        "secucode": "688798.SH",
        "name": "艾为电子",
        "mark": "艾为",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "上海",
        "products": ["音频功放", "触觉反馈", "电源管理", "射频前端", "显示驱动", "马达驱动"],
        "description": "消费电子模拟与混合信号芯片平台，产品覆盖音频、触觉和电源。",
    },
    {
        "id": "xin-hai",
        "code": "688595",
        "secucode": "688595.SH",
        "name": "芯海科技",
        "mark": "芯海",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "深圳",
        "products": ["ADC", "模拟前端", "MCU", "压力传感", "健康测量", "车规"],
        "description": "以 ADC 与模拟前端为核心，覆盖 MCU、健康测量和汽车电子。",
    },
    {
        "id": "di-ao",
        "code": "688381",
        "secucode": "688381.SH",
        "name": "帝奥微",
        "mark": "帝奥",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "南通",
        "products": ["信号链", "电源管理", "USB 开关", "LED 驱动", "车规", "工业"],
        "description": "信号链与电源管理模拟芯片设计企业，积极布局汽车与工业市场。",
    },
    {
        "id": "jing-hua",
        "code": "688130",
        "secucode": "688130.SH",
        "name": "晶华微",
        "mark": "晶华",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "杭州",
        "products": ["ADC", "模拟 SoC", "仪表", "健康测量", "工业控制", "传感器"],
        "description": "以 ADC 和模拟 SoC 见长，聚焦仪器仪表、健康测量与工控场景。",
    },
    {
        "id": "can-rui",
        "code": "688061",
        "secucode": "688061.SH",
        "name": "灿瑞科技",
        "mark": "灿瑞",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "上海",
        "products": ["霍尔传感器", "电源管理", "显示驱动", "电机驱动", "智能传感", "车规"],
        "description": "磁传感器与电源管理芯片供应商，覆盖消费、工业和汽车电子。",
    },
    {
        "id": "sh-belling",
        "code": "600171",
        "secucode": "600171.SH",
        "name": "上海贝岭",
        "mark": "贝岭",
        "market": "上交所主板",
        "category": "信号链 / 通用模拟",
        "location": "上海",
        "products": ["计量芯片", "电源管理", "信号链", "EEPROM", "功率器件", "车规"],
        "description": "老牌模拟集成电路平台，产品覆盖计量、电源、信号链和功率器件。",
    },
    {
        "id": "long-xun",
        "code": "688486",
        "secucode": "688486.SH",
        "name": "龙迅股份",
        "mark": "龙迅",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "合肥",
        "products": ["高速接口", "HDMI", "DisplayPort", "Type-C", "视频桥接", "汽车显示"],
        "description": "高速混合信号与视频接口芯片公司，覆盖消费、专业显示和汽车。",
    },
    {
        "id": "yu-tai",
        "code": "688515",
        "secucode": "688515.SH",
        "name": "裕太微",
        "mark": "裕太",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "苏州",
        "products": ["以太网 PHY", "车载以太网", "交换芯片", "网卡芯片", "工业互联", "混合信号"],
        "description": "以太网物理层芯片设计企业，重点布局车载与工业互联市场。",
    },
    {
        "id": "xin-dong",
        "code": "688582",
        "secucode": "688582.SH",
        "name": "芯动联科",
        "mark": "芯动",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "北京",
        "products": ["MEMS 陀螺仪", "加速度计", "惯性传感器", "工业导航", "无人系统", "高性能传感"],
        "description": "高性能 MEMS 惯性传感器企业，产品用于工业导航与无人系统。",
    },
    {
        "id": "min-xin",
        "code": "688286",
        "secucode": "688286.SH",
        "name": "敏芯股份",
        "mark": "敏芯",
        "market": "科创板",
        "category": "信号链 / 通用模拟",
        "location": "苏州",
        "products": ["MEMS 麦克风", "压力传感器", "惯性传感器", "声学", "汽车传感", "医疗"],
        "description": "MEMS 传感器平台，核心产品包括麦克风、压力传感器和惯性器件。",
    },
    {
        "id": "xin-peng",
        "code": "688508",
        "secucode": "688508.SH",
        "name": "芯朋微",
        "mark": "芯朋",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "无锡",
        "products": ["AC-DC", "DC-DC", "电源管理", "家电电源", "快充", "车规"],
        "description": "电源管理芯片设计企业，主要覆盖家电、工业与汽车电源市场。",
    },
    {
        "id": "li-xin",
        "code": "688601",
        "secucode": "688601.SH",
        "name": "力芯微",
        "mark": "力芯",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "无锡",
        "products": ["电源管理", "负载开关", "充电管理", "手机", "可穿戴", "车规"],
        "description": "以手机和可穿戴电源管理为核心，逐步拓展车规与工业产品。",
    },
    {
        "id": "jing-feng",
        "code": "688368",
        "secucode": "688368.SH",
        "name": "晶丰明源",
        "mark": "晶丰",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "上海",
        "products": ["LED 驱动", "AC-DC", "DC-DC", "电机驱动", "快充", "智能照明"],
        "description": "LED 驱动与电源管理芯片厂商，产品延伸至电机和快充领域。",
    },
    {
        "id": "ming-wei",
        "code": "688699",
        "secucode": "688699.SH",
        "name": "明微电子",
        "mark": "明微",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "深圳",
        "products": ["LED 显示驱动", "LED 照明驱动", "Mini LED", "电源管理", "智能照明", "显示控制"],
        "description": "LED 显示与照明驱动芯片供应商，聚焦显示控制和智能照明。",
    },
    {
        "id": "fu-man",
        "code": "300671",
        "secucode": "300671.SZ",
        "name": "富满微",
        "mark": "富满",
        "market": "创业板",
        "category": "电源管理 / 驱动",
        "location": "深圳",
        "products": ["电源管理", "LED 驱动", "射频芯片", "快充", "MOSFET", "MCU"],
        "description": "模拟与功率芯片平台，覆盖电源管理、LED 驱动和射频产品。",
    },
    {
        "id": "xi-di",
        "code": "688173",
        "secucode": "688173.SH",
        "name": "希荻微",
        "mark": "希荻",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "佛山",
        "products": ["充电管理", "DC-DC", "电源管理", "车规", "快充", "电池管理"],
        "description": "充电管理与电源管理芯片企业，布局手机、汽车和工业市场。",
    },
    {
        "id": "bi-yi",
        "code": "688045",
        "secucode": "688045.SH",
        "name": "必易微",
        "mark": "必易",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "深圳",
        "products": ["AC-DC", "DC-DC", "电机驱动", "LED 驱动", "快充", "家电"],
        "description": "电源管理与电机驱动芯片企业，在家电和消费电源市场份额较高。",
    },
    {
        "id": "ying-ji",
        "code": "688209",
        "secucode": "688209.SH",
        "name": "英集芯",
        "mark": "英集",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "深圳",
        "products": ["快充协议", "移动电源", "无线充电", "电源管理", "车规", "电池管理"],
        "description": "以快充协议和移动电源芯片为核心，覆盖电源管理与电池管理。",
    },
    {
        "id": "mei-xin",
        "code": "688458",
        "secucode": "688458.SH",
        "name": "美芯晟",
        "mark": "美芯",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "北京",
        "products": ["无线充电", "有线快充", "LED 驱动", "电源管理", "信号链", "车规"],
        "description": "无线充电与电源管理芯片设计企业，持续拓展汽车和工业应用。",
    },
    {
        "id": "nan-xin",
        "code": "688484",
        "secucode": "688484.SH",
        "name": "南芯科技",
        "mark": "南芯",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "上海",
        "products": ["充电管理", "电荷泵", "DC-DC", "电池管理", "AC-DC", "车规"],
        "description": "充电与电池管理芯片龙头，产品覆盖消费电子、工业和汽车。",
    },
    {
        "id": "jie-hua-te",
        "code": "688141",
        "secucode": "688141.SH",
        "name": "杰华特",
        "mark": "杰华",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "杭州",
        "products": ["DC-DC", "AC-DC", "电源管理", "电池管理", "车规", "服务器电源"],
        "description": "电源管理模拟芯片企业，产品覆盖 DC-DC、AC-DC、电池管理与服务器电源。",
    },
    {
        "id": "feng-tiao",
        "code": "688279",
        "secucode": "688279.SH",
        "name": "峰岹科技",
        "mark": "峰岹",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "深圳",
        "products": ["电机驱动", "MCU", "BLDC", "FOC", "工业", "汽车"],
        "description": "电机驱动控制芯片企业，在 BLDC 与 FOC 控制方案上具有特色。",
    },
    {
        "id": "xin-dao",
        "code": "688230",
        "secucode": "688230.SH",
        "name": "芯导科技",
        "mark": "芯导",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "上海",
        "products": ["ESD 保护", "TVS", "MOSFET", "功率器件", "电源管理", "车规"],
        "description": "功率器件与 ESD 保护芯片企业，覆盖消费电子、工业和汽车。",
    },
    {
        "id": "zhong-ying",
        "code": "300327",
        "secucode": "300327.SZ",
        "name": "中颖电子",
        "mark": "中颖",
        "market": "创业板",
        "category": "电源管理 / 驱动",
        "location": "上海",
        "products": ["MCU", "OLED 驱动", "锂电池管理", "家电控制", "工控", "汽车电子"],
        "description": "MCU 与显示驱动芯片平台，重点覆盖家电、锂电管理和工控。",
    },
    {
        "id": "zhuo-sheng",
        "code": "300782",
        "secucode": "300782.SZ",
        "name": "卓胜微",
        "mark": "卓胜",
        "market": "创业板",
        "category": "射频 / 混合信号",
        "location": "无锡",
        "products": ["射频开关", "LNA", "滤波器", "功率放大器", "射频模组", "Wi-Fi FEM"],
        "description": "射频前端芯片龙头，覆盖开关、低噪声放大器、滤波器和模组。",
    },
    {
        "id": "wei-jie",
        "code": "688153",
        "secucode": "688153.SH",
        "name": "唯捷创芯",
        "mark": "唯捷",
        "market": "科创板",
        "category": "射频 / 混合信号",
        "location": "天津",
        "products": ["射频功率放大器", "5G PA", "L-PAMiD", "Wi-Fi FEM", "射频前端", "车规"],
        "description": "射频功率放大器厂商，产品覆盖 5G 手机与 Wi-Fi 前端模组。",
    },
    {
        "id": "hui-zhi",
        "code": "688512",
        "secucode": "688512.SH",
        "name": "慧智微",
        "mark": "慧智",
        "market": "科创板",
        "category": "射频 / 混合信号",
        "location": "广州",
        "products": ["可重构射频", "5G PA", "射频前端", "LNA", "开关", "IoT"],
        "description": "可重构射频前端芯片公司，强调多频段与高集成度方案。",
    },
    {
        "id": "guo-bo",
        "code": "688375",
        "secucode": "688375.SH",
        "name": "国博电子",
        "mark": "国博",
        "market": "科创板",
        "category": "射频 / 混合信号",
        "location": "南京",
        "products": ["射频芯片", "微波器件", "T/R 组件", "有源相控阵", "基站射频", "特种电子"],
        "description": "射频与微波器件企业，覆盖基站、有源相控阵和特种电子。",
    },
    {
        "id": "cheng-chang",
        "code": "001270",
        "secucode": "001270.SZ",
        "name": "铖昌科技",
        "mark": "铖昌",
        "market": "深交所主板",
        "category": "射频 / 混合信号",
        "location": "杭州",
        "products": ["相控阵 T/R", "微波毫米波", "射频芯片", "卫星通信", "雷达", "特种"],
        "description": "微波毫米波 T/R 芯片企业，面向相控阵雷达与卫星通信。",
    },
    {
        "id": "hui-ding",
        "code": "603160",
        "secucode": "603160.SH",
        "name": "汇顶科技",
        "mark": "汇顶",
        "market": "上交所主板",
        "category": "射频 / 混合信号",
        "location": "深圳",
        "products": ["指纹识别", "触控芯片", "音频", "NFC", "安全芯片", "传感器"],
        "description": "触控与指纹识别芯片龙头，产品拓展至音频、NFC 和安全芯片。",
    },
    {
        "id": "zhen-hua",
        "code": "688439",
        "secucode": "688439.SH",
        "name": "振华风光",
        "mark": "振华",
        "market": "科创板",
        "category": "军工 / 特种模拟",
        "location": "贵阳",
        "products": ["放大器", "电源管理", "转换器", "接口", "特种模拟", "高可靠"],
        "description": "特种模拟集成电路企业，产品用于高可靠、军工与航空航天场景。",
    },
    {
        "id": "cheng-du-hua-wei",
        "code": "688709",
        "secucode": "688709.SH",
        "name": "成都华微",
        "mark": "成微",
        "market": "科创板",
        "category": "FPGA / 可编程计算",
        "location": "成都",
        "products": ["FPGA", "ADC / DAC", "MCU", "电源管理", "特种集成电路", "高可靠"],
        "description": "特种集成电路企业，产品覆盖 FPGA、转换器、MCU 与电源管理。",
    },
    {
        "id": "zhen-lei",
        "code": "688270",
        "secucode": "688270.SH",
        "name": "臻镭科技",
        "mark": "臻镭",
        "market": "科创板",
        "category": "军工 / 特种模拟",
        "location": "杭州",
        "products": ["射频前端", "电源管理", "ADC / DAC", "相控阵", "卫星通信", "特种"],
        "description": "面向特种应用提供射频、电源管理和信号转换芯片。",
    },
    {
        "id": "dian-ke",
        "code": "600877",
        "secucode": "600877.SH",
        "name": "电科芯片",
        "mark": "电科",
        "market": "上交所主板",
        "category": "军工 / 特种模拟",
        "location": "重庆",
        "products": ["模拟芯片", "射频芯片", "电源管理", "安全芯片", "汽车电子", "特种"],
        "description": "中电科体系内芯片平台，业务覆盖模拟、射频与安全芯片。",
    },
    {
        "id": "shi-lan",
        "code": "600460",
        "secucode": "600460.SH",
        "name": "士兰微",
        "mark": "士兰",
        "market": "上交所主板",
        "category": "IDM / 平台型",
        "location": "杭州",
        "products": ["功率器件", "模拟 IC", "电源管理", "LED", "MEMS", "车规"],
        "description": "功率半导体 IDM 平台，兼具模拟 IC、电源管理与 MEMS 产线。",
    },
    {
        "id": "hua-run-wei",
        "code": "688396",
        "secucode": "688396.SH",
        "name": "华润微",
        "mark": "华润",
        "market": "科创板",
        "category": "IDM / 平台型",
        "location": "无锡",
        "products": ["功率器件", "模拟 IC", "MCU", "传感器", "晶圆制造", "封测"],
        "description": "功率与模拟半导体 IDM，覆盖设计、晶圆制造和封装测试。",
    },
    {
        "id": "wei-er",
        "code": "603501",
        "secucode": "603501.SH",
        "name": "韦尔股份",
        "mark": "韦尔",
        "market": "上交所主板",
        "category": "IDM / 平台型",
        "location": "上海",
        "products": ["CIS", "汽车 CIS", "OLED DDIC", "模拟 IC", "TDDI", "分销"],
        "description": "图像传感器龙头，同时拥有显示驱动、模拟和分销业务。",
    },
    {
        "id": "jing-jun",
        "code": "300223",
        "secucode": "300223.SZ",
        "name": "君正股份",
        "mark": "君正",
        "market": "创业板",
        "category": "存储芯片",
        "location": "北京",
        "aliases": ["北京君正"],
        "products": ["DRAM", "SRAM", "NOR Flash", "模拟互联", "MCU", "车规"],
        "description": "存储与模拟互联芯片平台，原证券简称北京君正，车规和工业占比较高。",
    },
    {
        "id": "fu-dan-wei",
        "code": "688385",
        "secucode": "688385.SH",
        "name": "复旦微电",
        "mark": "复旦",
        "market": "科创板",
        "category": "FPGA / 可编程计算",
        "location": "上海",
        "products": ["FPGA", "安全芯片", "MCU", "模拟电路", "智能电表", "车规"],
        "description": "FPGA 与安全芯片平台，同时拥有 MCU、模拟和智能电表产品线。",
    },
    {
        "id": "rui-xin-wei",
        "code": "603893",
        "secucode": "603893.SH",
        "name": "瑞芯微",
        "mark": "瑞芯",
        "market": "上交所主板",
        "category": "SoC 芯片",
        "location": "福州",
        "products": ["AIoT SoC", "机器视觉", "汽车电子", "智能平板", "边缘计算", "音频 SoC"],
        "description": "AIoT SoC 平台型设计公司，产品覆盖平板、机器视觉、汽车与边缘计算。",
    },
    {
        "id": "jing-chen",
        "code": "688099",
        "secucode": "688099.SH",
        "name": "晶晨股份",
        "mark": "晶晨",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["多媒体 SoC", "智能机顶盒", "智能电视", "AI 音视频", "汽车座舱", "Wi-Fi"],
        "description": "多媒体智能终端 SoC 龙头，覆盖机顶盒、智能电视、AI 音视频和汽车座舱。",
    },
    {
        "id": "quan-zhi",
        "code": "300458",
        "secucode": "300458.SZ",
        "name": "全志科技",
        "mark": "全志",
        "market": "创业板",
        "category": "SoC 芯片",
        "location": "珠海",
        "products": ["智能应用 SoC", "车载 SoC", "工业控制", "机器视觉", "平板电脑", "AIoT"],
        "description": "智能应用处理器 SoC 企业，覆盖车载、工业、机器视觉和消费终端。",
    },
    {
        "id": "heng-xuan",
        "code": "688608",
        "secucode": "688608.SH",
        "name": "恒玄科技",
        "mark": "恒玄",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["智能音频 SoC", "TWS 耳机", "智能手表", "Wi-Fi SoC", "AI 音频", "低功耗"],
        "description": "智能音频与可穿戴 SoC 企业，重点覆盖 TWS 耳机、手表和 AI 音频终端。",
    },
    {
        "id": "le-xin",
        "code": "688018",
        "secucode": "688018.SH",
        "name": "乐鑫科技",
        "mark": "乐鑫",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["Wi-Fi MCU", "蓝牙 SoC", "AIoT", "RISC-V", "无线连接", "开发者生态"],
        "description": "Wi-Fi / 蓝牙 MCU 与 AIoT SoC 企业，拥有较强的开发者生态。",
    },
    {
        "id": "zhong-ke-lan-xun",
        "code": "688332",
        "secucode": "688332.SH",
        "name": "中科蓝讯",
        "mark": "蓝讯",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "深圳",
        "products": ["蓝牙音频 SoC", "TWS 耳机", "智能穿戴", "低功耗", "无线音频", "AI 音频"],
        "description": "蓝牙音频 SoC 企业，产品主要应用于 TWS 耳机和智能穿戴设备。",
    },
    {
        "id": "ju-xin",
        "code": "688049",
        "secucode": "688049.SH",
        "name": "炬芯科技",
        "mark": "炬芯",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "珠海",
        "products": ["音频 SoC", "蓝牙音频", "智能穿戴", "端侧 AI", "低功耗", "无线连接"],
        "description": "低功耗音频 SoC 与无线连接芯片企业，布局端侧 AI 音频应用。",
    },
    {
        "id": "fu-han",
        "code": "300613",
        "secucode": "300613.SZ",
        "name": "富瀚微",
        "mark": "富瀚",
        "market": "创业板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["视频处理 SoC", "安防 IPC", "汽车视觉", "图像信号处理", "AI 视觉", "ISP"],
        "description": "视频处理与视觉 SoC 企业，产品覆盖安防、汽车视觉和智能摄像头。",
    },
    {
        "id": "xing-chen",
        "code": "301536",
        "secucode": "301536.SZ",
        "name": "星宸科技",
        "mark": "星宸",
        "market": "创业板",
        "category": "SoC 芯片",
        "location": "厦门",
        "products": ["智能视觉 SoC", "安防 IPC", "行车记录仪", "AI 视觉", "视频编码", "低功耗"],
        "description": "智能视觉 SoC 企业，产品覆盖安防监控、行车记录仪与 AI 视觉终端。",
    },
    {
        "id": "tai-ling-wei",
        "code": "688591",
        "secucode": "688591.SH",
        "name": "泰凌微",
        "mark": "泰凌",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["低功耗蓝牙 SoC", "Zigbee", "Thread", "无线音频", "AIoT", "RISC-V"],
        "description": "低功耗无线连接 SoC 企业，覆盖蓝牙、Zigbee、Thread 与 AIoT。",
    },
    {
        "id": "ao-jie",
        "code": "688220",
        "secucode": "688220.SH",
        "name": "翱捷科技",
        "mark": "翱捷",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["蜂窝基带", "Cat.1", "5G", "Wi-Fi", "AIoT SoC", "射频"],
        "description": "蜂窝基带与无线通信 SoC 企业，覆盖 Cat.1、5G 与 AIoT 市场。",
    },
    {
        "id": "an-kai-wei",
        "code": "688620",
        "secucode": "688620.SH",
        "name": "安凯微",
        "mark": "安凯",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "广州",
        "products": ["视频监控 SoC", "物联网摄像机", "AI 视觉", "低功耗", "ISP", "H.264"],
        "description": "物联网摄像机 SoC 企业，聚焦视频监控、AI 视觉与低功耗连接。",
    },
    {
        "id": "guo-ke-wei",
        "code": "300672",
        "secucode": "300672.SZ",
        "name": "国科微",
        "mark": "国科",
        "market": "创业板",
        "category": "SoC 芯片",
        "location": "长沙",
        "products": ["智能机顶盒 SoC", "视频编码", "存储控制", "AI 视觉", "固态存储", "广播电视"],
        "description": "视频与存储控制 SoC 企业，覆盖机顶盒、视频编码、存储控制与 AI 视觉。",
    },
    {
        "id": "hai-guang",
        "code": "688041",
        "secucode": "688041.SH",
        "name": "海光信息",
        "mark": "海光",
        "market": "科创板",
        "category": "CPU / 处理器",
        "location": "天津",
        "products": ["服务器 CPU", "DCU 加速卡", "x86 兼容", "国产算力", "数据中心", "异构计算"],
        "description": "高端处理器设计公司，覆盖服务器 CPU、DCU 加速卡和数据中心算力。",
    },
    {
        "id": "han-wu-ji",
        "code": "688256",
        "secucode": "688256.SH",
        "name": "寒武纪",
        "mark": "寒武",
        "market": "科创板",
        "category": "GPU / AI 算力",
        "location": "北京",
        "products": ["AI 训练", "AI 推理", "智能加速卡", "云端芯片", "边缘 AI", "基础软件"],
        "description": "人工智能芯片企业，覆盖云端训练、推理和边缘 AI 加速场景。",
    },
    {
        "id": "jing-jia-wei",
        "code": "300474",
        "secucode": "300474.SZ",
        "name": "景嘉微",
        "mark": "景嘉",
        "market": "创业板",
        "category": "GPU / AI 算力",
        "location": "长沙",
        "products": ["图形 GPU", "显控模块", "信创 PC", "国产显卡", "图形渲染", "特种电子"],
        "description": "国产图形处理芯片企业，产品覆盖显控、信创 PC 和专用图形应用。",
    },
    {
        "id": "long-xin-zhong-ke",
        "code": "688047",
        "secucode": "688047.SH",
        "name": "龙芯中科",
        "mark": "龙芯",
        "market": "科创板",
        "category": "CPU / 处理器",
        "location": "北京",
        "products": ["LoongArch CPU", "服务器 CPU", "桌面 CPU", "工控芯片", "基础软件", "信创"],
        "description": "自主指令集 CPU 企业，产品覆盖桌面、服务器和工业控制。",
    },
    {
        "id": "xin-yuan",
        "code": "688521",
        "secucode": "688521.SH",
        "name": "芯原股份",
        "mark": "芯原",
        "market": "科创板",
        "category": "GPU / AI 算力",
        "location": "上海",
        "products": ["GPU IP", "NPU IP", "VPU IP", "芯片定制", "IP 授权", "Chiplet"],
        "description": "芯片定制与半导体 IP 企业，拥有 GPU、NPU、VPU 等计算 IP 组合。",
    },
    {
        "id": "mo-er-xian-cheng",
        "code": "688795",
        "secucode": "688795.SH",
        "name": "摩尔线程",
        "mark": "摩尔",
        "market": "科创板",
        "category": "GPU / AI 算力",
        "location": "北京",
        "products": ["全功能 GPU", "AI 训练", "图形渲染", "计算加速", "MUSA 生态", "智算集群"],
        "description": "国产全功能 GPU 企业，覆盖图形渲染、AI 训练与计算加速。",
    },
    {
        "id": "mu-xi",
        "code": "688802",
        "secucode": "688802.SH",
        "name": "沐曦股份",
        "mark": "沐曦",
        "market": "科创板",
        "category": "GPU / AI 算力",
        "location": "上海",
        "products": ["GPGPU", "AI 训练", "AI 推理", "通用计算", "国产算力", "智算集群"],
        "description": "通用 GPU 企业，产品面向 AI 训练、推理和通用计算市场。",
    },
    {
        "id": "zhong-xin-guo-ji",
        "code": "688981",
        "secucode": "688981.SH",
        "name": "中芯国际",
        "mark": "中芯",
        "market": "科创板",
        "category": "晶圆代工 FAB",
        "location": "上海",
        "products": ["逻辑芯片代工", "成熟制程", "先进制程", "12 英寸晶圆", "8 英寸晶圆", "eNVM"],
        "description": "中国大陆规模最大的晶圆代工厂，覆盖成熟与先进逻辑工艺。",
    },
    {
        "id": "hua-hong",
        "code": "688347",
        "secucode": "688347.SH",
        "name": "华虹公司",
        "mark": "华虹",
        "market": "科创板",
        "category": "晶圆代工 FAB",
        "location": "上海",
        "aliases": ["华虹宏力"],
        "products": ["特色工艺", "功率器件", "嵌入式存储", "模拟电源", "12 英寸晶圆", "8 英寸晶圆"],
        "description": "以特色工艺见长的晶圆代工企业，聚焦功率、存储与模拟电源平台。",
    },
    {
        "id": "jing-he",
        "code": "688249",
        "secucode": "688249.SH",
        "name": "晶合集成",
        "mark": "晶合",
        "market": "科创板",
        "category": "晶圆代工 FAB",
        "location": "合肥",
        "products": ["12 英寸代工", "显示驱动", "CIS", "MCU", "电源管理", "车规"],
        "description": "12 英寸晶圆代工企业，核心产品包括显示驱动、CIS 与电源管理芯片。",
    },
    {
        "id": "xin-lian",
        "code": "688469",
        "secucode": "688469.SH",
        "name": "芯联集成",
        "mark": "芯联",
        "market": "科创板",
        "category": "晶圆代工 FAB",
        "location": "绍兴",
        "products": ["MEMS", "IGBT", "SiC", "模拟 IC", "功率器件", "车规代工"],
        "description": "MEMS 与功率器件晶圆代工企业，重点布局汽车、工业和新能源。",
    },
    {
        "id": "yan-dong",
        "code": "688172",
        "secucode": "688172.SH",
        "name": "燕东微",
        "mark": "燕东",
        "market": "科创板",
        "category": "晶圆代工 FAB",
        "location": "北京",
        "products": ["12 英寸晶圆", "8 英寸晶圆", "功率器件", "模拟 IC", "晶圆代工", "车规"],
        "description": "特色工艺晶圆制造企业，产品覆盖功率器件、模拟芯片和晶圆代工。",
    },
    {
        "id": "bei-fang-hua-chuang",
        "code": "002371",
        "secucode": "002371.SZ",
        "name": "北方华创",
        "mark": "北方",
        "market": "深交所主板",
        "category": "半导体设备",
        "location": "北京",
        "products": ["刻蚀设备", "薄膜沉积", "清洗设备", "炉管设备", "真空装备", "核心零部件"],
        "description": "平台型半导体设备公司，覆盖刻蚀、薄膜、清洗和炉管等核心工艺。",
    },
    {
        "id": "zhong-wei",
        "code": "688012",
        "secucode": "688012.SH",
        "name": "中微公司",
        "mark": "中微",
        "market": "科创板",
        "category": "半导体设备",
        "location": "上海",
        "products": ["CCP 刻蚀", "ICP 刻蚀", "MOCVD", "薄膜沉积", "量测设备", "先进封装"],
        "description": "等离子体刻蚀设备企业，并向薄膜沉积和量测设备延伸。",
    },
    {
        "id": "tuo-jing",
        "code": "688072",
        "secucode": "688072.SH",
        "name": "拓荆科技",
        "mark": "拓荆",
        "market": "科创板",
        "category": "半导体设备",
        "location": "沈阳",
        "products": ["PECVD", "ALD", "SACVD", "晶圆键合", "先进封装", "薄膜沉积"],
        "description": "薄膜沉积设备供应商，产品覆盖 PECVD、ALD 与晶圆键合。",
    },
    {
        "id": "hua-hai-qing-ke",
        "code": "688120",
        "secucode": "688120.SH",
        "name": "华海清科",
        "mark": "华海",
        "market": "科创板",
        "category": "半导体设备",
        "location": "天津",
        "products": ["CMP 设备", "减薄设备", "清洗设备", "先进封装", "晶圆再生", "量测"],
        "description": "化学机械抛光设备龙头，产品延伸至减薄、清洗和先进封装。",
    },
    {
        "id": "xin-yuan-wei",
        "code": "688037",
        "secucode": "688037.SH",
        "name": "芯源微",
        "mark": "芯源",
        "market": "科创板",
        "category": "半导体设备",
        "location": "沈阳",
        "products": ["涂胶显影", "清洗设备", "先进封装", "前道设备", "化合物半导体", "湿法工艺"],
        "description": "涂胶显影与清洗设备企业，覆盖前道、先进封装和化合物半导体。",
    },
    {
        "id": "sheng-mei",
        "code": "688082",
        "secucode": "688082.SH",
        "name": "盛美上海",
        "mark": "盛美",
        "market": "科创板",
        "category": "半导体设备",
        "location": "上海",
        "products": ["清洗设备", "电镀设备", "炉管设备", "先进封装", "湿法工艺", "ECP"],
        "description": "半导体清洗与电镀设备企业，覆盖前道、先进封装和湿法工艺。",
    },
    {
        "id": "chang-chuan",
        "code": "300604",
        "secucode": "300604.SZ",
        "name": "长川科技",
        "mark": "长川",
        "market": "创业板",
        "category": "半导体设备",
        "location": "杭州",
        "products": ["测试机", "分选机", "探针台", "AOI 检测", "先进封装", "汽车电子"],
        "description": "半导体测试设备企业，产品覆盖测试机、分选机和检测设备。",
    },
    {
        "id": "jing-ce",
        "code": "300567",
        "secucode": "300567.SZ",
        "name": "精测电子",
        "mark": "精测",
        "market": "创业板",
        "category": "半导体设备",
        "location": "武汉",
        "products": ["量测设备", "缺陷检测", "晶圆检测", "显示检测", "先进封装", "AOI"],
        "description": "检测与量测设备企业，覆盖半导体晶圆、显示和先进封装。",
    },
    {
        "id": "zhong-ke-fei-ce",
        "code": "688361",
        "secucode": "688361.SH",
        "name": "中科飞测",
        "mark": "飞测",
        "market": "科创板",
        "category": "半导体设备",
        "location": "深圳",
        "products": ["缺陷检测", "量测设备", "晶圆检测", "先进封装", "无图形晶圆", "光学检测"],
        "description": "半导体质量控制设备企业，覆盖缺陷检测与量测环节。",
    },
    {
        "id": "zhi-chun",
        "code": "603690",
        "secucode": "603690.SH",
        "name": "至纯科技",
        "mark": "至纯",
        "market": "上交所主板",
        "category": "半导体设备",
        "location": "上海",
        "products": ["湿法清洗", "高纯工艺系统", "电子材料", "晶圆清洗", "工艺设备", "厂务系统"],
        "description": "高纯工艺系统与湿法清洗设备企业，覆盖晶圆制造和电子材料。",
    },
    {
        "id": "xian-dao-ji-dian",
        "code": "600641",
        "secucode": "600641.SH",
        "name": "先导基电",
        "mark": "先导",
        "market": "上交所主板",
        "category": "半导体设备",
        "location": "上海",
        "aliases": ["万业企业"],
        "products": ["离子注入机", "半导体设备", "核心零部件", "材料", "真空设备", "光伏设备"],
        "description": "离子注入机与半导体设备平台，原证券简称万业企业。",
    },
    {
        "id": "xin-yi-chang",
        "code": "688383",
        "secucode": "688383.SH",
        "name": "新益昌",
        "mark": "新益",
        "market": "科创板",
        "category": "半导体设备",
        "location": "深圳",
        "products": ["固晶机", "焊线机", "Mini LED", "半导体封装", "检测设备", "自动化"],
        "description": "半导体封装与 LED 固晶设备企业，覆盖固晶、焊线和检测自动化。",
    },
    {
        "id": "guo-xin-ke-ji",
        "code": "688262",
        "secucode": "688262.SH",
        "name": "国芯科技",
        "mark": "国芯",
        "market": "科创板",
        "category": "CPU / 处理器",
        "location": "苏州",
        "products": ["嵌入式 CPU IP", "汽车电子 MCU", "信息安全芯片", "SoC", "车规", "RISC-V"],
        "description": "嵌入式 CPU IP 与安全芯片企业，覆盖汽车电子、信息安全和自主可控。",
    },
    {
        "id": "zhong-guo-chang-cheng",
        "code": "000066",
        "secucode": "000066.SZ",
        "name": "中国长城",
        "mark": "长城",
        "market": "深交所主板",
        "category": "CPU / 处理器",
        "location": "深圳",
        "products": ["飞腾整机", "信创 PC", "服务器", "网络安全", "PK 体系", "自主计算"],
        "description": "飞腾生态与自主计算整机平台，覆盖信创 PC、服务器和网络安全。",
    },
    {
        "id": "hang-yu-wei",
        "code": "300053",
        "secucode": "300053.SZ",
        "name": "航宇微",
        "mark": "航宇",
        "market": "创业板",
        "category": "CPU / 处理器",
        "location": "珠海",
        "products": ["宇航级 SoC", "AI 芯片", "SiP 封装", "卫星大数据", "嵌入式系统", "高可靠"],
        "description": "宇航级 SoC 与嵌入式系统企业，覆盖卫星大数据、AI 芯片和高可靠应用。",
    },
    {
        "id": "guo-min-ji-shu",
        "code": "300077",
        "secucode": "300077.SZ",
        "name": "国民技术",
        "mark": "国民",
        "market": "创业板",
        "category": "CPU / 处理器",
        "location": "深圳",
        "products": ["安全芯片", "MCU", "无线连接", "BMS", "车规", "RISC-V"],
        "description": "安全芯片与 MCU 企业，产品覆盖无线连接、电池管理和汽车电子。",
    },
    {
        "id": "zhong-wei-ban-dao",
        "code": "688380",
        "secucode": "688380.SH",
        "name": "中微半导",
        "mark": "中微",
        "market": "科创板",
        "category": "CPU / 处理器",
        "location": "深圳",
        "products": ["MCU", "触控芯片", "电机控制", "家电", "汽车电子", "SoC"],
        "description": "MCU 与混合信号芯片企业，重点覆盖家电、电机控制和汽车电子。",
    },
    {
        "id": "dong-ruan-zai-bo",
        "code": "300183",
        "secucode": "300183.SZ",
        "name": "东软载波",
        "mark": "东软",
        "market": "创业板",
        "category": "CPU / 处理器",
        "location": "青岛",
        "products": ["MCU", "PLC 载波通信", "智能电网", "无线连接", "工业控制", "SoC"],
        "description": "MCU 与电力线载波通信芯片企业，覆盖智能电网和工业控制。",
    },
    {
        "id": "an-lu-ke-ji",
        "code": "688107",
        "secucode": "688107.SH",
        "name": "安路科技",
        "mark": "安路",
        "market": "科创板",
        "category": "FPGA / 可编程计算",
        "location": "上海",
        "products": ["FPGA", "FPSoC", "工业控制", "通信", "汽车电子", "EDA"],
        "description": "FPGA 与可编程 SoC 企业，产品覆盖工业、通信和汽车电子。",
    },
    {
        "id": "sui-yuan",
        "code": "688801",
        "secucode": "688801.SH",
        "name": "燧原科技",
        "mark": "燧原",
        "market": "科创板",
        "category": "GPU / AI 算力",
        "location": "上海",
        "aliases": ["燧原科技-U"],
        "products": ["AI 训练", "AI 推理", "云端 AI 芯片", "智算集群", "加速卡", "软件栈"],
        "description": "云端 AI 芯片与加速卡企业，覆盖训练、推理和智算集群。",
    },
    {
        "id": "yun-tian-li-fei",
        "code": "688343",
        "secucode": "688343.SH",
        "name": "云天励飞",
        "mark": "云天",
        "market": "科创板",
        "location": "深圳",
        "aliases": ["云天励飞-U"],
        "category": "GPU / AI 算力",
        "products": ["AI 推理", "边缘 AI", "AI SoC", "城市治理", "智能终端", "算法芯片化"],
        "description": "AI 推理芯片与算法平台企业，覆盖边缘 AI、智能终端和城市治理。",
    },
    {
        "id": "chang-xin-ke-ji",
        "code": "688825",
        "secucode": "688825.SH",
        "name": "长鑫科技",
        "mark": "长鑫",
        "market": "科创板",
        "category": "存储芯片",
        "location": "合肥",
        "products": ["DRAM", "DDR5", "LPDDR5", "HBM", "存储芯片", "晶圆制造"],
        "description": "DRAM 存储芯片企业，覆盖 DDR5、LPDDR5 和 HBM 等产品方向。",
    },
    {
        "id": "pu-ran",
        "code": "688766",
        "secucode": "688766.SH",
        "name": "普冉股份",
        "mark": "普冉",
        "market": "科创板",
        "category": "存储芯片",
        "location": "上海",
        "products": ["NOR Flash", "EEPROM", "MCU", "车规存储", "低功耗", "存储芯片"],
        "description": "NOR Flash 与 EEPROM 存储芯片企业，布局车规和低功耗应用。",
    },
    {
        "id": "dong-xin",
        "code": "688110",
        "secucode": "688110.SH",
        "name": "东芯股份",
        "mark": "东芯",
        "market": "科创板",
        "category": "存储芯片",
        "location": "上海",
        "products": ["NAND Flash", "NOR Flash", "DRAM", "EEPROM", "车规存储", "存储芯片"],
        "description": "中小容量存储芯片企业，产品覆盖 NAND、NOR、DRAM 与 EEPROM。",
    },
    {
        "id": "heng-shuo",
        "code": "688416",
        "secucode": "688416.SH",
        "name": "恒烁股份",
        "mark": "恒烁",
        "market": "科创板",
        "category": "存储芯片",
        "location": "合肥",
        "products": ["NOR Flash", "MCU", "存算一体", "AI 加速", "存储芯片", "低功耗"],
        "description": "NOR Flash 与存算一体芯片企业，布局低功耗存储和 AI 加速。",
    },
    {
        "id": "ju-chen",
        "code": "688123",
        "secucode": "688123.SH",
        "name": "聚辰股份",
        "mark": "聚辰",
        "market": "科创板",
        "category": "存储芯片",
        "location": "上海",
        "products": ["EEPROM", "NOR Flash", "DDR5 SPD", "车规存储", "马达驱动", "存储芯片"],
        "description": "EEPROM 与 NOR Flash 企业，DDR5 SPD 产品受益于服务器内存升级。",
    },
    {
        "id": "lan-qi",
        "code": "688008",
        "secucode": "688008.SH",
        "name": "澜起科技",
        "mark": "澜起",
        "market": "科创板",
        "category": "存储芯片",
        "location": "上海",
        "products": ["DDR5 RCD", "MRCD / MDB", "CKD", "PCIe Retimer", "CXL", "内存接口"],
        "description": "内存接口芯片龙头，覆盖 DDR5、CXL 和高速互连产品。",
    },
    {
        "id": "lian-yun",
        "code": "688449",
        "secucode": "688449.SH",
        "name": "联芸科技",
        "mark": "联芸",
        "market": "科创板",
        "category": "存储芯片",
        "location": "杭州",
        "products": ["SSD 主控", "存储主控", "数据存储", "AIoT", "车载存储", "固件"],
        "description": "SSD 与存储主控芯片企业，覆盖消费级、企业级和车载存储。",
    },
    {
        "id": "de-ming-li",
        "code": "001309",
        "secucode": "001309.SZ",
        "name": "德明利",
        "mark": "德明",
        "market": "深交所主板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["SSD 主控", "移动存储", "嵌入式存储", "内存模组", "企业级 SSD", "存储方案"],
        "description": "存储主控与模组企业，覆盖嵌入式存储、SSD 和内存模组。",
    },
    {
        "id": "jiang-bo-long",
        "code": "301308",
        "secucode": "301308.SZ",
        "name": "江波龙",
        "mark": "江波龙",
        "market": "创业板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["嵌入式存储", "SSD", "内存条", "移动存储", "企业级存储", "车规存储"],
        "description": "存储模组与品牌企业，覆盖嵌入式存储、SSD、内存条和车规存储。",
    },
    {
        "id": "bai-wei",
        "code": "688525",
        "secucode": "688525.SH",
        "name": "佰维存储",
        "mark": "佰维",
        "market": "科创板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["嵌入式存储", "SSD", "内存模组", "移动存储", "先进封测", "车规存储"],
        "description": "存储模组与先进封测企业，覆盖嵌入式存储、SSD 和车规应用。",
    },
    {
        "id": "da-pu-wei",
        "code": "301666",
        "secucode": "301666.SZ",
        "name": "大普微",
        "mark": "大普",
        "market": "创业板",
        "aliases": ["大普微-UW"],
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["企业级 SSD", "数据中心存储", "PCIe SSD", "存储主控", "固件", "AI 存储"],
        "description": "企业级 SSD 企业，面向数据中心、AI 存储和云基础设施。",
    },
    {
        "id": "lang-ke",
        "code": "300042",
        "secucode": "300042.SZ",
        "name": "朗科科技",
        "mark": "朗科",
        "market": "创业板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["移动存储", "SSD", "内存条", "闪存盘", "存储专利", "消费存储"],
        "description": "移动存储与消费级存储企业，拥有闪存盘等存储相关专利。",
    },
    {
        "id": "xiang-nong",
        "code": "300475",
        "secucode": "300475.SZ",
        "name": "香农芯创",
        "mark": "香农",
        "market": "创业板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["存储分销", "SK 海力士代理", "企业级存储", "半导体分销", "算力服务器", "存储方案"],
        "description": "半导体与存储分销平台，代理 SK 海力士等存储产品，并向算力基础设施延伸。",
    },
    {
        "id": "shen-ke-ji",
        "code": "000021",
        "secucode": "000021.SZ",
        "name": "深科技",
        "mark": "深科技",
        "market": "深交所主板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["存储制造", "HDD", "SSD", "内存模组", "封测", "计量系统"],
        "description": "存储制造与封测平台，覆盖 HDD、SSD、内存模组和计量系统。",
    },
    {
        "id": "lang-chao",
        "code": "000977",
        "secucode": "000977.SZ",
        "name": "浪潮信息",
        "mark": "浪潮",
        "market": "深交所主板",
        "category": "存储模组 / 系统",
        "location": "济南",
        "products": ["AI 服务器", "通用服务器", "存储系统", "数据中心", "液冷", "算力基础设施"],
        "description": "服务器与存储系统龙头，覆盖 AI 服务器、通用服务器和数据中心基础设施。",
    },
    {
        "id": "zhong-ke-shu-guang",
        "code": "603019",
        "secucode": "603019.SH",
        "name": "中科曙光",
        "mark": "曙光",
        "market": "上交所主板",
        "category": "存储模组 / 系统",
        "location": "北京",
        "products": ["高性能计算", "服务器", "存储系统", "液冷", "数据中心", "信创"],
        "description": "高性能计算与存储系统企业，覆盖服务器、液冷数据中心和信创。",
    },
    {
        "id": "zi-guang-gu-fen",
        "code": "000938",
        "secucode": "000938.SZ",
        "name": "紫光股份",
        "mark": "紫光",
        "market": "深交所主板",
        "category": "存储模组 / 系统",
        "location": "北京",
        "products": ["新华三", "服务器", "存储系统", "网络设备", "云计算", "数据中心"],
        "description": "新华三母公司，覆盖服务器、存储、网络和数据中心解决方案。",
    },
    {
        "id": "tong-you",
        "code": "300302",
        "secucode": "300302.SZ",
        "name": "同有科技",
        "mark": "同有",
        "market": "创业板",
        "category": "存储模组 / 系统",
        "location": "北京",
        "products": ["存储系统", "备份容灾", "分布式存储", "闪存阵列", "军工存储", "数据管理"],
        "description": "专业存储系统企业，覆盖分布式存储、闪存阵列和备份容灾。",
    },
    {
        "id": "tai-ji",
        "code": "600667",
        "secucode": "600667.SH",
        "name": "太极实业",
        "mark": "太极",
        "market": "上交所主板",
        "category": "存储配套",
        "location": "无锡",
        "products": ["DRAM 封测", "半导体工程", "洁净室", "存储封测", "光伏电站", "工程服务"],
        "description": "DRAM 封测与半导体工程服务企业，覆盖存储封测和洁净室工程。",
    },
    {
        "id": "ya-ke",
        "code": "002409",
        "secucode": "002409.SZ",
        "name": "雅克科技",
        "mark": "雅克",
        "market": "深交所主板",
        "category": "存储配套",
        "location": "宜兴",
        "products": ["前驱体", "电子特气", "光刻胶", "DRAM 材料", "LNG 保温", "半导体材料"],
        "description": "半导体材料平台，前驱体和电子特气覆盖 DRAM 等先进存储工艺。",
    },
    {
        "id": "ding-long",
        "code": "300054",
        "secucode": "300054.SZ",
        "name": "鼎龙股份",
        "mark": "鼎龙",
        "market": "创业板",
        "category": "存储配套",
        "location": "武汉",
        "products": ["CMP 抛光垫", "抛光液", "显示材料", "半导体材料", "存储材料", "打印耗材"],
        "description": "CMP 抛光垫与半导体材料企业，覆盖存储晶圆制造关键材料。",
    },
    {
        "id": "an-ji",
        "code": "688019",
        "secucode": "688019.SH",
        "name": "安集科技",
        "mark": "安集",
        "market": "科创板",
        "category": "存储配套",
        "location": "上海",
        "products": ["CMP 抛光液", "湿电子化学品", "电镀液", "清洗液", "先进封装", "晶圆制造"],
        "description": "半导体材料企业，核心产品包括 CMP 抛光液和功能性湿电子化学品。",
    },
    {
        "id": "jiang-feng",
        "code": "300666",
        "secucode": "300666.SZ",
        "name": "江丰电子",
        "mark": "江丰",
        "market": "创业板",
        "category": "存储配套",
        "location": "余姚",
        "products": ["溅射靶材", "半导体零部件", "存储材料", "真空部件", "集成电路", "面板靶材"],
        "description": "超高纯溅射靶材与半导体零部件企业，服务于晶圆制造和存储工艺。",
    },
    {
        "id": "hu-gui",
        "code": "688126",
        "secucode": "688126.SH",
        "name": "沪硅产业",
        "mark": "沪硅",
        "market": "科创板",
        "category": "存储配套",
        "location": "上海",
        "products": ["300mm 硅片", "200mm 硅片", "SOI 硅片", "外延片", "存储硅片", "半导体材料"],
        "description": "大尺寸硅片平台，产品覆盖 300mm、200mm 与 SOI 硅片。",
    },
    {
        "id": "zi-guang-gu-wei",
        "code": "002049",
        "secucode": "002049.SZ",
        "name": "紫光国微",
        "mark": "国微",
        "market": "深交所主板",
        "category": "FPGA / 可编程计算",
        "location": "北京",
        "products": ["FPGA", "特种集成电路", "安全芯片", "智能卡", "晶体", "车规"],
        "description": "特种集成电路与安全芯片平台，产品覆盖 FPGA、智能安全和汽车电子。",
    },
    {
        "id": "zhao-yi",
        "code": "603986",
        "secucode": "603986.SH",
        "name": "兆易创新",
        "mark": "兆易",
        "market": "上交所主板",
        "category": "存储芯片",
        "location": "北京",
        "products": ["NOR Flash", "DRAM", "MCU", "传感器", "PMIC", "车规存储"],
        "description": "存储与 MCU 平台型设计公司，NOR Flash 与通用 MCU 具备全球竞争力。",
    },
    {
        "id": "tong-fu-wei-dian",
        "code": "002156",
        "secucode": "002156.SZ",
        "name": "通富微电",
        "mark": "通富",
        "market": "深交所主板",
        "category": "封装测试",
        "location": "南通",
        "products": ["先进封装", "Chiplet", "倒装封装", "存储封测", "汽车电子", "功率器件"],
        "description": "国内封测龙头之一，深度参与高性能计算芯片的倒装与 Chiplet 封装。",
    },
    {
        "id": "chang-dian-ke-ji",
        "code": "600584",
        "secucode": "600584.SH",
        "name": "长电科技",
        "mark": "长电",
        "market": "上交所主板",
        "category": "封装测试",
        "location": "江阴",
        "products": ["先进封装", "2.5D / 3D", "SiP", "倒装封装", "存储封测", "汽车电子"],
        "description": "全球领先的集成电路封测企业，布局先进封装、汽车电子和存储封测。",
    },
    {
        "id": "li-yang-xin-pian",
        "code": "688135",
        "secucode": "688135.SH",
        "name": "利扬芯片",
        "mark": "利扬",
        "market": "科创板",
        "category": "封装测试",
        "location": "东莞",
        "products": ["晶圆测试", "成品测试", "存储测试", "汽车电子", "高可靠", "测试方案"],
        "description": "独立第三方集成电路测试企业，覆盖晶圆测试、成品测试和汽车电子。",
    },
    {
        "id": "qi-zhong-ke-ji",
        "code": "688352",
        "secucode": "688352.SH",
        "name": "颀中科技",
        "mark": "颀中",
        "market": "科创板",
        "category": "封装测试",
        "location": "合肥",
        "products": ["显示驱动封测", "金凸块", "COF", "先进封装", "车规", "存储"],
        "description": "显示驱动芯片先进封装与测试企业，覆盖金凸块、COF 和车规产品。",
    },
    {
        "id": "yong-xi-dian-zi",
        "code": "688362",
        "secucode": "688362.SH",
        "name": "甬矽电子",
        "mark": "甬矽",
        "market": "科创板",
        "category": "封装测试",
        "location": "宁波",
        "products": ["SiP", "倒装封装", "存储封测", "射频封测", "汽车电子", "先进封装"],
        "description": "集成电路封装测试企业，聚焦 SiP、倒装和高密度封装。",
    },
    {
        "id": "hui-cheng-gu-fen",
        "code": "688403",
        "secucode": "688403.SH",
        "name": "汇成股份",
        "mark": "汇成",
        "market": "科创板",
        "category": "封装测试",
        "location": "合肥",
        "products": ["显示驱动封测", "金凸块", "COF", "先进封装", "存储", "车规"],
        "description": "显示驱动芯片封装测试企业，覆盖金凸块、COF 和先进封装。",
    },
    {
        "id": "sheng-he-jing-wei",
        "code": "688820",
        "secucode": "688820.SH",
        "name": "盛合晶微",
        "mark": "盛合",
        "market": "科创板",
        "category": "封装测试",
        "location": "江阴",
        "products": ["2.5D / 3D", "晶圆级封装", "Chiplet", "三维集成", "先进封装", "HBM"],
        "description": "晶圆级先进封装企业，聚焦 2.5D/3D、Chiplet 和三维集成。",
    },
    {
        "id": "qiang-yi",
        "code": "688809",
        "secucode": "688809.SH",
        "name": "强一股份",
        "mark": "强一",
        "market": "科创板",
        "category": "封装测试",
        "location": "苏州",
        "products": ["探针卡", "MEMS 探针", "晶圆测试", "存储测试", "先进封装", "测试接口"],
        "description": "半导体测试接口企业，核心产品覆盖探针卡、MEMS 探针和晶圆测试。",
    },
    {
        "id": "shen-ke-da",
        "code": "688328",
        "secucode": "688328.SH",
        "name": "深科达",
        "mark": "深科达",
        "market": "科创板",
        "category": "封装测试",
        "location": "深圳",
        "products": ["固晶机", "贴合设备", "半导体封装", "检测设备", "显示设备", "自动化"],
        "description": "半导体封装与显示设备企业，覆盖固晶、贴合和检测自动化。",
    },
    {
        "id": "nai-ke-zhuang-bei",
        "code": "688419",
        "secucode": "688419.SH",
        "name": "耐科装备",
        "mark": "耐科",
        "market": "科创板",
        "category": "封装测试",
        "location": "铜陵",
        "products": ["封装设备", "挤出模具", "半导体封装", "自动化", "光伏", "材料"],
        "description": "半导体封装设备与挤出模具企业，覆盖封装自动化和光伏应用。",
    },
    {
        "id": "dong-wei-ban-dao",
        "code": "688261",
        "secucode": "688261.SH",
        "name": "东微半导",
        "mark": "东微",
        "market": "科创板",
        "category": "功率半导体",
        "location": "苏州",
        "products": ["高压 MOSFET", "超级结", "IGBT", "功率器件", "汽车电子", "工业"],
        "description": "高压功率器件企业，核心产品覆盖超级结 MOSFET 和 IGBT。",
    },
    {
        "id": "xin-jie-neng",
        "code": "605111",
        "secucode": "605111.SH",
        "name": "新洁能",
        "mark": "新洁能",
        "market": "上交所主板",
        "category": "功率半导体",
        "location": "无锡",
        "products": ["MOSFET", "IGBT", "SiC", "功率器件", "汽车电子", "工业"],
        "description": "功率半导体设计企业，产品覆盖 MOSFET、IGBT 和 SiC 器件。",
    },
    {
        "id": "xin-xiang-wei",
        "code": "688593",
        "secucode": "688593.SH",
        "name": "新相微",
        "mark": "新相",
        "market": "科创板",
        "category": "显示驱动",
        "location": "上海",
        "products": ["显示驱动", "DDIC", "TDDI", "AMOLED", "车规", "可穿戴"],
        "description": "显示驱动芯片企业，覆盖 LCD、AMOLED、TDDI 和车规显示。",
    },
    {
        "id": "chang-guang-hua-xin",
        "code": "688048",
        "secucode": "688048.SH",
        "name": "长光华芯",
        "mark": "长光",
        "market": "科创板",
        "category": "光通信 / 激光芯片",
        "location": "苏州",
        "products": ["半导体激光器", "VCSEL", "高功率激光", "光通信", "激光雷达", "工业"],
        "description": "半导体激光芯片企业，产品覆盖高功率激光、VCSEL 和光通信。",
    },
    {
        "id": "you-xun",
        "code": "688807",
        "secucode": "688807.SH",
        "name": "优迅股份",
        "mark": "优迅",
        "market": "科创板",
        "category": "光通信 / 激光芯片",
        "location": "厦门",
        "products": ["光通信芯片", "光收发", "PON", "5G", "数据中心", "激光驱动"],
        "description": "光通信芯片企业，覆盖 PON、5G 和数据中心光模块应用。",
    },
    {
        "id": "can-xin",
        "code": "688691",
        "secucode": "688691.SH",
        "name": "灿芯股份",
        "mark": "灿芯",
        "market": "科创板",
        "category": "ASIC / 设计服务",
        "location": "上海",
        "products": ["ASIC 设计服务", "SoC 定制", "IP", "55nm / 28nm", "AIoT", "一站式"],
        "description": "一站式芯片定制服务企业，提供 ASIC、SoC 和 IP 解决方案。",
    },
    {
        "id": "sheng-ke-tong-xin",
        "code": "688702",
        "secucode": "688702.SH",
        "name": "盛科通信",
        "mark": "盛科",
        "market": "科创板",
        "category": "网络 / 交换芯片",
        "location": "苏州",
        "aliases": ["盛科通信-U"],
        "products": ["以太网交换芯片", "数据中心", "工业网络", "5G", "国产网络", "交换芯片"],
        "description": "以太网交换芯片企业，覆盖数据中心、工业和运营商网络。",
    },
    {
        "id": "a-shi-chuang",
        "code": "300706",
        "secucode": "300706.SZ",
        "name": "阿石创",
        "mark": "阿石创",
        "market": "创业板",
        "category": "半导体材料",
        "location": "福州",
        "products": ["溅射靶材", "蒸镀材料", "PVD", "光学镀膜", "半导体材料", "显示"],
        "description": "PVD 镀膜材料企业，产品覆盖溅射靶材、蒸镀材料和平板显示。",
    },
    {
        "id": "you-yan-xin-cai",
        "code": "600206",
        "secucode": "600206.SH",
        "name": "有研新材",
        "mark": "有研",
        "market": "上交所主板",
        "category": "半导体材料",
        "location": "北京",
        "products": ["高纯金属", "靶材", "稀土材料", "半导体材料", "红外", "新材料"],
        "description": "稀有金属与电子材料平台，产品覆盖高纯金属、靶材和半导体材料。",
    },
    {
        "id": "zhong-chuan-te-qi",
        "code": "688146",
        "secucode": "688146.SH",
        "name": "中船特气",
        "mark": "中船",
        "market": "科创板",
        "category": "半导体材料",
        "location": "邯郸",
        "products": ["电子特气", "NF3", "WF6", "高纯气体", "半导体材料", "显示"],
        "description": "电子特种气体企业，产品覆盖三氟化氮、六氟化钨和高纯电子气体。",
    },
    {
        "id": "shen-gong",
        "code": "688233",
        "secucode": "688233.SH",
        "name": "神工股份",
        "mark": "神工",
        "market": "科创板",
        "category": "半导体材料",
        "location": "锦州",
        "products": ["单晶硅材料", "硅电极", "刻蚀用硅", "存储", "晶圆", "半导体材料"],
        "description": "大直径单晶硅材料企业，产品用于刻蚀硅电极和半导体零部件。",
    },
    {
        "id": "tian-yue-xian-jin",
        "code": "688234",
        "secucode": "688234.SH",
        "name": "天岳先进",
        "mark": "天岳",
        "market": "科创板",
        "category": "半导体材料",
        "location": "济南",
        "products": ["SiC 衬底", "6 英寸", "8 英寸", "功率器件", "汽车", "半导体材料"],
        "description": "碳化硅衬底企业，产品覆盖 6 英寸、8 英寸 SiC 衬底。",
    },
    {
        "id": "qing-yi-guang-dian",
        "code": "688138",
        "secucode": "688138.SH",
        "name": "清溢光电",
        "mark": "清溢",
        "market": "科创板",
        "category": "半导体材料",
        "location": "深圳",
        "products": ["光掩膜版", "面板掩膜", "半导体掩膜", "OLED", "PCB", "微电子"],
        "description": "光掩膜版企业，产品覆盖平板显示、半导体和 PCB 掩膜版。",
    },
    {
        "id": "lu-wei-guang-dian",
        "code": "688401",
        "secucode": "688401.SH",
        "name": "路维光电",
        "mark": "路维",
        "market": "科创板",
        "category": "半导体材料",
        "location": "深圳",
        "products": ["光掩膜版", "面板", "半导体", "PCB", "微电子", "掩膜版"],
        "description": "光掩膜版企业，覆盖平板显示、半导体和微电子掩膜版。",
    },
    {
        "id": "you-yan-gui",
        "code": "688432",
        "secucode": "688432.SH",
        "name": "有研硅",
        "mark": "有研硅",
        "market": "科创板",
        "category": "半导体材料",
        "location": "北京",
        "products": ["硅片", "硅材料", "刻蚀硅", "功率器件", "存储", "半导体材料"],
        "description": "硅材料企业，产品覆盖半导体硅片、刻蚀硅材料和功率器件用硅。",
    },
    {
        "id": "ou-lai-xin-cai",
        "code": "688530",
        "secucode": "688530.SH",
        "name": "欧莱新材",
        "mark": "欧莱",
        "market": "科创板",
        "category": "半导体材料",
        "location": "韶关",
        "products": ["溅射靶材", "铜靶", "铝靶", "钛靶", "半导体材料", "显示"],
        "description": "溅射靶材企业，产品覆盖铜、铝、钛等靶材和显示镀膜材料。",
    },
    {
        "id": "hua-hai-cheng-ke",
        "code": "688535",
        "secucode": "688535.SH",
        "name": "华海诚科",
        "mark": "华海",
        "market": "科创板",
        "category": "半导体材料",
        "location": "连云港",
        "products": ["环氧塑封料", "先进封装材料", "存储封装", "车规", "电子胶", "半导体材料"],
        "description": "半导体封装材料企业，产品覆盖环氧塑封料、先进封装材料和电子胶。",
    },
    {
        "id": "heng-kun-xin-cai",
        "code": "688727",
        "secucode": "688727.SH",
        "name": "恒坤新材",
        "mark": "恒坤",
        "market": "科创板",
        "category": "半导体材料",
        "location": "厦门",
        "products": ["光刻胶", "前驱体", "电子材料", "半导体材料", "存储", "显示"],
        "description": "半导体电子材料企业，产品覆盖光刻胶、前驱体和电子特气材料。",
    },
    {
        "id": "ai-sen",
        "code": "688720",
        "secucode": "688720.SH",
        "name": "艾森股份",
        "mark": "艾森",
        "market": "科创板",
        "category": "半导体材料",
        "location": "昆山",
        "products": ["电镀液", "光刻胶", "清洗液", "半导体材料", "先进封装", "存储"],
        "description": "半导体湿电子化学品企业，覆盖电镀液、光刻胶和清洗液。",
    },
    {
        "id": "kai-de-shi-ying",
        "code": "920179",
        "secucode": "920179.BJ",
        "name": "凯德石英",
        "mark": "凯德",
        "market": "北交所",
        "category": "半导体材料",
        "location": "北京",
        "products": ["石英制品", "扩散管", "石英舟", "半导体材料", "存储", "光伏"],
        "description": "石英制品企业，产品覆盖扩散管、石英舟和半导体用石英部件。",
    },
    {
        "id": "ke-ma-ke-ji",
        "code": "301611",
        "secucode": "301611.SZ",
        "name": "珂玛科技",
        "mark": "珂玛",
        "market": "创业板",
        "category": "半导体材料",
        "location": "苏州",
        "products": ["先进陶瓷", "半导体零部件", "刻蚀腔体", "存储设备", "显示", "材料"],
        "description": "先进陶瓷材料与零部件企业，产品用于刻蚀腔体和半导体设备。",
    },
    {
        "id": "jing-yi-zhuang-bei",
        "code": "688652",
        "secucode": "688652.SH",
        "name": "京仪装备",
        "mark": "京仪",
        "market": "科创板",
        "category": "半导体设备",
        "location": "北京",
        "products": ["温控设备", "废气处理", "晶圆传片", "半导体设备", "存储", "零部件"],
        "description": "半导体专用设备企业，产品覆盖温控、废气处理和晶圆传片。",
    },
    {
        "id": "wei-dao-na-mi",
        "code": "688147",
        "secucode": "688147.SH",
        "name": "微导纳米",
        "mark": "微导",
        "market": "科创板",
        "category": "半导体设备",
        "location": "无锡",
        "products": ["ALD", "CVD", "半导体设备", "先进封装", "存储", "光伏"],
        "description": "原子层沉积设备企业，产品覆盖 ALD、CVD 和先进封装。",
    },
    {
        "id": "hua-feng-ce-kong",
        "code": "688200",
        "secucode": "688200.SH",
        "name": "华峰测控",
        "mark": "华峰",
        "market": "科创板",
        "category": "半导体设备",
        "location": "北京",
        "products": ["模拟测试机", "SoC 测试机", "功率测试", "存储测试", "ATE", "测试板卡"],
        "description": "半导体自动化测试设备企业，覆盖模拟、功率、SoC 和存储测试。",
    },
    {
        "id": "jin-hai-tong",
        "code": "603061",
        "secucode": "603061.SH",
        "name": "金海通",
        "mark": "金海通",
        "market": "上交所主板",
        "category": "半导体设备",
        "location": "天津",
        "products": ["测试分选机", "平移式分选", "存储测试", "汽车电子", "温控", "自动化"],
        "description": "半导体测试分选设备企业，覆盖存储、汽车电子和温控测试。",
    },
    {
        "id": "lian-dong-ke-ji",
        "code": "301369",
        "secucode": "301369.SZ",
        "name": "联动科技",
        "mark": "联动",
        "market": "创业板",
        "category": "半导体设备",
        "location": "佛山",
        "products": ["功率测试", "分立器件测试", "老化设备", "测试系统", "汽车", "半导体"],
        "description": "功率与分立器件测试设备企业，覆盖老化、测试系统和汽车电子。",
    },
    {
        "id": "xi-dian-gu-fen",
        "code": "301629",
        "secucode": "301629.SZ",
        "name": "矽电股份",
        "mark": "矽电",
        "market": "创业板",
        "category": "半导体设备",
        "location": "深圳",
        "products": ["探针台", "晶圆测试", "半导体设备", "存储测试", "先进封装", "自动化"],
        "description": "探针台与晶圆测试设备企业，覆盖存储、先进封装和自动化测试。",
    },
    {
        "id": "fu-chuang-jing-mi",
        "code": "688409",
        "secucode": "688409.SH",
        "name": "富创精密",
        "mark": "富创",
        "market": "科创板",
        "category": "半导体设备",
        "location": "沈阳",
        "products": ["精密零部件", "腔体", "气体管路", "半导体设备", "存储设备", "航空"],
        "description": "半导体设备精密零部件企业，产品覆盖腔体、气体管路和模组。",
    },
    {
        "id": "xian-feng-jing-ke",
        "code": "688605",
        "secucode": "688605.SH",
        "name": "先锋精科",
        "mark": "先锋",
        "market": "科创板",
        "category": "半导体设备",
        "location": "南通",
        "products": ["精密零部件", "刻蚀腔体", "薄膜沉积", "半导体设备", "存储", "医疗"],
        "description": "半导体设备精密零部件企业，覆盖刻蚀腔体和薄膜沉积部件。",
    },
    {
        "id": "yi-tang-gu-fen",
        "code": "688729",
        "secucode": "688729.SH",
        "name": "屹唐股份",
        "mark": "屹唐",
        "market": "科创板",
        "category": "半导体设备",
        "location": "北京",
        "products": ["干法去胶", "快速热处理", "干法刻蚀", "半导体设备", "存储", "晶圆制造"],
        "description": "半导体前道设备企业，产品覆盖干法去胶、快速热处理和刻蚀。",
    },
    {
        "id": "zhen-bao",
        "code": "688797",
        "secucode": "688797.SH",
        "name": "臻宝科技",
        "mark": "臻宝",
        "market": "科创板",
        "category": "半导体设备",
        "location": "上海",
        "products": ["精密零部件", "石英", "陶瓷", "半导体设备", "存储", "面板"],
        "description": "半导体设备精密零部件企业，覆盖石英、陶瓷和清洗部件。",
    },
    {
        "id": "tuo-lun-si",
        "code": "301583",
        "secucode": "301583.SZ",
        "name": "托伦斯",
        "mark": "托伦斯",
        "market": "创业板",
        "category": "半导体设备",
        "location": "苏州",
        "products": ["精密零部件", "半导体设备", "腔体", "模组", "真空", "清洗"],
        "description": "半导体设备精密零部件与模组企业，覆盖腔体、真空和清洗系统。",
    },
    {
        "id": "chao-chun-ying-cai",
        "code": "301717",
        "secucode": "301717.SZ",
        "name": "超纯应材",
        "mark": "超纯",
        "market": "创业板",
        "category": "半导体材料",
        "location": "上海",
        "products": ["高纯材料", "湿电子化学品", "清洗", "半导体材料", "晶圆制造", "存储"],
        "description": "超高纯半导体材料企业，覆盖湿电子化学品和晶圆制造材料。",
    },
    {
        "id": "jing-sheng",
        "code": "688478",
        "secucode": "688478.SH",
        "name": "晶升股份",
        "mark": "晶升",
        "market": "科创板",
        "category": "半导体设备",
        "location": "南京",
        "products": ["晶体生长设备", "SiC", "硅单晶", "蓝宝石", "半导体设备", "自动化"],
        "description": "晶体生长设备企业，覆盖 SiC、硅单晶和蓝宝石长晶。",
    },
    {
        "id": "yue-xin-ban-dao",
        "code": "301660",
        "secucode": "301660.SZ",
        "name": "粤芯半导",
        "mark": "粤芯",
        "market": "创业板",
        "aliases": ["粤芯半导-U"],
        "category": "晶圆代工 FAB",
        "location": "广州",
        "products": ["12 英寸代工", "模拟芯片", "电源管理", "CIS", "BCD", "汽车"],
        "description": "12 英寸特色工艺晶圆代工企业，覆盖模拟、电源、CIS 和汽车芯片。",
    },
    {
        "id": "he-lin-wei-na",
        "code": "688661",
        "secucode": "688661.SH",
        "name": "和林微纳",
        "mark": "和林",
        "market": "科创板",
        "category": "封装测试",
        "location": "苏州",
        "products": ["MEMS 零部件", "探针卡", "半导体测试", "微纳制造", "存储", "消费电子"],
        "description": "微纳制造与半导体测试零部件企业，产品覆盖 MEMS 部件和探针卡。",
    },
    {
        "id": "da-gang-gu-fen",
        "code": "002077",
        "secucode": "002077.SZ",
        "name": "大港股份",
        "mark": "大港",
        "market": "深交所主板",
        "category": "封装测试",
        "location": "镇江",
        "products": ["集成电路测试", "晶圆测试", "成品测试", "园区运营", "环保服务", "半导体"],
        "description": "以集成电路测试和环保资源服务为主业，覆盖晶圆测试与成品测试。",
    },
    {
        "id": "kang-qiang-dian-zi",
        "code": "002119",
        "secucode": "002119.SZ",
        "name": "康强电子",
        "mark": "康强",
        "market": "深交所主板",
        "category": "半导体材料",
        "location": "宁波",
        "products": ["引线框架", "键合丝", "蚀刻框架", "封装材料", "汽车电子", "5G"],
        "description": "半导体封装基础材料企业，核心产品为引线框架和键合丝。",
    },
    {
        "id": "hua-tian-ke-ji",
        "code": "002185",
        "secucode": "002185.SZ",
        "name": "华天科技",
        "mark": "华天",
        "market": "深交所主板",
        "category": "封装测试",
        "location": "天水",
        "products": ["晶圆级封装", "基板封装", "引线框封装", "晶圆测试", "先进封装", "汽车电子"],
        "description": "全球知名集成电路封测企业，提供封装设计、晶圆测试和成品测试。",
    },
    {
        "id": "da-wei-gu-fen",
        "code": "002213",
        "secucode": "002213.SZ",
        "name": "大为股份",
        "mark": "大为",
        "market": "深交所主板",
        "category": "存储模组 / 系统",
        "location": "深圳",
        "products": ["半导体存储", "存储模组", "智能终端", "汽车电子", "新能源", "缓速器"],
        "description": "形成“新能源+汽车”和“半导体存储+智能终端”双主业布局。",
    },
    {
        "id": "zhong-jing-ke-ji",
        "code": "003026",
        "secucode": "003026.SZ",
        "name": "中晶科技",
        "mark": "中晶",
        "market": "深交所主板",
        "category": "半导体材料",
        "location": "湖州",
        "products": ["单晶硅棒", "研磨硅片", "抛光硅片", "高压整流器件", "半导体材料", "功率器件"],
        "description": "半导体单晶硅材料及制品企业，覆盖硅棒、研磨片和抛光片。",
    },
    {
        "id": "hua-ya-zhi-neng",
        "code": "003043",
        "secucode": "003043.SZ",
        "name": "华亚智能",
        "mark": "华亚",
        "market": "深交所主板",
        "category": "半导体设备",
        "location": "苏州",
        "products": ["精密钣金", "半导体设备零部件", "精密焊接", "模组", "轨道交通", "医疗器械"],
        "description": "精密钣金与设备结构件企业，为半导体设备提供精密零部件和模组。",
    },
    {
        "id": "tai-ji-gu-fen",
        "code": "300046",
        "secucode": "300046.SZ",
        "name": "台基股份",
        "mark": "台基",
        "market": "创业板",
        "category": "功率半导体",
        "location": "襄阳",
        "products": ["晶闸管", "功率模块", "功率组件", "散热器", "电力电子", "工业"],
        "description": "大功率晶闸管与功率半导体模块企业，覆盖电力电子和工业应用。",
    },
    {
        "id": "yang-jie-ke-ji",
        "code": "300373",
        "secucode": "300373.SZ",
        "name": "扬杰科技",
        "mark": "扬杰",
        "market": "创业板",
        "category": "功率半导体",
        "location": "扬州",
        "products": ["MOSFET", "IGBT", "SiC", "整流器件", "功率模块", "汽车电子"],
        "description": "功率半导体 IDM 企业，覆盖分立器件芯片、封装和功率模块。",
    },
    {
        "id": "sai-wei-dian-zi",
        "code": "300456",
        "secucode": "300456.SZ",
        "name": "赛微电子",
        "mark": "赛微",
        "market": "创业板",
        "category": "晶圆代工 FAB",
        "location": "北京",
        "products": ["MEMS 代工", "特色工艺", "硅光子", "激光雷达", "高频通信", "晶圆制造"],
        "description": "高端特色工艺晶圆制造商，重点覆盖 MEMS、硅光子和高频通信。",
    },
    {
        "id": "jie-jie-wei-dian",
        "code": "300623",
        "secucode": "300623.SZ",
        "name": "捷捷微电",
        "mark": "捷捷",
        "market": "创业板",
        "category": "功率半导体",
        "location": "南通",
        "products": ["晶闸管", "MOSFET", "IGBT", "SiC", "功率器件", "汽车电子"],
        "description": "功率半导体器件企业，覆盖晶闸管、MOSFET、IGBT 和 SiC。",
    },
    {
        "id": "pai-rui",
        "code": "300831",
        "secucode": "300831.SZ",
        "name": "ST派瑞",
        "mark": "派瑞",
        "market": "创业板",
        "aliases": ["派瑞股份"],
        "category": "功率半导体",
        "location": "西安",
        "products": ["功率半导体", "晶闸管", "变流装置", "测试设备", "电力电子", "高功率"],
        "description": "大功率半导体器件与电力电子变流装置企业，原简称派瑞股份。",
    },
    {
        "id": "fu-le-de",
        "code": "301297",
        "secucode": "301297.SZ",
        "name": "富乐德",
        "mark": "富乐德",
        "market": "创业板",
        "category": "半导体设备",
        "location": "铜陵",
        "products": ["设备精密洗净", "涂层", "表面处理", "半导体设备", "显示面板", "再生服务"],
        "description": "泛半导体设备精密洗净与再生服务企业，覆盖半导体和显示面板。",
    },
    {
        "id": "lan-jian-dian-zi",
        "code": "301348",
        "secucode": "301348.SZ",
        "name": "蓝箭电子",
        "mark": "蓝箭",
        "market": "创业板",
        "category": "功率半导体",
        "location": "佛山",
        "products": ["MOSFET", "二极管", "三极管", "晶闸管", "分立器件", "封装测试"],
        "description": "半导体分立器件研发制造企业，产品覆盖 MOSFET、二极管和晶闸管。",
    },
    {
        "id": "xin-heng-hui",
        "code": "301678",
        "secucode": "301678.SZ",
        "name": "新恒汇",
        "mark": "新恒汇",
        "market": "创业板",
        "category": "封装测试",
        "location": "淄博",
        "products": ["智能卡", "柔性引线框架", "eSIM 封测", "蚀刻引线框架", "封装材料", "物联网"],
        "description": "智能卡封装材料与 eSIM 封测企业，覆盖柔性引线框架和模块封装。",
    },
    {
        "id": "zhan-xin",
        "code": "301707",
        "secucode": "301707.SZ",
        "name": "展芯股份",
        "mark": "展芯",
        "market": "创业板",
        "category": "电源管理 / 驱动",
        "location": "南京",
        "products": ["DC-DC", "LDO", "负载开关", "微模块", "信号链", "高可靠"],
        "description": "高可靠模拟芯片与微模块企业，以电源管理和信号链产品为主。",
    },
    {
        "id": "hua-wei-dian-zi",
        "code": "600360",
        "secucode": "600360.SH",
        "name": "华微电子",
        "mark": "华微",
        "market": "上交所主板",
        "category": "功率半导体",
        "location": "吉林",
        "products": ["功率半导体", "MOSFET", "IGBT", "分立器件", "晶圆制造", "封装测试"],
        "description": "功率半导体 IDM 企业，拥有功率器件芯片设计、制造和封测能力。",
    },
    {
        "id": "san-jia-ke-ji",
        "code": "600520",
        "secucode": "600520.SH",
        "name": "三佳科技",
        "mark": "三佳",
        "market": "上交所主板",
        "category": "封装测试",
        "location": "铜陵",
        "products": ["封装模具", "封装设备", "挤出模具", "半导体封装", "自动化", "精密制造"],
        "description": "集成电路封装模具与设备企业，覆盖封装模具、设备和精密制造。",
    },
    {
        "id": "wen-tai",
        "code": "600745",
        "secucode": "600745.SH",
        "name": "*ST闻泰",
        "mark": "闻泰",
        "market": "上交所主板",
        "aliases": ["闻泰科技"],
        "category": "IDM / 平台型",
        "location": "嘉兴",
        "products": ["功率器件", "模拟芯片", "晶圆制造", "封测", "终端产品", "汽车电子"],
        "description": "半导体与产品集成平台，覆盖功率器件、模拟芯片、晶圆制造和终端。",
    },
    {
        "id": "jing-fang-ke-ji",
        "code": "603005",
        "secucode": "603005.SH",
        "name": "晶方科技",
        "mark": "晶方",
        "market": "上交所主板",
        "category": "封装测试",
        "location": "苏州",
        "products": ["晶圆级封装", "CIS 封装", "WLCSP", "光学封装", "汽车电子", "传感器"],
        "description": "晶圆级封装企业，核心覆盖 CMOS 图像传感器和光学传感器封装。",
    },
    {
        "id": "bo-tong-ji-cheng",
        "code": "603068",
        "secucode": "603068.SH",
        "name": "博通集成",
        "mark": "博通",
        "market": "上交所主板",
        "category": "射频 / 混合信号",
        "location": "上海",
        "products": ["无线连接", "Wi-Fi", "蓝牙", "RF SoC", "物联网", "车联网"],
        "description": "无线连接芯片企业，覆盖 Wi-Fi、蓝牙、RF SoC 和物联网。",
    },
    {
        "id": "si-da-ban-dao",
        "code": "603290",
        "secucode": "603290.SH",
        "name": "斯达半导",
        "mark": "斯达",
        "market": "上交所主板",
        "category": "功率半导体",
        "location": "嘉兴",
        "products": ["IGBT", "SiC MOSFET", "GaN HEMT", "功率模块", "汽车电子", "新能源"],
        "description": "IGBT 与功率模块企业，产品覆盖 SiC、GaN 和新能源汽车。",
    },
    {
        "id": "cheng-bang",
        "code": "603316",
        "secucode": "603316.SH",
        "name": "诚邦股份",
        "mark": "诚邦",
        "market": "上交所主板",
        "category": "存储模组 / 系统",
        "location": "杭州",
        "products": ["半导体存储", "存储模组", "芯片封测", "生态环保", "古建修缮", "综合治理"],
        "description": "形成“生态环境+半导体存储”双主业，布局存储模组和芯片封测。",
    },
    {
        "id": "sheng-jing-wei",
        "code": "603375",
        "secucode": "603375.SH",
        "name": "盛景微",
        "mark": "盛景",
        "market": "上交所主板",
        "category": "SoC 芯片",
        "location": "无锡",
        "products": ["工业电子雷管芯片", "控制芯片", "低功耗 SoC", "起爆控制器", "安全系统", "汽车"],
        "description": "工业电子雷管核心控制芯片与起爆控制器企业，并向汽车安全延伸。",
    },
    {
        "id": "ling-xian-gu-fen",
        "code": "603991",
        "secucode": "603991.SH",
        "name": "领先股份",
        "mark": "领先",
        "market": "上交所主板",
        "category": "半导体相关",
        "location": "深圳",
        "products": ["半导体产业", "线缆材料", "高分子材料", "热缩材料", "电子材料", "产业转型"],
        "description": "原线缆用高分子材料企业，正在向半导体科技产业转型。",
    },
    {
        "id": "li-ang-wei",
        "code": "605358",
        "secucode": "605358.SH",
        "name": "立昂微",
        "mark": "立昂",
        "market": "上交所主板",
        "category": "半导体材料",
        "location": "杭州",
        "products": ["半导体硅片", "功率芯片", "射频芯片", "外延片", "晶圆制造", "车规"],
        "description": "半导体硅片与功率芯片平台，覆盖硅片、外延、芯片设计和制造。",
    },
    {
        "id": "ju-guang-ke-ji",
        "code": "688167",
        "secucode": "688167.SH",
        "name": "炬光科技",
        "mark": "炬光",
        "market": "科创板",
        "category": "光通信 / 激光芯片",
        "location": "西安",
        "products": ["半导体激光器", "激光光学", "微纳光学", "光通信", "汽车应用", "泛半导体制程"],
        "description": "高功率半导体激光器与光子应用企业，覆盖光通信和汽车应用。",
    },
    {
        "id": "si-te-wei",
        "code": "688213",
        "secucode": "688213.SH",
        "name": "思特威",
        "mark": "思特威",
        "market": "科创板",
        "category": "图像传感器",
        "location": "上海",
        "products": ["CMOS 图像传感器", "安防 CIS", "机器视觉", "车载 CIS", "手机 CIS", "高端成像"],
        "description": "CMOS 图像传感器企业，覆盖安防、机器视觉、车载和智能手机。",
    },
    {
        "id": "qi-pai-ke-ji",
        "code": "688216",
        "secucode": "688216.SH",
        "name": "气派科技",
        "mark": "气派",
        "market": "科创板",
        "category": "封装测试",
        "location": "深圳",
        "products": ["集成电路封装", "集成电路测试", "封装方案", "消费电子", "工业", "汽车电子"],
        "description": "集成电路封装测试企业，提供封装设计、封装和测试服务。",
    },
    {
        "id": "tian-de-yu",
        "code": "688252",
        "secucode": "688252.SH",
        "name": "天德钰",
        "mark": "天德钰",
        "market": "科创板",
        "category": "显示驱动",
        "location": "深圳",
        "products": ["显示驱动", "摄像头马达驱动", "快充协议", "电子标签驱动", "移动终端", "AIoT"],
        "description": "移动智能终端芯片企业，覆盖显示驱动、马达驱动和快充协议。",
    },
    {
        "id": "chuang-yao",
        "code": "688259",
        "secucode": "688259.SH",
        "name": "创耀科技",
        "mark": "创耀",
        "market": "科创板",
        "category": "网络 / 交换芯片",
        "location": "苏州",
        "products": ["宽带接入芯片", "电力载波", "通信 SoC", "短距无线", "工业互联", "物理层算法"],
        "description": "宽带接入与电力载波通信芯片企业，覆盖通信 SoC 和工业互联。",
    },
    {
        "id": "sai-wei-wei-dian",
        "code": "688325",
        "secucode": "688325.SH",
        "name": "赛微微电",
        "mark": "赛微",
        "market": "科创板",
        "category": "电源管理 / 驱动",
        "location": "广州",
        "products": ["电池管理", "电池计量", "充电管理", "电源管理", "模拟芯片", "可穿戴"],
        "description": "电池管理与电源管理模拟芯片企业，覆盖计量、充电和安全芯片。",
    },
    {
        "id": "wei-ce-ke-ji",
        "code": "688372",
        "secucode": "688372.SH",
        "name": "伟测科技",
        "mark": "伟测",
        "market": "科创板",
        "category": "封装测试",
        "location": "上海",
        "products": ["晶圆测试", "成品测试", "SLT 测试", "老化测试", "车规测试", "测试方案"],
        "description": "独立第三方集成电路测试企业，覆盖晶圆、成品和车规测试。",
    },
    {
        "id": "ju-quan",
        "code": "688391",
        "secucode": "688391.SH",
        "name": "钜泉科技",
        "mark": "钜泉",
        "market": "科创板",
        "category": "SoC 芯片",
        "location": "上海",
        "products": ["计量芯片", "MCU", "电力载波", "BMS", "智能电表", "电力物联网"],
        "description": "智能电表芯片企业，产品覆盖计量芯片、MCU、PLC 和 BMS。",
    },
    {
        "id": "yuan-jie",
        "code": "688498",
        "secucode": "688498.SH",
        "name": "源杰科技",
        "mark": "源杰",
        "market": "科创板",
        "category": "光通信 / 激光芯片",
        "location": "西安",
        "products": ["磷化铟激光器", "光通信芯片", "数据中心", "5G", "光纤到户", "工业物联网"],
        "description": "磷化铟激光器芯片企业，覆盖光纤到户、数据中心和 5G。",
    },
    {
        "id": "shang-hai-he-jing",
        "code": "688584",
        "secucode": "688584.SH",
        "name": "上海合晶",
        "mark": "合晶",
        "market": "科创板",
        "category": "半导体材料",
        "location": "上海",
        "products": ["硅外延片", "晶体生长", "衬底成型", "外延生长", "功率器件", "模拟芯片"],
        "description": "半导体硅外延片一体化企业，覆盖晶体生长、衬底和外延。",
    },
    {
        "id": "li-he-wei",
        "code": "688589",
        "secucode": "688589.SH",
        "name": "力合微",
        "mark": "力合",
        "market": "科创板",
        "category": "网络 / 交换芯片",
        "location": "深圳",
        "products": ["电力线通信", "PLC SoC", "智能电网", "物联网", "智能家居", "通信芯片"],
        "description": "电力线通信芯片企业，覆盖智能电网、智能家居和物联网。",
    },
    {
        "id": "kang-xi-tong-xin",
        "code": "688653",
        "secucode": "688653.SH",
        "name": "康希通信",
        "mark": "康希",
        "market": "科创板",
        "category": "射频 / 混合信号",
        "location": "上海",
        "products": ["Wi-Fi FEM", "射频前端", "GaAs", "CMOS", "V2X", "物联网"],
        "description": "Wi-Fi 射频前端芯片企业，覆盖路由器、终端、IoT 和车联网。",
    },
    {
        "id": "yin-he-wei-dian",
        "code": "688689",
        "secucode": "688689.SH",
        "name": "银河微电",
        "mark": "银河",
        "market": "科创板",
        "category": "功率半导体",
        "location": "常州",
        "products": ["MOSFET", "IGBT", "整流桥", "IPM", "SiC", "汽车电子"],
        "description": "功率半导体器件 IDM 企业，覆盖 MOSFET、IGBT、IPM 和 SiC。",
    },
    {
        "id": "kai-wei-te",
        "code": "688693",
        "secucode": "688693.SH",
        "name": "锴威特",
        "mark": "锴威特",
        "market": "科创板",
        "category": "功率半导体",
        "location": "苏州",
        "products": ["功率 MOSFET", "IGBT", "功率 IC", "SiC", "工业", "汽车电子"],
        "description": "智能功率半导体器件与功率集成芯片企业，覆盖工业与汽车。",
    },
    {
        "id": "hong-wei-ke-ji",
        "code": "688711",
        "secucode": "688711.SH",
        "name": "宏微科技",
        "mark": "宏微",
        "market": "科创板",
        "category": "功率半导体",
        "location": "常州",
        "products": ["IGBT", "MOSFET", "FRD", "SiC", "功率模块", "工业"],
        "description": "功率半导体器件企业，覆盖 IGBT、FRD、SiC 芯片和模块。",
    },
    {
        "id": "long-tu-guang-zhao",
        "code": "688721",
        "secucode": "688721.SH",
        "name": "龙图光罩",
        "mark": "龙图",
        "market": "科创板",
        "category": "半导体材料",
        "location": "深圳",
        "products": ["半导体掩模版", "成熟制程", "功率器件", "MEMS", "先进封装", "光罩"],
        "description": "独立第三方半导体掩模版企业，覆盖成熟制程和特色工艺。",
    },
    {
        "id": "ge-ke-wei",
        "code": "688728",
        "secucode": "688728.SH",
        "name": "格科微",
        "mark": "格科",
        "market": "科创板",
        "category": "图像传感器",
        "location": "上海",
        "products": ["CMOS 图像传感器", "显示驱动", "手机 CIS", "汽车电子", "Fab-Lite", "特色封测"],
        "description": "CMOS 图像传感器与显示驱动企业，采用 Fab-Lite 经营模式。",
    },
    {
        "id": "xi-an-yi-cai",
        "code": "688783",
        "secucode": "688783.SH",
        "name": "西安奕材",
        "mark": "奕材",
        "market": "科创板",
        "aliases": ["西安奕材-U"],
        "category": "半导体材料",
        "location": "西安",
        "products": ["12 英寸硅片", "抛光片", "外延片", "存储硅片", "逻辑芯片", "功率器件"],
        "description": "12 英寸电子级硅片企业，产品覆盖抛光片和外延片。",
    },
    {
        "id": "ang-rui-wei",
        "code": "688790",
        "secucode": "688790.SH",
        "name": "昂瑞微",
        "mark": "昂瑞",
        "market": "科创板",
        "aliases": ["昂瑞微-UW"],
        "category": "射频 / 混合信号",
        "location": "北京",
        "products": ["射频前端", "功率放大器", "LNA", "射频开关", "无线通信", "车规"],
        "description": "射频前端与无线通信芯片企业，覆盖 PA、LNA 和开关。",
    },
    {
        "id": "chuang-da-xin-cai",
        "code": "920012",
        "secucode": "920012.BJ",
        "name": "创达新材",
        "mark": "创达",
        "market": "北交所",
        "category": "半导体材料",
        "location": "无锡",
        "products": ["环氧模塑料", "液态封装料", "有机硅胶", "酚醛模塑料", "封装材料", "半导体"],
        "description": "高性能热固性复合材料企业，产品用于半导体封装材料。",
    },
    {
        "id": "jie-li-ke-ji",
        "code": "920138",
        "secucode": "920138.BJ",
        "name": "杰理科技",
        "mark": "杰理",
        "market": "北交所",
        "category": "SoC 芯片",
        "location": "珠海",
        "products": ["蓝牙音视频 SoC", "智能穿戴", "智能物联", "射频", "音频", "低功耗"],
        "description": "蓝牙音视频与智能穿戴 SoC 企业，覆盖智能物联终端。",
    },
    {
        "id": "hua-ling-gu-fen",
        "code": "920139",
        "secucode": "920139.BJ",
        "name": "华岭股份",
        "mark": "华岭",
        "market": "北交所",
        "category": "封装测试",
        "location": "上海",
        "products": ["晶圆测试", "成品测试", "系统级测试", "测试软硬件", "高可靠", "车规"],
        "description": "专业集成电路测试服务企业，覆盖晶圆、成品和系统级测试。",
    },
    {
        "id": "sai-ying-dian-zi",
        "code": "920181",
        "secucode": "920181.BJ",
        "name": "赛英电子",
        "mark": "赛英",
        "market": "北交所",
        "category": "半导体材料",
        "location": "江阴",
        "products": ["陶瓷管壳", "IGBT 基板", "GTO 管壳", "IGCT 管壳", "功率封装", "陶瓷材料"],
        "description": "大功率半导体器件陶瓷管壳与基板企业，覆盖 IGBT、GTO 和 IGCT。",
    },
]


SILERGY_COMPANY = {
    "id": "silergy",
    "code": "6415.TW",
    "name": "矽力杰",
    "mark": "矽力",
    "market": "台湾证交所",
    "category": "电源管理 / 驱动",
    "location": "新北",
    "aliases": ["矽力*-KY", "Silergy", "6415"],
    "currency": "TWD",
    "fxPair": "TWD/CNY",
    "products": [
        "电源管理 IC",
        "DC-DC",
        "AC-DC",
        "电池管理",
        "LED 驱动",
        "汽车 / 工业",
    ],
    "description": "台湾上市模拟 IC 公司，聚焦电源管理；财务数据按 TWD/CNY 汇率折算为人民币。",
}


REPORT_NAMES = {
    "income": "RPT_F10_FINANCE_GINCOME",
    "balance": "RPT_F10_FINANCE_GBALANCE",
    "cashflow": "RPT_F10_FINANCE_GCASHFLOW",
    "main": "RPT_F10_FINANCE_MAINFINADATA",
}


def fetch_report(company: dict, kind: str) -> list[dict]:
    query = {
        "reportName": REPORT_NAMES[kind],
        "columns": "ALL",
        "filter": f'(SECUCODE="{company["secucode"]}")',
        "pageNumber": "1",
        "pageSize": "60",
        "sortTypes": "-1",
        "sortColumns": "REPORT_DATE",
    }
    url = f"{API}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Referer": "https://emweb.securities.eastmoney.com/",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            result = payload.get("result")
            if not result:
                return []
            return result.get("data") or []
        except Exception:
            if attempt == 2:
                raise
            time.sleep(0.8 * (attempt + 1))
    return []


def fetch_company(company: dict) -> tuple[str, dict[str, list[dict]]]:
    return company["id"], {
        kind: fetch_report(company, kind)
        for kind in ("income", "balance", "cashflow", "main")
    }


def number(value) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def report_date(row: dict) -> str:
    return str(row.get("REPORT_DATE") or "")[:10]


def quarter_label(date_string: str) -> str:
    date = datetime.strptime(date_string, "%Y-%m-%d")
    quarter = (date.month - 1) // 3 + 1
    return f"{date.year}Q{quarter}"


def year_label(date_string: str) -> str:
    return date_string[:4]


def index_rows(rows: list[dict]) -> dict[str, dict]:
    return {report_date(row): row for row in rows if report_date(row)}


def single_quarter_value(
    current: float | None,
    previous: float | None,
    is_first_quarter: bool,
) -> float | None:
    if current is None:
        return None
    if is_first_quarter:
        return current
    if previous is None:
        return None
    return current - previous


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def to_yi(value: float | None) -> float | None:
    return value / 100_000_000 if value is not None else None


def round_value(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def build_company(company: dict, payload: dict[str, list[dict]]) -> dict:
    income = index_rows(payload["income"])
    balance = index_rows(payload["balance"])
    cashflow = index_rows(payload["cashflow"])
    main_rows = {
        report_date(row): row
        for row in payload["main"]
        if report_date(row)
    }

    quarter_dates = sorted(
        date
        for date in set(income) | set(balance) | set(cashflow)
        if START_DATE <= date <= END_DATE
    )

    quarterly = []
    annual = []

    for date in quarter_dates:
        income_row = income.get(date)
        balance_row = balance.get(date)
        cashflow_row = cashflow.get(date)
        if not income_row:
            continue

        year = date[:4]
        month = date[5:7]
        previous_date = {
            "03": None,
            "06": f"{year}-03-31",
            "09": f"{year}-06-30",
            "12": f"{year}-09-30",
        }.get(month)
        previous_income = income.get(previous_date) if previous_date else None
        previous_cashflow = cashflow.get(previous_date) if previous_date else None
        is_first_quarter = month == "03"

        revenue_cum = number(income_row.get("TOTAL_OPERATE_INCOME"))
        cost_cum = number(income_row.get("OPERATE_COST"))
        profit_cum = number(income_row.get("PARENT_NETPROFIT"))
        rd_cum = number(income_row.get("RESEARCH_EXPENSE"))
        ocf_cum = number(cashflow_row.get("NETCASH_OPERATE")) if cashflow_row else None

        revenue = single_quarter_value(
            revenue_cum,
            number(previous_income.get("TOTAL_OPERATE_INCOME")) if previous_income else None,
            is_first_quarter,
        )
        cost = single_quarter_value(
            cost_cum,
            number(previous_income.get("OPERATE_COST")) if previous_income else None,
            is_first_quarter,
        )
        net_profit = single_quarter_value(
            profit_cum,
            number(previous_income.get("PARENT_NETPROFIT")) if previous_income else None,
            is_first_quarter,
        )
        rd_expense = single_quarter_value(
            rd_cum,
            number(previous_income.get("RESEARCH_EXPENSE")) if previous_income else None,
            is_first_quarter,
        )
        ocf = single_quarter_value(
            ocf_cum,
            number(previous_cashflow.get("NETCASH_OPERATE")) if previous_cashflow else None,
            is_first_quarter,
        )

        trade_finasset = 0.0
        if balance_row:
            trade_finasset = (
                number(balance_row.get("TRADE_FINASSET_NOTFVTPL")) or 0.0
            ) + (number(balance_row.get("TRADE_FINASSET")) or 0.0)

        cash = None
        if balance_row and number(balance_row.get("MONETARYFUNDS")) is not None:
            cash = number(balance_row.get("MONETARYFUNDS")) + trade_finasset

        gross_margin = None
        if revenue not in (None, 0) and cost is not None:
            gross_margin = ((revenue - cost) / revenue) * 100

        quarterly.append(
            {
                "period": quarter_label(date),
                "revenue": round_value(to_yi(revenue)),
                "grossMargin": round_value(gross_margin),
                "netProfit": round_value(to_yi(net_profit)),
                "ocf": round_value(to_yi(ocf)),
                "rdExpense": round_value(to_yi(rd_expense)),
                "rdIntensity": round_value(
                    safe_ratio(rd_expense, revenue) * 100
                    if safe_ratio(rd_expense, revenue) is not None
                    else None
                ),
                "cash": round_value(to_yi(cash)),
            }
        )

        if month == "12":
            main_row = main_rows.get(date) or {}
            headcount = number(main_row.get("STAFF_NUM"))
            rd_staff = number(main_row.get("RDPERSONNEL"))
            staff_cash = number(cashflow_row.get("PAY_STAFF_CASH")) if cashflow_row else None
            rd_expense_annual = number(income_row.get("RESEARCH_EXPENSE"))
            avg_pay = (
                staff_cash / headcount / 10_000
                if staff_cash is not None and headcount not in (None, 0)
                else None
            )
            rd_pay_total = (
                staff_cash * (rd_staff / headcount)
                if staff_cash is not None
                and headcount not in (None, 0)
                and rd_staff is not None
                else None
            )
            rd_pay_per_person = (
                staff_cash / headcount / 10_000
                if staff_cash is not None and headcount not in (None, 0)
                else None
            )
            rd_expense_per_staff = (
                rd_expense_annual / rd_staff / 10_000
                if rd_expense_annual is not None and rd_staff not in (None, 0)
                else None
            )

            annual.append(
                {
                    "period": year,
                    "revenue": round_value(to_yi(revenue_cum)),
                    "grossMargin": round_value(
                        number(main_row.get("XSMLL"))
                        if number(main_row.get("XSMLL")) is not None
                        else (
                            ((revenue_cum - cost_cum) / revenue_cum) * 100
                            if revenue_cum not in (None, 0) and cost_cum is not None
                            else None
                        )
                    ),
                    "netProfit": round_value(to_yi(profit_cum)),
                    "ocf": round_value(to_yi(ocf_cum)),
                    "rdExpense": round_value(to_yi(rd_expense_annual)),
                    "rdIntensity": round_value(
                        safe_ratio(rd_expense_annual, revenue_cum) * 100
                        if safe_ratio(rd_expense_annual, revenue_cum) is not None
                        else None
                    ),
                    "cash": round_value(to_yi(cash)),
                    "headcount": int(headcount) if headcount is not None else None,
                    "avgPay": round_value(avg_pay),
                    "rdStaff": int(rd_staff) if rd_staff is not None else None,
                    "rdStaffRatio": round_value(
                        (rd_staff / headcount) * 100
                        if rd_staff is not None and headcount not in (None, 0)
                        else None
                    ),
                    "rdComp": round_value(to_yi(rd_pay_total)),
                    "rdPay": round_value(rd_pay_per_person),
                    "rdExpensePerStaff": round_value(rd_expense_per_staff),
                    "totalComp": round_value(to_yi(staff_cash)),
                }
            )

    annual = [row for row in annual if row["period"] >= "2021"]
    quarterly = [row for row in quarterly if row["period"] >= "2021Q1"]

    return {
        **{key: value for key, value in company.items() if key != "secucode"},
        "annual": annual,
        "quarterly": quarterly,
    }


def fetch_json_url(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Referer": "https://www.silergy.com/",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.0 * (attempt + 1))
    return {}


def fetch_finmind(dataset: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "dataset": dataset,
            "data_id": "6415",
            "start_date": "2021-01-01",
        }
    )
    payload = fetch_json_url(f"{FINMIND_API}?{query}")
    return payload.get("data") or []


def load_twd_cny_rates() -> list[tuple[datetime, float]]:
    payload = fetch_json_url(YAHOO_FX_API)
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    closes = result["indicators"]["quote"][0].get("close") or []
    rates = []
    for timestamp, close in zip(timestamps, closes):
        if close is None or not math.isfinite(float(close)):
            continue
        rates.append(
            (
                datetime.utcfromtimestamp(timestamp).date(),
                float(close),
            )
        )
    if not rates:
        raise RuntimeError("TWD/CNY exchange-rate series is unavailable")
    return rates


def average_fx(
    rates: list[tuple[datetime, float]],
    start_date: str,
    end_date: str,
) -> float:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    values = [rate for date, rate in rates if start <= date <= end]
    if not values:
        raise RuntimeError(f"No TWD/CNY rate between {start_date} and {end_date}")
    return statistics.fmean(values)


def end_fx(rates: list[tuple[datetime, float]], date_string: str) -> float:
    target = datetime.strptime(date_string, "%Y-%m-%d").date()
    candidates = [rate for date, rate in rates if date <= target]
    if not candidates:
        raise RuntimeError(f"No period-end TWD/CNY rate for {date_string}")
    return candidates[-1]


def quarter_start(date_string: str) -> str:
    date = datetime.strptime(date_string, "%Y-%m-%d")
    month = (date.month - 1) // 3 * 3 + 1
    return f"{date.year:04d}-{month:02d}-01"


def build_silergy() -> dict:
    income_rows = fetch_finmind("TaiwanStockFinancialStatements")
    balance_rows = fetch_finmind("TaiwanStockBalanceSheet")
    cashflow_rows = fetch_finmind("TaiwanStockCashFlowsStatement")
    rates = load_twd_cny_rates()

    def group_rows(rows: list[dict]) -> dict[str, dict[str, float]]:
        grouped: dict[str, dict[str, float]] = {}
        for row in rows:
            date = row.get("date")
            row_type = row.get("type")
            if not date or not row_type or row_type.endswith("_per"):
                continue
            value = number(row.get("value"))
            if value is not None:
                grouped.setdefault(date, {})[row_type] = value
        return grouped

    income = group_rows(income_rows)
    balance = group_rows(balance_rows)
    cashflow = group_rows(cashflow_rows)
    dates = sorted(
        date
        for date in set(income) & set(balance) & set(cashflow)
        if date >= "2021-03-31"
    )

    def cash_at(date: str) -> float | None:
        values = balance.get(date, {})
        cash = values.get("CashAndCashEquivalents")
        if cash is None:
            return None
        current_financial_assets = sum(
            value
            for key, value in values.items()
            if key.startswith("FinancialAssets") and "NonCurrent" not in key
        )
        return cash + current_financial_assets

    quarterly = []
    for date in dates:
        values = income[date]
        cash_values = cashflow[date]
        year = date[:4]
        month = date[5:7]
        previous_date = {
            "03": None,
            "06": f"{year}-03-31",
            "09": f"{year}-06-30",
            "12": f"{year}-09-30",
        }.get(month)
        previous_cashflow = cashflow.get(previous_date) if previous_date else None
        is_first_quarter = month == "03"
        revenue = values.get("Revenue")
        cost = values.get("CostOfGoodsSold")
        gross_profit = values.get("GrossProfit")
        net_profit = values.get("EquityAttributableToOwnersOfParent")
        ocf = single_quarter_value(
            cash_values.get("CashFlowsFromOperatingActivities"),
            (
                previous_cashflow.get("CashFlowsFromOperatingActivities")
                if previous_cashflow
                else None
            ),
            is_first_quarter,
        )
        gross_margin = (
            (gross_profit / revenue) * 100
            if revenue not in (None, 0) and gross_profit is not None
            else (
                ((revenue - cost) / revenue) * 100
                if revenue not in (None, 0) and cost is not None
                else None
            )
        )
        flow_rate = average_fx(rates, quarter_start(date), date)
        cash = cash_at(date)
        cash_rate = end_fx(rates, date)

        quarterly.append(
            {
                "period": f"{year}Q{int(month) // 3}",
                "revenue": round_value(to_yi(revenue * flow_rate) if revenue is not None else None),
                "grossMargin": round_value(gross_margin),
                "netProfit": round_value(
                    to_yi(net_profit * flow_rate) if net_profit is not None else None
                ),
                "ocf": round_value(to_yi(ocf * flow_rate) if ocf is not None else None),
                "cash": round_value(
                    to_yi(cash * cash_rate) if cash is not None else None
                ),
                "rdExpense": None,
                "rdIntensity": None,
            }
        )

    annual = []
    for year in ("2021", "2022", "2023", "2024", "2025"):
        year_dates = sorted(date for date in dates if date.startswith(year))
        if len(year_dates) != 4:
            continue
        revenue = sum(income[date].get("Revenue") or 0 for date in year_dates)
        cost = sum(income[date].get("CostOfGoodsSold") or 0 for date in year_dates)
        gross_profit = sum(income[date].get("GrossProfit") or 0 for date in year_dates)
        net_profit = sum(
            income[date].get("EquityAttributableToOwnersOfParent") or 0
            for date in year_dates
        )
        end_date = f"{year}-12-31"
        ocf = cashflow.get(end_date, {}).get("CashFlowsFromOperatingActivities")
        gross_margin = (
            (gross_profit / revenue) * 100
            if revenue not in (None, 0) and gross_profit is not None
            else None
        )
        flow_rate = average_fx(rates, f"{year}-01-01", end_date)
        cash = cash_at(end_date)
        cash_rate = end_fx(rates, end_date)
        annual.append(
            {
                "period": year,
                "revenue": round_value(
                    to_yi(revenue * flow_rate) if revenue is not None else None
                ),
                "grossMargin": round_value(gross_margin),
                "netProfit": round_value(
                    to_yi(net_profit * flow_rate) if net_profit is not None else None
                ),
                "ocf": round_value(to_yi(ocf * flow_rate) if ocf is not None else None),
                "rdExpense": None,
                "rdIntensity": None,
                "cash": round_value(
                    to_yi(cash * cash_rate) if cash is not None else None
                ),
                "headcount": None,
                "avgPay": None,
                "rdStaff": None,
                "rdStaffRatio": None,
                "rdComp": None,
                "rdPay": None,
                "rdExpensePerStaff": None,
                "totalComp": None,
            }
        )

    return {
        **SILERGY_COMPANY,
        "fxMethod": "流量指标按期间日均 TWD/CNY，现金按期末 TWD/CNY",
        "annual": annual,
        "quarterly": quarterly,
    }


def main() -> None:
    data = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_company, company): company for company in COMPANIES}
        for index, future in enumerate(as_completed(futures), start=1):
            company = futures[future]
            company_id, payload = future.result()
            data[company_id] = payload
            print(f"[{index:02d}/{len(COMPANIES)}] {company['name']} fetched")

    built = []
    for company in COMPANIES:
        payload = data[company["id"]]
        built.append(build_company(company, payload))
        latest_annual = built[-1]["annual"][-1]["period"] if built[-1]["annual"] else "—"
        latest_quarter = built[-1]["quarterly"][-1]["period"] if built[-1]["quarterly"] else "—"
        print(f"  -> 年报 {latest_annual}, 单季 {latest_quarter}")

    silergy = build_silergy()
    built.append(silergy)
    print(
        f"  -> 矽力杰 6415.TW: 年报 {silergy['annual'][-1]['period']}, "
        f"单季 {silergy['quarterly'][-1]['period']}（TWD/CNY 折算）"
    )

    output = {
        "meta": {
            "title": "半导体公司对比",
            "source": "东方财富公开财务数据接口",
            "sourceUrl": "https://emweb.securities.eastmoney.com/",
            "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "startPeriod": "2021Q1",
            "latestQuarter": max(
                (row["quarterly"][-1]["period"] for row in built if row["quarterly"]),
                default="—",
            ),
            "latestAnnual": max(
                (row["annual"][-1]["period"] for row in built if row["annual"]),
                default="—",
            ),
            "currency": "人民币亿元",
            "payUnit": "万元 / 年",
            "notes": [
                "季度数据由累计报表逐季差分得到单季值。",
                "毛利率按单季营业收入与营业成本计算；年度视图采用年报口径。",
                "账上现金 = 货币资金 + 交易性金融资产。",
                "人均薪酬 = 支付给职工以及为职工支付的现金 ÷ 期末员工人数。",
                "研发薪酬为按研发人员占比分摊现金薪酬的估算值，并非年报单独披露口径。",
                "员工、薪酬与研发人员数据仅年度披露，季度视图不提供。",
                "矽力杰为台湾证交所上市公司，财务数据按 TWD/CNY 汇率折算人民币；流量指标使用期间日均汇率，现金使用期末汇率。",
            ],
        },
        "companies": built,
    }

    OUTPUT.write_text(
        "window.IC_DATA = "
        + json.dumps(output, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
