import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 读取Excel数据
data = pd.read_excel('delay.xlsx')

# 初始化一个长度为1440的一维数组，表示一天24小时（每分钟一个值）
power_array = np.zeros(1440)

# 设置时间格式
time_format = "%Y-%m-%d %H:%M:%S"

# 遍历每一行充电数据
for _, row in data.iterrows():
    # 直接使用 pandas 的 Timestamp 对象，不需要 strptime
    start_time = row['充电开始时间']
    end_time = row['充电结束时间']
    power_value = row['平均充电功率']

    # 将开始时间和结束时间转换为分钟索引
    start_index = int((start_time.hour * 60 + start_time.minute) % 1440)  # 分钟数
    end_index = int((end_time.hour * 60 + end_time.minute) % 1440)  # 分钟数

    # 判断充电时间段，累加功率值到数组中
    if start_index <= end_index:
        # 如果充电段在一天内（没有跨天）
        power_array[start_index:end_index+1] += power_value
    else:
        # 如果充电段跨越了午夜
        power_array[start_index:] += power_value
        power_array[:end_index+1] += power_value

# 输出功率变化数组（可视化或保存）
print(power_array)

# 如果需要保存为Excel文件
pd.DataFrame(power_array, columns=['功率']).to_excel('power_curve1.xlsx', index=False)
