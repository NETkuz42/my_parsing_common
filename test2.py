import subprocess
import pandas as pd


def run_speedtest(path_result):
    path_to_speedtest = r"D:\DISTRIB_LOCAL\PROGRAM\speedtest\speedtest.exe"
    servers = {"mts_mos": "librarian.comstar.ru", "dom_spb": "speedtest.spb.ertelecom.ru", "near": ""}
    try:
        result_frame = pd.read_csv(path_result, encoding="UTF-8", sep=";")
    except FileNotFoundError:
        result_frame = pd.DataFrame()

    for server in servers:
        run_test = subprocess.run([path_to_speedtest, "-o", servers["dom_spb"], "-u", "Mbps"], capture_output=True)
        dataframe = pd.DataFrame()
        dataframe.loc[len(dataframe), "result"] = str(run_test)
        dataframe.to_csv("speedtest.csv", sep=";", encoding="UTF-8")

        run_test = pd.read_csv("speedtest.csv", encoding='UTF-8', sep=";").loc[0, "result"]
        results_list = str(run_test).split(r"\n")

        clean_list = [result.replace('  ', '').replace(r'\r', "") for result in results_list]
        result_dict = {"server": {"full": clean_list[3], "shot": int(clean_list[3].split("id:")[1].replace(")","").strip())},
                       "provider": {"full": clean_list[4], "shot": clean_list[4].replace('ISP:', '').strip()},
                       "idle_letancy": {"full": clean_list[5], "shot": float(clean_list[5].split(" ms")[0].replace("Idle Latency:", "").strip())},
                       "down_speed": {"full": clean_list[6], "shot": float(clean_list[6].split(" Mbps")[0].replace("Download:", "").strip())},
                       "down_letancy": {"full": clean_list[7], "shot": float(clean_list[7].split(" ms")[0].strip())},
                       "up_speed": {"full": clean_list[8], "shot": float(clean_list[8].split(" Mbps")[0].replace("Upload: ", "").strip())},
                       "up_letancy": {"full": clean_list[9], "shot": float(clean_list[9].split(" ms")[0].strip())},
                       "packet_loss": {"full": clean_list[10], "shot": clean_list[10].replace(" Packet Loss: ", "").replace("%", "").strip()}}

        index_row = len(result_frame)

        for param, vol in result_dict.items():
            for type_result, result in vol.items():
                name_result = f"{param}_{type_result}"
                result_frame.loc[index_row, name_result] = result

    result_frame.to_csv("speedtest_result.csv", encoding="UTF-8", sep=";")


run_speedtest(r"C:\PYTHON\my_parsing_common\speedtest_result.csv")
