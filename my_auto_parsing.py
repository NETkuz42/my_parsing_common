from my_parsing_common.my_surfshark_functions import My_surf as ms
from my_parsing_common.my_browsers import Chrome
from time import sleep


def auto_parsing(browser, ID, country_explorer=False, ):
    driver_control = Chrome(browser)  # Ввожу управление
    real_agent = driver_control.info_user_agent()  # Сохраняет раельный юзер агент

    tab_surf_id = ms().surf_start(browser)  # Запускаю первое окно с сурфом
    tab_pars_id = driver_control.new_tab(1)  # Заупускает пустое окно для парсинга
    tab_setting_id = driver_control.new_tab(2)  # Запускает пусто окно для сброса настроек

    surf = ms(ID, browser, driver_control, country_explorer, real_agent, tab_surf_id, tab_pars_id, tab_setting_id,
              lose_sleep_time=60)  # Определяю браузер с которым будет работать сурф

    # Коннектится к первой стране
    browser.switch_to.window(tab_surf_id)  # Переключается на окно с сурфом и Поехали
    if country_explorer:
        country=country_explorer.get_country(ID)  # Если задан эксплорер получает страну из него
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
