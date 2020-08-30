from subprocess import Popen, PIPE, STDOUT
from _lib.configUtils import ffmpegPath

ffprobeExe = "/".join([ffmpegPath, 'ffprobe.exe'])


def getDuration(filename):
    result = Popen([ffprobeExe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename], stdout=PIPE, stderr=STDOUT)
    return float(result.stdout.read().decode().strip())
