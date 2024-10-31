from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen


class StartScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.animate, 0)
        Clock.schedule_once(self.change_screen, 1.8)

    def animate(self, dt):
        (Animation(opacity=1, duration=0.7) +
         Animation(duration=0.3) +
         Animation(font_size=0, opacity=0, duration=0.3)).start(self.ids.start_label)

    def change_screen(self, dt):
        self.manager.current = 'MainScreen'
