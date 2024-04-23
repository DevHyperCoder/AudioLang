from gi.repository import Gtk
from gi.repository.GObject import (
    TYPE_BOOLEAN,
    TYPE_OBJECT,
    TYPE_STRING,
    SignalFlags,
    signal_new,
)
from gi.repository.Gio import Task


@Gtk.Template(resource_path="/com/devhypercoder/audiolang/choose_dir.ui")
class ChooseDirPage(Gtk.Box):
    __gtype_name__ = "ChooseDirPage"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        signal_new(
            "dir-choose", TYPE_OBJECT, SignalFlags.RUN_LAST, TYPE_BOOLEAN, [TYPE_STRING]
        )

    @Gtk.Template.Callback()
    def show_dir_chooser(self, _):
        dir_chooser = Gtk.FileDialog()
        dir_chooser.select_folder(callback=self.dir_chooser_finalize)

    def dir_chooser_finalize(self, chooser: Gtk.FileDialog, a: Task):
        # Don't do anything if dialog is dismissed
        if a.had_error():
            return

        res = chooser.select_folder_finish(a)
        if not res:
            return

        path = res.get_path()
        if not path:
            return

        self.emit("dir-choose", path)
