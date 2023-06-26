import os

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
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
from numpy import array_split
from random import randrange, shuffle


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
    def __init__(self, path_save_dir=None):
        self.path_to_surf = r"C:\Program Files (x86)\Surfshark\Surfshark.exe"
        self.path_to_log_ip = r""
        self.surf: application.WindowSpecification = None
        self.country_name_list = []
        self.log_ip = {}
        self.path_to_result = None
        self.path_to_browser_optim_user = r"browsers\chrome\112.0.5615.50\optim_user"
        self.opened_browser: Chrome = None
        self.country_tree_objects = None
        self.vmachine_id = None
        self.number_vmachines = None
        self.path_to_split_country = fr"data\country_split\country_split_vmashines.csv"
        self.path_to_dir_test_result = r"data\country_tests"

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

    def __check_popup_background_process(self):
        try:
            got_it_button = self.surf.child_window(title="Got it", auto_id="popup_primary_button", control_type="Button")
            got_it_button.click_input()
            print("выведено сообщение о работе в фоне")
        except ElementNotFoundError:
            return False
        return True

    def __cancel_incomplete_connection(self):
        try:
            self.surf.child_window(title="Cancel connecting", auto_id="connect_button", control_type="Button").click_input()
        except ElementNotFoundError:
            return False
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
        sleep(1)
        self.__check_popup_background_process()

    def reload_surf_interface(self):
        print("В интерфейсе сурфа есть мусор, перезагружаю")
        self.__close_surf()
        sleep(5)
        self.__get_interface()
        self.__get_country_list()

    def __get_country_list(self):
        """Получает список стран из списка"""
        self.country_tree_objects = self.surf.child_window(title="Armenia", auto_id="location_armenia",
                                                           control_type="Button").parent().parent()
        country_name_list = []

        for country_row in self.country_tree_objects.texts():
            country = country_row[0]
            if country == "{DisconnectedItem}":
                self.reload_surf_interface()
                break
            country_name_list.append(country)
        self.country_name_list = country_name_list

        return self.country_name_list

    def __split_country_by_vmachines(self, number_vmachines, mode):
        """mode = supplement - перераспределяет не проверенные страны по виртуальным машинам
           mode = new - начинает проверку стран с начала"""
        def split_not_ready_country():
            shuffle(self.country_name_list)
            divided_countries = list(array_split(self.country_name_list, self.number_vmachines))
            country_frame = pd.DataFrame(columns=["country", "vm_id", "result"])
            counter = 0
            for list_country in divided_countries:
                for county in list_country:
                    number_row = len(country_frame)
                    country_frame.loc[number_row, "country"] = county
                    country_frame.loc[number_row, "vm_id"] = counter
                counter += 1
            return country_frame

        def check_country_old_status():
            country_old_frame = pd.read_csv(self.path_to_split_country, sep=";", encoding="UTF-8", dtype=str)
            ready_country_frame = country_old_frame[country_old_frame["result"] == "ok"]
            ready_country_frame.loc[:, "vm_id"] = None
            not_ready_country_frame = country_old_frame[country_old_frame["result"] != "ok"]
            self.country_name_list = list(not_ready_country_frame["country"])
            not_ready_country_frame = split_not_ready_country()
            result_frame = pd.concat([ready_country_frame, not_ready_country_frame])
            return result_frame

        self.number_vmachines = number_vmachines

        if mode == "supplement":
            country_spliter_on_vm = check_country_old_status()
        elif mode == "new":
            country_spliter_on_vm = split_not_ready_country()
        else:
            raise "Не ввел тип"

        country_spliter_on_vm.to_csv(self.path_to_split_country, encoding="UTF-8", sep=";", index=False)
        return country_spliter_on_vm

    def __check_ip(self):
        """Проверяет номер ip адреса на внутренней старнице"""
        ip_details = self.surf.child_window(title="Real:", control_type="Text").wait("exists", 10, 1)
        current_ip = ip_details.parent().children()[10].texts()[0]
        print("Текущий IP:", current_ip)
        return current_ip

    def __connect_to_country(self, country, max_sleep_time=30):
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

        sleep_time = randrange(0, max_sleep_time)
        print("Переключусь на ip через", sleep_time, "секунд")
        sleep(sleep_time)

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
                                                   control_type="Button").wait("exists", 10, 2)
        disconnect_button.click_input()
        print("Отключился от страны")

    def start_browser(self):
        print("Запускаю браузер")
        my_help_func.profile_manager(1, self.path_to_browser_optim_user)
        self.opened_browser = Chrome(0).start_chrome(path_brow_folder=r"D:")

    def check_popular_pages(self):
        def check_ip_on_2ip():
            try:
                cookie_popup = brow.find_element(By.CSS_SELECTOR, "a.notice__container__ok")
                cookie_popup.click()
                sleep(2)
            except NoSuchElementException:
                pass

            trash_list = ["Уточнить?", "Исправить?", "\n"]
            result_dict = {}

            table_details = brow.find_element(By.CLASS_NAME, "data_table")
            list_elements = table_details.find_elements(By.CLASS_NAME, "data_item")
            for element in list_elements:
                element = element.text
                for word in trash_list:
                    element = element.replace(word, "")
                element_params = element.split(":")
                result_dict.update({element_params[0].strip(): element_params[1].strip()})

            return result_dict

        def confirm_policy_auto_ru():
            try:
                brow.find_element(By.CSS_SELECTOR, "#confirm-button").click()
            except NoSuchElementException:
                pass
            sleep(2)

        def frame_update(target_dict, target_frame):
            for column, mean in target_dict.items():
                target_frame.loc[number_row, column] = mean

        self.opened_browser.change_fake_agent()
        self.opened_browser.clear_cache()

        sleep(2)

        dict_checked = {"https://2ip.ru/": "div.page-wrapper",
                        "https://www.drom.ru/": "div.css-184qm5b",
                        "https://www.avito.ru/": "div.index-navigation-gCayT",
                        "https://www.farpost.ru/": "td.col_logo.js-show-additional-navigation",
                        "https://auto.ru/": "div.Header__logo",
                        "https://www.wildberries.ru/": "div.header__nav-element.nav-element",
                        "https://www.ozon.ru/": "div.ed6"}
        result_columns = ["link", "pass_number", "load_status", "load_correctness", "load_speed"]
        frame_site_result = pd.DataFrame(columns=result_columns)
        frame_ip_result = pd.DataFrame(columns=result_columns)
        brow = self.opened_browser.browser
        number_tests_on_page = 1
        for link, check_row in dict_checked.items():
            for pass_number in range(number_tests_on_page):
                number_row = len(frame_site_result)
                time_test = datetime.now().strftime("%Y_%m_%d %H:%M")
                link_info_dict = {"link": link, "pass_number": pass_number, "time_test": time_test}
                try:
                    brow.get(link)
                    load_status = "ok"
                    sleep(3)
                except Exception as error:
                    print(type(error))
                    load_status = type(error)

                if link == "https://auto.ru/" and load_status == "ok":
                    confirm_policy_auto_ru()

                try:
                    brow.find_element(By.CSS_SELECTOR, check_row)
                    load_correctness = "ok"
                except Exception as error:
                    print(type(error))
                    load_correctness = type(error)

                load_speed = brow.execute_script(
                    "return ( window.performance.timing.loadEventEnd - window.performance.timing.navigationStart )")

                link_info_dict.update({"load_status": load_status,
                                       "load_correctness": load_correctness, "load_speed": load_speed})

                if link == "https://2ip.ru/":
                    ip_info_dict = link_info_dict.copy()
                    if load_correctness == "ok":
                        print("Запускаю тест")
                        ip_info_dict.update(check_ip_on_2ip())
                    frame_update(ip_info_dict, frame_ip_result)

                frame_update(link_info_dict, frame_site_result)
                sleep(2)

        return {"site_result": frame_site_result, "ip_detail": frame_ip_result}

    def get_preparing_on_real_machine(self, number_vmachines, mode="supplement"):

        self.__get_interface()
        self.__get_country_list()
        self.__split_country_by_vmachines(number_vmachines, mode=mode)

        now_time = datetime.now().strftime("%Y_%m_%d_%H_%M")
        mather_path = fr"{self.path_to_dir_test_result}\{now_time}"
        os.mkdir(mather_path)
        os.mkdir(fr"{mather_path}\ip_info")
        os.mkdir(fr"{mather_path}\web_test")

    def get_test_in_vm(self, id_vmachine):

        def update_result_frame(small_frame, big_frame):
            total_time = (datetime.now() - start_time).total_seconds()
            small_frame.loc[:, "country"] = country
            small_frame.loc[:, "ip_addres"] = ip_address
            small_frame.loc[:, "total_test_time"] = total_time
            big_frame = pd.concat([big_frame, small_frame])
            return big_frame

        self.start_browser()
        self.__get_interface()
        self.__get_country_list()

        id_vmachine = str(id_vmachine)
        list_country = pd.read_csv(self.path_to_split_country, encoding="UTF-8", sep=";", dtype=str)
        print(list_country)
        list_country = list_country[list_country["vm_id"] == id_vmachine]
        start_test_time = datetime.now().strftime("%Y_%m_%d_%H_%M")
        last_folder = my_help_func.sorted_files_by_date(self.path_to_dir_test_result)[-1]
        path_to_save_web_test = fr"{last_folder}\web_test\web_test_{id_vmachine}_{start_test_time}.csv"
        path_to_save_ip_info = fr"{last_folder}\ip_info\ip_info_{id_vmachine}_{start_test_time}.csv"
        site_detail_frame = pd.DataFrame()
        ip_info_frame = pd.DataFrame()
        number_counter = 3

        for country in list_country["country"]:
            sleep_time = randrange(300, 400)
            connect_status = False
            while connect_status is False:
                self.reload_surf_interface()
                connect_status = self.__connect_to_country(country)

            for counter in range(number_counter):
                if counter != 0:
                    sleep(sleep_time)
                ip_address = self.__check_ip()
                sleep(1)
                start_time = datetime.now()
                sites_result_list = self.check_popular_pages()
                site_detail_frame = update_result_frame(sites_result_list["site_result"], site_detail_frame)
                ip_info_frame = update_result_frame(sites_result_list["ip_detail"], ip_info_frame)
                ip_info_frame.to_csv(path_to_save_ip_info, encoding="UTF-8", sep=";", index=False)
                site_detail_frame.to_csv(path_to_save_web_test, encoding="UTF-8", sep=";", index=False)

            self.disconnect_country()
            sleep(sleep_time)

    def test(self):
        print("Вывожу интерфейс")
        self.__get_interface()
        print("пробую закрыть")
        self.__close_surf()

    def collect_temporary_results(self):
        def collect_result():
            destination_dict = {"ip_info": fr"{last_general_folder}\ip_info", "web_test": fr"{last_general_folder}\web_test"}
            result_frames_dict = {}
            for name, path_destination in destination_dict.items():
                full_path_to_save = fr"{path_save_result}\{name}\{last_date_dir}.csv"
                result_frame = my_help_func.merge_files(path_destination, full_path_to_save)
                result_frames_dict.update({name: result_frame})
            return result_frames_dict

        def analise_speed_connect(web_test_frame: pd.DataFrame):
            web_test_frame["load_speed"] = web_test_frame["load_speed"].astype("int64")
            abnormal_time = web_test_frame[web_test_frame["load_speed"] <= 0].index
            web_test_frame.loc[abnormal_time, "load_speed"] = 100000

            country_group = web_test_frame.groupby(["link", "country"]).agg({"load_speed": "mean",
                                                                             "load_status": list}).reset_index()

            for index, list_status in country_group["load_status"].items():
                total_counter = len(list_status)
                successful_counter = list_status.count("ok")
                country_group.loc[index, "percent_success_connect"] = successful_counter/total_counter

            country_group = country_group.drop(columns=["load_status"])

            return country_group

        def analise_ip_rotation(ip_info_frame: pd.DataFrame):
            ip_info_frame["time_test"] = pd.to_datetime(ip_info_frame["time_test"], format="%Y_%m_%d %H:%M")
            country_group = ip_info_frame.groupby("country").agg({"ip_addres": list, "Имя вашего компьютера": list,
                                                                  "time_test": list}).reset_index()
            ip_analise_frame = pd.DataFrame()
            for index, row in country_group.iterrows():
                count_number_connections = len(row["ip_addres"])
                count_ip_on_surf = len(set(row["ip_addres"]))
                count_ip_on_2ip = len(set(row["Имя вашего компьютера"]))
                start_test = min(row["time_test"])
                end_test = max(row["time_test"])
                duration_test = end_test - start_test
                ip_analise_frame.loc[index, "country"] = row["country"]
                ip_analise_frame.loc[index, "chang_ip_surf_percent"] = count_ip_on_surf/count_number_connections
                ip_analise_frame.loc[index, "chang_ip_2ip_percent"] = count_ip_on_2ip/count_number_connections
                ip_analise_frame.loc[index, "duration_test"] = duration_test.seconds/60

            return ip_analise_frame

        path_save_result = r"data\results"
        last_general_folder = my_help_func.sorted_files_by_date(self.path_to_dir_test_result)[-1]
        last_date_dir = last_general_folder.split("\\")[-1]
        frames_dict = collect_result()
        speed_connect_frame = analise_speed_connect(frames_dict["web_test"])
        ip_rotation_frame = analise_ip_rotation(frames_dict["ip_info"])
        final_result_frame = speed_connect_frame.merge(ip_rotation_frame, "left", "country")
        path_to_save_super_final = fr"{path_save_result}\super_final\{last_date_dir}.csv"
        final_result_frame.to_csv(path_to_save_super_final, sep=";", encoding="UTF-8", index=False, float_format="%.2f")


        # ip_info_path = fr"{last_general_folder}\ip_info"
        # web_test_path = fr"{last_general_folder}\web_test"
        # result_path = fr"{last_general_folder}\results"
        # country_frame = pd.read_csv(self.path_to_split_country, encoding="UTF-8", sep=";", dtype=str,
        #                             index_col="country")
        # result_frame = my_help_func.merge_files(ip_info_path, result_path)
        #
        # for country in result_frame["country"]:
        #     country_frame.loc[country, "result"] = "ok"
        #
        # country_frame.reset_index()
        # country_frame.to_csv(self.path_to_split_country, encoding="UTF-8", sep=";")





if __name__ == "__main__":
    with prevent_sleep():
        # id_vm = input("Введи ID вирт машины")
        # SurfWindowControl().get_preparing_on_real_machine(5, mode="new")
        SurfWindowControl().collect_temporary_results()
        # SurfWindowControl().get_preparing_on_real_machine(5, mode="supplement")
        # sleep(10)
        # SurfWindowControl().get_test_in_vm(id_vm)
