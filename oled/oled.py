from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
from PIL import ImageFont, Image
import time
import psutil
import subprocess
import re


def format_size(bytes_value):
    if bytes_value < 1024 ** 2:
        return f"{bytes_value / 1024:.1f}K"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value / 1024 ** 2:.1f}M"
    else:
        return f"{bytes_value / 1024 ** 3:.1f}G"


def cpu_usage():
    result = psutil.cpu_percent(interval=None)
    return int(result)


def memory_usage():
    mem = psutil.virtual_memory()
    return format_size(mem.used), format_size(mem.total)


def cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return float(f.read()) / 1000


def freq():
    result = psutil.cpu_freq().current
    return int(result)


def fan_status():
    result = subprocess.run(["cat", "/sys/class/gpio/gpio74/value"], capture_output=True, text=True)
    return int(result.stdout)


def disk(mount_point):
    du = psutil.disk_usage(mount_point)
    return format_size(du.used), format_size(du.total)


def network_io(interface='br-lan'):
    net_io_start = psutil.net_io_counters(pernic=True).get(interface, None)
    if net_io_start:
        time.sleep(1)
        net_io_end = psutil.net_io_counters(pernic=True)[interface]
        bytes_sent_diff = net_io_end.bytes_sent - net_io_start.bytes_sent
        bytes_recv_diff = net_io_end.bytes_recv - net_io_start.bytes_recv
        return format_size(bytes_sent_diff) + "/S", format_size(bytes_recv_diff) + "/S"
    return "0K/S", "0K/S"


def ip_address(interface='br-lan'):
    result = subprocess.run(['ifconfig', interface], capture_output=True, text=True, shell=True)
    match = re.search(r'inet addr:(\S+)', result.stdout)
    return match.group(1) if match else "N/A"


if __name__ == '__main__':
    serial_interface = i2c(port=1, address=0x3C)
    device = sh1106(serial_interface)
    font = ImageFont.truetype("/etc/oled/Anonymous.ttf", 12)
    logo_image = Image.open("/etc/oled/logo.png").resize((device.width, device.height))
    boot_image = Image.open("/etc/oled/boot.png").resize((device.width, device.height))
    device.clear()
    device.contrast(50)
    value = 0
    with canvas(device) as draw:
        draw.bitmap((0, 0), boot_image, fill=255)
    device.show()
    time.sleep(5)
    while True:
        show_time = time.localtime().tm_hour
        if 6 <= show_time <= 23:
            mem_used, mem_total = memory_usage()
            disk_use, disk_total = disk('/opt')
            download, upload = network_io()
            with canvas(device) as draw:
                if fan_status() == 1:
                    draw.text((0, 0), f"{'*':>18}", fill=255, font=font)
                draw.text((0, 0), f"TMP: {cpu_temperature():.1f}°C", fill=255, font=font)
                draw.text((0, 10), f"CPU: {freq()}MHz[{cpu_usage()}%]", fill=255, font=font)
                draw.text((0, 21), f"RAM: {mem_used}/{mem_total}", fill=255, font=font)
                draw.text((0, 32), f"HDD: {disk_use}/{disk_total}", fill=255, font=font)
                draw.text((0, 43), f"LAN: {ip_address()}", fill=255, font=font)
                draw.text((0, 54), f"{download:<9}{upload:>9}", fill=255, font=font)

            device.show()
            value += 1
            if value >= 60:
                with canvas(device) as draw:
                    draw.bitmap((0, 0), logo_image, fill=255)
                    draw.text((20, 54), "O P E N W R T", fill=255, font=font)
                device.show()
                time.sleep(10)
                device.clear()
                device.hide()
                time.sleep(10)
                value = 0

        else:
            device.clear()
            device.hide()
            while True:
                hide_time = time.localtime().tm_hour
                if 23 <= hide_time <= 6:
                    time.sleep(60)
                else:
                    break
