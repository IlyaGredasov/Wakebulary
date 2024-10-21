from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
import src.application.StartScreen
import src.application.MainScreen

class MainApp(MDApp):
    Window.maximize()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'
        sm = ScreenManager(transition=NoTransition())
        screens = ['StartScreen', 'MainScreen']
        for screen in screens:
            sm.add_widget(Builder.load_file('src/application/'+screen+'.kv'))
        return sm


if __name__ == '__main__':
    MainApp().run()
