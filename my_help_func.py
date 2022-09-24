from base64 import encode
import pandas as pd
import os
import shutil

#Сканирует директорию и определяет пути ко всем файлам


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


# Переводит всё содержимое файла в нижний регистр
def lower_case(path_to_file,path_to_save):
    with open(path_to_file,"r") as file_to_read:
        data=file_to_read.read()
    data_lower=data.lower()
    with open(path_to_save,"w") as file_to_write:
        file_to_write.write(data_lower)


# Клонирует папку с учётной записью хрома на указанное количество папок
def profile_cloning(path_to_reference, number_clones=None):  # Принимает путь к папке с эталонной учёткой и кол копий
    print(f"Делаю {number_clones} копий профиля")
    split_name = str(path_to_reference).split("_")[:-1]  # Разделяет путь на составляющие убирает последнюю часть
    name = "_".join(split_name)  # Соединяет название обратной без последней цифры
    number_profile = 0
    while number_profile < number_clones:
        number_profile=number_profile+1
        new_name = f"{name}_{number_profile}"
        shutil.copytree(path_to_reference, new_name, dirs_exist_ok=True)
    print(f"{number_profile} копий профиля создано")
    return True

# Возращает текстовые значения при парсинге

def find_values(value_type, table, clarification):
    try:
        name = value_type.find(table, class_=clarification).text
    except AttributeError:
        name = None
    return name

#test





