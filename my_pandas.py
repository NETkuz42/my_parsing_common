# Сценариий:
# 0. Сканирует созданную директорию.
# 1. Открывает файлы threadов.
# 2. Преобразует в датафрейм.
# 3. Выисляет дельту между подходами, добавялет в последний столбец.
# 4. Создаёт общий файл. 
# 5. Подводит итоги:
#     а.Выводит итоги по столбам сохраняет их в отдельную папку.
#     б. Разделяет файл на белый и чёрный список. Сохраняет каждый в отдельнмой папке.

from operator import concat
import os
import pandas as pd
from datetime import datetime, timedelta
import random
from time import sleep
import numpy as np
import my_help_func

class My_file_work:
    def __init__(self) -> None:
        pass

    #Сканирует результаты всех поток и сохраняет итоги
    def save_county_test(self,name_test_folder,time_to_sleep=5):
        name_dir=f"data\\available_countries\\{name_test_folder}\\" #Папка где лежат итоги
        name_files=os.listdir(name_dir) #Список файлов с результатами
        result=pd.DataFrame() #Создаёт датафрейм куда будут записываться все данные
        for name_file in name_files: #Обрабатывает каждое название файла
            if name_file!='result.csv': #Проверяет все файлы в папке кроме результирующего
                full_path=os.path.join(name_dir,name_file) #Полный путь до файла
                data=pd.read_csv(full_path,sep=';',parse_dates=['start_time']) #Читает файл, заносит итоги в датафрейм
                data["time_delta"]=0 #Создаёт столбец где хранится время прохода
                for i in range(1,len(data['start_time'])): #ПРОходит по номерам строк, начиная со второй
                    time=data.loc[i,"start_time"]-data.loc[(i-1),"start_time"] #Вычисляет время прохода
                    data.loc[i,"time_delta"]=time #Заносит данные в столбец
                data.loc[0,"time_delta"]=data["time_delta"].astype('timedelta64[ns]').mean() #Заносит в 0 строку avarege_time за сессию (чтобы потом корректно считалась средняя)
                data["surf_stop"]=0 #Создаёт стольбец где будут хранится "блокировки сурфшарка"
                for i in range(0,len(data["time_delta"])): #Проходит по всем строкам с 0
                    if data.loc[i,"time_delta"]>=timedelta(minutes=int(time_to_sleep)):  #Если время прохода больше указанных минут тогда засчитывает блокировку
                        data.loc[i,"surf_stop"]=True #status если блокировка есть
                    else: data.loc[i,"surf_stop"]=False #Cтатус если блокировки нет
                result=pd.concat([result,data], ignore_index=True) #Дополняет общий файл
        
        result.to_csv(f"{name_dir}result.csv") #Сохраняет результаты всех threadов в файл

        white=result[result["status"]=='ok'].copy() #Вычисляет список белых серверов, т.е. там где не было проблем с подключением. Создаёт отдельную переменную с ними
        white.reset_index(drop=True, inplace=True) #Сбрасывает индексы
        white["speed"]="" #Создаёт дополнительный столбец
        time_connect=white["load_seconds"].describe() #Считает распределние по времени коннекта
        for i in range(0,len(white["load_seconds"])): #Пошёл по строкам
            if white.loc[i,"load_seconds"]<=time_connect[4]: white.loc[i,"speed"]="fast" #Если время меньше, чем у 25% серверов значит быстрый.
            elif white.loc[i,"load_seconds"]>=time_connect[6]: white.loc[i,"speed"]="slow" #Если медленнее, чем у 75% серверов значит медленный.
            else: white.loc[i,"speed"]="middle" #Всё остальное среднее


        name_file=name_dir.split('\\')[-2] #Задёт имя для строки
        path_to_save=lambda type:f'data\\country_lists\\{type}\\{name_file}_{type}.csv' #Лямбда для полного пути файла
        white.to_csv(path_to_save("white"), sep=";") #"Сохраняет белый список"

        black=result[result["status"]!='ok'].copy() #Создаёт чёрный список
        black.reset_index(drop=True, inplace=True) #Сбрасывает индексы
        black.to_csv(path_to_save("black"), sep=";") #Сохраняет чёрный список

        #Для подведения общих итогов
        total_time=result["start_time"].max()-result["start_time"].min() #Все время теста
        number_threads=(result["thread"].max()+1) #threads_number
        average_time=result["time_delta"].astype("timedelta64[ns]").mean() #avarege_time коннекта к стране
        number_sleep=len(result[result["surf_stop"]==True]) #Подсчёт количества остановок.

        time_to_sleep=result[result["surf_stop"]==True] #Фильтрует список по остановкам для следущего расчёта
        time_to_sleep_mean=time_to_sleep["time_delta"].astype("timedelta64[ns]").mean() #Считает avarege_time остановки

        number_countrys=len(result["country"]) #Количество стран
        number_white_countrys=len(result[result["status"]=='ok']) #Количество стран в белом списке
        number_capcha=len(result[result["status"]=='capcha_detect']) #Количество вылезших капч
        namber_block_ip=len(result[result["status"]=='block ip'])+len(result[result["status"]=='empty page']) #Количество блокировок по IP

        testing_result=[name_file, total_time, number_threads,average_time,number_sleep,time_to_sleep_mean,number_countrys,number_white_countrys,number_capcha, namber_block_ip] #Список сохраняемых столбов
        headers=["file_name","total_time","threads_number","avarage_time","stop_numbers","average_time_block","countries_numbers","white_numbers","captha_numbers","block_ip_numbers"] #Заголвоки столбов
        path_to_file='data\\servers_analitics.csv' #путь к файлу
        self.apdate_csv(testing_result,headers,path_to_file) #Сохранение файла
        return True
    
    def apdate_csv(self,result_list,header, path_to_file,):
        try:
            old_data=pd.read_csv(path_to_file, sep=";")
            new_data=pd.DataFrame([result_list],columns=header)
            big_data=pd.concat([old_data,new_data])
            big_data.to_csv(path_to_file, encoding="UTF-8", sep=";", index=False)
        except FileNotFoundError:
            big_data=pd.DataFrame([result_list],columns=header)
            big_data.to_csv(path_to_file, encoding="UTF-8", sep=";", index=False)
        return len(big_data)

    #Объеденяет csv файлы из директории в один файл
    def merge_csv(self,path_to_dir,path_to_save):
        file_list=my_help_func.path_cheker(path_to_dir)
        fraim=pd.DataFrame()
        
        for file in file_list:
            file_internals=pd.read_csv(file,encoding="UTF-8",sep=";")
            if len(fraim)==0: fraim=file_internals
            else: 
                fraim=pd.concat([fraim,file_internals])
        
        fraim.to_csv(path_to_save, encoding="UTF-8", sep=";", index=False)

    
    #Делит список обьявлений на нужное количество частей и сохраняет где надо
    def split_list_csv(path_to_big, divider=1, path_to_chunks=None):
        data=pd.read_csv(path_to_big, sep=";") #Читает файл с большим списком
        chunks=np.array_split(data,divider) #Делит список на указанное количество частей
        name_file=path_to_big.split("\\")[-1].split(".")[0] #Вычисляет название файла списка

        if path_to_chunks==None: #если путь к сохранению частей не задан тогда будет сохранять в ту же папку
            split_folders=path_to_big.split("\\") #Делит пуtть на составляющие
            path_to_chunks="\\".join(split_folders[0:-1]) #Объеденяет путь без названия файла
        
        full_path_to_chunks=f"{path_to_chunks}\\{name_file} {datetime.now().strftime('%d_%m_%Y %H_%M_%S')}" #Задаёт имя папки в которой будут храниться части листов
        os.mkdir(full_path_to_chunks) #Создаёт папку куда будут сохранятьс ячасти листа

        number_chunk=0 #Счётчик частей
        chunk_puth_list=[] #Создаёт список к который будут заноиться пути к частям
        for chunk in chunks: #Часть из частей
            fraim=pd.DataFrame(chunk) #Создаёт датафрейм
            fraim_mixed=fraim #Отключает перемешивание списка 
            # fraim_mixed=fraim.sample(frac=1) #Перемешивает строки в фрейме #Времено выключаю перемешивание, потом нужно обязательно включить.
            path_to_chunk=f"{full_path_to_chunks}\\{name_file}{number_chunk}.csv" #Задаёт путь для сохранения
            chunk_puth_list.append(path_to_chunk) #Добавяляет путь до файла в список
            fraim_mixed.to_csv(path_to_chunk,index=False, sep=";") #Сохраняет части к csv, сбрасывая индекс
            number_chunk=number_chunk+1 #Добавляет 1 к счётчику
        return chunk_puth_list #Возвращает список путей к файлам
    
    
