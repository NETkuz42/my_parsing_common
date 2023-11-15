from gtts import gTTS
from gtts.tts import gTTSError
import vlc
from time import sleep
from typing import Literal
from os import path


class Voices:
    standard_voices = Literal["капча появилась", "капча всё ещё тут", "капча пройдена"]

    def __init__(self):
        self.work_dir = path.dirname(path.abspath(__file__))
        self.dir_sounds = fr"{self.work_dir}\multimedia\sounds"
        self.default_letter_wait = 0.09
        self.standard_voice_dict = {"капча появилась": "captcha_appeared.mp3",
                                    "капча всё ещё тут": "captcha_still_here.mp3",
                                    "капча пройдена": "captcha passed.mp3"}

    def __create_voice(self, text_for_play, path_to_save=None):
        if path_to_save is None:
            path_to_save = fr"{self.dir_sounds}\new_voice.mp3"
        language = 'ru'
        try:
            s = gTTS(text=text_for_play, lang=language, slow=False)
            s.save(path_to_save)
        except gTTSError:
            print("ошибка создания голоса пробую ещё раз")
            self.__create_voice(text_for_play)
        return path_to_save

    def __play(self, path_to_file, text: str = "length from here"):
        wait_playback = len(text) * self.default_letter_wait + 2
        player = vlc.MediaPlayer(path_to_file)
        player.play()
        sleep(wait_playback)
        player.stop()

    def play_new_voice(self, text="забыл ввести текст", path_to_save=None):
        path_to_file = self.__create_voice(text, path_to_save)
        self.__play(path_to_file, text)

    def play_default_voice(self, default_voice: standard_voices):
        default_file = self.standard_voice_dict[default_voice]
        path_to_default_file = fr"{self.dir_sounds}\{default_file}"
        self.__play(path_to_default_file)


Voices().play_default_voice("капча появилась")
