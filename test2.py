import subprocess
import sys

path_to_speedtest = r"D:\DISTRIB_LOCAL\PROGRAM\speedtest\speedtest.exe"
servers = {"mts_mos": "librarian.comstar.ru", "dom_spb": "speedtest.spb.ertelecom.ru", "near": ""}

result = subprocess.run([path_to_speedtest, "-o", servers["dom_spb"]], capture_output=True)

print(result)


