import os
from subprocess import Popen, PIPE
from kivy import __version__ as VERSION
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore


def run_syscall(cmd):
    """
    run_syscall; handle sys calls this function used as shortcut.
    ::cmd: String, shell command is expected.
    """
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()


PATH_SEPERATOR = '/'
if os.path.realpath(__file__).find('\\') != -1:
    PATH_SEPERATOR = '\\'

PROJECT_PATH = PATH_SEPERATOR.join(os.path.realpath(__file__).split(PATH_SEPERATOR)[:-1])

if PATH_SEPERATOR == '/':
    cmd = "echo $HOME"
else:
    cmd = "echo %USERPROFILE%"

out = run_syscall(cmd)
REPOFILE = "%(out)s%(ps)s.kivy-mines%(ps)smines" % {'out': out.rstrip(), 'ps': PATH_SEPERATOR}

DB = JsonStore(REPOFILE)
directory = os.path.dirname(REPOFILE)
if not os.path.exists(directory):
    os.makedirs(directory)

KIVY_VERSION = VERSION

HOVER = get_color_from_hex('ACACAC')
NORMAL = get_color_from_hex('E2DDD5')
RED = get_color_from_hex('990000')
COLOR_PALETTE = {
    1: "ff0000",
    2: "ff8000",
    3: "ffff00",
    4: "80ff00",
    5: "00ff00",
    6: "00ff80",
    7: "00ffff",
    8: "0080ff"
}