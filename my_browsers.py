import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from user_agent import generate_user_agent
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidSessionIdException
from os import path
from my_parsing_common import my_help_func as mhf
import shutil
import pandas as pd
import random
from typing import Optional
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Literal
import json
from datetime import datetime


class Chrome:
    # Определяет браузер в классе
    Chrome_locations = Literal[r"D:", r"browsers\chrome"]

    def __init__(self, id_browser=None, path_to_profiles = r"D:\DISTRIB_LOCAL\PARSING\\CHROME"):
        self.browser: webdriver.Chrome = None
        self.path_to_dir = path.dirname(__file__)  # Путь к текущей папке
        self.id_browser = id_browser
        self.page_counter = 0
        self.error_counter = 0
        self.random_delimiter = random.randrange(1, 30)
        self.path_to_profile = fr"{path_to_profiles}\FAKE_USER_DATA_{str(self.id_browser)}"
        self.path_to_dir_profiles = path_to_profiles
        self.sample_profile = r"my_parsing_common\browsers\chrome\112.0.5615.50\optim_user"
        self.sample_profile_no_optimize = r"my_parsing_common\browsers\chrome\112.0.5615.50\optim_user_with_picture"
        self.header = None
        self.limited_load = False

    # Запускает Хром
    def start_chrome(self, header=True, control_window=True, path_brow_folder: Chrome_locations = r"D:",
                     resolution='2560,1440', limited_load=False, javascript=True):  # Принимает номер профиля, по умолчанию 0)
        sleep(self.id_browser*2)
        ser = Service(executable_path=path.join(self.path_to_dir, fr"{path_brow_folder}\112.0.5615.50\chromedriver_112.0.5615.50.exe"))  # путь к chromedriver
        op = webdriver.ChromeOptions()  # опции для не разлоченного селениума
        self.header = False if control_window is True and self.id_browser == 0 else header
        if self.header:
            op.add_argument('--headless')  # Параметр запуска безголового режима
            op.add_argument(f"--window-size={resolution}")  # Задаёт разрешение экрана
        if limited_load:
            self.limited_load = limited_load
            op.set_capability('pageLoadStrategy', 'none')  # Ждать ли полной загрузки страницы
        if javascript is False:
            op.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})

        op.binary_location = path.join(self.path_to_dir, fr"{path_brow_folder}\112.0.5615.50\Chrome 112.0.5615.50\chrome.exe")  # Путь к старой версии хрома
        op.add_argument(
            fr"--user-data-dir={self.path_to_profile}")  # Путь к папке с профилями
        op.add_argument("--profile-directory=default")  # Загружает нужный профиль
        op.add_argument(
            '--log-level=3')  # Отображает только критические ошибки в логе, вылазили некритичные ошибки в VC code
        op.add_argument("--disable-blink-features=AutomationControlled")  # Убирает данные что хром в авто режиме
        op.add_argument("--ignore-certificate-errors-spki-list")
        op.add_argument("--ignore-ssl-errors")
        op.add_argument("--disk-cache-size=0")

        fake_user_agent = generate_user_agent(device_type="desktop", navigator='chrome')  # генерит рандомного юзер агента
        op.add_argument(f"user-agent={fake_user_agent}")  # устанавливает фиктивный юзер агент
        # op.add_argument("--disable-notifications") # Отключает уведомления, включение этой функции даёт не прохождение проверки на intoli.com
        op.add_experimental_option("excludeSwitches", ["enable-automation"])  # Убирает данные что хром в авто режиме
        op.add_experimental_option("useAutomationExtension", False)  # Убирает данные что хром в авто режиме

        self.browser = webdriver.Chrome(service=ser, options=op)  # Запускает селениум
        self.browser.set_page_load_timeout(60)  # Максимальное время ожидания загрузки страницы.
        return self

    def wait_it(self, what_wait: str, where_wait=None, how_long: int = 10, by_what=By.XPATH):
        if where_wait is None:
            where_wait = self.browser
        wait_result = WebDriverWait(where_wait, how_long).until(EC.presence_of_element_located((by_what, what_wait)))
        return wait_result

    # Возвращает информацию от текущем юзер агенте
    def info_user_agent(self):
        agent_info = self.browser.execute_script("return navigator.userAgent")  # Возвращает данные от текущем юзер агенте
        return agent_info

    # Устанавливает рандомный юзер агент
    def change_fake_agent(self):
        fake_user_agent = generate_user_agent(device_type="desktop", navigator='chrome')  # Создаёт фиктивного рандомного юзер агента
        sleep(1)
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": f'{fake_user_agent}'})  # Заносит юзер агента в систему
        sleep(1)
        agent_info = self.info_user_agent()  # сохраняет данные о полученном юзер агенте
        return agent_info

    # Устанавливает указанного юзер агента, как правило, сохранённого стандартного
    def change_manual_agent(self, agent):
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride',
                                     {"userAgent": f'{agent}'})  # Устанавливает мануального юзер агента
        sleep(1)
        agent_info = self.info_user_agent()  # Сохраняет полученного юзер агента
        return agent_info

    # переключается на окно с настройками и удаляет кэш
    def clear_cache(self):
        def clear_from_interface():  # Сбрасывает куки через интерфейс
            self.browser.get('chrome://settings/clearBrowserData')  # Открывает настройки
            sleep(3)
            actions = ActionChains(self.browser)  # Определяет начала действия
            sleep(2)
            actions.send_keys(Keys.TAB * 1 + Keys.ENTER)  # Переключается на кнопку "выполнить сброс"
            sleep(2)
            actions.perform()  # Подтверждает сброс
            sleep(2)

        if self.header is False :
            clear_from_interface()

        sleep(2)
        self.clear_file_in_cache()
        sleep(2)
        self.browser.delete_all_cookies()
        sleep(2)
        # self.browser.remove_all_credentials()
        # self.browser.remove_virtual_authenticator()

    def clear_file_in_cache(self, path_to_profile=None):  # Сбрасывает кэш и куки удалением файлов
        list_cleaning_folder = [r"\Default\Cache", r"\Default\Code Cache"]
        if path_to_profile is None:
            path_to_profile = self.path_to_profile

        for item in list_cleaning_folder:
            item_path = fr"{path_to_profile}{item}"
            list_files_patches = mhf.path_cheker(item_path)
            for child_item_path in list_files_patches:
                # final_path = fr"{item_path}\{child_item}"
                try:
                    os.remove(child_item_path)
                except PermissionError:
                    pass
                except OSError:
                    pass

    # Открывает новую вкладку и определяет её ID
    def new_tab(self, tab_number):  # Функция запускающая новое окно и возвращающая его ID
        self.browser.execute_script(f'''window.open("", "_blank");''')  # Запускает новое пустое окно
        sleep(1)
        self.browser.switch_to.window(self.browser.window_handles[tab_number])  # переключается на новое окно
        sleep(1)
        tab_id = self.browser.current_window_handle  # Определяет ID нового окна
        return tab_id  # Возвращает ID окна

    def get_limited_load(self, expected_xpath, load_link: bool = False, link=None):
        w = WebDriverWait(self.browser, 15)
        if load_link:
            self.browser.get(link)
        test = w.until(EC.presence_of_element_located((By.XPATH, expected_xpath)))
        self.browser.execute_script("window.stop();")
        print(self.id_browser, test)

        # if self.browser.find_element(By.XPATH, expected_xpath) is None:
        #     self.browser.refresh()
        #     self.get_limited_load(expected_xpath, load_link, link)

    # Проверяет страница на ошибки возвращает содержимое
    def simple_check(self, link, verif_note, sleep_time=3, mass_error_sleep_time=300, reset_counter=60,
                     verif_by_what=By.CSS_SELECTOR, check_current_url=False, errors_before_stop=0):
        def remove_track():
            self.error_counter += 1
            if self.error_counter == 5:
                print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter,
                      f"больше 5 ошибок, сплю {mass_error_sleep_time} секунд, потом меняю лицо")
                sleep(mass_error_sleep_time)
                self.clear_cache()
                sleep(1)
                self.change_fake_agent()
                sleep(1)
                self.error_counter = 0
            source = self.simple_check(link=link,
                                       verif_note=verif_note,
                                       sleep_time=sleep_time,
                                       mass_error_sleep_time=mass_error_sleep_time,
                                       reset_counter=reset_counter,
                                       verif_by_what=verif_by_what,
                                       check_current_url=False,
                                       errors_before_stop=errors_before_stop)
            print(self.id_browser, link) # Временно
            return source

        def check_verif_note(time_to_sleep):
            try:
                self.browser.find_element(verif_by_what, verif_note)
                sleep(1)
                source = self.browser.page_source
                sleep(time_to_sleep)
            except NoSuchElementException:
                print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter, "нет_контрольной_надписи")
                source = remove_track()
            except TimeoutException as er:
                print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter, "ошибка в момент проверки",
                      er)
                source = remove_track()
            except WebDriverException as er:
                print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter, "ошибка в момент проверки",
                      er)
                source = remove_track()
            return source

        max_page = reset_counter-self.random_delimiter
        if max_page < reset_counter:
            max_page = reset_counter

        if self.error_counter >= errors_before_stop != 0:
            return False

        if self.page_counter % max_page == 0 and self.page_counter != 0:
            print("ID:", self.id_browser, "link:", link,  ", стр:", self.page_counter, ", меняю агента")
            self.clear_cache()
            sleep(1)
            self.change_fake_agent()
            sleep(1)

        try:
            if check_current_url:
                pass
            else:
                if self.limited_load:
                    self.get_limited_load(verif_note, True, link)
                else:
                    self.browser.get(link)
                sleep(1)

            check_verif_note(sleep_time)
            source_page = check_verif_note(1)
            self.page_counter += 1
            self.error_counter = 0

        except TimeoutException:
            print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter, "ошибка времени загрузки страницы, повторяю")
            source_page = remove_track()

        except InvalidSessionIdException:
            print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter, "непонятная ошибка InvalidSession")
            source_page = remove_track()

        except WebDriverException:
            print("ID:", datetime.now(), self.id_browser, "link:", link, ", cтр:", self.page_counter, "ошибка драйвера")
            source_page = remove_track()

        return source_page

    def test_worked_change_agent(self, number_tests):
        url_for_test = "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
        worked_chrome = Chrome(self.id_browser).start_chrome(header=False, control_window=False)
        sleep(2)
        worked_chrome.browser.get(url_for_test)
        sleep(5)
        for test in range(number_tests):
            worked_chrome.clear_cache()
            worked_chrome.change_fake_agent()
            sleep(1)
            print(worked_chrome.info_user_agent())
            worked_chrome.browser.get(url_for_test)
            sleep(5)

    # Управляет профилями, создаёт или удаляет папки.
    def profile_manager(self, cloning_numbers: int, not_optimize_user=False):
        def clear_cache():
            for number in range(cloning_numbers):
                name = f"FAKE_USER_DATA_{number}"
                new_path = os.path.join(self.path_to_dir_profiles, name)
                self.clear_file_in_cache(new_path)
                print("профиль", name, "кэш очищен")

        def create_new_profiles():
            print("создаю", cloning_numbers, "профилей")
            for number in range(cloning_numbers):
                name = f"FAKE_USER_DATA_{number}"
                new_path = os.path.join(self.path_to_dir_profiles, name)
                if os.path.exists(new_path) is False:
                    path_sample = self.sample_profile_no_optimize if not_optimize_user else self.sample_profile
                    shutil.copytree(path_sample, new_path, dirs_exist_ok=True)
                    change_user_name(new_path, number)
                    print("профиль", name, "создан")

        def delete_profiles():
            numbers_too_delete = count_prof_exist - cloning_numbers
            print("профили уже были созданы, удаляю", numbers_too_delete, "лишних")
            for number in range(1, numbers_too_delete + 1):
                final_number = count_prof_exist - number
                name = f"FAKE_USER_DATA_{final_number}"
                path_to_delete = os.path.join(self.path_to_dir_profiles, name)
                shutil.rmtree(path_to_delete, ignore_errors=True)
                print(final_number, "удалён")

        def change_user_name(path_to_user_data, number_user):
            path_to_pref_list = [r"\Default\Preferences", r"\Local State"]
            for path_to_pref in path_to_pref_list:
                full_path = fr"{path_to_user_data}\{path_to_pref}"
                new_name = f"USER_{number_user}"
                with open(full_path, 'r', encoding="UTF-8") as preference:
                    pref_json = json.load(preference)
                if path_to_pref == path_to_pref_list[0]:
                    pref_json["profile"]["name"] = str(new_name)
                elif path_to_pref == path_to_pref_list[1]:
                    pref_json["profile"]["info_cache"]["default"]["name"] = new_name
                with open(full_path, 'w', encoding="UTF-8") as preference:
                    json.dump(pref_json, preference)

        list_items = os.listdir(self.path_to_dir_profiles)

        profiles_exist = []
        for item in list_items:
            path_to_item = os.path.join(self.path_to_dir_profiles, item)
            if os.path.isdir(path_to_item):
                profiles_exist.append(path_to_item)

        count_prof_exist = len(profiles_exist)

        if count_prof_exist < cloning_numbers:
            create_new_profiles()

        elif count_prof_exist > cloning_numbers:
            delete_profiles()

        clear_cache()

        return cloning_numbers

    # def parsing_list_with_surf(self, links_list, key_func):
    #     number_pages = 0
    #     successful_page = 0
    #     result_frame = pd.DataFrame()
    #     for link in links_list:  # В списке ссылок берёт ссылку и список номеров страниц
    #         number_pages += 1
    #         if number_pages != 0 and number_pages % 30 == 0:  # Для недопущения блокировки сурфом, спит с заданной периодичностью.
    #             sleep_time = 600  # сплю 10 минут
    #             print(f"ID:{self.id_browser} промежуточный лимит: {number_pages} сплю {sleep_time}")
    #             sleep(sleep_time)
    #         else:
    #             sleep(random.randrange(0, 2))  # Время ожидания между подходами
    #
    #         self.work_surf.connect_error_detect(link, status=None, successful_pages=successful_page,
    #                                             max_page=130)  # Проверяет прошла ли проверка на успешность загрузки по многим параметрам
    #         part_frame = key_func(self.browser, link)  # Выгружает список объявлений
    #         result_frame = pd.concat([result_frame, part_frame])
    #     return result_frame



