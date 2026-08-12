import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

wheel_order = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

sectors = {
    "1. Sektor (0-tól)": wheel_order[0:9],
    "2. Sektor (Jobb)": wheel_order[9:18],
    "3. Sektor (Alsó)": wheel_order[18:28],
    "4. Sektor (Bal)": wheel_order[28:37]
}

consecutive_probabilities = {
    1: 75.68, 2: 57.27, 3: 43.34, 4: 32.80, 5: 24.82,
    6: 18.78, 7: 14.21, 8: 10.75, 9: 8.14, 10: 6.16,
    11: 4.66, 12: 3.53, 13: 2.67, 14: 2.02, 15: 1.53,
    16: 1.16, 17: 0.88, 18: 0.66, 19: 0.50, 20: 0.39
}

class RulettApp(App):
    def build(self):
        self.filename = "rulett_mentes.json"
        self.history = []
        self.bankroll = 10000.0
        self.initial_bankroll = 10000.0
        self.unit_bet = 50.0
        self.sector_streaks = {s_name: 0 for s_name in sectors.keys()}
        self.state = "INIT_BANKROLL"

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.info_label = Label(text="Add meg a kezdő tőkét:", size_hint_y=None, height=50)
        layout.add_widget(self.info_label)

        self.input_box = TextInput(text='10000', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.input_box)

        self.submit_btn = Button(text="Következő", size_hint_y=None, height=50)
        self.submit_btn.bind(on_press=self.process_input)
        layout.add_widget(self.submit_btn)

        scroll = ScrollView()
        self.result_label = Label(text="Üdv! Add meg az adatokat.\n", size_hint_y=None, halign='left', valign='top')
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        scroll.add_widget(self.result_label)
        layout.add_widget(scroll)

        return layout

    def log(self, text):
        self.result_label.text += text + "\n"

    def process_input(self, instance):
        val = self.input_box.text.strip()
        self.input_box.text = ''

        if self.state == "INIT_BANKROLL":
            try:
                self.initial_bankroll = float(val) if val else 10000.0
                self.bankroll = self.initial_bankroll
            except ValueError:
                self.initial_bankroll = 10000.0
                self.bankroll = 10000.0
            self.state = "INIT_UNIT"
            self.info_label.text = "Add meg az 1 számra eső tétet (min. 50 Ft):"
            self.input_box.text = "50"
            self.log(f"Kezdő tőke: {self.initial_bankroll} Ft")

        elif self.state == "INIT_UNIT":
            try:
                ub = float(val) if val else 50.0
                if ub < 50:
                    self.log(">>> Minimum 50 Ft kell legyen! <<<")
                    return
                self.unit_bet = ub
            except ValueError:
                self.unit_bet = 50.0

            self.state = "PLAYING"
            self.info_label.text = "Írj be egy számot (0-36), vagy 'stat':"
            self.log("Játék elindulva. Írd be a pörgetett számot.")

        elif self.state == "PLAYING":
            if val.lower() == 'stat':
                self.log(f"Eddigi pörgetések száma: {len(self.history)}")
                return
            try:
                number = int(val)
                if number < 0 or number > 36:
                    self.log(">>> 0 és 36 közötti számot adj meg! <<<")
                    return
            except ValueError:
                self.log(">>> Érvénytelen érték! <<<")
                return

            self.history.append(number)
            total = len(self.history)
            self.log(f"[{total}. dobás] Beérkezett szám: {number}")

if __name__ == '__main__':
    RulettApp().run()

