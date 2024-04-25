from datetime import datetime
from typing import cast
from gi.repository import Adw, Gtk, GObject

import os
import sqlite3
from fsrs import FSRS, Rating

from .db import configure_db, cards_due_before_now, update_card


@Gtk.Template(resource_path="/com/devhypercoder/audiolang/ui/word_guess.ui")
class WordGuess(Gtk.Box):
    __gtype_name__ = "WordGuess"

    word_progress_label = cast(Gtk.Label, Gtk.Template.Child("word_progress_label"))  # type: ignore
    word_progress_bar = cast(Gtk.ProgressBar, Gtk.Template.Child("word_progress_bar"))  # type: ignore
    prev_btn = cast(Gtk.Button, Gtk.Template.Child("prev_btn"))  # type:ignore
    next_btn = cast(Gtk.Button, Gtk.Template.Child("next_btn"))  # type:ignore

    # fmt:skip
    toast_overlay = cast(Adw.ToastOverlay, Gtk.Template.Child("toast_overlay"))  # type:ignore

    _current_word = 0
    _base_path = ""
    word_cards = []
    f = FSRS()

    @GObject.Property(type=int, nick="current-word")
    def current_word(self):
        return self._current_word

    @current_word.setter
    def propCurrentWordSetter(self, value):
        self._current_word = value

    @GObject.Property(type=str, nick="base-path")
    def base_path(self):
        return self._base_path

    @base_path.setter
    def propBasePathSetter(self, value):
        self._base_path = value

    def get_con(self, configure=False):
        con = None
        db_path = os.path.join(self.base_path, "db.sqlite3")
        if configure:
            con = configure_db(self.base_path, db_path)
        else:
            con = sqlite3.connect(db_path)
        return con

    def load_words(self):
        if not self._base_path:
            return
        con = self.get_con(configure=True)
        self.word_cards = cards_due_before_now(con)
        self.current_word = 0

    def __init__(self, base_path: str, current_word=0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.connect("notify::base-path", lambda _a, _b: self.load_words())
        self.connect("notify::current-word", lambda _a, _b: self.use_current_word())

        self.base_path = base_path
        self.current_word = current_word

    def update_btns(self):
        """
        Disable prev and next buttons when on the boundary
        """

        self.prev_btn.set_sensitive(True)
        self.next_btn.set_sensitive(True)

        if self.current_word == 0:
            self.prev_btn.set_sensitive(False)
        if self.current_word == len(self.word_cards) - 1:
            self.next_btn.set_sensitive(False)

    def use_current_word(self):
        if not self.word_cards:
            return

        self.media = Gtk.MediaFile.new_for_filename(
            os.path.join(self.base_path, self.word_cards[self.current_word].word_path)
        )

        self.word_progress_bar.set_fraction(
            (self.current_word + 1) / len(self.word_cards)
        )
        self.word_progress_bar.set_tooltip_text(
            f"{self.current_word+1}/{len(self.word_cards)} ({( self.current_word +1)*100/len(self.word_cards)}%)"
        )
        self.word_progress_label.set_label(
            f"{self.current_word+1}/{len(self.word_cards)}"
        )

        self.update_btns()

    @Gtk.Template.Callback()
    def show_word(self, _: Gtk.LinkButton):
        dia = Gtk.AlertDialog()
        dia.set_message(f"Word is: {self.word_cards[self.current_word].fname}")
        dia.show(parent=self.get_root())  # type:ignore
        pass

    @Gtk.Template.Callback()
    def on_guess(self, e: Gtk.Entry):
        guess = e.get_text()
        e.set_text("")

        wc = self.word_cards[self.current_word]
        result = self.f.repeat(wc.card, datetime.utcnow())

        if guess == wc.fname:
            rating = Rating.Good
            toast_title_lbl = "CORRECT!"
            toast_title_css = "success"
        else:
            rating = Rating.Again
            toast_title_lbl = "INCORRECT!"
            toast_title_css = "error"

        toast_lbl = Gtk.Label(
            label=toast_title_lbl, use_markup=True, css_classes=[toast_title_css]
        )
        self.toast_overlay.add_toast(Adw.Toast(custom_title=toast_lbl))

        new_wcard = result[rating].card
        update_card(self.get_con(), wc.id, new_wcard)
        self.word_cards[self.current_word].card = new_wcard

    @Gtk.Template.Callback()
    def prev_click(self, _: Gtk.Button):
        if self.current_word > 0:
            self.current_word -= 1

    @Gtk.Template.Callback()
    def next_click(self, _: Gtk.Button):
        if self.current_word < len(self.word_cards):
            self.current_word += 1

    @Gtk.Template.Callback()
    def play_handler(self, _: Gtk.Button):
        if self.media.get_playing():
            self.media.pause()
        self.media.seek(0)
        self.media.play()

    def set_base_path(self, base_path):
        self.base_path = base_path
