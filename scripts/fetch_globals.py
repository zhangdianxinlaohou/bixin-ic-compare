"""Fetch major global semiconductor companies from SEC XBRL company facts.

Outputs global_data.js with values converted to CNY. Flow metrics use the
average exchange rate for the reported period; cash uses the period-end rate.
"""

from __future__ import annotations

import json
import math
import statistics
import tempfile
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "global_data.js"
CACHE = Path(tempfile.gettempdir()) / "ic_compare_sec_cache"
SEC_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
HEADERS = {"User-Agent": "Mozilla/5.0 ICCompare/1.0"}
START_DATE = "2021-01-01"
END_DATE = "2026-09-30"


GLOBAL_COMPANIES = [
    {
        "id": "nvidia",
        "cik": "0001045810",
        "code": "NVDA",
        "name": "英伟达",
        "mark": "英伟",
        "market": "NASDAQ",
        "region": "美国",
        "location": "圣克拉拉",
        "category": "GPU / AI 算力",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["NVIDIA", "Nvidia", "英伟达公司"],
        "products": ["GPU", "AI 加速卡", "数据中心", "GeForce", "CUDA", "汽车芯片"],
        "description": "全球 AI 与 GPU 龙头；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "amd",
        "cik": "0000002488",
        "code": "AMD",
        "name": "AMD",
        "mark": "AMD",
        "market": "NASDAQ",
        "region": "美国",
        "location": "圣克拉拉",
        "category": "GPU / AI 算力",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Advanced Micro Devices", "超威半导体"],
        "products": ["CPU", "GPU", "AI 加速器", "FPGA", "数据中心", "嵌入式"],
        "description": "CPU 与 GPU 设计公司；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "intel",
        "cik": "0000050863",
        "code": "INTC",
        "name": "英特尔",
        "mark": "英特尔",
        "market": "NASDAQ",
        "region": "美国",
        "location": "圣克拉拉",
        "category": "CPU / 处理器",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Intel", "Intel Corporation"],
        "products": ["x86 CPU", "晶圆代工", "AI 加速器", "FPGA", "网络芯片", "PC 芯片"],
        "description": "x86 CPU 与 IDM/代工平台；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "texas-instruments",
        "cik": "0000097476",
        "code": "TXN",
        "name": "德州仪器",
        "mark": "德州",
        "market": "NASDAQ",
        "region": "美国",
        "location": "达拉斯",
        "category": "信号链 / 通用模拟",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["TI", "Texas Instruments"],
        "products": ["模拟芯片", "电源管理", "嵌入式", "MCU", "汽车电子", "工业"],
        "description": "全球模拟与嵌入式芯片龙头；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "analog-devices",
        "cik": "0000006281",
        "code": "ADI",
        "name": "亚德诺",
        "mark": "亚德诺",
        "market": "NASDAQ",
        "region": "美国",
        "location": "威尔明顿",
        "category": "信号链 / 通用模拟",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["ADI", "Analog Devices"],
        "products": ["信号链", "放大器", "数据转换器", "电源管理", "射频", "传感器"],
        "description": "高性能模拟与混合信号芯片企业；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "broadcom",
        "cik": "0001730168",
        "code": "AVGO",
        "name": "博通",
        "mark": "博通",
        "market": "NASDAQ",
        "region": "美国",
        "location": "帕洛阿尔托",
        "category": "网络 / 交换芯片",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Broadcom", "Broadcom Inc."],
        "products": ["定制 ASIC", "以太网交换", "光通信", "存储控制", "无线连接", "基础设施软件"],
        "description": "网络、定制 ASIC 与基础设施芯片平台；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "qualcomm",
        "cik": "0000804328",
        "code": "QCOM",
        "name": "高通",
        "mark": "高通",
        "market": "NASDAQ",
        "region": "美国",
        "location": "圣迭戈",
        "category": "SoC 芯片",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Qualcomm", "Qualcomm Incorporated"],
        "products": ["骁龙 SoC", "基带", "射频前端", "汽车芯片", "IoT", "PC 芯片"],
        "description": "移动 SoC、基带与射频芯片龙头；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "micron",
        "cik": "0000723125",
        "code": "MU",
        "name": "美光",
        "mark": "美光",
        "market": "NASDAQ",
        "region": "美国",
        "location": "博伊西",
        "category": "存储芯片",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Micron", "Micron Technology"],
        "products": ["DRAM", "NAND", "HBM", "SSD", "数据中心", "汽车存储"],
        "description": "全球主要 DRAM/NAND 存储厂商；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "asml",
        "cik": "0000937966",
        "code": "ASML",
        "name": "阿斯麦",
        "mark": "ASML",
        "market": "NASDAQ / 阿姆斯特丹",
        "region": "荷兰",
        "location": "费尔德霍芬",
        "category": "半导体设备",
        "currency": "EUR",
        "fxPair": "EUR/CNY",
        "aliases": ["ASML Holding", "ASML"],
        "products": ["EUV 光刻", "DUV 光刻", "量测", "计算光刻", "设备服务", "先进制程"],
        "description": "全球光刻机龙头；已接入年度核心财务，季度数据暂未接入；财务数据按 EUR/CNY 汇率折算为人民币。",
    },
    {
        "id": "applied-materials",
        "cik": "0000006951",
        "code": "AMAT",
        "name": "应用材料",
        "mark": "应材",
        "market": "NASDAQ",
        "region": "美国",
        "location": "圣克拉拉",
        "category": "半导体设备",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Applied Materials", "AMAT"],
        "products": ["薄膜沉积", "刻蚀", "离子注入", "CMP", "量测", "先进封装"],
        "description": "全球半导体设备龙头之一；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "lam-research",
        "cik": "0000707549",
        "code": "LRCX",
        "name": "泛林集团",
        "mark": "泛林",
        "market": "NASDAQ",
        "region": "美国",
        "location": "弗里蒙特",
        "category": "半导体设备",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["Lam Research", "Lam"],
        "products": ["刻蚀", "薄膜沉积", "晶圆清洗", "3D NAND", "DRAM", "先进制程"],
        "description": "全球刻蚀与沉积设备龙头；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "kla",
        "cik": "0000319201",
        "code": "KLAC",
        "name": "科磊",
        "mark": "KLA",
        "market": "NASDAQ",
        "region": "美国",
        "location": "米尔皮塔斯",
        "category": "半导体设备",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["KLA Corporation", "KLA-Tencor"],
        "products": ["缺陷检测", "量测", "过程控制", "晶圆检测", "先进封装", "面板检测"],
        "description": "半导体过程控制与量测设备龙头；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "nxp",
        "cik": "0001413447",
        "code": "NXPI",
        "name": "恩智浦",
        "mark": "恩智浦",
        "market": "NASDAQ",
        "region": "荷兰",
        "location": "埃因霍温",
        "category": "信号链 / 通用模拟",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["NXP", "NXP Semiconductors"],
        "products": ["汽车 MCU", "安全芯片", "模拟", "射频", "工业", "物联网"],
        "description": "汽车与安全芯片平台；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "stmicro",
        "cik": "0000932787",
        "code": "STM",
        "name": "意法半导体",
        "mark": "ST",
        "market": "NYSE",
        "region": "瑞士",
        "location": "日内瓦",
        "category": "信号链 / 通用模拟",
        "currency": "USD",
        "fxPair": "USD/CNY",
        "aliases": ["STMicroelectronics", "ST"],
        "products": ["MCU", "功率器件", "SiC", "模拟", "MEMS", "汽车芯片"],
        "description": "MCU、功率与汽车芯片企业；已接入年度核心财务，季度数据暂未接入；财务数据按 USD/CNY 汇率折算为人民币。",
    },
    {
        "id": "tsmc",
        "cik": "0001046179",
        "code": "TSM",
        "name": "台积电",
        "mark": "台积",
        "market": "NYSE ADR",
        "region": "中国台湾",
        "location": "新竹",
        "category": "晶圆代工 FAB",
        "currency": "TWD",
        "fxPair": "TWD/CNY",
        "aliases": ["TSMC", "Taiwan Semiconductor", "台积电公司"],
        "products": ["先进制程", "3nm", "5nm", "CoWoS", "晶圆代工", "HPC"],
        "description": "全球最大晶圆代工厂；财务数据按 TWD/CNY 汇率折算为人民币。",
    },
]


