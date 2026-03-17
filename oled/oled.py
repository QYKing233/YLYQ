from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
from PIL import ImageFont, Image
import time
import psutil
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor


def format_size(bytes_value):
    """数据格式化"""
    if bytes_value < 1024 ** 2:
        return f"{bytes_value / 1024:.1f}KB"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value / 1024 ** 2:.1f}MB"
    else:
        return f"{bytes_value / 1024 ** 3:.1f}GB"


class OLEDMonitor:
    """整合显示与监控的单一类"""

    def __init__(self):
        # 初始化硬件
        self.device = sh1106(i2c(port=1, address=0x3C))
        self.font = ImageFont.truetype("/etc/oled/ter-u12n.bdf", 12)
        self.logo = Image.open("/etc/oled/logo.png").resize((self.device.width, self.device.height))
        self.boot = Image.open("/etc/oled/boot.png").resize((self.device.width, self.device.height))
        self.device.contrast(50)

        # 创建线程池（最多4线程）
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.counter = 0

    def _parallel_fetch(self):
        """并行获取监控数据"""
        futures = {
            'cpu': self.executor.submit(psutil.cpu_percent, 0.1),
            'mem': self.executor.submit(psutil.virtual_memory),
            'temp': self.executor.submit(self._get_temp),
            'freq': self.executor.submit(lambda: psutil.cpu_freq().current),
            'fan': self.executor.submit(self._get_fan),
            'disk': self.executor.submit(psutil.disk_usage, '/opt'),
            'net': self.executor.submit(self._get_network),
            'ip': self.executor.submit(self._get_ip),
        }
        return {k: v.result() for k, v in futures.items()}

    @staticmethod
    def _get_temp():
        with open("/sys/class/thermal/thermal_zone0/temp") as temp:
            return float(temp.read()) / 1000

    @staticmethod
    def _get_fan():
        result = subprocess.run(["cat", "/sys/class/gpio/gpio74/value"],
                                capture_output=True, text=True)
        return int(result.stdout)

    @staticmethod
    def _get_network():
        """简化网络监控"""
        start = psutil.net_io_counters(pernic=True)['br-lan']
        time.sleep(1)
        end = psutil.net_io_counters(pernic=True)['br-lan']
        return (
            f"{format_size(end.bytes_recv - start.bytes_recv)}/S",
            f"{format_size(end.bytes_sent - start.bytes_sent)}/S"
        )

    @staticmethod
    def _get_ip():
        try:
            return psutil.net_if_addrs()['br-lan'][0].address
        except:
            return "N/A"

    def _display(self, data):
        """显示核心方法"""
        with canvas(self.device) as draw:
            # 状态栏
            if data['fan'] == 1:
                draw.text((0, 0), f"{'*':>21}", fill=255, font=self.font)
            # 主体信息
            draw.text((0, 0), f"REC:{data['net'][0]}", fill=255, font=self.font)
            draw.text((0, 10), f"SEN:{data['net'][1]}", fill=255, font=self.font)
            draw.text((0, 21), f"LAN:{data['ip']}", font=self.font, fill=255)
            draw.text((0, 32), f"RAM:{format_size(data['mem'].used)}/{format_size(data['mem'].total)}", fill=255,
                      font=self.font)
            draw.text((0, 43), f"HDD:{format_size(data['disk'].used)}/{format_size(data['disk'].total)}", fill=255,
                      font=self.font)
            draw.text((0, 54), f"CPU:{int(data['freq'])}MHz|{int(data['cpu'])}%|{int(data['temp'])}°C", font=self.font,
                      fill=255)

        self.device.show()

    def _shutdown(self):
        self.device.clear()
        self.device.hide()

    def run(self):
        """主运行逻辑"""
        # 显示启动画面
        with canvas(self.device) as draw:
            draw.bitmap((0, 0), self.boot, fill=255)
        self.device.show()
        time.sleep(5)
        self.device.clear()
        while True:
            if 6 <= time.localtime().tm_hour <= 23:
                data = self._parallel_fetch()
                self._display(data)

                # 每60s显示一次LOGO
                self.counter += 1
                if self.counter >= 60:  # 60s
                    with canvas(self.device) as draw:
                        draw.bitmap((0, 0), self.logo, fill=255)
                        draw.text((21, 54), "O P E N W R T", fill=255, font=self.font)
                    self.device.show()
                    time.sleep(10)
                    self._shutdown()
                    time.sleep(10)
                    self.counter = 0
            else:
                self._shutdown()
                self.executor.shutdown(wait=False)
                while True:
                    if 6 <= time.localtime().tm_hour <= 23:
                        break
                    else:
                        time.sleep(60)


if __name__ == '__main__':
    monitor = OLEDMonitor()
    monitor.run()
