import pandas as pd
import numpy as np 
import math
import streamlit as st

#Информация о последнем товаре
clients_lp = pd.read_csv('https://mb.phenomen.org/public/question/038ff8f2-0f4b-4d00-aa16-bac9abd792d5.csv',sep=',')
counter = len(clients_lp.client.unique().tolist())

st.header('Выбор клиента')
st.write("На данный момент в списке " + str(counter) + " клиента")

#Товары популярных категорий - для холодного старта
popular_products = pd.read_csv('https://mb.phenomen.org/public/question/80db04fa-45d2-4098-87e5-c72043aae934.csv',sep=',')
popular_products_list = popular_products.products.tolist()

#Популярные товары за квартал по всем категориям
popular_products_all = pd.read_csv('https://mb.phenomen.org/public/question/0f0a3968-e85a-4246-9b9b-d6a8ff509a03.csv',sep=',')

#Создание матрицы для поиска 
def get_matrix():
  df = clients_lp.copy() 
  df['num'] = 1  
  matrix = df.pivot_table(index='client', columns='product', values='num', aggfunc=np.sum).fillna(0)
  return matrix
matrix_for_search = get_matrix()


#Порядок покупок
def get_matrix():
    df = pd.read_csv('https://mb.phenomen.org/public/question/16a56b14-23d0-4d4b-8491-ef4d1545e522.csv',sep=',')
    n_str, n_stb = df.shape
    df.columns = range(n_stb)
    df.index = range(n_str)
    return df
matrix_for_plans = get_matrix()

def rec_system (cl):
    interest_list = ((clients_lp.loc[clients_lp.client == cl])['product']).tolist()
    last_product = interest_list[0]
    
    st.write("_**Список купленных товаров:**_")
    for j in range( len(interest_list[:10])):
        st.write( str(j + 1) + '. ' + interest_list[j])
    st.write("и т.д. Всего " + str(len(interest_list)) + " товаров.")
    
    matrix = matrix_for_search[interest_list]
    s = 0 
    l_clients = matrix.index.tolist()
    similar_clients = [] 
    for client in l_clients:
        for interest in interest_list:
            if matrix[interest][client] == 1:
                s = s + 1
        if s >= math.ceil(len(interest_list)/4):
            similar_clients.append(client)
            s = 0  
        else: 
            s = 0
    similar_clients = ([x for x in similar_clients  if str(x) != cl])
    st.write("_**Список клиентов с похожим интересом:**_")
    if len(similar_clients) > 0: 
        for j in range( len(similar_clients[:10])):
            st.write( str(j + 1) + '. ' + similar_clients[j])
        st.write("и т.д. Всего " + str(len(similar_clients)) + " клиентов.") 
    else:
        st.write("Мы не нашли похожих клиентов:(")
        
    rec_list = []
    if len(similar_clients) > 0: 
        for client in similar_clients:
            rec_list.append((clients_lp.loc[clients_lp.client ==  client])['product'].values[0])
    def get_unique_items(lst):
        unique = []
        for l in lst:
            if l not in unique:
                unique.append(l)
        return unique 
    rec_list = get_unique_items(rec_list)
    for interest in interest_list:
        rec_list = ([x for x in rec_list  if str(x) != interest]) 
        
    st.write("_**Список товаров от клиентов с похожими интересами:**_ ")
    if len(rec_list) > 0:
        for j in range( len(rec_list[:15])):
            st.write( str(j + 1) + '. ' + rec_list[j])
    else:
        st.write("Данные клиенты не могут предложить что-то новое или отсутствуют:(")
        
    if len(rec_list) < 15:
        st.write("_**Маловато будет, посмотрим, что еще может заинтересовать клиента:**_ ")
        start_elem =  len(rec_list) 
        category = ((clients_lp.loc[clients_lp.client == cl])['category']).values[0]
        st.write("Категория последнего товара: " + category)
        n_str, n_stb = matrix_for_plans.shape
        lst_cats = []
        for i in range(n_str):
            for j in range(n_stb):
                if matrix_for_plans[j][i] == category:
                    for x in range(j+1, n_stb):
                        lst_cats.append(matrix_for_plans[x][i] )
        lst_cats  = [x for x in lst_cats  if str(x) != 'nan']
        lst_cats = get_unique_items(lst_cats)
        popular_list = (popular_products_all.loc[popular_products_all['category'].isin (lst_cats)])['products'].unique().tolist()
        full_cats = ' '.join(lst_cats)
        st.write("Какие категории могут заинтересовать: "+ full_cats)
        st.write("Список товаров из этих категорий:") 
        rec_list = get_unique_items(rec_list +  popular_list  + popular_products_list)
        rec_list = rec_list[0:15]
        for j in range( start_elem, len(rec_list)):
            st.write( str(j + 1) + '. ' + rec_list[j])
    rec_list = rec_list[:15]
    df = pd.DataFrame(rec_list)
    df.columns = ['Список рекомендаций']
    df.index = range(1,16)
    df = df.to_csv().encode('utf-8')
    st.download_button( label="Скачать список", data=df, file_name= 'rec_list_'+ cl +'.csv', mime='text/csv')
    st.write('Список будет скачан в csv формате, открывайте его через приложение "Блокнот"')   


def cl_changed():
    st.subheader('Сформирован список для ' + st.session_state.cl)
    rec_system (st.session_state.cl)  

cl = st.selectbox("Список рекомендаций появится сверху после выбора клиента", clients_lp.client.unique().tolist(), key="cl", on_change=cl_changed)
st.markdown("___")


st.header('Для прочих клиентов')
st.write("Можно _**порекомендовать товары**_, ставшие популярными за квартал: ")
for j in range( len(popular_products_list)):
    st.write( str(j + 1) + '. ' + popular_products_list[j])
df1 = pd.DataFrame(popular_products_list)
df1.columns = ['Общий список рекомендаций']
df1.index = range(1,16)
df1 = df1.to_csv().encode('utf-8')
st.download_button( label="Скачать общий список", data=df1, file_name= 'general_rec_list.csv', mime='text/csv')
st.write('Список будет скачан в csv формате, открывайте его через приложение "Блокнот"')
st.markdown("___")

