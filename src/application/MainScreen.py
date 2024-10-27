from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivymd.uix.responsivelayout import MDResponsiveLayout

from backend.db_client import DataBaseClient


class Preparation(BoxLayout):
    def preparation_to_learn(self):
        MainScreen.preparation_to_learn(self)

    def confirm(self, instance):
        MainScreen.confirm(self, instance)

    def update_button_activity(self):
        MainScreen.update_button_activity(self)

    def change_screen(self, sample_size, language):
        MainScreen.change_screen(self, sample_size, language)


class BaseView(FloatLayout):
    def preparation_to_learn(self):
        MainScreen.preparation_to_learn(self)

    def confirm(self, instance):
        MainScreen.confirm(self, instance)

    def update_button_activity(self):
        MainScreen.update_button_activity(self)

    def change_screen(self, sample_size, language):
        MainScreen.change_screen(self, sample_size, language)

    def add_to_base(self):
        MainScreen.add_to_base(self)


class MobileView(BaseView):
    pass


class TabletView(BaseView):
    pass


class DesktopView(BaseView):
    pass


class MainScreen(MDResponsiveLayout, Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rus = None
        self.sample_size_words_input = None
        self.confirm_button = None
        self.eng = None
        self.dialog = None
        self.show = None
        self.mobile_view = MobileView()
        self.tablet_view = TabletView()
        self.desktop_view = DesktopView()

    def preparation_to_learn(self):
        size_h = (1, 1)
        match self.name:
            case 'tablet_view':
                size_h = (self.width / 2, self.height / 2)
            case 'mobile_view':
                size_h = (self.width, self.height / 2)
            case 'desktop_view':
                size_h = (self.width / 4, self.height / 4)

        self.show = Preparation()
        self.dialog = Popup(title='',
                            content=self.show,
                            auto_dismiss=True,
                            size_hint=(0.3, 0.4),
                            size_hint_min=size_h,
                            separator_color='#282828')
        self.dialog.open()

        self.eng = self.show.ids.eng_checkbox
        self.rus = self.show.ids.rus_checkbox
        self.confirm_button = self.show.ids.confirm_button
        self.sample_size_words_input = self.show.ids.sample_size_input

        self.eng.bind(active=lambda instance, value: self.update_button_activity())
        self.rus.bind(active=lambda instance, value: self.update_button_activity())
        self.confirm_button.bind(on_press=self.confirm), self.show.ids.cancel_button.bind(on_press=self.dialog.dismiss)
        self.sample_size_words_input.bind(text=lambda instance, value: self.update_button_activity())

    def update_button_activity(self):
        self.confirm_button.disabled = self.sample_size_words_input.text == '' or not (
                self.eng.active or self.rus.active)

    def confirm(self, instance):
        sample_size = self.sample_size_words_input.text
        language = ('eng' if self.eng.active else 'rus')
        self.change_screen(sample_size, language)

    def change_screen(self, sample_size: int, language: str):
        self.parent.manager.get_screen('LearnScreen').set_values(sample_size, language)
        self.dialog.dismiss()
        self.parent.manager.current = 'LearnScreen'

    def add_to_base(self):
        db = DataBaseClient()
        db.insert_transl(self.ids.word_input.text, [self.ids.translation_input.text])
        self.ids.word_input.focus = True
        self.ids.translation_input.text = ''
        self.ids.word_input.select_all()
