from crawler_utils.utils import reset_mcu
import psutil

def kill_gpio_hogs():
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in p.info['name'] and 'hal' in ' '.join(p.info['cmdline']):
                print(f"Killing GPIO hog: PID {p.pid}")
                p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

reset_mcu()
kill_gpio_hogs()