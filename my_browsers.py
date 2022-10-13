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
from os import path
import pandas as pd
import random
from typing import Optional


class Chrome:
    # Определяет браузер в классе
    def __init__(self, id_browser,):
        self.browser: webdriver.Chrome = None
        self.path_to_dir = path.dirname(__file__)  # Путь к текущей папке
        self.id_browser = id_browser
        self.page_counter = 0
        self.error_counter = 0
        self.random_delimiter = random.randrange(1, 10)

    # Запускает Хром
    def start_chrome(self, header=True):  # Принимает номер профиля, по умолчанию 0)
        sleep(self.id_browser*5)
        ser = Service(executable_path=path.join(self.path_to_dir, 'browsers\\chromedriver.exe'))  # путь к chromedriver
        op = webdriver.ChromeOptions()  # опции для не разлоченного селениума
        if header:
            op.add_argument('--headless')  # Параметр запуска безголового режима
        op.binary_location = path.join(self.path_to_dir, 'browsers\\chrome\\Chrome 105.0.5195.127\\chrome.exe')  # Путь к старой версии хрома
        op.add_argument(
            f"--user-data-dir=D:\\DISTRIB_LOCAL\\PARSING\\CHROME\\FAKE_USER_DATA_{str(self.id_browser)}")  # Путь к папке с профилями
        op.add_argument("--profile-directory=default")  # Загружает нужный профиль
        op.add_argument(
            'log-level=3')  # Отображает только критические ошибки в логе, вылазили некритичные ошибки в VC code
        op.add_argument("--disable-blink-features=AutomationControlled")  # Убирает данные что хром в авто режиме
        op.add_argument("--ignore-certificate-error")
        op.add_argument("--ignore-ssl-errors")

        fake_user_agent = generate_user_agent(device_type="desktop", navigator='chrome')  # генерит рандомного юзер агента
        op.add_argument(f"user-agent={fake_user_agent}")  # устанавливает фиктивный юзер агент
        # op.add_argument("--disable-notifications") # Отключает уведомления, включение этой функции даёт не прохождение проверки на intoli.com

        op.add_experimental_option("excludeSwitches", ["enable-automation"])  # Убирает данные что хром в авто режиме
        op.add_experimental_option("useAutomationExtension", False)  # Убирает данные что хром в авто режиме
        self.browser = webdriver.Chrome(service=ser, options=op)  # Запускает селениум
        self.browser.set_page_load_timeout(60)  # Максимальное время ожидания загрузки страницы.
        return self

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
        self.browser.get('chrome://settings/clearBrowserData')  # Открывает настройки
        sleep(3)
        actions = ActionChains(self.browser)  # Определяет начала действия
        sleep(2)
        actions.send_keys(Keys.TAB * 7 + Keys.ENTER)  # Переключается на кнопку "выполнить сброс"
        sleep(2)
        actions.perform()  # Подтверждает сброс
        sleep(2)

    # Открывает новую вкладку и определяет её ID
    def new_tab(self, tab_number):  # Функция запускающая новое окно и возвращающая его ID
        self.browser.execute_script(f'''window.open("", "_blank");''')  # Запускает новое пустое окно
        sleep(1)
        self.browser.switch_to.window(self.browser.window_handles[tab_number])  # переключается на новое окно
        sleep(1)
        tab_id = self.browser.current_window_handle  # Определяет ID нового окна
        return tab_id  # Возвращает ID окна

    # Проверяет страница на ошибки возвращает содержимое
    def simple_check(self, link, verif_note, reset_counter=100):
        def remove_track():
            self.error_counter += 1
            if self.error_counter == 5:
                print("ID:", self.id_browser, "link:", link, ", cтр:", self.page_counter,
                      "больше 5 ошибок, меняю лицо")
                sleep(1)
                self.clear_cache()
                sleep(1)
                self.change_fake_agent()
                sleep(1)
                self.error_counter = 0
            self.simple_check(link, reset_counter)

        max_page = reset_counter-self.random_delimiter
        try:
            self.browser.get(link)
        except TimeoutException:
            print("ID:", self.id_browser, "link:", link, ", cтр:", self.page_counter, "ошибка времени загрузки страницы, повторяю")
            remove_track()

        except WebDriverException as err:
            print("ID:", self.id_browser, "link:", link, ", cтр:", self.page_counter, "ошибка драйвера", err)
            remove_track()
        finally:
            sleep(1)

        try:
            self.browser.find_element(By.CSS_SELECTOR, verif_note)
            sleep(1)
        except NoSuchElementException:
            print("ID:", self.id_browser, "link:", link, ", cтр:", self.page_counter, "нет_контрольной_надписи")
            remove_track()

        self.page_counter += 1
        self.error_counter = 0
        source_page = self.browser.page_source
        if self.page_counter % max_page == 0 and self.page_counter != 0:
            print("ID:", self.id_browser, "link:", link,  ", стр:", self.page_counter, ", меняю агента")
            self.clear_cache()
            sleep(1)
            self.change_fake_agent()
            sleep(1)
        return source_page

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



