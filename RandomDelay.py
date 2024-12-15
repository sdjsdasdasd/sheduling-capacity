import pandas as pd
import numpy as np
from datetime import timedelta

# 读取 Excel 文件
df = pd.read_excel('classified.xlsx')

# 将 '充电开始时间' 和 '充电结束时间' 列转换为 datetime 类型
df['充电开始时间'] = pd.to_datetime(df['充电开始时间'], errors='coerce')
df['充电结束时间'] = pd.to_datetime(df['充电结束时间'], errors='coerce')

# 删除转换失败的行
df = df.dropna(subset=['充电开始时间', '充电结束时间'])

# 设置延迟的正态分布参数
mean_delay = 45  # 平均延迟时间（分钟）
std_deviation = 10  # 标准差（分钟）

# 初始化字典，用于记录设备在 21:00-04:00 之间的出现次数
charging_start_times = {}

# 延时条件：21:00 - 04:00
def should_apply_delay(start_time):
    return start_time.hour >= 21 or start_time.hour < 4

def calculate_charging_times(row):
    device = row['终端名称']
    current_start_time = row['充电开始时间']
    current_end_time = row['充电结束时间']

    # 延迟时间初始化为 0
    delay = timedelta(minutes=0)

    # 只有在 21:00-04:00 时间段内才应用延迟
    if should_apply_delay(current_start_time):
        # 如果设备第一次在这个时间段出现，增加一个基于正态分布的延迟
        if device not in charging_start_times:
            charging_start_times[device] = 1  # 设备第一次出现
            delay_minutes = max(0, np.random.normal(mean_delay, std_deviation))  # 随机生成延迟时间
            delay = timedelta(minutes=delay_minutes)  # 将延迟时间转换为 timedelta
        else:
            charging_start_times[device] += 1  # 设备出现次数加1
            # 根据设备出现次数生成延迟（每次增加一个正态分布的延迟）
            delay_minutes = max(0, np.random.normal(mean_delay * charging_start_times[device], std_deviation))
            delay = timedelta(minutes=delay_minutes)

        # 最后加上 120 分钟的额外延迟
        delay += timedelta(minutes=120)

    # 计算并返回调整后的充电开始时间和结束时间
    adjusted_start_time = current_start_time + delay
    adjusted_end_time = current_end_time + delay

    return pd.Series([adjusted_start_time, adjusted_end_time])

# 应用函数计算调整后的时间
df[['调整后的充电开始时间', '调整后的充电结束时间']] = df.apply(calculate_charging_times, axis=1)

# 输出处理后的 DataFrame
print(df)

# 保存处理后的数据到 Excel 文件
df.to_excel('delay.xlsx', index=False)
