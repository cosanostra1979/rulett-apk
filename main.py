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
        self.history = []
        self.bankroll = 10000.0
        self.initial_bankroll = 10000.0
        self.unit_bet = 50.0
        self.sector_streaks = {s_name: 0 for s_name in sectors.keys()}

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.info_label = Label(text="Add meg a pörgetett számot (0-36):", size_hint_y=None, height=40)
        layout.add_widget(self.info_label)

        self.input_box = TextInput(text='', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.input_box)

        self.submit_btn = Button(text="Küldés / Pörgetés", size_hint_y=None, height=50)
        self.submit_btn.bind(on_press=self.process_number)
        layout.add_widget(self.submit_btn)

        scroll = ScrollView()
        self.result_label = Label(text="Itt jelennek meg az adatok...", size_hint_y=None, halign='left', valign='top')
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        scroll.add_widget(self.result_label)
        layout.add_widget(scroll)

        return layout

    def process_number(self, instance):
        val = self.input_box.text.strip()
        self.input_box.text = ''
        try:
            number = int(val)
            if number < 0 or number > 36:
                self.result_label.text = "Hiba: 0 és 36 közötti számot adj meg!"
                return
        except ValueError:
            self.result_label.text = "Hiba: Érvénytelen szám!"
            return

        self.history.append(number)
        total = len(history_len := len(self.history))

        current_sector_name = ""
        for s_name, s_nums in sectors.items():
            if number in s_nums:
                current_sector_name = s_name
                self.sector_streaks[s_name] = 0
            else:
                self.sector_streaks[s_name] += 1

        expected_per_sector = total / 4.0
        text_out = f"Dobás: {number} (Helye: {current_sector_name})\nÖsszes pörgetés: {total}\n\n"

        for s_name, s_nums in sectors.items():
            c = sum(1 for n in self.history if n in s_nums)
            tension = c - expected_per_sector
            streak = self.sector_streaks[s_name]
            pct = (c / total) * 100
            text_out += f"- {s_name}: {c} találat ({pct:.1f}%) | Fesz.: {tension:+.1f} | Kimaradás: {streak}\n"

        self.result_label.text = text_out

if __name__ == '__main__':
    RulettApp().run()
