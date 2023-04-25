from pywinauto import Desktop, Application, timings
from pywinauto import findwindows, ElementNotFoundError
from pywinauto.timings import always_wait_until_passes
from time import sleep
import subprocess
import pandas as pd
from datetime import datetime


def run_speedtest(path_result):
    path_to_speedtest = r"D:\DISTRIB_LOCAL\PROGRAM\speedtest\speedtest.exe"
    servers = {"mts_mos": "librarian.comstar.ru", "dom_spb": "speedtest.spb.ertelecom.ru"}
    try:
        result_frame = pd.read_csv(path_result, encoding="UTF-8", sep=";")
    except FileNotFoundError:
        result_frame = pd.DataFrame()

    for server in servers.values():
        run_test = subprocess.run([path_to_speedtest, "-o", server, "-u", "Mbps"], capture_output=True)
        results_list = str(run_test).split(r"\n")

        clean_list = [result.replace('  ', '').replace(r'\r', "") for result in results_list]
        result_dict = {"server": {"full": clean_list[3], "shot": int(clean_list[3].split("id:")[1].replace(")", "").strip())},
                       "provider": {"full": clean_list[4], "shot": clean_list[4].replace('ISP:', '').strip()},
                       "idle_letancy": {"full": clean_list[5], "shot": float(clean_list[5].split(" ms")[0].replace("Idle Latency:", "").strip())},
                       "down_speed": {"full": clean_list[6], "shot": float(clean_list[6].split(" Mbps")[0].replace("Download:", "").strip())},
                       "down_letancy": {"full": clean_list[7], "shot": float(clean_list[7].split(" ms")[0].strip())},
                       "up_speed": {"full": clean_list[8], "shot": float(clean_list[8].split(" Mbps")[0].replace("Upload: ", "").strip())},
                       "up_letancy": {"full": clean_list[9], "shot": float(clean_list[9].split(" ms")[0].strip())},
                       "packet_loss": {"full": clean_list[10], "shot": clean_list[10].replace(" Packet Loss: ", "").replace("%", "").strip()}}

        index_row = len(result_frame)

        result_frame.loc[index_row, "test_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for param, vol in result_dict.items():
            for type_result, result in vol.items():
                name_result = f"{param}_{type_result}"
                result_frame.loc[index_row, name_result] = result

    result_frame.to_csv("speedtest_result.csv", encoding="UTF-8", sep=";")


class SurfWindowControl:
    def __init__(self):
        path_to_surf = r"C:\Program Files (x86)\Surfshark\Surfshark.exe"
        test = Application(backend="uia").start(path_to_surf)
        sleep(2)
        app = Application(backend="uia").connect(path="Surfshark.exe")
        self.surf = app["Surfshark"]
        self.surf.set_focus()
        test = self.surf.child_window(auto_id="vpn_page").wait("exists", 30, 2)
        # test_visible = self.surf.child_window(title="Armenia", auto_id="location_armenia", control_type="Button").wait("exists", 20, 10)
        print("элемент появился")
        self.check_popup_another_vpn()
        # self.country_list = []
        # self.result_country = []

    def check_popup_another_vpn(self):
        try:
            close_click = self.surf.child_window(title="Close pop up", auto_id="popup_close_button",
                                                    control_type="Button")
            close_click.click_input()
            print(close_click)
        except ElementNotFoundError:
            return False
        return True

    def get_country_list(self):
        country_tree_list = self.surf.child_window(title="Armenia", auto_id="location_armenia", control_type="Button").parent().parent().texts()
        country_list = []
        for country_row in country_tree_list:
            country = country_row[0]
            country_list.append(country)
        self.country_list = country_list
        return country_list

    def connect_to_country(self, country):
        select_country = self.surf.child_window(title=country, control_type="Button")
        select_country.wrapper_object().click_input()
        try:
            self.surf.child_window(title="Disconnect", auto_id="connect_button", control_type="Button").wait("exists", 10, 1)
            print("Успешно подключился к стране")
        except timings.TimeoutError:
            print("коннект не удался")

        select_details = self.surf.child_window(title="Home info", auto_id="homeinfo_connectionlabel", control_type="Button")
        select_details.wrapper_object().click_input()

        ip_button = self.surf.child_window(auto_id="homeinfo_ipaddress_button", control_type="Button").wait("exists", 10, 1)
        ip_button.click_input()

        ip_details = self.surf.child_window(title="Real:", control_type="Text").wait("exists", 10, 1)
        current_ip = ip_details.parent().children()[10].texts()[0]
        print("Текущий IP:", current_ip)
        return current_ip

    def disconnect_country(self):
        self.surf.child_window(title="Back", auto_id="BackButton", control_type="Button").wrapper_object().click_input()
        disconnect_button = self.surf.child_window(title="Disconnect", auto_id="connect_button", control_type="Button").wait("exists", 10, 1)
        disconnect_button.click_input()
        print("Отключился от страны")

    def get_test(self):
        self.get_country_list()
        self.connect_to_country(self.country_list[0])


SurfWindowControl()

# run_speedtest(r"C:\PYTHON\my_parsing_common\speedtest_result.csv")


