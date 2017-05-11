import pickle
import os
import config
import statistics
from math import sqrt
from font import RenderError, Font
from display.configwindow import GtkLoadingWindow, GtkConfigWindow
from gi.repository import Gtk

keys = list()
fonts = dict()

COMPARABLE_FEATURES = ["slant", "thickness", "width", "height",
                       "ratio", "thickness_variation"]

total_files = 0
loaded_files = 0
current_file_name = ""
total_cache = 0
loaded_cache = 0

def load_cache():
    # TODO if you have a lot of fonts this might kill memory, we should load and
    # del fonts as necessary.
    global total_cache, loaded_cache
    cachedfonts = os.listdir(config.CACHE_LOCATION)
    total_cache = len(cachedfonts)
    for f in cachedfonts:
        if f[-7:] != ".pickle":
            continue
        fontname = f[:-7]
        try:
            loadfont = pickle.load(open("{}/{}".format(
                                          config.CACHE_LOCATION, f), "rb"))
            fonts[fontname] = loadfont
            print("Loaded {} from cache".format(fonts[fontname].name))
        except RenderError:
            print("Skipping {}, unable to render correctly.".format(fontname))
        loaded_cache += 1
    global keys
    keys = list(fonts.keys())


def load_files():

    fontpaths = []
    global total_files, loaded_files
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
            g = Font(f)
            fonts[fontname] = g
            g.save()
            print("Loaded {} from file".format(
                  g.name))
        except Exception as e:
            print(("Failed to read font at path {}"
                   "with exception {}").format(
                   f, e))
        loaded_files += 1

    global keys
    keys = list(fonts.keys())


def load_fonts():
    load_cache()
    load_files()


def scale(feature, value):
    """ Scales a value to its standard dev. across the font set. """
    return (config.SCALE[feature][0] - value) / config.SCALE[feature][1]


def scale_features():
    """
    Calculates the stddev and mean of each feature.
    Not necessary to be run more than once in a while.
    I might end up pasting the scales from my own fonts into the code, should
    be just fine.
    """
    for f in COMPARABLE_FEATURES:
        population = []
        for k in keys:
            population.append(fonts[k].__dict__[f])
        mean = sum(population) / max(len(population), 1)
        stddev = statistics.pstdev(population)
        print("Feature {} Mean {} Standard Dev. {}".format(f, mean, stddev))


def find_features(features, values):
    def sortkey(vals):
        total = 0
        for v, f in zip(values, features):
            if type(v) in [float, int]:
                # TODO feature scaling
                total += abs(scale(f, (v - fonts[vals].__dict__[f])**2))
            else:
                total += 0 if v == fonts[vals].__dict__[f] else 1
        return sqrt(total)
    keys.sort(key=sortkey)


def search_fonts(searchstr):
    def sortkey(vals):
        return 0 if searchstr.lower() in vals.lower() else 1
    keys.sort(key=sortkey)
