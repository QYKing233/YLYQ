#!/bin/bash

# 导出 GPIO 通道
echo -n 226 > /sys/class/gpio/export

# 设置 gpio 226 引脚为输出模式
echo out > /sys/class/gpio/gpio226/direction

# 定义温度阈值和相应操作
high_threshold_temp=55000  # 单位：0.001 °C，即 55°C
low_threshold_temp=45000  # 单位：0.001 °C，即 45°C

while true; do
    temp=$(cat /sys/class/thermal/thermal_zone0/temp)
    if [ $temp -gt $high_threshold_temp ]; then
        # CPU 温度大于 55°C，设置最大速度
        echo -n 1 > /sys/class/gpio/gpio226/value
        sleep 5
    elif [ $temp -lt $low_threshold_temp ]; then
        # CPU 温度低于等于 45°C，关闭风扇
        echo -n 0 > /sys/class/gpio/gpio226/value
    fi
    
    sleep 2
done
