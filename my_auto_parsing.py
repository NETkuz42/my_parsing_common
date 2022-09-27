import pandas as pd

from my_parsing_common.my_surfshark_functions import My_surf as ms
from my_parsing_common.my_browsers import Chrome
from time import sleep
import random


def auto_parsing(browser, ID, link_pages, key_func, country_explorer=False,):
    sleep(ID*10)
    driver_control = Chrome(browser)  # Ввожу управление
    real_agent = driver_control.info_user_agent()  # Сохраняет реальный юзер агент

    tab_surf_id = ms().surf_start(browser)  # Запускаю первое окно с сурфом
    tab_pars_id = driver_control.new_tab(1)  # Запускает пустое окно для парсинга
    tab_setting_id = driver_control.new_tab(2)  # Запускает пусто окно для сброса настроек

    surf = ms(ID, browser, driver_control, country_explorer, real_agent, tab_surf_id, tab_pars_id, tab_setting_id,
              lose_sleep_time=60)  # Определяю браузер с которым будет работать сурф

    # Коннектится к первой стране
    browser.switch_to.window(tab_surf_id)  # Переключается на окно с сурфом и Поехали
    if country_explorer:
        country = country_explorer.get_country(ID)  # Если задан эксплорер получает страну из него
    else:
        country = None  # Если нет эксплорера тогда пустое значение, чтобы получить страну рандомно.
    sleep(1)
    country_info=surf.surf_connect(country)  # Коннектится к первой стране

    # Проверка на успешность подключения
    if country_info[2] != "fail":
        sleep(1)
        browser.switch_to.window(tab_pars_id)  # Переключается на окно для парсинга
        driver_control.change_fake_agent()  # Присваивает фейкового агента
    elif country_info[2] == "fail":
        country_info=surf.remove_evidence("empty_country")  # Если подключение не получилось, будет коннектится через новую страну
    surf.log(ID, cause="start", country=country_info[0], ip=country_info[2])  # Записывает данные в лог

    number_pages = 0
    successful_page = 0
    result_frame = pd.DataFrame()
    for link in link_pages:  # В списке ссылок берёт ссылку и список номеров страниц
        number_pages += 1
        if number_pages != 0 and number_pages % 30 == 0:  # Для недопущения блокировки сурфом, спит с заданной периодичностью.
            sleep_time = 600  # сплю 10 минут
            print(f"ID:{ID} промежуточный лимит: {number_pages} сплю {sleep_time}")
            sleep(sleep_time)
        else:
            sleep(random.randrange(0, 2))  # Время ожидания между подходами

        surf.connect_error_detect(link, status=None, successful_pages=successful_page,
                                  max_page=130)  # Проверяет прошла ли проверка на успешность загрузки по многим параметрам
        part_frame = key_func(browser, link)  # Выгружает список объявлений
        result_frame = pd.concat([result_frame,part_frame])
    return result_frame

