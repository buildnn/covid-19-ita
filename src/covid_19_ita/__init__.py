from os.path import abspath, dirname, join


__version__ = "0.0.2"
PACKAGE_DIR = dirname(abspath(__file__))
PROJECT_DIR = dirname(dirname(PACKAGE_DIR))
SITE_DIR = join(PROJECT_DIR, "docs")
CONFIG_DIR = join(PROJECT_DIR, "config")
TEMPLATES_DIR = join(PACKAGE_DIR, "templates")
