from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
import asyncio
from application import StartScreen, MainScreen, LearnScreen

class MainApp(MDApp):
    Window.maximize()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'
        sm = ScreenManager(transition=NoTransition())
        screens = ['StartScreen', 'MainScreen', 'LearnScreen']
        for screen in screens:
            sm.add_widget(Builder.load_file('src/application/'+screen+'.kv'))
        return sm

    async def async_run_app(self):
        await self.async_run(async_lib='asyncio')


if __name__ == '__main__':
    instanceApp = MainApp()
    asyncio.run(instanceApp.async_run_app())
