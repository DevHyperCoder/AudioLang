from typing import cast
from gi.repository import Gtk
from gi.repository.Gio import Task

import requests


@Gtk.Template(resource_path="/com/devhypercoder/audiolang/ui/feedback_window.ui")
class FeedbackWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "FeedbackWindow"

    title_entry = cast(Gtk.Entry, Gtk.Template.Child("title_entry"))  # type:ignore
    # fmt:skip
    descr_text_view = cast( Gtk.TextView, Gtk.Template.Child("descr_text_view"))  # type:ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @Gtk.Template.Callback()
    def on_cancel(self, _: Gtk.Button):
        self.close()

    @Gtk.Template.Callback()
    def on_submit(self, _: Gtk.Button):
        title = self.title_entry.get_text()

        descr_buf = self.descr_text_view.get_buffer()
        descr = descr_buf.get_text(
            descr_buf.get_start_iter(), descr_buf.get_end_iter(), False
        )

        try:
            url = "https://audiolang.netlify.app/feedback"
            requests.post(
                url, data={"name": title, "message": descr, "form-name": "contact"}
            )

            dia = Gtk.AlertDialog()
            dia.set_message("Feedback has been sent!")
            dia.choose(parent=self, callback=self.done)
        except requests.RequestException as e:
            print(str(e))

            dia = Gtk.AlertDialog()
            dia.set_message("Error!")
            dia.set_detail(f"{str(e)}")
            dia.choose(parent=self, callback=self.err_finish)

    def done(self, _dia: Gtk.AlertDialog, _task: Task):
        self.close()

    def err_finish(self, _dia: Gtk.AlertDialog, _task: Task):
        pass
