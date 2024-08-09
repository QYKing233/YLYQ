from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
from PIL import ImageFont, Image
import time
import psutil
import subprocess


def cpu_usage():
    cpu = psutil.cpu_percent(interval=None)
    return cpu


def memory_usage():
    mem = psutil.virtual_memory()
    if (mem.used / 1024 ** 3) < 1:
        used = "{:.1f}M".format(mem.used / 1024 ** 2)  # 转换为MB
    else:
        used = "{:.1f}G".format(mem.used / 1024 ** 3)  # 转换为GB
    if (mem.total / 1024 ** 3) < 1:
        total = "{:.1f}M".format(mem.total / 1024 ** 2)  # 转换为MB
    else:
        total = "{:.1f}G".format(mem.total / 1024 ** 3)  # 转换为GB

    return used, total


def cpu_temperature():
    temperature = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"]).decode("utf-8")
    cpu_temp = float(temperature) / 1000
    return cpu_temp


def disk(mount_point):
    du = psutil.disk_usage(mount_point)
    if (du.used / 1024 ** 3) < 1:
        du_use = "{:.1f}M".format(du.used / 1024 ** 2)
    else:
        du_use = "{:.1f}G".format(du.used / 1024 ** 3)
    if (du.total / 1024 ** 3) < 1:
        du_total = "{:.1f}M".format(du.total / 1024 ** 2)
    else:
        du_total = "{:.1f}G".format(du.total / 1024 ** 3)

    return du_use, du_total


def network_io():
    net_io_counters = psutil.net_io_counters(pernic=True)

    # 获取特定网卡（例如 'eth0' 或 'en0'，取决于你的系统和网络接口名称）
    lan_interface = 'br-lan'  # 替换为实际的LAN接口名称
    if lan_interface in net_io_counters:
        lan_stats = net_io_counters[lan_interface]
        bytes_sent = lan_stats.bytes_sent
        bytes_recv = lan_stats.bytes_recv

        # 计算过去一段时间的增量
        time.sleep(1)  # 延迟一秒以便计算下一秒的数据
        next_lan_stats = psutil.net_io_counters(pernic=True)[lan_interface]
        bytes_sent_diff = next_lan_stats.bytes_sent - bytes_sent
        bytes_recv_diff = next_lan_stats.bytes_recv - bytes_recv

        # 转换为KB/s或MB/s
        if (bytes_sent_diff / 1024 ** 2) < 1:
            send_speed_mbps = "{:.1f}K/S".format(bytes_sent_diff / 1024)
        else:
            send_speed_mbps = "{:.1f}M/S".format(bytes_sent_diff / 1024 ** 2)
        if (bytes_recv_diff / 1024 ** 2) < 1:
            recv_speed_mbps = "{:.1f}K/S".format(bytes_recv_diff / 1024)
        else:
            recv_speed_mbps = "{:.1f}M/S".format(bytes_recv_diff / 1024 ** 2)
        return send_speed_mbps, recv_speed_mbps


# 上述代码将无限循环打印网络上传和下载速率


def ip_address():
    result = subprocess.run(['ifconfig', 'br-lan'], capture_output=True, text=True, shell=False)
    lines = result.stdout.split('\n')
    for line in lines:
        if 'inet' in line:
            ip = line.split(':')[1]
            ip = ip.split()[0]
            return ip


if __name__ == '__main__':
    # 定义I2C端口和地址，SH1106的默认I2C地址通常是0x3C
    serial_interface = i2c(port=1, address=0x3C)

    # 创建SH1106设备实例
    device = sh1106(serial_interface)

    # 加载字体
    font = ImageFont.truetype("/etc/oled/Anonymous.ttf", 12)

    # 加载你的败家之眼Logo图片
    logo_image = Image.open("/etc/oled/logo.png")  # 替换为你的Logo文件路径

    # 调整Logo大小以适应OLED屏幕分辨率（假设是128x64）
    logo_image_resized = logo_image.resize((device.width, device.height))

    # 清除屏幕
    device.clear()
    value = 0
    while True:
        mem_used, mem_total = memory_usage()
        disk_use, disk_total = disk('/opt')
        download, upload = network_io()

        # 在屏幕上显示硬盘空间、内存剩余、CPU温度和IP地址
        with canvas(device) as draw:
            draw.text((0, 0), f"CPU: {cpu_usage()}%", fill='white', font=font)
            draw.text((0, 10), "TMP: {:.1f}°C".format(cpu_temperature()), fill='white', font=font)
            draw.text((0, 21), "RAM: {}/{}".format(mem_used, mem_total), fill='white', font=font)
            draw.text((0, 32), "HDD: {}/{}".format(disk_use, disk_total), fill='white', font=font)
            draw.text((0, 43), f"LAN: {ip_address()}", fill=255, font=font)
            draw.text((0, 54), "{:<8s}  {:>8s}".format(download, upload), fill='white', font=font)

        # 更新屏幕显示内容
        device.show()

        # 防止烧屏幕
        value += 1
        if value >= 120:
            device.clear()

            # 在屏幕上绘制Logo
            with canvas(device) as draw:
                draw.bitmap((0, 0), logo_image_resized, fill='white')
                draw.text((20, 54), "O P E N W R T", fill='white', font=font)
            device.show()
            time.sleep(10)
            device.clear()
            time.sleep(10)
            value = 0
