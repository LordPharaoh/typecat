import os

import pickle
import threading
from gi.repository import GLib, GObject, Gtk
import typecat.config as config
from typecat.display.configwindow import GtkFontLoadingWindow
from typecat.font import Font


total_files = 0
loaded_files = 0
current_file_name = ""
total_cache = 0
loaded_cache = 0


def load_cache():
    # TODO if you have a lot of fonts this might kill memory, we should load and
    # del fonts as necessary.
    exceptions = set()
    try:
        exceptions = pickle.load(open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "rb"))
        print("Loaded exceptions list!")
    except FileNotFoundError:
        print("Exception file not found, initializing blank one")
        exceptions = set()
    global total_cache, loaded_cache
    cachedfonts = os.listdir(config.CACHE_LOCATION)
    total_cache = len(cachedfonts)
    for f in cachedfonts:
        if f[-7:] != ".pickle" or f[:-7] in exceptions:
            print("File {} is in exception list".format(f))
            continue
        fontname = f[:-7]
        try:
            loadfont = pickle.load(open("{}/{}".format(config.CACHE_LOCATION, f), "rb"))
            Font.fonts[fontname] = loadfont
            print("Loaded {} from cache".format(Font.fonts[fontname].name))
        except font.RenderError:
            print("Skipping {}, unable to render correctly, adding to exceptions".format(fontname))
            exceptions.add(fontname)
        loaded_cache += 1
    pickle.dump(exceptions, open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "wb"))
    print("Dumping to path {}/exceptions.tcat".format(config.CACHE_LOCATION))


def load_files():
    def run():
        t = threading.currentThread()

        fontpaths = []
        global total_files, loaded_files, current_file_name, exceptions
        try:
            exceptions = pickle.load(open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "rb"))
        except FileNotFoundError:
            exceptions = set()
            print("Exception file not found, initializing blank one")
        for fontdir in config.FONT_DIRS:
            for dirpath, dirnames, filenames in os.walk(fontdir):
                for d in filenames:
                    idx = d.rfind(".")
                    if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                        fontpaths.append(os.path.join(dirpath, d))
        total_files = len(fontpaths)

        for f in fontpaths:
            try:
                fontname = Font.extract_name(f)
                current_file_name = fontname
                if fontname in exceptions or f in exceptions:
                    print("Skipping font {}, in exception list".format(fontname))
                    continue
                g = Font(f)
                Font.fonts[fontname] = g
            except Exception as e:
                print(("Failed to read font at path {}"
                       "with exception {}").format(
                    f, e))
                exceptions.add(f)
                pickle.dump(exceptions, open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "wb"))

            loaded_files += 1
            GLib.idle_add(win.update_bar, [float(loaded_files / total_files), current_file_name])

            if getattr(t, "stop_flag", True):
                break
            if loaded_files == total_files:
                GLib.idle_add(win.cancel, None)

        Font.extract_category()
        for font in Font.fonts.values():
            print(font.name + " " + font.category)
            font.save()

    thread = threading.Thread(target=run)
    setattr(thread, "stop_flag", False)
    thread.daemon = True
    win = GtkFontLoadingWindow(thread)
    win.connect("delete-event", win.exit_handler)
    win.show_all()
    GObject.threads_init()
    thread.start()
    Gtk.main()
    thread.join()


def load_fonts():
    load_cache()
    load_files()
