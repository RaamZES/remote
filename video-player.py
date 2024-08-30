import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, \
    QTimeEdit, QComboBox, QLineEdit, QInputDialog, QMenu, QMessageBox
from PyQt5.QtCore import Qt
import toml
from datetime import datetime
import requests

online_pc = []

def save_to_toml(timetable, path):
    try:
        with open(path, 'w') as f:
            toml.dump({'Timetable': timetable}, f)
    except Exception as e:
        print(f"Błąd podczas zapisywania: {e}")

def load_from_toml(path):
    with open(path, 'r') as f:
        return toml.load(f)['Timetable']

def send_data(room):
    url = "http://10.123.120.47:5000/send_data"
    data = {"room_name": room}
    response = requests.post(url, json=data)
    print(response.json())

def create_gui():
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Harmonogram aplikacji")
    layout = QVBoxLayout()

    app_list = QTreeWidget()
    app_list.setHeaderLabels(["Typ", "Nazwa/Ścieżka", "Czas rozpoczęcia", "Czas zakończenia", "Czas trwania"])
    time_editor_start = QTimeEdit()
    time_editor_start.setDisplayFormat('HH:mm:ss')
    time_editor_stop = QTimeEdit()
    time_editor_stop.setDisplayFormat('HH:mm:ss')
    time_editor_duration = QTimeEdit()
    time_editor_duration.setDisplayFormat('HH:mm:ss')
    schedule = QLabel("Harmonogram")
    main_program = QComboBox()
    main_program.addItem("Wybierz komputer")

    computers = os.listdir('I:\\Common\\IT\\PRAKTYKI')

    for computer in computers:
        response = requests.get('http://10.123.120.47:5000/get_rooms')
        dict = response.json()
        for sid in dict:
            online_pc.append(dict[sid])
        if computer in online_pc:
            main_program.addItem(computer)
        else:
            main_program.addItem(computer +" is offline")

    save_button = QPushButton("Zapisz")
    add_button = QPushButton("Dodaj")
    send_button = QPushButton("Send Data")
    restart_button = QPushButton("Restart")

    def on_save_clicked():
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Czy na pewno chcesz zapisać?")
        msgBox.setWindowTitle("Potwierdzenie")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            timetable = []
            for i in range(app_list.topLevelItemCount()):
                item = app_list.topLevelItem(i)
                if item.text(0) == 'mp4':
                    timetable.append({'type': 'mp4', 'path': item.text(1), 'start': item.text(2), 'stop': item.text(3),
                                      'duration': item.text(4)})
                else:
                    timetable.append(
                        {'type': 'program', 'name': item.text(1), 'start': item.text(2), 'stop': item.text(3)})
            save_to_toml(timetable, f'I:\\Common\\IT\\PRAKTYKI\\{main_program.currentText()}\\config.toml')

    save_button.clicked.connect(on_save_clicked)

    def on_add_clicked():
        type, ok = QInputDialog.getItem(window, "Dodaj", "Wybierz typ:", ["mp4", "program"], 0, False)
        if ok and type:
            name, ok = QInputDialog.getText(window, "Dodaj", "Wprowadź nazwę/ścieżkę:")
            if ok and name:
                start = time_editor_start.time().toString('HH:mm:ss')
                stop = time_editor_stop.time().toString('HH:mm:ss')
                duration = time_editor_duration.time().toString('HH:mm:ss') if type == 'mp4' else ''
                new_item = QTreeWidgetItem(app_list, [type, name, start, stop, duration])
                for i in range(new_item.columnCount()):
                    new_item.setFlags(new_item.flags() | Qt.ItemIsEditable)

    add_button.clicked.connect(on_add_clicked)

    def on_context_menu(position):
        menu = QMenu()
        delete_action = menu.addAction("Usuń")
        action = menu.exec_(app_list.mapToGlobal(position))
        if action == delete_action:
            item = app_list.currentItem()
            if item is not None:
                app_list.takeTopLevelItem(app_list.indexOfTopLevelItem(item))

    app_list.setContextMenuPolicy(Qt.CustomContextMenu)
    app_list.customContextMenuRequested.connect(on_context_menu)

    def on_main_program_changed():
        app_list.clear()
        computer_name = main_program.currentText().replace(" is offline", "")
        path = f'I:\\Common\\IT\\PRAKTYKI\\{computer_name}\\config.toml'
        if os.path.exists(path):
            timetable = load_from_toml(path)
            for item in timetable:
                start_time = datetime.strptime(item['start'], '%H:%M:%S').time()
                stop_time = datetime.strptime(item['stop'], '%H:%M:%S').time()
                duration = item['duration'] if 'duration' in item else ''
                tree_item = QTreeWidgetItem(app_list, [item['type'], item['path'] if 'path' in item else item['name'],
                                                       start_time.strftime('%H:%M:%S'), stop_time.strftime('%H:%M:%S'),
                                                       duration])

                for i in range(tree_item.columnCount()):
                    tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)

    main_program.currentTextChanged.connect(on_main_program_changed)

    def on_send_clicked():
        room = main_program.currentText()
        send_data(room)

    send_button.clicked.connect(on_send_clicked)

    def on_restart_clicked():
        python = sys.executable
        os.execl(python, python, * sys.argv)

    restart_button.clicked.connect(on_restart_clicked)

    layout.addWidget(app_list)
    layout.addWidget(QLabel("Czas rozpoczęcia"))
    layout.addWidget(time_editor_start)
    layout.addWidget(QLabel("Czas zakończenia"))
    layout.addWidget(time_editor_stop)
    layout.addWidget(QLabel("Czas trwania"))
    layout.addWidget(time_editor_duration)
    layout.addWidget(schedule)
    layout.addWidget(main_program)
    layout.addWidget(save_button)
    layout.addWidget(add_button)
    layout.addWidget(send_button)
    layout.addWidget(restart_button)

    window.setLayout(layout)
    window.show()

    app.exec_()

create_gui()