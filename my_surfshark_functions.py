from my_parsing_common.my_browsers import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from time import sleep, time
import random
import time
from datetime import datetime


class MySurf:

    def __init__(self, ID, country_explorer=False, connect_method='random_all', lose_sleep_time=900, max_page=10000):
        self.control: Chrome = None
        self.ID = ID
        self.tab_surf_id = None
        self.tab_setting_id = None
        self.real_agent = None
        self.tab_pars_id = None
        self.successful_pages = 0
        self.attempts = 0
        self.face_reset_numbers = 0
        self.min_page = max_page/2+self.ID*10
        self.max_page = max_page
        self.country_explorer = country_explorer  # Диспетчер стран распределяющий их по скорости
        self.lose_sleep_time = lose_sleep_time  # Вреамя сна если вылезла ошибка сурфа или 3 неудачных коннекта
        pass

    # Ждёт пока появится кнопка "Подключено".
    def waiting_ip(self):
        if self.control.browser.find_element(By.XPATH,
                                             '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div[1]/div/div[1]').text == 'ПОДКЛЮЧЕНО':
            sleep(1)
            ip = self.control.browser.find_element(By.CSS_SELECTOR,
                                                   '#root > div > div._27JzB > div:nth-child(2) > div > div._3I6Eb.content-connecting-exit-done > div._3idt3 > div > div._2ozSG > div > div._10EWD').text  # Определяет новый IP адрес
        else:  # Если слова Подключено нет, ждёт 1 секунду и уходит на второй круг.
            sleep(2)
            ip = self.waiting_ip()
        return ip

    # Определяет наличие окна с предупреждением.
    def alert_detect(self):
        handless_list = self.control.browser.window_handles  # Опредлеяет ID всех окон.
        try:
            if len(handless_list) > 3:  # Если количество окон больше трёх, значит вылезло предупреждение
                self.control.browser.switch_to.window(handless_list[-1])  # Переключается на последнее окно
                if self.control.browser.find_element(By.XPATH,
                                                     '//*[@id="root"]/div/div/div[3]/h1').text:  # Если по указному ХПАТХ находит какой либо текст (должен быть такой "Подключиться повторно для сохранения защиты")
                    print("ID", self.ID, "Вылезла блокировка сурфа, cплю", self.lose_sleep_time, "секунд")
                    sleep(self.lose_sleep_time)  # Спит указанное в параметрах время
                    self.control.browser.close()  # Закрывает вкладку
                    sleep(1)
                    self.control.browser.switch_to.window(self.tab_surf_id)  # Переключается на окно с сурфом
                    return True
        except NoSuchElementException:  # Если исключение значит нет, всплывающего окна тоже нет
            pass

    # Функция дожидается успешного коннекта сурфа.
    def chek_connect(self):
        try:
            new_ip = self.waiting_ip()
        except NoSuchElementException:  # Если не может найти элемент выше, значит что то случилось с окном и будем решать:
            sleep(1)  # Ждём 1 секунду
            self.alert_detect()  # Проверяет, открылась ли вкладка с предупрждением, если да, ждёт 5 мнут, закрывает и возвращает фокус.
            self.control.browser.find_element(By.XPATH,
                                              '/html/body/div/div/div[2]/div[1]/button').click()  # Закрывает всплывающее окно
            new_ip = None
        return new_ip  # Возвращает ip

    # Функция подключения сурфа.
    def surf_connect(self, country=None, attempts=0):
        countrys = self.surf_list_country()  # Получается список и словарь стран.
        if country:
            self.country = country  # Если страна есть, принимает страну.
        else:
            self.country = random.choice(countrys[0])  # Если страны нет, коннектится к рандомной стране

        ip = None
        self.attempts = attempts + 1  # Добавляет единицу к счётчику попыток
        if self.attempts % 3 == 0:
            print("ID", self.ID, "3 раза не подключился к стране, сплю", self.lose_sleep_time, "секунд")
            sleep(self.lose_sleep_time)  # При каждой третьей попытке будет ждать указанное в параметрах время
        if self.attempts == 11:
            print("ID", self.ID, "пытался подлючитья к старне 10 раз, возвращаю бэд ip")
            ip = "fail"  # Если попыток больше 10 возвращает бэд IP
        if self.country not in countrys[
            0]:  # Проверяет наличие страны в списке сурфа, если отсутсвует возвращает бэд IP.
            print("ID", self.ID, "страна", self.country, "отсутвет в сурфе")
            ip = "fail"

        if ip != "fail":  # Если нет блокировок едем дальше
            countrys[1][self.country].click()  # Тыкает на выбранную страну.
            ip = self.chek_connect()  # Проверяет присвоение IP
            if ip is None:
                ip = self.surf_connect(country=self.country, attempts=self.attempts)[
                    2]  # Если сразу IP не дали, уходит в рекурсию
            if ip != None:
                pass

        return [self.country, countrys[0], ip,
                self.attempts]  # Возвращает список: 1-название строны 2-список стран 3-новый ip 4-попыток переподключения

    # Проверяет авторизован ли сурфшарк
    def shek_login(self):
        sleep(1)
        try:
            email = self.control.browser.find_element(By.ID, 'email')
            email.clear()
            password = self.control.browser.find_element(By.ID, 'password')
            password.clear()
            sleep(1)
            email.send_keys('netkuz42@gmail.com')
            password.send_keys('lkzVfvsYt;fkrj42!')
            sleep(1)
            self.control.browser.find_element(By.XPATH,
                                              '//*[@id="root"]/div/div[2]/div[2]/section/div[1]/form/button[2]').click()
            sleep(1)
        except NoSuchElementException:
            pass
        return True

    # Функция запуска сурфа
    def surf_start(self):
        self.control.browser.get('chrome-extension://ailoabdmgclmfmhdagmlohpjlbpffblp/index.html')
        self.shek_login()
        tab_surf_id = self.control.browser.current_window_handle  # Определяет индекс окна с сурфом.
        # Проверка на скорость запуска SurfShark
        start_surf = False  # Объявляет статус запуска сурф
        while start_surf == False:  # Цикл опредлеяющий прогрузился ли сурф.
            try:
                self.shek_login()
                start_surf = self.control.browser.find_elements(By.CLASS_NAME,
                                                                '_5nzqL')  # Ждёт пока не появится список стран
                start_surf = True
            except NoSuchElementException:  # Кидает исключение если элемента ещё нет
                start_surf = False  # Обновляет статус
                sleep(1)
        return tab_surf_id

    def surf_list_country(self):
        countries = self.control.browser.find_elements(By.CLASS_NAME, '_5nzqL')[1].find_elements(By.CLASS_NAME,
                                                                                                 '_1TL9x')  # Ищет список стран
        countries_dict = {}  # словарь ключ - назв страны, значение - кликабельный элемент
        countries_list = []  # Список найденных стран
        for country in countries:  # Ищет страны и заносит в словарь и список.
            all_name = country.text
            clear_name = all_name.replace('\n', ' ')
            countries_dict.update({clear_name: country})  # Заносит в словарь
            countries_list.append(clear_name)  # Заносит в список стран
        return countries_list, countries_dict  # Возвращает [0] список стран, [1] словарь стран.

    # Функция отключения сурфа
    def surf_disconnect(self):
        self.control.browser.switch_to.window(self.tab_surf_id)  # Переключается на окно с сурфом и спит 1 сек.
        sleep(1)
        time_to_disconnect = 0  # Вводит счётчик секунд на разьединение
        if self.control.browser.find_element(By.XPATH,
                                             '/html/body/div/div/div[2]/div[2]/div/div[3]/div[1]/div/div[1]').text == "ПОДКЛЮЧЕНО":  # Если видит что подключено, то
            self.control.browser.find_element(By.XPATH,
                                      '/html/body/div/div/div[2]/div[2]/div/div[3]/div[2]/button').click()  # Находит кнопку ОТКЛЮЧИТЬ
            while self.control.browser.find_element(By.XPATH,
                                            '/html/body/div/div/div[2]/div[2]/div/div[3]/div[1]/div/div[1]').text != 'НЕ ПОДКЛЮЧЕНО':  # Фикисрует поменлось ли с ПОДКЛЮЧЕНО
                sleep(1)
                time_to_disconnect = time_to_disconnect + 1  # Добавляет значние к счётчику
        ip = self.control.browser.find_element(By.XPATH,
                                               '/html/body/div/div/div[2]/div[2]/div/div[3]/div[1]/div/div[2]/div/div[2]').text  # Определяет мой фищический Ip
        return str(f"Соединение разорвано; время{time_to_disconnect} сек, физический ip {ip}")

    # Функция ведения лога серверов сурфа.
    def log(self, reason_gap=None, successful_pages=None, cause=None, country=None,
            ip=None):  # Определяет 6 параметров.
        now_time = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
        with open(f"Data\\log\\log_thread_{self.ID}.csv", "a") as log:
            if cause == "start":  # Опредлеяет первый запуск сурфшарка, чтобы не выводить показатели "Причины разрыва" и "Числа отработанных страниц"
                log.write(f"\n{now_time};{cause};{country};{ip}")
            elif cause == "end":
                log.write(f";{reason_gap};{successful_pages}")
            else:
                log.write(
                    f";{reason_gap};{successful_pages}\n{now_time};{cause};{country};{ip}")  # Если запуск сурфа не первый значит выодит все параметры.

    # Функция обходда капчи и пустых окон путём переключения серверов сурфшарка.
    def remove_evidence(self, status):
        # Функция реконнекта к новой стране.
        def reload_country(status_low):  # Общая функция
            if not self.country_explorer:  # Если диспетчер стран не задан, задаёт страну нон
                new_country = None
            else:
                new_country = self.country_explorer.get_another_country(self.ID,
                                                                        old_country_status=status_low)  # Возвращает статус старой страны, получает новую из эксплорера
            try_session = self.surf_connect(country=new_country)  # Коннектит сурфшарк к новому серверу
            if try_session[2] == "fail":
                reload_country("empty_country")
            return try_session  # Возрващает страну, список стран, новый ip, количество попыток

        self.control.browser.switch_to.window(self.tab_pars_id),  # Переключаюсь на окно парсинга
        sleep(1)
        self.control.browser.get('about:blank'),  # Открывает пустую страницу
        sleep(2)
        self.control.browser.switch_to.window(self.tab_setting_id)  # Переключается на окно с настройками
        sleep(2)
        self.control.change_manual_agent(self.real_agent),  # Меняет агента на реального
        sleep(1)
        self.control.clear_cache(),  # Удаляет весь кэш и куки
        sleep(1)
        self.surf_disconnect(),  # Разрывает соединение
        sleep(1)
        surf_session = reload_country(status)  # Коннекится к новой стране
        sleep(1)
        self.control.browser.switch_to.window(self.tab_pars_id),  # переключается на окно с парсингом
        sleep(1)
        self.control.change_fake_agent(),  # Меняет юзер агента на фиктивного
        sleep(1)
        return surf_session  # Возрващается список 1-страна, 2-IP адрес.

    # Удаляет все следы.
    def connect_error_detect(self, page, status=None,):

        # Запускает переподключение по новому кругу
        def full_new_face(new_status):
            reload = self.remove_evidence(status=new_status)  # Удаляет все следы
            self.log(new_status, self.successful_pages, f"after_{new_status}", reload[0],
                     reload[2])  # Записывает данные в лог
            sleep(3)
            self.successful_pages = 0  # Обнуляет счётчик успешных страниц
            self.face_reset_numbers = 0
            self.connect_error_detect(page, status=new_status,)  # Идёт на новый круг
            return True

        def reload_face(err_status):
            if err_status != "page_limit":
                self.face_reset_numbers += 1
            if self.face_reset_numbers >= 5:
                full_new_face(err_status)
            self.control.browser.switch_to.window(self.tab_pars_id),  # Переключаюсь на окно парсинга
            sleep(1)
            self.control.browser.get('about:blank'),  # Открывает пустую страницу
            sleep(2)
            self.control.browser.switch_to.window(self.tab_setting_id)  # Переключается на окно с настройками
            sleep(1)
            self.control.clear_cache(),  # Удаляет весь кэш и куки
            sleep(1)
            self.control.browser.switch_to.window(self.tab_pars_id),  # переключается на окно с парсингом
            sleep(1)
            self.control.change_fake_agent(),  # Меняет юзер агента на фиктивного
            sleep(1)
            self.successful_pages += 1
            self.connect_error_detect(page, status=None,)
            return True
        # Проверка на максимальное количество загруженных страниц
        if self.min_page < self.max_page:
            page_limit = random.randrange(int(self.min_page), int(self.max_page))  # Проверяет чтобы минимальный лимит был больше максимального
        else:
            page_limit = self.max_page  # Если min>max тогда лимит=max.
        if self.successful_pages >= page_limit:
            print("ID ", self.ID, " лимит ", f"{self.successful_pages}")
            full_new_face("page_limit")  # Если блокировка есть уходит на новый круг

        if self.successful_pages % 30 == 0 and self.successful_pages != 0:
            print("ID ", self.ID, "обновляю лицо", f"стр:{self.successful_pages}")
            reload_face("page_limit")

        try:
            self.control.browser.get(page)  # Пробует открыть страницу
        except TimeoutException:
            print("ID ", self.ID, " ошибка загрузки ", "страница за указанное время не загрузилась")
            reload_face("timeout_err")  # Коннектится под новым лицом
        except WebDriverException:  # Если ошибка при открытии, уходит в рекурсивную функцию смены VPN серверов.
            print("ID ", self.ID, " ошибка загрузки ", "ошибка драйвера")
            reload_face("driver_err")  # Коннектится под новым лицом
        sleep(1)
        surf_lock_status = self.alert_detect()  # Проверяет наличие блокировки сурфом
        if surf_lock_status:
            print("ID ", self.ID, " блокировка ", "surf_alert")
            full_new_face("surf_alert")  # Если блокировка есть уходит на новый круг
        sleep(1)
        website_lock_status = self.website_lock_detect()  # Проверяряет наличие блокировки сайтом
        if website_lock_status != False:
            print("ID ", self.ID, " блокировка ", website_lock_status)
            reload_face(website_lock_status)  # Если блокировка есть уходит на новый круг
        sleep(1)
        website_confirm_status = self.website_confirm_detect()
        if website_confirm_status == False:
            print("ID ", self.ID, "нет подтерждения успеха(ХЗ почему)")
            reload_face("not_confirm")  # Если нет подтверждения успеха,уходит на новый круг

        self.successful_pages += 1
        self.face_reset_numbers = 0
        return True  # Возращает значение "успешности" проверки

    # Функция для проверки успешности при прозвоне стран
    def defines_a_lock(self, page,
                       sleep_time=10):  # Проверяет сайты на ошибки, принимает:страницу для анализа, максимально время ожидания.
        start_time = datetime.now()  # Засикает время начала теста
        try:  # Пробует открыт страницу
            self.control.browser.get(page)  # Принимает страницу для открытия
            time_to_open = (datetime.now() - start_time).seconds  # Если открыть получилось, считает время на открытие
            sleep(int(sleep_time))  # Спит указанное количество времени
            lock_status = self.website_lock_detect()  # Проверяет на капчи и прочую херню
            if lock_status != False:
                return [lock_status, time_to_open]  # Если проверка не пройдена возвращает причину
            else:
                return ["ok", time_to_open]  # Если успешно возвращает время открытия и статус
        except:  # Если вылезла ошибка при открытии
            time_to_open = (datetime.now() - start_time).seconds  # Вычисляет время для попытки
            return ["empty page", time_to_open]  # Возвращает статус и время открытия
        finally:  # В конце должен обязательно передать браузеру пустую страницу
            self.control.browser.get('about:blank')  # В конце возвращает браузеру пустое окно

    # Словарь с признаками блокироки и статусом
    def website_lock_detect(self):
        # Список всех блокировок
        all_known_lock = {"'Вы не робот?' in self.control.browser.find_element(By.ID,'content').text": "captha farpost",
                          "self.control.browser.find_element(By.CSS_SELECTOR,'body > div.container > div > h1').text=='Доступ ограничен: проблема с IP'": "block ip Avito"}
        for lock, name_lock in all_known_lock.items():  # Пербирает все типы блокировок
            try:
                if eval(lock): return name_lock  # Если находит блокировку возвращает название
            except TimeoutException:
                return "за заданное время время сайт не загрузился"
            except NoSuchElementException:
                pass
        return False  # Если не наход возвращает False

    # Словарь с признаками успешной загрузки страницы
    def website_confirm_detect(self):
        all_known_confirm = {
            "self.control.browser.find_element(By.CSS_SELECTOR, 'div[data-ftid=\"component_header\"]')": "Появился логит дрома"}
        for confirm, name_confirm in all_known_confirm.items():
            try:
                test = bool(eval(confirm))
                if test is True:
                    return True
            except NoSuchElementException:
                pass
            except TimeoutException:
                pass
            except WebDriverException:
                pass
        return False  # Если не находит подтверждение возвращает False

    # Запускает сурф
    def start_with_surf(self, country_explorer=False):
        sleep(self.ID * 10)
        self.control = Chrome(self.ID).start_chrome(header=False)  # Ввожу управление
        self.real_agent = self.control.info_user_agent()  # Сохраняет реальный юзер агент

        self.tab_surf_id = self.surf_start()
        self.tab_pars_id = self.control.new_tab(1)  # Запускает пустое окно для парсинга
        self.tab_setting_id = self.control.new_tab(2)  # Запускает пусто окно для сброса настроек

        # Коннектится к первой стране
        self.control.browser.switch_to.window(self.tab_surf_id)  # Переключается на окно с сурфом и Поехали
        if country_explorer:
            country = country_explorer.get_country(self.ID)  # Если задан эксплорер получает страну из него
        else:
            country = None  # Если нет эксплорера тогда пустое значение, чтобы получить страну рандомно.
        sleep(1)
        country_info = self.surf_connect(country)  # Коннектится к первой стране

        # Проверка на успешность подключения
        if country_info[2] != "fail":
            sleep(1)
            self.control.browser.switch_to.window(self.tab_pars_id)  # Переключается на окно для парсинга
            self.control.change_fake_agent()  # Присваивает фейкового агента
        elif country_info[2] == "fail":
            country_info = self.remove_evidence(
                "empty_country")  # Если подключение не получилось, будет коннектится через новую страну
        self.log(self.ID, cause="start", country=country_info[0], ip=country_info[2])  # Записывает данные в лог
        return self
