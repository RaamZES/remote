import toml
from datetime import datetime, timedelta
import time as t
import pyautogui
import os
import subprocess
import shutil
import socketio
import threading

file_versions = {}
pyautogui.FAILSAFE = False
# name = os.getlogin()
name = "PC-0"
apps = []
config = toml.load("config.toml")

def copier():
    source_path = f"I:\\Common\\IT\\PRAKTYKI\\{name}"
    target_path = r"C:\\Users\\ujapraktykant\\Desktop\\v3"

    files = os.listdir(source_path)

    for file_name in files:
        source_file = os.path.join(source_path, file_name)
        target_file = os.path.join(target_path, file_name)

        if os.path.exists(source_file):
            shutil.copy(source_file, target_file)
            print(f"{file_name} has been copied from {source_path} to {target_path}")
        else:
            print(f"{file_name} was not found in {source_path}")

def Slidefunc(app_start, programm_id, stop):
    pyautogui.hotkey('win', str(programm_id + 2))
    pyautogui.hotkey('win', 'up')
    pyautogui.hotkey('f11')

    current_time_str = t.strftime("%H:%M:%S", t.localtime())
    current_time = datetime.strptime(current_time_str, "%H:%M:%S").time()

    stop_time = str_to_time(stop)

    while current_time < stop_time:
        t.sleep(1)
        current_time = t.strftime("%H:%M:%S", t.localtime())
        current_time = datetime.strptime(current_time, "%H:%M:%S").time()
        config = toml.load("config.toml")
        for app in config['Timetable']:
            if app['type'] == "program" and app["start"] == app_start:
                stop_time = app["stop"]
    pyautogui.hotkey('win', '1')

def programm_runner(program):
    subprocess.Popen(program, shell=True)
    t.sleep(1)
    pyautogui.hotkey('win', '1')

def video_player(video_path, duration, video_num):
    os.system(f'start vlc {video_path} --play-and-exit')
    t.sleep(duration)

def str_to_time(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").time()

def str_to_duration(duration_str):
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 1:
        return timedelta(seconds=parts[0])
    elif len(parts) == 3:
        h, m, s = parts
        return timedelta(hours=h, minutes=m, seconds=s)

def Updater(apps):
    while True:
        text = toml.load("config.toml")
        if text and 'Timetable' in text:
            for app in text['Timetable']:
                if 'name' in app and app['name'] not in apps and app['type'] == 'program':
                    programm_runner(app['name'])
                    apps.append(app['name'])
                app_start = str_to_time(app['start'])
                app_stop = str_to_time(app['stop'])
                current_time = datetime.now().time()
                if app_start < current_time and app_stop > current_time:
                    if app['type'] == 'program':
                        Slidefunc(app_start, apps.index(app['name']), app['stop'])
                    elif app['type'] == 'mp4':
                        duration = str_to_duration(app['duration']).total_seconds()
                        video_player(app['path'], duration, len(apps)+2)
            close_extra_apps(apps, text)
            t.sleep(1)


def close_extra_apps(apps, config):
    config_apps = [app['name'] for app in config['Timetable'] if app['type'] == 'program']
    extra_apps = set(apps) - set(config_apps)

    for app in extra_apps:
        os.system(f"taskkill /f /im {app}.exe")
        if app in apps:
            apps.remove(app)
        os.system(f'taskkill /IM {app} /F')
        print(f'Closed {app} as it is not in config.toml')

def stop_time_updater(programm_id):
    counter = 0
    stop_time = None
    config = toml.load("config.toml")
    for app in config['Timetable']:
        if app['type'] == 'program':
            if counter == programm_id:
                stop_time = str_to_time(app["stop"])
                break
            counter += 1
    return stop_time

def connector(name):
    @sio.event
    def connect():
        print("I'm connected!")
        sio.emit('join', name)

    @sio.event
    def response_json(data):
        print('received response: ' + str(data))
        if data:
            copier()

    @sio.event
    def disconnect(name):
        print("I'm disconnected!")
        sio.emit('leave', name)

    try:
        sio.connect('http://localhost:5000')
        sio.wait()
    except socketio.exceptions.ConnectionError:
        print("Server doesn't work")
        t.sleep(5)
        connector(name)

for app in config['Timetable']:
    if app['type'] == 'program' and app['name'] not in apps:
        programm_runner(app['name'])
        apps.append(app['name'])

updater_thread = threading.Thread(target=Updater, args=(apps,))
updater_thread.start()

sio = socketio.Client()
connector(name)
