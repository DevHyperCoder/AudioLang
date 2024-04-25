from typing import cast
from gi.repository import GObject, Gtk

import os


@Gtk.Template(resource_path="/com/devhypercoder/audiolang/ui/word_preview.ui")
class WordPreview(Gtk.Box):
    __gtype_name__ = "WordPreview"

    word_label = cast(Gtk.Label, Gtk.Template.Child("word_label"))  # type: ignore
    prev_btn = cast(Gtk.Button, Gtk.Template.Child("prev_btn"))  # type:ignore
    next_btn = cast(Gtk.Button, Gtk.Template.Child("next_btn"))  # type:ignore

    _current_word = 0

    @GObject.Property(type=int, nick="current-word")
    def current_word(self):
        return self._current_word

    @current_word.setter
    def propCurrentWordSetter(self, value):
        self._current_word = value

    def __init__(
        self,
        base_path: str,
        words: list[tuple[str, str]],
        current_word=0,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.base_path = base_path
        self.words = words

        self.current_word = current_word
        self.connect("notify::current-word", lambda _a, _b: self.use_current_word())

        if self.words:
            self.use_current_word()

    def update_btns(self):
        """
        Disable prev and next buttons when on the boundary
        """

        self.prev_btn.set_sensitive(True)
        self.next_btn.set_sensitive(True)

        if self.current_word == 0:
            self.prev_btn.set_sensitive(False)
        if self.current_word == len(self.words) - 1:
            self.next_btn.set_sensitive(False)

    def use_current_word(self):
        self.media = Gtk.MediaFile.new_for_filename(
            os.path.join(self.base_path, self.words[self.current_word][1])
        )
        self.word_label.set_label(self.words[self.current_word][0])

        self.update_btns()

    @Gtk.Template.Callback()
    def prev_click(self, _: Gtk.Button):
        if self.current_word > 0:
            self.current_word -= 1

    @Gtk.Template.Callback()
    def next_click(self, _: Gtk.Button):
        if self.current_word < len(self.words):
            self.current_word += 1

    @Gtk.Template.Callback()
    def play_handler(self, _: Gtk.Button):
        if self.media.get_playing():
            self.media.pause()
        self.media.seek(0)
        self.media.play()

    def set_base_path(self, base_path):
        self.base_path = base_path

    def set_words(self, words):
        self.words = words
        self.current_word = 0
