#!/usr/bin/env python3
"""
北交所新股申购资金测算模型 v1.0
基于历史数据反推 k 系数，输出各档位申购策略
"""

import json
from dataclasses import dataclass
from typing import List, Optional

# ============================================================
# 1. 历史数据库（从公开信息收集，用于反推 k 系数）
# ============================================================

@dataclass
class IPORecord:
    name: str           # 股票名称
    code: str           # 代码
    P: float            # 发行价（元）
    S: int              # 网上发行股数（股）
    E: float            # 实际冻资总额（元）
    C_actual: float     # 实际稳中1手门槛（元，来自市场公布）
    F_actual: float     # 实际碎股门槛（元，来自市场公布）
    date: str           # 申购日期

# 历史数据（来源：鑫爷低风险投资、知乎、东方财富等公开数据）
HISTORY = [
    IPORecord(
        name="志高机械", code="920101",
        P=17.41, S=2040_0000,       # 网上发行约2040万股
        E=7315.54e8,                 # 冻资7315亿
        C_actual=340_0000,           # 稳中1手约340万
        F_actual=450_0000,           # 碎股门槛约450万
        date="2025-08"
    ),
    IPORecord(
        name="宏远股份", code="920xxx",
        P=0,                         # 发行价待补充
        S=0,
        E=7408.33e8,                 # 冻资7408亿
        C_actual=240_0000,           # 稳中1手约240万
        F_actual=300_0000,           # 碎股门槛约300万
        date="2025-08"
    ),
    IPORecord(
        name="北矿检测", code="920160",
        P=6.70, S=2548_0000,         # 网上发行约2549万股
        E=7500e8,                    # 预估冻资7500亿
        C_actual=294_0000,           # 稳中1手约294万
        F_actual=520_0000,           # 碎股门槛约520万（预测值）
        date="2025-11"
    ),
    IPORecord(
        name="能之光", code="920xxx2",
        P=0,
        S=0,
        E=0,
        C_actual=270_0000,           # 稳中1手约270万
        F_actual=400_0000,           # 碎股门槛约400万
        date="2025-08"
    ),
    IPORecord(
        name="巴兰仕", code="920112",
        P=0,
        S=0,
        E=0,
        C_actual=320_0000,
        F_actual=450_0000,
        date="2025-xx"
    ),
]

# ============================================================
# 2. 核心算法层
# ============================================================

def calc_C(P: float, S: int, E: float) -> float:
    """
    计算稳中1手（100股）所需基础资金 C
    R = 中签率 = (S * P) / E  （发行总市值 / 冻资）
    C = 100 / R * P = 100 * E / S
    """
    if S <= 0 or E <= 0:
        return 0
    R = (S * P) / E
    C = (100 / R) * P
    return C

def calc_k_from_history() -> dict:
    """从历史数据反推 k 系数分布"""
    k_values = []
    print("=" * 60)
    print("历史数据反推 k 系数")
    print("=" * 60)
    
    for rec in HISTORY:
        if rec.C_actual > 0 and rec.F_actual > 0:
            k = rec.F_actual / rec.C_actual
            k_values.append(k)
            print(f"{rec.name}({rec.date}): C={rec.C_actual/1e4:.0f}万  F={rec.F_actual/1e4:.0f}万  k={k:.3f}")
    
    if k_values:
        k_min = min(k_values)
        k_max = max(k_values)
        k_avg = sum(k_values) / len(k_values)
        k_median = sorted(k_values)[len(k_values)//2]
        print(f"\nk 系数统计:")
        print(f"  最小值: {k_min:.3f}")
        print(f"  最大值: {k_max:.3f}")
        print(f"  平均值: {k_avg:.3f}")
        print(f"  中位值: {k_median:.3f}")
        return {"min": k_min, "max": k_max, "avg": k_avg, "median": k_median, "values": k_values}
    return {}

# ============================================================
# 3. 输出层：N+1 模型
# ============================================================

def run_model(
    name: str,
    P: float,
    S: int,
    E_estimate: float,
    k: float = None,
    k_low: float = 0.5,   # 保守 k（冷门股）
    k_high: float = 0.85, # 激进 k（热门股）
    max_N: int = 5,
):
    """
    计算各档位申购资金
    
    Args:
        name: 新股名称
        P: 发行价（元）
        S: 网上发行股数（股）
        E_estimate: 预估冻资总额（元）
        k: 指定 k 系数（不指定则输出低/中/高三档）
        k_low: 冷门股 k（碎股门槛较低）
        k_high: 热门股 k（碎股门槛较高）
        max_N: 最大正股手数
    """
    C = calc_C(P, S, E_estimate)
    R = (S * P) / E_estimate
    
    print("\n" + "=" * 60)
    print(f"新股申购测算：{name}")
    print("=" * 60)
    print(f"发行价:     {P:.2f} 元")
    print(f"网上发行量: {S/1e4:.0f} 万股")
    print(f"预估冻资:   {E_estimate/1e8:.0f} 亿元")
    print(f"预估中签率: {R*100:.4f}%")
    print(f"稳中1手(C): {C/1e4:.1f} 万元")
    print()
    
    scenarios = {}
    if k is not None:
        scenarios = {"指定k": k}
    else:
        scenarios = {
            f"冷门股(k={k_low})": k_low,
            f"普通(k=0.65)": 0.65,
            f"热门股(k={k_high})": k_high,
        }
    
    for scenario_name, k_val in scenarios.items():
        F = k_val * C
        print(f"--- {scenario_name} --- F碎股门槛={F/1e4:.1f}万")
        print(f"  {'档位':<12} {'申购资金':>12} {'预期获配'}")
        print(f"  {'-'*45}")
        
        # 0+1 仅博碎股
        print(f"  {'0+1(仅碎股)':<12} {F/1e4:>10.1f}万  博1手碎股")
        
        for N in range(1, max_N + 1):
            fund = N * C + F
            print(f"  {str(N)+'+1(保'+str(N)+'冲'+str(N+1)+')':<12} {fund/1e4:>10.1f}万  保{N}手+碎股1手")
        
        # 顶格参考
        top_fund = S * P * 0.05  # 顶格5%
        print(f"  {'顶格参考':<12} {top_fund/1e4:>10.1f}万  申购上限5%")
        print()

# ============================================================
# 4. 主程序
# ============================================================

if __name__ == "__main__":
    # Step 1: 反推历史 k 系数
    k_stats = calc_k_from_history()
    
    # Step 2: 示例测算（以北矿检测为例验证）
    print("\n【验证：北矿检测（已知数据回测）】")
    run_model(
        name="北矿检测(回测)",
        P=6.70,
        S=2548_0000,
        E_estimate=7500e8,
        k_low=0.5,
        k_high=0.85,
    )
    
    # Step 3: 示例测算（新股预测模板）
    print("\n【模板：新股预测（填入P、S、E即可）】")
    run_model(
        name="新股XXX（示例）",
        P=10.0,          # ← 替换为发行价
        S=3000_0000,     # ← 替换为网上发行股数
        E_estimate=6000e8,  # ← 替换为预估冻资
        k_low=0.5,
        k_high=0.8,
    )

print("\n\n【使用说明】")
print("调用 run_model(name, P, S, E_estimate) 即可输出各档位资金")
print("k 系数参考：热门股 0.75-0.9 | 普通 0.55-0.7 | 冷门 0.3-0.5")
