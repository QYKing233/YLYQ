#!/bin/bash

# 检查 GPIO74 目录是否存在
if [ ! -d /sys/class/gpio/gpio74 ]; then
    echo 74 > /sys/class/gpio/export
    sleep 2
    echo out > /sys/class/gpio/gpio74/direction
fi

# 定义温度阈值和相应操作
high_threshold_temp=55000  # 单位：0.001 °C，即 55°C
low_threshold_temp=45000  # 单位：0.001 °C，即 45°C

while true; do
    temp=$(cat /sys/class/thermal/thermal_zone0/temp)
    if [ $temp -ge $high_threshold_temp ]; then
        # CPU 温度大于 55°C，设置最大速度
        echo -n 1 > /sys/class/gpio/gpio74/value
        sleep 5
    elif [ $temp -le $low_threshold_temp ]; then
        # CPU 温度低于等于 45°C，关闭风扇
        echo -n 0 > /sys/class/gpio/gpio74/value
    fi
    
    sleep 2
done
