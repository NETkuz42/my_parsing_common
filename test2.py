import subprocess

path_to_speedtest = r"D:\DISTRIB_LOCAL\PROGRAM\speedtest\speedtest.exe"
servers = {"mts_mos": "librarian.comstar.ru", "dom_spb": "speedtest.spb.ertelecom.ru", "near": ""}

result_test = subprocess.run([path_to_speedtest, "-o", servers["dom_spb"]], capture_output=True)

result = str(result_test).split(r"\n")

text = r"         ISP: Rostelecom\r"
result_dict = {3: "target_server",
               4: ["provider", text.replace('ISP:', '').replace(r'\r', '').replace(' ', '')],
               5: "Idle letancy",
               6: "Download speed",
               7: "Download latency",
               8: "Upload speed",
               9: "Upload latency",
               10: "packets lost"}

test = result_dict[4][1]

print(test)