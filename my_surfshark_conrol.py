from pywinauto import Desktop, Application, timings, application
from pywinauto import findwindows, ElementNotFoundError
from pywinauto.timings import always_wait_until_passes
from time import sleep
import subprocess
import pandas as pd
from datetime import datetime
from adrenaline import prevent_sleep
import my_help_func
from my_browsers import Chrome
from selenium.webdriver.common.by import By


def test_speedtest(path_result):
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
        result_dict = {
            "server": {"full": clean_list[3], "shot": int(clean_list[3].split("id:")[1].replace(")", "").strip())},
            "provider": {"full": clean_list[4], "shot": clean_list[4].replace('ISP:', '').strip()},
            "idle_letancy": {"full": clean_list[5],
                             "shot": float(clean_list[5].split(" ms")[0].replace("Idle Latency:", "").strip())},
            "down_speed": {"full": clean_list[6],
                           "shot": float(clean_list[6].split(" Mbps")[0].replace("Download:", "").strip())},
            "down_letancy": {"full": clean_list[7], "shot": float(clean_list[7].split(" ms")[0].strip())},
            "up_speed": {"full": clean_list[8],
                         "shot": float(clean_list[8].split(" Mbps")[0].replace("Upload: ", "").strip())},
            "up_letancy": {"full": clean_list[9], "shot": float(clean_list[9].split(" ms")[0].strip())},
            "packet_loss": {"full": clean_list[10],
                            "shot": clean_list[10].replace(" Packet Loss: ", "").replace("%", "").strip()}}

        index_row = len(result_frame)

        result_frame.loc[index_row, "test_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for param, vol in result_dict.items():
            for type_result, result in vol.items():
                name_result = f"{param}_{type_result}"
                result_frame.loc[index_row, name_result] = result

    result_frame.to_csv("speedtest_result.csv", encoding="UTF-8", sep=";")


class SurfWindowControl:
    def __init__(self):
        self.path_to_surf = r"C:\Program Files (x86)\Surfshark\Surfshark.exe"
        self.path_to_log_ip = r""
        self.surf: application.WindowSpecification = None
        self.country_name_list = []
        self.log_ip = {}
        self.path_to_result = None
        self.path_to_browser_optim_user = r"\browsers\chrome\112.0.5615.50\optim_user"
        self.opened_browser: Chrome = None
        self.country_tree_objects = None

    def __get_interface(self):
        """Запускает сурф, выводит интерфейс на передний план"""
        Application().start(self.path_to_surf)
        sleep(2)
        app = Application(backend="uia").connect(path="Surfshark.exe")
        self.surf = app["Surfshark"]
        self.surf.set_focus()
        self.surf.child_window(auto_id="vpn_page").wait("exists", 30, 2)
        print("Интерфейс сурфа выведен и готов")
        self.__check_popup_another_vpn()
        return self.surf

    def __check_popup_another_vpn(self):
        """Проверяет наличие вслывающего окна о другом впн, закрывает окно"""
        try:
            close_click = self.surf.child_window(title="Close pop up", auto_id="popup_close_button",
                                                 control_type="Button")
            close_click.click_input()
            print("Выведено предупреждение о другом впн, закрываю")
        except ElementNotFoundError:
            return False
        return True

    def __cancel_incomplete_connection(self):
        self.surf.child_window(title="Cancel connecting", auto_id="connect_button", control_type="Button").click_input()
        try:
            close_click = self.surf.child_window(title="Cancel connection", auto_id="popup_secondary_button",
                                                 control_type="Button").wait("exists", 10, 1)
            close_click.click_input()
            print("Выведено окно о продлении времени")
        except ElementNotFoundError:
            return False
        return True

    def __close_surf(self):
        self.surf.child_window(title="Close application", control_type="Button").click_input()

    def __get_country_list(self):
        """Получает список стран из списка"""
        self.country_tree_objects = self.surf.child_window(title="Armenia", auto_id="location_armenia",
                                                   control_type="Button").parent().parent()
        country_name_list = []
        for country_row in self.country_tree_objects.texts():
            country = country_row[0]
            self.country_name_list.append(country)
        print(self.country_name_list)

        return self.country_name_list

    def __check_ip(self):
        """Проверяет номер ip адреса на внутренней старнице"""
        ip_details = self.surf.child_window(title="Real:", control_type="Text").wait("exists", 10, 1)
        current_ip = ip_details.parent().children()[10].texts()[0]
        print("Текущий IP:", current_ip)
        return current_ip

    def __connect_to_country(self, country):
        """Коннектится у казанной стране"""
        select_country = self.country_tree_objects.get_item(country).set_focus()
        # select_country = self.surf.child_window(title="Poland Gdansk", auto_id="location_poland_gdansk", control_type="Button").set_focus()
        print("Подключаюсь к", country)
        select_country.click_input()
        self.__check_popup_another_vpn()
        try:
            self.surf.child_window(title="Disconnect", auto_id="connect_button", control_type="Button").wait("exists",
                                                                                                             10, 1)
            print("Успешно подключился к", country)
        except timings.TimeoutError:
            print("коннект к", country, "не удался")
            self.__cancel_incomplete_connection()
            return False

        select_details = self.surf.child_window(title="Home info", auto_id="homeinfo_connectionlabel",
                                                control_type="Button")
        select_details.wrapper_object().click_input()

        ip_button = self.surf.child_window(auto_id="homeinfo_ipaddress_button", control_type="Button").wait("exists",
                                                                                                            10, 1)
        print(ip_button)
        ip_button.click_input()

        return True

    def disconnect_country(self):
        """Разрывает соединение"""
        self.surf.child_window(title="Back", auto_id="BackButton", control_type="Button").wrapper_object().click_input()
        disconnect_button = self.surf.child_window(title="Disconnect", auto_id="connect_button",
                                                   control_type="Button").wait("exists", 10, 1)
        disconnect_button.click_input()
        print("Отключился от страны")

    def start_browser(self):
        print("Запускаю браузер")
        my_help_func.profile_manager(1, r"browsers\chrome\112.0.5615.50\optim_user",
                                     cloning_path=r"D:\DISTRIB_LOCAL\PARSING\CHROME")
        self.opened_browser = Chrome(0, path_to_profiles=r"D:\DISTRIB_LOCAL\PARSING\\CHROME").start_chrome()

    def check_popular_pages(self):
        def check_ip_on_2ip():
            if brow.find_element(By.CSS_SELECTOR, "a.notice__container__ok"):
                brow.find_element(By.CSS_SELECTOR, "a.notice__container__ok").click()
                sleep(2)

            trash_list = ["Уточнить?","Исправить?","\n"]
            result_series = pd.Series()

            table_details = brow.find_element(By.CLASS_NAME, "data_table")
            list_elements = table_details.find_elements(By.CLASS_NAME, "data_item")
            for element in list_elements:
                element = element.text
                for word in trash_list:
                    element = element.replace(word, "")
                element_params = element.split(":")
                result_series[element_params[0].strip()] = element_params[1].strip()

            print(result_series)
            input("жду")

        dict_checked = {"https://2ip.ru/": "div.page-wrapper",
                        "https://www.drom.ru/": "div.css-184qm5b",
                        "https://www.avito.ru/": "div.index-navigation-gCayT",
                        "https://www.farpost.ru/": "td.col_logo.js-show-additional-navigation",
                        "https://auto.ru/": "div.Header__logo",
                        "https://www.wildberries.ru/": "div.header__nav-element.nav-element",
                        "https://www.ozon.ru/": "div.ed6"}
        result_columns = ["link", "pass_number", "load_status", "load_correctness", "load_speed"]
        frame_site_result = pd.DataFrame(columns = result_columns)
        brow = self.opened_browser.browser
        number_tests_on_page = 1
        for link, check_row in dict_checked.items():
            for pass_number in range(number_tests_on_page):
                number_row = len(frame_site_result)
                try:
                    brow.get(link)
                    load_status = "ok"
                    sleep(3)
                except Exception as error:
                    load_status = error

                try:
                    brow.find_element(By.CSS_SELECTOR, check_row)
                    load_correctness = "ok"
                except Exception as error:
                    print(error)
                    input("вылезла ошибка, проверь и нажми на кнопку")
                    load_correctness = error

                load_speed = brow.execute_script(
                    "return ( window.performance.timing.loadEventEnd - window.performance.timing.navigationStart )")

                if link == "https://2ip.ru/" and load_correctness == "ok":
                    print("Запускаю тест")
                    check_ip_on_2ip()

                collation_dict = {"link": link, "pass_number": pass_number, "load_status": load_status,
                                  "load_correctness": load_correctness, "load_speed": load_speed}

                for column, mean in collation_dict.items():
                    frame_site_result.loc[number_row, column] = mean

                sleep(2)

        return frame_site_result

    def get_test(self):
        self.start_browser()
        self.__get_interface()
        self.__get_country_list()
        path_to_save = r"C:\PYTHON\my_parsing_common\data\country_tests\result_tests.csv"

        sleep_time = 330
        results_frame = pd.DataFrame()
        country_to_connect = None

        for country in self.country_name_list:
            connect_status = False
            while connect_status is False:
                connect_status = self.__connect_to_country(country)

            ip_address = self.__check_ip()
            sleep(1)
            sites_result = self.check_popular_pages()
            sites_result.loc[:, "country"] = country
            sites_result.loc[:, "ip_addres"] = ip_address
            results_frame = pd.concat([results_frame, sites_result])
            results_frame.to_csv(path_to_save, encoding="UTF-8", sep=";")
            sleep(1)
            self.disconnect_country()
            sleep(5)


if __name__ == "__main__":
    with prevent_sleep():
        SurfWindowControl().get_test()

# run_speedtest(r"C:\PYTHON\my_parsing_common\speedtest_result.csv")
