import os
import ConfigParser

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))

config = ConfigParser.ConfigParser()
config.read(os.path.join(PROJECT_ROOT, "project.conf"))

#config.get('wepawet', 'username')