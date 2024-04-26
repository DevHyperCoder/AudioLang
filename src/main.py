import os
import gi
import sys


gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio, Gtk, Adw, Gdk

from .choose_dir import ChooseDirPage
from .word_preview import WordPreview
from .word_guess import WordGuess
from .feedback_window import FeedbackWindow

from typing import cast


@Gtk.Template(resource_path="/com/devhypercoder/audiolang/ui/window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    view_stack = cast(Gtk.Stack, Gtk.Template.Child("view_stack"))  # type: ignore
    back_btn = cast(Gtk.Button, Gtk.Template.Child("back_btn"))  # type: ignore

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        about_action = Gio.SimpleAction(name="about")
        feedback_action = Gio.SimpleAction(name="feedback")

        self.add_action(about_action)
        self.add_action(feedback_action)

        about_action.connect("activate", self.open_about_dialog)
        feedback_action.connect("activate", self.open_feedback_window)

        self.path = path
        self.words = []

        if path is not None:
            self.parse_dir(path)

        self.choose_dir = ChooseDirPage()
        self.choose_dir.connect("dir-choose", self.on_dir_choose)
        self.view_stack.add_named(self.choose_dir, "choose_dir")

        self.word_preview = WordPreview(self.path, self.words)
        self.view_stack.add_named(self.word_preview, "word_preview")

        self.word_guess = WordGuess(self.path)
        self.view_stack.add_named(self.word_guess, "word_guess")

        if path is not None:
            self.view_stack.set_visible_child_name("preview_or_guess_box")
            self.back_btn.set_visible(True)
        else:
            self.view_stack.set_visible_child_name("choose_dir")
            self.back_btn.set_visible(False)

    @Gtk.Template.Callback()
    def on_back_btn_click(self, _):
        self.view_stack.set_visible_child_name("choose_dir")
        self.back_btn.set_visible(False)

    @Gtk.Template.Callback()
    def on_preview_btn_click(self, _):
        self.view_stack.set_visible_child_name("word_preview")

    @Gtk.Template.Callback()
    def on_guess_btn_click(self, _):
        self.view_stack.set_visible_child_name("word_guess")

    def open_feedback_window(self, _action, _):
        win = FeedbackWindow()
        win.show()

    def open_about_dialog(self, _action, _):
        dia = Gtk.AboutDialog()
        dia.set_program_name("AudioLang")
        dia.set_authors(["DevHyperCoder <devan@devhypercoder.com>"])
        dia.set_license_type(Gtk.License.GPL_3_0)
        dia.set_comments("Learn how to spell by listening")
        dia.set_logo_icon_name("com.devhypercoder.audiolang")
        dia.add_credit_section("Audio files", ["LinguaLibre https://lingualibre.org"])
        dia.show()

    def parse_dir(self, dir_path):
        self.words = []
        for path in os.listdir(dir_path):
            self.words.append((path.split(".")[0], path))

    def on_dir_choose(self, _, dir_path):
        print(f"Loading {dir_path=}")
        self.path = dir_path
        self.parse_dir(dir_path)
        if len(self.words) <= 0:
            err_dia = Gtk.AlertDialog()
            err_dia.set_message("No audio files!")
            err_dia.set_detail(f"{dir_path} does not contain any audio files!")
            err_dia.show(self)
            return

        self.word_preview.set_base_path(self.path)
        self.word_preview.set_words(self.words)
        self.word_guess.set_base_path(self.path)
        self.view_stack.set_visible_child_name("preview_or_guess_box")
        self.back_btn.set_visible(True)


class AudioLangApp(Adw.Application):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self.path = path

    def on_activate(self, app):
        self.win = MainWindow(self.path, application=app)
        self.win.present()


def main(_version):
    app = AudioLangApp(path=None, application_id="com.devhypercoder.audiolang")
    app.run(sys.argv)
