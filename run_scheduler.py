import time
import os

while True:
    os.system(r'C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\.venv\Scripts\python.exe C:\Users\xiaoh\Downloads\solar_panel_monitoring_system_project\manage.py update_zone_snapshots')
    time.sleep(60)  # 每 60 秒执行一次
