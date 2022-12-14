from base64 import encode

import numpy as np
import pandas as pd
import os
import shutil


# Сканирует директорию и определяет пути ко всем файлам
def path_cheker(papka, result_list=None):
    if result_list==None:
        result_list=[]
    for item in os.listdir(papka):
        full_path=os.path.join(papka,item)
        if os.path.isdir(full_path):
            path_cheker(full_path,result_list)
        elif os.path.isfile(full_path):
            result_list.append(full_path)
    return result_list


def test_list():
    li=[]
    for i in range(1,1000):
        li.append("https://www.farpost.ru/")
        # li.append("https://aliexpress.ru/")
        li.append("https://www.wildberries.ru/")
        li.append("https://www.avito.ru/")
        # li.append("https://www.ozon.ru/")

    test=pd.DataFrame()

    for i in li:
        test.loc[len(test.index),'Ссылка']=i

    test.to_csv("data\list_test.csv", sep=";")


def lower_case(path_to_file,path_to_save):
    with open(path_to_file,"r") as file_to_read:
        data=file_to_read.read()
    data_lower=data.lower()
    with open(path_to_save,"w") as file_to_write:
        file_to_write.write(data_lower)


# Управляет профилями, создаёт или удаляет папки.
def profile_manager(cloning_numbers: int, sample_profile=r"my_parsing_common\browsers\chrome\optim_user", cloning_path=r"D:\DISTRIB_LOCAL\PARSING\CHROME"):

    list_items = os.listdir(cloning_path)

    profiles_exist = []
    for item in list_items:
        path_to_item = os.path.join(cloning_path, item)
        if os.path.isdir(path_to_item):
            profiles_exist.append(path_to_item)

    if len(profiles_exist) < cloning_numbers:
        print("создаю", cloning_numbers, "профилей")
        for number in range(cloning_numbers):
            name = f"FAKE_USER_DATA_{number}"
            new_path = os.path.join(cloning_path, name)
            shutil.copytree(sample_profile, new_path, dirs_exist_ok=True)
            print("профиль", name, "создан")

    if cloning_numbers == 0:
        print("Удаляю", len(profiles_exist),"профилей")
        for profile in profiles_exist:
            shutil.rmtree(profile, ignore_errors=True)
            print(profile, "удалён")



# Возращает текстовые значения при парсинге
def find_values(value_type, table, clarification):
    try:
        name = value_type.find(table, class_=clarification).text
    except AttributeError:
        name = None
    return name


#Объеденяет все .csv файлы в папке в один датафрейм.
def merge_files(papka_files, path_to_save):
    list_paths = path_cheker(papka_files)
    result_frame = pd.DataFrame()
    for file in list_paths:
        small_frame = pd.read_csv(file, sep=";", encoding="UTF-8", dtype=str, low_memory=False)
        result_frame = pd.concat([result_frame, small_frame], ignore_index=True)
    result_frame.to_csv(path_to_save, encoding="UTF-8", sep=";", index=False)


def delete_first_column(papka_files):
    list_paths = path_cheker(papka_files)
    for path in list_paths:
        frame = pd.read_csv(path, sep=";", encoding="UTF-8", dtype=str, low_memory=False)
        frame.drop(columns=["Unnamed: 0"], axis=1, inplace=True)
        frame.to_csv(path, sep=";", encoding="UTF-8", index=False)


# Сортирует файлы в папке по дате от старых к новым
def sorted_files_by_date(path_to_folder):
    list_file = os.listdir(path_to_folder)
    list_path_files = (os.path.join(path_to_folder, file) for file in list_file)
    list_path_sorted = sorted(list_path_files, key=os.path.getmtime)
    return list_path_sorted
