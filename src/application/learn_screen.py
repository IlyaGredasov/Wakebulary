import asyncio
import re
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen


class LearnScreen(Screen):
    question_word = StringProperty("")
    # question_answer = StringProperty("")
    sample_size = NumericProperty(0)
    language = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generator = None
        self.loop_event = asyncio.Event()
        self.loop_task = None
        self.press_event = asyncio.Event()

    def on_enter(self):
        from backend.sample_generator import SampleGenerator
        self.generator = SampleGenerator(self.language)
        self.loop_event.set()
        self.loop_task = asyncio.create_task(
            self.generator.start_learning_loop(sample_size=self.sample_size, screen=self))

    def set_values(self, sample_size, language):
        self.sample_size = sample_size
        self.language = language

    async def pressed(self):
        if re.match(re.compile(r'([^0-9]+)'), self.ids.translation_input.text) is not None:
            print(self.ids.translation_input.text.title())
            self.ids.feedback_label.opacity = 0
            if self.ids.translation_input.text.capitalize() in self.generator.question_word.translation:
                self.ids.feedback_label.text = f'Да! {self.ids.translation_input.text}!'
                self.ids.feedback_label.canvas.before.children[0].rgba = [0, 177 / 255, 26 / 255, 0.8]
                (Animation(opacity=1, duration=1) + Animation(opacity=0, duration=0.3)).start(self.ids.feedback_label)
            else:
                self.ids.feedback_label.text = 'Нет! '
                for transl in self.generator.question_word.translation:
                    self.ids.feedback_label.text += transl + '/'
                self.ids.feedback_label.text = self.ids.feedback_label.text[:-1]
                self.ids.feedback_label.canvas.before.children[0].rgba = [138 / 255, 0, 0, 0.8]
                (Animation(opacity=1, duration=0.05 * len(self.ids.feedback_label.text)) + Animation(opacity=0,
                                                                                                     duration=0.3)).start(
                    self.ids.feedback_label)
            self.press_event.set()
            self.ids.translation_input.focus = True
            self.ids.translation_input.select_all()

    async def exit(self):
        self.loop_event.clear()
        self.loop_task.cancel()
        self.press_event.clear()
        self.manager.current = 'MainScreen'

    def update_label(self):
        self.question_word = self.generator.question_word.word