REVENUE_CONCEPTS = [
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"),
    ("us-gaap", "Revenues"),
    ("us-gaap", "SalesRevenueNet"),
    ("ifrs-full", "Revenue"),
    ("ifrs-full", "RevenueFromContractsWithCustomers"),
]
GROSS_PROFIT_CONCEPTS = [
    ("us-gaap", "GrossProfit"),
    ("ifrs-full", "GrossProfit"),
]
COST_CONCEPTS = [
    ("us-gaap", "CostOfRevenue"),
    ("us-gaap", "CostOfGoodsAndServicesSold"),
    ("us-gaap", "CostOfGoodsSold"),
    ("ifrs-full", "CostOfSales"),
]
NET_PROFIT_CONCEPTS = [
    ("us-gaap", "NetIncomeLoss"),
    ("us-gaap", "ProfitLoss"),
    ("ifrs-full", "ProfitLossAttributableToOwnersOfParent"),
    ("ifrs-full", "ProfitLoss"),
]
RD_CONCEPTS = [
    ("us-gaap", "ResearchAndDevelopmentExpense"),
    ("us-gaap", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"),
    ("ifrs-full", "ResearchAndDevelopmentExpense"),
]
OCF_CONCEPTS = [
    ("us-gaap", "NetCashProvidedByUsedInOperatingActivities"),
    ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
    ("ifrs-full", "CashFlowsFromUsedInOperatingActivities"),
    ("ifrs-full", "CashFlowsFromUsedInOperatingActivitiesContinuingOperations"),
]
CASH_CONCEPTS = [
    ("us-gaap", "CashAndCashEquivalentsAtCarryingValue"),
    ("ifrs-full", "CashAndCashEquivalents"),
]
SHORT_INVESTMENT_CONCEPTS = [
    ("us-gaap", "CashCashEquivalentsAndShortTermInvestments"),
    ("us-gaap", "ShortTermInvestments"),
    ("us-gaap", "MarketableSecuritiesCurrent"),
    ("us-gaap", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"),
    ("ifrs-full", "CurrentFinancialAssetsAtAmortisedCost"),
    ("ifrs-full", "CurrentFinancialAssetsAtFairValueThroughProfitOrLoss"),
]

FX_SYMBOLS = {
    "USD": "CNY=X",
    "EUR": "EURCNY=X",
    "TWD": "TWDCNY=X",
}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def companyfacts(company: dict) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{company['code']}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = fetch_json(SEC_FACTS.format(cik=company["cik"]))
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def load_fx(currency: str) -> list[tuple[datetime, float]]:
    symbol = FX_SYMBOLS[currency]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=6y&interval=1d"
    data = fetch_json(url)
    result = data["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    closes = result["indicators"]["quote"][0].get("close") or []
    points = []
    for timestamp, close in zip(timestamps, closes):
        if close is None or not math.isfinite(float(close)):
            continue
        points.append((datetime.utcfromtimestamp(timestamp).date(), float(close)))
    if not points:
        raise RuntimeError(f"No FX series for {currency}")
    return points


def average_fx(points: list[tuple[datetime, float]], start: str, end: str) -> float:
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    values = [rate for date, rate in points if start_date <= date <= end_date]
    return statistics.fmean(values)


def end_fx(points: list[tuple[datetime, float]], end: str) -> float:
    target = datetime.strptime(end, "%Y-%m-%d").date()
    values = [rate for date, rate in points if date <= target]
    return values[-1]


def fact_rows(data: dict, concepts: list[tuple[str, str]], currency: str) -> list[dict]:
    rows = []
    for priority, (taxonomy, concept) in enumerate(concepts):
        entry = data.get("facts", {}).get(taxonomy, {}).get(concept)
        if not entry:
            continue
        units = entry.get("units", {})
        unit_key = currency if currency in units else next(
            (key for key in ("USD", "EUR", "TWD") if key in units),
            None,
        )
        if not unit_key:
            continue
        for raw in units[unit_key]:
            value = raw.get("val")
            end = raw.get("end")
            if value is None or not end:
                continue
            rows.append(
                {
                    "start": raw.get("start"),
                    "end": end,
                    "value": float(value),
                    "filed": raw.get("filed") or "1900-01-01",
                    "form": raw.get("form"),
                    "priority": priority,
                }
            )
    return rows


def dedupe_periods(rows: list[dict]) -> dict[tuple[str | None, str], dict]:
    periods = {}
    for row in sorted(rows, key=lambda item: (item["priority"], item["filed"])):
        key = (row.get("start"), row["end"])
        if key not in periods:
            periods[key] = row
        elif row["filed"] > periods[key]["filed"]:
            periods[key] = row
    return periods


def duration_days(row: dict) -> int | None:
    if not row.get("start"):
        return None
    start = datetime.strptime(row["start"], "%Y-%m-%d")
    end = datetime.strptime(row["end"], "%Y-%m-%d")
    return (end - start).days


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


def annual_rows(rows: list[dict]) -> dict[str, dict]:
    result = {}
    for row in rows:
        days = duration_days(row)
        if days is None or not 330 <= days <= 400:
            continue
        if row["end"] < "2021-12-01" or row["end"] > "2025-12-31":
            continue
        existing = result.get(row["end"])
        if not existing or row["filed"] > existing["filed"]:
            result[row["end"]] = row
    return result


def quarter_rows(rows: list[dict]) -> dict[str, dict]:
    direct = {}
    for row in rows:
        days = duration_days(row)
        if days is None or not 55 <= days <= 115:
            continue
        if row["end"] < START_DATE or row["end"] > END_DATE:
            continue
        existing = direct.get(row["end"])
        if not existing or row["filed"] > existing["filed"]:
            direct[row["end"]] = row

    result = dict(direct)
    annuals = [
        row
        for row in rows
        if duration_days(row) is not None
        and 330 <= duration_days(row) <= 400
        and row["end"] <= END_DATE
    ]
    for annual in annuals:
        start = annual.get("start")
        if not start:
            continue
        cumulative = [
            row
            for row in rows
            if row.get("start") == start
            and row["end"] < annual["end"]
            and duration_days(row) is not None
            and duration_days(row) < 330
        ]
        cumulative = sorted(cumulative, key=lambda item: item["end"])
        if not cumulative:
            continue
        previous_value = 0.0
        previous_end = start
        for row in cumulative:
            if row["end"] not in result:
                result[row["end"]] = {
                    **row,
                    "value": row["value"] - previous_value,
                    "start": previous_end,
                }
            previous_value = row["value"]
            previous_end = row["end"]
        if annual["end"] not in result:
            result[annual["end"]] = {
                **annual,
                "value": annual["value"] - previous_value,
                "start": previous_end,
            }

    cumulative_by_start: dict[str, list[dict]] = {}
    for row in rows:
        days = duration_days(row)
        if (
            row.get("start")
            and days is not None
            and 115 < days < 330
            and row["end"] <= END_DATE
        ):
            cumulative_by_start.setdefault(row["start"], []).append(row)

    for fiscal_rows in cumulative_by_start.values():
        fiscal_rows = sorted(fiscal_rows, key=lambda item: item["end"])
        previous_cumulative = None
        for row in fiscal_rows:
            if previous_cumulative:
                previous_value = previous_cumulative["value"]
                previous_end = previous_cumulative["end"]
            else:
                earlier_direct = [
                    direct_row
                    for direct_row in direct.values()
                    if direct_row["end"] < row["end"]
                    and direct_row["end"] >= row["start"]
                ]
                if earlier_direct:
                    previous_direct = max(earlier_direct, key=lambda item: item["end"])
                    previous_value = previous_direct["value"]
                    previous_end = previous_direct["end"]
                else:
                    previous_value = 0.0
                    previous_end = row["start"]
            if row["end"] not in result:
                result[row["end"]] = {
                    **row,
                    "value": row["value"] - previous_value,
                    "start": previous_end,
                }
            previous_cumulative = row
    return result


def instant_rows(rows: list[dict]) -> list[dict]:
    result = {}
    for row in rows:
        if row.get("start"):
            continue
        existing = result.get(row["end"])
        if not existing or row["filed"] > existing["filed"]:
            result[row["end"]] = row
    return sorted(result.values(), key=lambda item: item["end"])


def cash_value(
    cash_rows: list[dict],
    investment_rows: list[dict],
    end: str,
) -> float | None:
    def nearest(rows: list[dict]) -> float | None:
        candidates = [row for row in rows if row["end"] <= end]
        if not candidates:
            return None
        latest = candidates[-1]
        if latest["end"] < (
            datetime.strptime(end, "%Y-%m-%d") - timedelta(days=120)
        ).strftime("%Y-%m-%d"):
            return None
        return latest["value"]

    cash = nearest(cash_rows)
    if cash is None:
        return None
    investment = nearest(investment_rows)
    return cash + (investment or 0)


def quarter_label(end: str) -> str:
    date = datetime.strptime(end, "%Y-%m-%d")
    return f"{date.year}Q{(date.month - 1) // 3 + 1}"


def period_start(end: str) -> str:
    date = datetime.strptime(end, "%Y-%m-%d")
    return (date - timedelta(days=90)).strftime("%Y-%m-%d")


def cny_yi(value: float | None, rate: float) -> float | None:
    if value is None:
        return None
    return round(value * rate / 100_000_000, 4)


def build_company(data: dict, company: dict, fx: dict[str, list]) -> dict:
    currency = company["currency"]
    rate_points = fx[currency]
    metrics = {
        "revenue": dedupe_periods(fact_rows(data, REVENUE_CONCEPTS, currency)),
        "grossProfit": dedupe_periods(fact_rows(data, GROSS_PROFIT_CONCEPTS, currency)),
        "cost": dedupe_periods(fact_rows(data, COST_CONCEPTS, currency)),
        "netProfit": dedupe_periods(fact_rows(data, NET_PROFIT_CONCEPTS, currency)),
        "rdExpense": dedupe_periods(fact_rows(data, RD_CONCEPTS, currency)),
        "ocf": dedupe_periods(fact_rows(data, OCF_CONCEPTS, currency)),
        "cash": instant_rows(fact_rows(data, CASH_CONCEPTS, currency)),
        "investments": instant_rows(
            fact_rows(data, SHORT_INVESTMENT_CONCEPTS, currency)
        ),
    }

    annual = []
    annual_revenue = annual_rows(list(metrics["revenue"].values()))
    for end, revenue_row in sorted(annual_revenue.items()):
        period = end[:4]
        if not 2021 <= int(period) <= 2025:
            continue

        def annual_value(name: str) -> float | None:
            row = next(
                (
                    candidate
                    for key, candidate in metrics[name].items()
                    if candidate["end"] == end
                    and duration_days(candidate) is not None
                    and 330 <= duration_days(candidate) <= 400
                ),
                None,
            )
            return row["value"] if row else None

        revenue = revenue_row["value"]
        gross_profit = annual_value("grossProfit")
        cost = annual_value("cost")
        if gross_profit is None and cost is not None:
            gross_profit = revenue - cost
        net_profit = annual_value("netProfit")
        rd_expense = annual_value("rdExpense")
        ocf = annual_value("ocf")
        rate = average_fx(rate_points, revenue_row["start"], end)
        cash = cash_value(metrics["cash"], metrics["investments"], end)
        annual.append(
            {
                "period": period,
                "revenue": cny_yi(revenue, rate),
                "grossMargin": round(gross_profit / revenue * 100, 4)
                if gross_profit is not None and revenue
                else None,
                "netProfit": cny_yi(net_profit, rate),
                "ocf": cny_yi(ocf, rate),
                "rdExpense": cny_yi(rd_expense, rate),
                "rdIntensity": round(rd_expense / revenue * 100, 4)
                if rd_expense is not None and revenue
                else None,
                "cash": cny_yi(cash, end_fx(rate_points, end)),
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

    quarters = {}
    for name, rows in metrics.items():
        if name in ("cash", "investments"):
            continue
        quarters[name] = quarter_rows(list(rows.values()))

    all_ends = sorted(
        {
            end
            for metric_rows in quarters.values()
            for end in metric_rows
            if START_DATE <= end <= END_DATE
        }
    )
    quarterly = []
    for end in all_ends:
        revenue_row = quarters["revenue"].get(end)
        if not revenue_row:
            continue
        revenue = revenue_row["value"]
        gross_row = quarters["grossProfit"].get(end)
        cost_row = quarters["cost"].get(end)
        gross_profit = gross_row["value"] if gross_row else None
        if gross_profit is None and cost_row:
            gross_profit = revenue - cost_row["value"]
        net_row = quarters["netProfit"].get(end)
        rd_row = quarters["rdExpense"].get(end)
        ocf_row = quarters["ocf"].get(end)
        start = revenue_row.get("start") or period_start(end)
        rate = average_fx(rate_points, start, end)
        cash = cash_value(metrics["cash"], metrics["investments"], end)
        net_profit = net_row["value"] if net_row else None
        rd_expense = rd_row["value"] if rd_row else None
        ocf = ocf_row["value"] if ocf_row else None
        quarterly.append(
            {
                "period": quarter_label(end),
                "revenue": cny_yi(revenue, rate),
                "grossMargin": round(gross_profit / revenue * 100, 4)
                if gross_profit is not None and revenue
                else None,
                "netProfit": cny_yi(net_profit, rate),
                "ocf": cny_yi(ocf, rate),
                "rdExpense": cny_yi(rd_expense, rate),
                "rdIntensity": round(rd_expense / revenue * 100, 4)
                if rd_expense is not None and revenue
                else None,
                "cash": cny_yi(cash, end_fx(rate_points, end)),
            }
        )

    return {
        **company,
        "isGlobal": True,
        "fxMethod": "流量指标按财报期间日均汇率，现金按期末汇率",
        "annual": annual,
        "quarterly": quarters_to_sorted(quarterly),
    }


def fetch_finmind_dataset(dataset: str, stock_id: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "dataset": dataset,
            "data_id": stock_id,
            "start_date": START_DATE,
        }
    )
    data = fetch_json(f"https://api.finmindtrade.com/api/v4/data?{query}")
    return data.get("data") or []


def build_tsmc_from_finmind(data: dict, company: dict, rates: list) -> dict:
    income_rows = fetch_finmind_dataset("TaiwanStockFinancialStatements", "2330")
    balance_rows = fetch_finmind_dataset("TaiwanStockBalanceSheet", "2330")
    cashflow_rows = fetch_finmind_dataset("TaiwanStockCashFlowsStatement", "2330")

    def group_rows(rows: list[dict]) -> dict[str, dict[str, float]]:
        grouped = {}
        for row in rows:
            date = row.get("date")
            row_type = row.get("type")
            if not date or not row_type or row_type.endswith("_per"):
                continue
            value = row.get("value")
            if value is None:
                continue
            grouped.setdefault(date, {})[row_type] = float(value)
        return grouped

    income = group_rows(income_rows)
    balance = group_rows(balance_rows)
    cashflow = group_rows(cashflow_rows)
    dates = sorted(
        date
        for date in set(income) & set(balance) & set(cashflow)
        if START_DATE <= date <= END_DATE
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

    rd_rows = dedupe_periods(fact_rows(data, RD_CONCEPTS, "TWD"))
    rd_annual = annual_rows(list(rd_rows.values()))

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
        previous_cash = cashflow.get(previous_date) if previous_date else None
        is_first_quarter = month == "03"
        revenue = values.get("Revenue")
        gross_profit = values.get("GrossProfit")
        net_profit = values.get("EquityAttributableToOwnersOfParent") or values.get(
            "ProfitLossAttributableToOwnersOfParent"
        )
        ocf = single_quarter_value(
            cash_values.get("CashFlowsFromOperatingActivities")
            or cash_values.get("CashFlowsFromUsedInOperatingActivities"),
            (
                previous_cash.get("CashFlowsFromOperatingActivities")
                or previous_cash.get("CashFlowsFromUsedInOperatingActivities")
                if previous_cash
                else None
            ),
            is_first_quarter,
        )
        rate = average_fx(rates, period_start(date), date)
        cash = cash_at(date)
        quarterly.append(
            {
                "period": quarter_label(date),
                "revenue": cny_yi(revenue, rate),
                "grossMargin": round(gross_profit / revenue * 100, 4)
                if gross_profit is not None and revenue
                else None,
                "netProfit": cny_yi(net_profit, rate),
                "ocf": cny_yi(ocf, rate),
                "rdExpense": None,
                "rdIntensity": None,
                "cash": cny_yi(cash, end_fx(rates, date)),
            }
        )

    annual = []
    for year in ("2021", "2022", "2023", "2024", "2025"):
        year_dates = sorted(date for date in dates if date.startswith(year))
        if len(year_dates) != 4:
            continue
        revenue = sum(income[date].get("Revenue") or 0 for date in year_dates)
        gross_profit = sum(income[date].get("GrossProfit") or 0 for date in year_dates)
        net_profit = sum(
            (
                income[date].get("EquityAttributableToOwnersOfParent")
                or income[date].get("ProfitLossAttributableToOwnersOfParent")
                or 0
            )
            for date in year_dates
        )
        end = f"{year}-12-31"
        ocf = cashflow.get(end, {}).get("CashFlowsFromOperatingActivities") or cashflow.get(
            end, {}
        ).get("CashFlowsFromUsedInOperatingActivities")
        rate = average_fx(rates, f"{year}-01-01", end)
        rd_row = next(
            (value for value in rd_annual.values() if value["end"][:4] == year),
            None,
        )
        rd_expense = rd_row["value"] if rd_row else None
        cash = cash_at(end)
        annual.append(
            {
                "period": year,
                "revenue": cny_yi(revenue, rate),
                "grossMargin": round(gross_profit / revenue * 100, 4)
                if revenue
                else None,
                "netProfit": cny_yi(net_profit, rate),
                "ocf": cny_yi(ocf, rate),
                "rdExpense": cny_yi(rd_expense, rate),
                "rdIntensity": round(rd_expense / revenue * 100, 4)
                if rd_expense is not None and revenue
                else None,
                "cash": cny_yi(cash, end_fx(rates, end)),
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
        **company,
        "isGlobal": True,
        "fxMethod": "季度财务来自台湾公开财报；流量按期间日均 TWD/CNY，现金按期末汇率",
        "annual": annual,
        "quarterly": quarters_to_sorted(quarterly),
    }


def quarters_to_sorted(rows: list[dict]) -> list[dict]:
    result = {}
    for row in rows:
        result[row["period"]] = row
    return [result[key] for key in sorted(result)]


def main() -> None:
    fx = {currency: load_fx(currency) for currency in ("USD", "EUR", "TWD")}
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(companyfacts, company): company
            for company in GLOBAL_COMPANIES
        }
        for index, future in enumerate(as_completed(futures), start=1):
            company = futures[future]
            data = future.result()
            if company["id"] == "tsmc":
                results[company["id"]] = build_tsmc_from_finmind(
                    data, company, fx["TWD"]
                )
            else:
                results[company["id"]] = build_company(data, company, fx)
            print(f"[{index:02d}/{len(GLOBAL_COMPANIES)}] {company['name']} ready")

    companies = [results[company["id"]] for company in GLOBAL_COMPANIES]
    output = {
        "meta": {
            "title": "国际半导体大厂",
            "source": "SEC EDGAR XBRL company facts",
            "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fx": "流量指标按期间日均汇率，现金按期末汇率",
            "companies": len(companies),
        },
        "companies": companies,
    }
    OUTPUT.write_text(
        "window.IC_GLOBAL_DATA = "
        + json.dumps(output, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
