import subprocess
import requests


def install_luma_oled_models():
    status_code = requests.get("http://www.baidu.com").status_code
    result = subprocess.run(['python', '-m', 'pip', 'list'], capture_output=True, text=True).stdout
    if ("luma.oled" not in result) and (status_code == 200):
        subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip", "-i", "https://mirrors.aliyun.com/pypi/simple/"])
        subprocess.run(["python", "-m", "pip", "install", "luma.oled", "-i", "https://mirrors.aliyun.com/pypi/simple/"])


if __name__ == '__main__':
    install_luma_oled_models()