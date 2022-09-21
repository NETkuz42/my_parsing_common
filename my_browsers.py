from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from user_agent import generate_user_agent
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException


class Chrome:

    # Определяет браузер в классе
    def __init__(self, browser=None):
        self.browser = browser
        pass

    # Запускает Хром
    def start_chrome(self, profile=0, header=True):  # Принимает номер профиля, по умолчанию 0)
        ser = Service(executable_path='D:\\ONEDRIVE\\DISTRIB\\chromedriver.exe')
        op = webdriver.ChromeOptions()  # опции для неразлоченного селениума
        if header:
            op.add_argument('--headless')
        op.add_argument(
            f"--user-data-dir=D:\\DISTRIB\\PARSING\\CHROME\\FAKE_USER_DATA_{str(profile)}")  # Путь к папке с профилями
        op.add_argument("--profile-directory=default")  # Загружает нужный профиль
        op.add_argument(
            'log-level=3')  # Отображает только критические ошибки в логе, вылазили некритичные ошибки в VC code
        op.add_argument("--disable-blink-features=AutomationControlled")  # Убирает данные что хром в авто режиме
        op.add_argument("--ignore-certificate-error")
        op.add_argument("--ignore-ssl-errors")

        fake_user_agent = generate_user_agent(device_type="desktop", navigator='chrome')  # генерит рандомного юзер агента
        op.add_argument(f"user-agent={fake_user_agent}")  # устанавливает фиктивный юзер агент
        # op.add_argument("--disable-notifications") # Отключает уведомления, включение этой функции даёт не прохождение проверки на intoli.com

        op.add_experimental_option("excludeSwitches", ["enable-automation"])  # Убирает данные что хром в авторежиме
        op.add_experimental_option("useAutomationExtension", False)  # Убирает данные что хром в авторежиме
        self.browser = webdriver.Chrome(service=ser, options=op)  # Запускает селениум
        self.browser.set_page_load_timeout(60)  # Максимальное время ожидания прогрузки старницы.
        return self.browser

    # Возвращает информацию от текущем юзер агенте
    def info_user_agent(self):
        agent_info = self.browser.execute_script(
            "return navigator.userAgent")  # Возвращает данные от текущем юзер агенте
        return agent_info

    # Устанавливает рандомный юзер агент
    def change_fake_agent(self):
        fake_user_agent = generate_user_agent(device_type="desktop",
                                              navigator='chrome')  # Создаёт фиктивного рандомного юзер агента
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride',
                                     {"userAgent": f'{fake_user_agent}'})  # Заносит юзер агента в систему
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

    # переключается на окно с натройкамии и удаляет кэш
    def clear_cache(self):
        self.browser.get('chrome://settings/clearBrowserData')  # Открывает настройки
        sleep(2)
        actions = ActionChains(self.browser)  # Определяет начала дейсвия
        actions.send_keys(Keys.TAB * 7 + Keys.ENTER)  # Переключается на кнопку "выполнить сброс"
        actions.perform()  # Подтверждает сброк

    # Открывает новую вкладку и определяет её ID
    def new_tab(self, tab_number):  # Функция запускающая новое окнои возвращающая его ID
        self.browser.execute_script(f'''window.open("", "_blank");''')  # Запускает новое пустое окно
        self.browser.switch_to.window(self.browser.window_handles[tab_number])  # переключается на новое окно
        tab_id = self.browser.current_window_handle  # Определяет ID нового окна
        return (tab_id)  # Возвращает ID окна

    # Проверяет страница на ошибки возвращает содержимое
    def check_source(self, work_chrome, link):
        try:
            work_chrome.get(link)
        except TimeoutException:
            print("ошибка времени загрузки страницы, повторяю")
            self.check_source(work_chrome, link)
        except WebDriverException:
            print("непонятная ошибка драйвера, повторяю")
            self.check_source(work_chrome, link)
        finally:
            sleep(1)
        return work_chrome.page_source

#test