from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from backend.sample_generator import SampleGenerator


class Preparation(BoxLayout):
    pass


class MainScreen(Screen):

    def preparation_to_learn(self):
        self.show = Preparation()
        self.dialog = Popup(title='', content=self.show, auto_dismiss=True, size_hint=(0.3, 0.4),
                            separator_color='#282828')
        self.dialog.open()

        self.eng = self.show.ids.eng_checkbox
        self.rus = self.show.ids.rus_checkbox
        self.confirm_button = self.show.ids.confirm_button
        self.count_words_input = self.show.ids.CountInput

        self.eng.bind(active=lambda instance, value: self.update_button_activity())
        self.rus.bind(active=lambda instance, value: self.update_button_activity())
        self.confirm_button.bind(on_press=self.confirm), self.show.ids.cancel_button.bind(on_press=self.dialog.dismiss)
        self.count_words_input.bind(text=lambda instance, value: self.update_button_activity())

    def update_button_activity(self):
        self.confirm_button.disabled = self.count_words_input.text == '' or not (self.eng.active or self.rus.active)

    def confirm(self, instance):
        count = self.count_words_input.text
        language = ('eng' if self.eng.active else 'rus')
        generator = SampleGenerator("rus" if language == 'rus' else "eng")
        generator.start_learning_loop(count)

    def change_screen(self):
        self.manager.current = 'StartScreen'
        print('true')
