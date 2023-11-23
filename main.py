from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import BoundedNumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

import paho.mqtt.client as mqtt


Builder.load_file('main.kv')



flag_connect_internet = False
Status = 'OffLine'
CHstatus = 'OFF'
Flame = 'OFF'
TBoiler = 0
CHTSet = 0
CHTSet_change = 0


class MyLayout(AnchorLayout):
    CHstatus_Switch = BooleanProperty(False)
    connect_status = StringProperty('OffLine')
    CHTSet_text = StringProperty('OffLine')
    set_value = NumericProperty(0)
    flame_status = ListProperty([1, 1, 1, 1])
    bar_color = ListProperty([255 / 255, 210 / 255, 122 / 255, 1])
    bar_width = NumericProperty(30)
    text = StringProperty("30" + u'\N{DEGREE SIGN}' + 'C')
    text_CHTSet = StringProperty("30" + u'\N{DEGREE SIGN}' + 'C')
    back_color_status = ListProperty([0.98, 0.05, 0.11, 1])
    back_color_CHTSet = ListProperty([0.19, 0.6, 0.89, 1])


    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        host = '192.168.31.12'
        port = 1883
        username = 'username'
        password = 'password'

        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.username_pw_set(username, password)
        self.client.connect(host, port, 60)
        self.client.loop_start()
        self.client.subscribe("ESP-B176C4/Opentherm/Status")
        self.client.subscribe("ESP-B176C4/Opentherm/CHstatus")
        self.client.subscribe("ESP-B176C4/Opentherm/TBoiler")
        self.client.subscribe("ESP-B176C4/Opentherm/CHTSet")
        self.client.subscribe("ESP-B176C4/Opentherm/Flame")


    def on_message(self, client, userdata, msg):
        global flag_connect_internet
        global CHTSet
        global CHTSet_change
        global TBoiler
        global CHstatus
        global Status
        global Flame
        print(msg.topic + " " + msg.payload.decode())

        if msg.topic == "ESP-B176C4/Opentherm/TBoiler":
            TBoiler = int(float(msg.payload.decode()))
            print('TBoiler = ', TBoiler)
            self.text = str(TBoiler) + u'\N{DEGREE SIGN}' + 'C'
            # Ставим - 30 градусов так как ноль это 30 градусов
            self.set_value = TBoiler - 30
            print('self.set_value = ', self.set_value)
            self.bar_color = [self.bar_color[0], (150 - (self.set_value + 30)) / 255, (112 - (self.set_value + 30)) / 255, 1]


        elif msg.topic == "ESP-B176C4/Opentherm/Flame":
            Flame = msg.payload.decode()
            print('Flame = ', Flame)
            if Flame == 'ON':
                self.flame_status = [0, 0, 0, 0]
            elif Flame == 'OFF':
                self.flame_status = [0, 0, 0, 1]

        elif msg.topic == "ESP-B176C4/Opentherm/Status":
            Status = msg.payload.decode()
            print('Status = ', Status)
            self.connect_status = Status
            if Status == 'OnLine':
                self.back_color_status = [0.08, 0.47, 0.21, 1]
            elif Status == 'OffLine':
                self.back_color_status = [0.44, 0.45, 0.44, 1]
            elif Status == 'Fault':
                self.back_color_status = [0.98, 0.05, 0.11, 1]


        elif msg.topic == "ESP-B176C4/Opentherm/CHTSet":
            CHTSet = int(float(msg.payload.decode()))
            print('CHTSet = ', CHTSet)
            self.text_CHTSet = str(CHTSet) + u'\N{DEGREE SIGN}' + 'C'
            CHTSet_change = CHTSet
            self.CHTSet_text = 'Заданная температура\nтеплоносителя ' + str(CHTSet) + u'\N{DEGREE SIGN}' + 'C'
            self.back_color_CHTSet = [220 / 255, 220 / 255, 220 / 255, 1]


        elif msg.topic == "ESP-B176C4/Opentherm/CHstatus":
            CHstatus = msg.payload.decode()
            print('CHstatus = ', CHstatus)
            if CHstatus == 'ON':
                self.CHstatus_Switch = True
            elif CHstatus == 'OFF':
                self.CHstatus_Switch = False


    def press_CHTSet(self):
        global CHTSet
        global CHTSet_change
        print('Задать температуру до = ', CHTSet_change)
        self.client.publish("ESP-B176C4/Opentherm/SetCHtemp", f'{CHTSet_change}')
        print('Задать температуру после = ', CHTSet_change)


    def press_CHTSet_minus(self):
        global CHTSet
        global CHTSet_change
        if CHTSet_change > 30:
            CHTSet_change = CHTSet_change - 1
            self.text_CHTSet = str(CHTSet_change) + u'\N{DEGREE SIGN}' + 'C'
            print('minus')
            if CHTSet_change == CHTSet:
                self.CHTSet_text = 'Заданная температура\nтеплоносителя ' + str(CHTSet) + u'\N{DEGREE SIGN}' + 'C'
                self.back_color_CHTSet = [220 / 255, 220 / 255, 220 / 255, 1]
            elif CHTSet_change < CHTSet:
                self.CHTSet_text = 'Уменьшить температуру\nна ' + str(abs(
                    CHTSet - CHTSet_change)) + u'\N{DEGREE SIGN}' + 'C'
                self.back_color_CHTSet = [0 / 255, 206 / 255, 209 / 255, 1]
            elif CHTSet_change > CHTSet:
                self.CHTSet_text = 'Увеличить температуру\nна ' + str(abs(
                    CHTSet_change - CHTSet)) + u'\N{DEGREE SIGN}' + 'C'
                self.back_color_CHTSet = [255 / 255, 105 / 255, 180 / 255, 1]


    def press_CHTSet_plus(self):
        global CHTSet
        global CHTSet_change
        if CHTSet_change < 70:
            CHTSet_change = CHTSet_change + 1
            self.text_CHTSet = str(CHTSet_change) + u'\N{DEGREE SIGN}' + 'C'
            print('plus')
            if CHTSet_change == CHTSet:
                self.CHTSet_text = 'Заданная температура\nтеплоносителя ' + str(CHTSet) + u'\N{DEGREE SIGN}' + 'C'
                self.back_color_CHTSet = [220 / 255, 220 / 255, 220 / 255, 1]
            elif CHTSet_change < CHTSet:
                self.CHTSet_text = 'Уменьшить температуру\nна ' + str(abs(
                    CHTSet - CHTSet_change)) + u'\N{DEGREE SIGN}' + 'C'
                self.back_color_CHTSet = [0 / 255, 206 / 255, 209 / 255, 1]
            elif CHTSet_change > CHTSet:
                self.CHTSet_text = 'Увеличить температуру\nна ' + str(abs(
                    CHTSet_change - CHTSet)) + u'\N{DEGREE SIGN}' + 'C'
                self.back_color_CHTSet = [255 / 255, 105 / 255, 180 / 255, 1]


    def CHstatus_Set(self, switchObject, switchValue):
        print(switchValue)
        if switchValue == False:
            self.client.publish("ESP-B176C4/Opentherm/SetCHmode", f'{1}')
            print('Котел отключен')
        elif switchValue == True:
            self.client.publish("ESP-B176C4/Opentherm/SetCHmode", f'{0}')
            print('Котел включен')


class MyApp(App):
    def build(self):
        return MyLayout()



if __name__ == '__main__':
    MyApp().run()