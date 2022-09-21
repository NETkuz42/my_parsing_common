import re
from collections import Counter
from numpy import var
import pandas as pd
import difflib

class word_clining:

    #Принимаем пути к :файлу обявлений, словарб моделей, словарю мусора
    def __init__(self,sample_dict_path=None,trash_dict_path=None):
        self.sample_dict_path=sample_dict_path
        self.trash_dict_path=trash_dict_path
        pass

    # Функция определения мусора, цель: сделать файл мусора
    def trash_type_dict(self,abs_path=None):
        fraim=pd.read_csv(abs_path,sep=";", encoding="UTF-8", usecols=["название"]) #Читаю все обьявления
        dirt_text=" ".join(fraim["название"]) #Перевожу список обявлений в текст

        clear_text=self._clean_text(dirt_text)
        repet_dict=Counter(clear_text.split(" ")) #Счтаю количесто повторений каждого слова, создаю словарь слово:повторений.
        frame_name_abs=pd.DataFrame.from_dict(repet_dict,orient="index").reset_index() #Создаю фрей данных из словаря слово:повторений

        #Проверка на вхождение слов в название видях
        samles_dict=pd.read_csv(self.sample_dict_path,sep=";", encoding="UTF-8", usecols=["name"]) #Читаю файл моделей
        sample_text=" ".join(samles_dict["name"]).lower().split(" ") #Перевожу список в одну строку

        for index,value in frame_name_abs["index"].items(): #Беру каждое слово из объявление
            if value in sample_text: frame_name_abs.loc[index,"type"]="ok" #Проверяю вхождения слов из объявлений в строку образцов
        
        frame_name_abs.to_csv(self.trash_dict_path, sep=";",index=False) #Сохраняет фрейм

    # Функция для возврата моделей в файл объявлений
    def model_detect_to_dict(self,names_list=None):
        trash_fraim=pd.read_csv(self.trash_dict_path,sep=";", encoding="UTF-8") #Читаю словарь мусора
        model_fraim=pd.read_csv(self.sample_dict_path,sep=";", encoding="UTF-8",index_col=["name"]) #Читаю словарь моделей индексирую по варианту

        trash_list=[] #Список мусора
        for index_trash,vol_trash in trash_fraim["type"].items(): #Проходит по словарю мусора
            if vol_trash=="trash" or vol_trash=="vendor": #Определяю какие типы считать за мусор
                trash_list.append(trash_fraim.loc[index_trash,"word"]) #Создаёт список мусорный слов

        result_dict={}
        for name in names_list: #Пошёл по списку названий
            clear_text=self._clean_text(name) #очищаю текст от мусора

            #Удаляю мусор из навзвания
            dirt_word_list=clear_text.split(" ") #разбиваю название на список слов
            word_list=[]
            for i in dirt_word_list: #Прохожу по каждому слову
                i=i.strip()#Удаляю внутренние пробелы
                if i not in trash_list: word_list.append(i) #если слово не в списке мусора добавляет в чистый список
            step5=" ".join(word_list).strip() #Объеденяет список слов обрато в преложение, удаляю пробелы по краям.

            matcher=difflib.get_close_matches(step5,model_fraim.index,n=1,cutoff=0.6) #Сопоставляет название со словарём моделей, находит самое похожее.

            try: model=matcher[0] #Пробует назначить лучшее сопоставление
            except IndexError: model=None #Если соответсвий нет возврщает ничего

            if model==None: result_dict.update({name:[None,None,None,None]})
            else:
                match_sample=model_fraim.loc[model,"sample"]
                category=model_fraim.loc[model,"category"]
                vendor=model_fraim.loc[model,"vendor"]
                perfomance=model_fraim.loc[model,"g3f mark"]
                result_dict.update({name:[match_sample,category,vendor,perfomance]}) #Дополняет словарь название:модель
            
            print(len(result_dict),name,":",step5,":",model)
        return result_dict


    def _clean_text(self,text):
        step1=text.lower() #Убираю капс
        step2=re.sub(r'[^\w\s]',' ',step1) #Убираю все знаки
        step3=step2.replace("\n","").replace("гб","gb") #замению гигабайты на английские
        step4=re.sub(r'[а-яА-Я]','',step3) #Удаляю все руссие буквы
        return(step4)
    
    #Считает вхождение повторяющихся слов из объялений в словарь моделей, цель создать словарь моделей
    def numbers_word(self,dict_model,dict_trash):
        model_file=pd.read_csv(dict_model,sep=";",encoding="UTF-8")
        trash_file=pd.read_csv(dict_trash,sep=";",encoding="UTF-8",index_col=["word"])

        for index,vol in model_file['name'].items():
            print(vol)
            clen_word_list=self._clean_text(vol).split(" ")
            number_col=0
            for word in clen_word_list:
                number_col+=1
                try:
                    confirm=trash_file.loc[word,"number"]
                except KeyError:
                    confirm=None
                col_word=[f"{number_col}_word"]
                col_mumbers=[f"{number_col}_numbers"]
                model_file.loc[index,col_word]=word
                model_file.loc[index,col_mumbers]=confirm
        model_file.to_csv("data\\test.csv", sep=";")

    #Функция для загрузки списка обявлений
    def load_abs_too_list(self, path_to_abs):
        all_abs=pd.read_csv(path_to_abs, sep=";", encoding="UTF-8")
        names_list=all_abs["название"]
        return names_list

    #Функция для сохранения разультатов
    def save_result(self,dict,path_to_save):
        fraim=pd.DataFrame(dict)
        fraim.to_csv(path_to_save, sep=";", encoding="UTF-8")
        return True
    
    