# Отвечает за выдачу стран и хранение статусов
class Country_explorer:
    save_result=lambda self,fraim, file_name: fraim.to_csv(f"data\countrys_explorer\\{file_name}.csv", sep=";", encoding="UTF-8")

    def __init__(self,path_to_white,explorer_file):
        self.explorer_file=explorer_file
        self.countrys_list=pd.read_csv(path_to_white, sep=";", usecols=["speed","country"],index_col="country") #создаёт фрейм страна,скорость страна-индекс        
        self.countrys_list[['status','status','start_time','end_time','delta_time']]="" #Создаю несколько столбов для аналитики
        self.countrys_list['use_numbers']=0
        self.save_result(self.countrys_list,self.explorer_file) #Сохраняет данные в файл
        pass

    def get_country(self,ID,speed="normal"): #Отдаёт страну согласно скорости
        free_countrys=lambda x:self.countrys_list.query(f'status=="" & status=="" & speed=="{x}"').index #Лямбда выводит список стран с пустым статусом и условием скорости х
        random_country=lambda x:random.choice(free_countrys(x)) #Лямабда выводит случайную страну соответсвенно скорости х
        if len(free_countrys("fast"))!=0: final_country=random_country("fast") #Если список быстрых не пустой тогда отдаёт рандомного быстрого
        elif len(free_countrys("middle"))!=0: final_country=random_country("middle") #Если список средних не пустой тогда отдаёт рандомного среднего
        elif speed!="normal" and len(free_countrys("slow"))!=0: final_country=random_country("slow") #Если список медленных не пустой и изменена скорость тогда отдаёт рандомного медленного
        else: final_country=self.reuse_country() #Если нет не пройденных стран тогда будет брать использованные.

        self.countrys_list.loc[final_country,"status"]=ID #Заносит номер потока
        self.countrys_list.loc[final_country,"start_time"]=datetime.now() #Заносит время начала

        use_numbers=self.countrys_list.loc[final_country,"use_numbers"]+1 #Прибавляет единицу к количеству использования страны
        self.countrys_list.loc[final_country,"use_numbers"]=use_numbers #Заносит данные в столбец

        self.save_result(self.countrys_list,self.explorer_file) #Сохраняет файл
        return final_country #Возвращает название страны
    
    #Функция принимает статус блокировки и отдаёт новую страну
    def get_another_country(self,ID,old_country_status="fail"): 
        old_country=self.countrys_list[self.countrys_list['status']==ID].index[0] #Вычисляет старую страну
        new_country=self.get_country(ID) #выдаёт новую страну

        #Записывает лог по старой стране
        now_time=datetime.now() #Считет текущее время
        self.countrys_list.loc[old_country,"status"]="" #Удаляет номер потока
        self.countrys_list.loc[old_country,"status"]=old_country_status #Записывает статус ошибки
        self.countrys_list.loc[old_country,"end_time"]=now_time #Записывает время окончания
        self.countrys_list.loc[old_country,"delta_time"]=now_time-self.countrys_list.loc[old_country,"start_time"] #Считает и записывает время использоания страны
        self.save_result(self.countrys_list,self.explorer_file) #Сохраняет файл
        return new_country
    
    # Вычисляет самую старую страну из использованных
    def reuse_country(self):
        start_time=self.countrys_list['start_time'].astype('datetime64[ns]') #Считывает столбец с временем начала как формтат даты
        old_date=start_time.min() #Находит минимальное значение
        old_country=self.countrys_list[start_time==old_date].index[0] #Возвращает индекс (страну) с минимальным временем начала
        return old_country #Возвращает страну
    

