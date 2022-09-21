from my_surfshark_functions import My_surf as ms
from time import sleep, time
import time
from multiprocessing.pool import ThreadPool as Pool
import math
import os
from my_browsers import Chrome
from my_pandas import My_file_work

class Purity_check:

    def __init__(self,url=None,threads=4,sleep_time=30):
        self.url=url #Анализируемый сайт
        self.threads=threads #Количество копий хрома
        self.sleep_time=sleep_time #Время ожидания страницы после загрузки.

    #Тестирует страны
    def country_reputation(self,browser,country_list,ID, folder_name): #Тестирует коннект списка стран в указанному ресурсу
        session=Chrome(browser)
        surf=ms(browser=browser,lose_sleep_time=300) #Определяю браузер с которым будет работать сурф и время простоя при ошибке
        surf_id=surf.surf_start() #Запускаю перво окно с сурфом
        real_agent=session.info_user_agent() #Сохраняет раельный юзер агент

        tab_pars_id=session.new_tab(1) #Заупускает пустое окно для парсинга
        tab_clear_id=session.new_tab(2) #Запускает пусто окно для сброса настроек
        browser.switch_to.window(surf_id) #Переключается на окно с сурфом и Поехали
        sleep(int(ID)*20) #Потоки будут запускаться через 20 секунд.

        number_of_country=len(country_list)
        for country in country_list:
            connect_info=surf.surf_connect(country=country) #Коннектится к старне из списка
            new_ip=connect_info[2] #Определяет IP
            if new_ip!="fail": #Если функция выдала нормальный IP значит всё ок и :
                browser.switch_to.window(tab_pars_id) #Переключается на окно с парсингом
                session.change_fake_agent() #Меняет юзер агента на рандомного при каждом коннекте.
                sleep(1)
                error_status=surf.defines_a_lock(self.url,self.sleep_time) #Проверяет и возвращает статус соединения !!! ОБЯЗАТЕЛЬНО УКАЗАТЬ Время простоя.
                sleep(1)
                session.change_manual_agent(real_agent) #Меняет юзер агента на стандартного
                browser.switch_to.window(tab_clear_id) #переключается на окно с настройками
                session.clear_cache() #Удаляет кэш и куки
                browser.switch_to.window(surf_id) #Переключается на окно сурфшарка
                sleep(1)
                surf.surf_disconnect() #Разрывает соединение и уходит на новый круг
                sleep(1)
            if new_ip=='fail': #если к стране не получилось подключится:
                error_status[0]="Not connect to VPN" #Вовзращает статус подключения с ошиибкой.
                error_status[1]="" #Устанавливает время коннекта с сайтом на неопредлено
            header=["thread","country","ip","status","load_seconds","attempt","start_time"] #Загловки для сохранения
            result_list=[ID,connect_info[0],new_ip,error_status[0],error_status[1],connect_info[3],(time.strftime('%d-%m-%Y %H:%M:%S', time.localtime()))] #Информация для записи
            path_to_file=f"data\\available_countries\\{folder_name}\Thread_{ID}.csv" #Путь до файла
            country_number=My_file_work().apdate_csv(result_list,header,path_to_file) #Сохраняет результаты прохода в файл, возвращает число строк в файле.
            print("Поток:", ID," страна №:",country_number, " Страна:", result_list[1]," Cтатус:", result_list[3]," Осталось стран:", number_of_country-country_number) #Печатает инфорацию о проходе
        browser.quit()

    #Опредлеяет список стрна в сурфе и возвращает список и словарь
    def division_of_countries(self,browser, number_of_threads): #Разделяет список стран в сурфшарке по потокам, возвращает словарь поток:список стран
        surf=ms(browser=browser) #Определяю браузер с которым будет работать сурф
        surf.surf_start() #Запускаю перво окно с сурфом
        country_list=surf.surf_list_country()[0] #Определяю список страни из настроек сурфа
        serving_size=math.ceil((len(country_list)/number_of_threads)) #Делит список стран на указанное чилсо потоков, округляя в большую сторону

        country_parts_dict={} #Словарь куда записывается распредление стран по потокам
        country_parts_list=[] #Список стран для потока
        namber_serving=0 #Количество потоков
        for country in country_list: #Для каждоый страны в списке стран
            country_parts_list.append(country) #Добавляет страну в список стран для потока
            if len(country_parts_list)==serving_size or country==country_list[-1]: #Если число стран равно заданному или последняя страна в общем списке
                country_parts_dict.update({namber_serving:country_parts_list}) #Заносит в словарь номер стека и список стран стека
                country_parts_list=[] #Обнуляет список стран стека
                namber_serving=namber_serving+1 #Добавляет 1 к счётчику стеков
        browser.quit() #Закрывает браузер после определния

        return country_parts_dict #Возвращает словарь номер стека : список стран
            
    def start_tesing(self): #Запускает тестирование стран

        work_browser=Chrome().start_chrome(profile=0) #Запускает 1 экземпляр браузера для опрделения списка стран

        target_threads=self.threads #Задаёт количество потоков
        threads_dict=self.division_of_countries(work_browser,target_threads) #Получает список стран из сурфшарка и делит на указанное число потоков

        folder_name=f"{self.url.split('/')[2]}_{time.strftime('%d_%m_%Y %H_%M_%S', time.localtime())}" #Определяет название папки в которую будут записываться итоги
        os.mkdir(f"data\\available_countries\\{folder_name}") #Создаёт папку куда будут писаться итоги
        print("итоги будут в папке :", folder_name) #Печатает название папки куда будет сохранять

        list_thread=[] #Список в котором будет храниться потоки сурфшарка для мультизадачности
        while len(list_thread)!=target_threads: #Цикл открывает хром пока не достигнет указанного значения копий
            number_profile=len(list_thread) #Определяет номер профиля для хрома 
            list_thread.append(Chrome().start_chrome(number_profile)) #Запускает хром

        list_params=[] #Список в котором будут хранится параметры запука потоков
        while len(list_params)!=target_threads: #Пока не запущено нужное количество потоков
            session=len(list_params) #Счётчик потоков
            list_params.append((list_thread[session],threads_dict[session],f'{session}',folder_name)) #набор параметров для многопоточности

        pool=Pool(processes=target_threads) #Запускает нужное количество потоков
        pool.starmap(self.country_reputation,list_params) #Запускает хром в нужно количесте сессий с нужным количеством парметров

        My_file_work().save_county_test(folder_name) #После прохождения всех Сохраняет результаты тестированию в результирующие файлы


