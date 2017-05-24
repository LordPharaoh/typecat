import manager
import config
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
class FilterOption(Gtk.Box):
    def __init__(self, title, callback):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.checkbox = Gtk.CheckButton(title)
        self.feature = title
        self.adj = Gtk.Adjustment(0.0, -5.0, 5.0, 0.1, 0.5, 0)
        self.slider = Gtk.Scale(adjustment=self.adj, orientation=Gtk.Orientation.HORIZONTAL)
        self.slider.add_mark(0.0, Gtk.PositionType.BOTTOM)
        self.checkbox_state = self.checkbox.get_state()
        self.slider_value = self.slider.get_value()

        self.checkbox.connect("toggled", self.on_click_checkbox)
        self.slider.connect("value-changed", self.on_move_slider)

        self.pack_start(self.checkbox, False, False, 0)
        self.pack_end(self.slider, True, True, 0)

    def on_click_checkbox(self):
        self.checkbox_state = self.checkbox.get_state()
        self.callback()

    def on_move_slider(self):
        self.slider_value = self.slider.get_value()
        if self.checkbox_state:
            self.callback()


class FilterPane(Gtk.Box):
    def filter(self):
        active_feats = []
        active_values = []
        for fo in self.filterwidgets:
            active_feats.append(fo.feature)
            active_values.append(fo.slider_value * config.SCALE[fo.feature][1] + config.SCALE[fo.feature][0])
        manager.find_features(active_feats, active_values)
        self.refresh()

    def __init__(self, refresh_callback):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.filterwidgets = []
        self.refresh = refresh_callback
        for num, f in enumerate(manager.COMPARABLE_FEATURES):
            fw = FilterOption(f, self.filter)
            self.filterwidgets.append(fw)
            self.pack_start(fw, False, False, 0)

win = Gtk.Window()
win.add(FilterPane(None))
win.set_border_width(10)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
