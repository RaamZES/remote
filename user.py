import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

all_rooms = ['PC-0','PC-1','PC-2']
rooms = []

def offline_rooms(dict,all_rooms):
    offline = []
    try:
        response = requests.get('http://10.123.120.47:5000/get_rooms')
        dict = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Blad: {e}")
    for sid in dict:
        if dict[sid] not in rooms:
            rooms.append(dict[sid])
    for room in all_rooms:
        if room not in rooms:
            offline.append(room)
    return offline

def Send(getter, subject, text):
    smtp_server = 'smtp.phg.ads'
    smtp_port = 25
    login = 'ujaeuro.praktykant@dunapack-packaging.com'

    msg = MIMEMultipart()
    msg['From'] = login
    msg['To'] = getter
    msg['Subject'] = subject

    msg.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.send_message(msg)
    server.quit()

def sender(offline):
    if offline:
        offline_rooms = [room for room in offline]
        message = f"Rooms offline: {', '.join(offline_rooms)} are offline"
        Send("ujaeuro.praktykant@dunapack-packaging.com", "Rooms offline", message)
        print("Message is sent")
old_offline = []
while True:
    offline = offline_rooms(dict,all_rooms)
    if old_offline:
        if old_offline != offline:
            sender(offline)
            old_offline = offline
    else:
        sender(offline)
        old_offline = offline
    time.sleep(600)