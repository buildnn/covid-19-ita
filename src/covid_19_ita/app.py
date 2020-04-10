from os.path import abspath, dirname, join, relpath
from flask import Flask, Blueprint
from dotenv import load_dotenv
import logging
import glob
from . import CONFIG_DIR, TEMPLATES_DIR, SITE_DIR
from .render import render_from_configfile

app = Flask(
    __name__, static_url_path="/assets", static_folder=join(SITE_DIR, "assets")
)
here = dirname(abspath(__file__))

blueprint = Blueprint(
    "figures",
    __name__,
    static_url_path="/figures",
    static_folder=join(SITE_DIR, "figures"),
)
app.register_blueprint(blueprint)

config_files = glob.glob(join(CONFIG_DIR, "*.yml"))
config_files += glob.glob(join(CONFIG_DIR, "**/*.yml"))

config_files = [
    ("/" + relpath(conf, CONFIG_DIR).rsplit(".yml", 1)[0], conf) for conf in config_files
]

for n, (route, configfile) in enumerate(config_files):
    print(route, " -> ", configfile)
    def autoroute():
        config_path = join(CONFIG_DIR, configfile)
        print(config_files)
        return render_from_configfile(config_path, TEMPLATES_DIR, CONFIG_DIR)
    autoroute.__name__ = "autorute_{:04d}".format(n)
    app.route(route)(autoroute)
