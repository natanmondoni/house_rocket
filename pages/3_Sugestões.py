import pandas as pd

from datetime import datetime

import streamlit as st
import folium 
import plotly.express as px

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


st. set_page_config(page_title='Sugestão Compra/Venda',page_icon = '💲',layout="wide")

def criacao_mapa(df_sugestao):
    mapa = folium.Map(max_bounds=True)
    marker_cluster = MarkerCluster().add_to(mapa)


    for index,location_info in df_sugestao.iterrows():
        id_imovel= location_info["id"]
        date = location_info["date"]
        zipcode = location_info["zipcode"]
        price = round(location_info["price"],2)
        lucro= round(location_info["lucro"],2)
        m2_living = location_info["m2_living"]



        html = "<p><strong>{}</strong></p>"
        html += "<p>Date:{}"
        html += "<p>Zipcode: {},00"
        html += "<p>Price: {} "
        html += "<p>Lucro: {}"
        html = html.format(id_imovel,date,zipcode,price,lucro)

        popup = folium.Popup(
            folium.Html(html, script=True),
            max_width=500,)

        folium.Marker([location_info['lat'], 
                       location_info['long']],
                       popup=popup).add_to(marker_cluster)
        
        
    marker_cluster = MarkerCluster().add_to(mapa) 

                

               

    return mapa



def sugestao_venda(df_sugestao):
        #-----------------------------------------------------------------------------------------------------------
        # 1.Agrupando os dados por região, para diminuir a influencia de preço por região
        # 2. Buscar a mediana por região. Porque podem ter outliers
        # 3. Agrupando por season para eliminar a sazonalidade

        df_price = df_sugestao[['price', 'zipcode', 'season']].groupby(['zipcode', 'season']).median().reset_index()

        # Trocando o nome da coluna (price)
        df_price.columns = ['zipcode', 'season', 'price_season']

        # Combinando o price_season com o Data
        df_sugestao = pd.merge(df_sugestao,df_price,on=['zipcode', 'season'], how='inner')
        ## ----------------------------------------------------------------------------------------


        # 1. Fazendo percentual de lucro pela coluna 'price_season'.
        # Na qual essa coluna elimina o fator região e isola a estação do ano


        df_sugestao['price_sales'] = df_sugestao.apply(lambda x: (x['price'] * 1.1)
                                                       if (x['price'] >= x['price_season'])

                                                       else(x['price'] * 1.3), axis=1)

        # Fiz o preço de venda menos o de compra, para saber o lucro
        # O imposto não está colocado na soma.
        df_sugestao['lucro'] = df_sugestao['price_sales'] - df_sugestao['price']
        
        return df_sugestao

def sugestao_compras(data):
        # mediana de price per zipcode
        zipcode_median = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()

        # juntei a variavel com o dataframe e troquei o nome da variavel
        data = pd.merge(data, zipcode_median, on='zipcode', how='inner')


        data.rename(columns={'price_y': 'price_median_zip','price_x':'price'}, inplace=True)






        # fiz a condição de compra e nao compra / que pode ser feita com lambda tambem

        for i in range(len(data)):
            if (data.loc[i, 'price'] < data.loc[i, 'price_median_zip']) & (data.loc[i,'condition'] >= 3):
                data.loc[i,'status'] = 'compra'

            else:
                data.loc[i,'status'] = 'nao_compra'

        df_sugestao = data.loc[data['status']=='compra'].copy().reset_index(drop=True)
        
        
        return df_sugestao




def per (val1,val2):
    perc = round(100 * (val2 - val1) / val1, 2)
    return perc



def transformation_clean(data):

# LIMPEZA E TRANSFORMACAO

    # Removendo ids duplicados e permanecendo os mais recentes 
    data = data.drop_duplicates(subset=['id'], keep='last').reset_index(drop=True)

    # Entendemos que o valor 33 foi um erro de digitação
    data.loc[data['bedrooms']==33,'bedrooms'] = 3
    #Convert object to  date
    data['date'] = pd.to_datetime(data['date'])

    # Criando variavel apartir do ANO da variavel DATE
    data['year'] = pd.to_datetime(data['date']).dt.year

    # Criando variavel apartir do YEAR e MONTH da vairavel DATE.
    #Usaremos na hipotese 8
    data['month_year'] = data['date'].dt.strftime('%Y-%m')

    #Criando variavel apartir da semana do ano
    data['year_week'] = pd.to_datetime(data['date']).dt.strftime('%Y-%U')

    #Criando variavel apartir do MONTH da variavel DATE.
    #Usaremos na hípotese 9?
    data['month'] = pd.to_datetime(data['date']).dt.month

    #Alterando variável bathrooms de float para int
    data['bathrooms'] = data['bathrooms'].astype('int64')

    data['floors'] = data['floors'].astype('int64')

    #Converting variable to square meters 
    data['sqft_living'] = data['sqft_living'] * 0.093
    data['sqft_above'] = data['sqft_above'] * 0.093
    data['sqft_lot'] = data['sqft_lot'] * 0.093
    data['sqft_basement'] = data['sqft_basement'] * 0.093

    #renomeando colunas
    data.rename(columns={'sqft_living': 'm2_living',
                       'sqft_above':    'm2_above',
                       'sqft_lot':      'm2_lot',
                       'sqft_basement': 'm2_basement'}, inplace = True)


    
    # Criando variavel Ano de Construção e guardando os valores de acordo com a condição 
    #Usaremos na hipotese1
    data['yr_construction'] = data['yr_built'].apply(lambda x: '1900 - 1954 ' if x <= 1954 else '1955 - 2015')




    #Transformando valor 'com_porao' e 'sem_porao'
    # Usaremos para a hipotese 3
    data['porao'] = data['m2_basement'].apply(lambda x: 'sem_porao' if x == 0 else 'com_porao' )



    #Transformando o valor da variavel floors em 'house' e 'house_more_floors'
    data['floors_h7'] = data['floors'].apply(lambda x : 'house' if x <= 1 else 'house_more_floors')


    # Classificando estilo de casas por quantidades de quartos
    data['dormitory_type'] = data['bedrooms'].apply(lambda x: 'studio' if x == 1 else 
                                                              'apartament' if x == 2 else
                                                              'house' )


    # Modificando valor 0 e 1. Para "sem_vista" e "com_vista"
    #Usaremos na hipotese 2,8 e 9
    data['is_waterfront'] = data['waterfront'].apply(lambda x: 'com_vista' if x == 1 else 'sem_vista')

    
    # Criando a coluna de estação
    data['season'] = data['month'].apply( lambda x: 'winter' if (x == 12 or x <= 2) else 'spring' if (3 <= x < 6) else 'summer' if (6 <= x <= 8) else 
    'Autumn')
    
    
    
    return data


#---------------------- Inicio da Estrutura Lógica do Código--------------------------------

#----------------
#Import Dataset
#----------------

df_sujo = pd.read_csv('dataset/kc_house_data.csv')

df = transformation_clean(df_sujo)
data = df.copy()


#=======================================
# BARRA LATERAL NO STREAMLIT
#=======================================

image_path = open('houserocket.png','rb')

image = image_path.read()

st.sidebar.image(image)


st.sidebar.markdown("""___""")

#===============================================================================================



#------------------------------------------------------------------------------------------
# criando os filtros

price_min = int(data['price'].min())
price_max = int(data['price'].max())
price_avg = int(data['price'].mean())


f_price = st.sidebar.slider('Selecione o valor ',
                                     price_min,
                                     price_max,
                                     value=364791)
st.sidebar.markdown("""___""")


#------------------------------------------------------------------------------------------

# filters Date
st.sidebar.subheader('Selecione a data ')
data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
min_date = datetime.strptime(data['date'].min(), '%Y-%m-%d')
max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d')

f_date = st.sidebar.slider('Date', min_date, max_date, max_date)

data['date'] = pd.to_datetime(data['date'])
    

#------------------------------------------------------------------------------------------
zipcode_options = st.sidebar.multiselect(label = 'Selecione o CEP ',
                       options = data.loc[:,'zipcode'].unique().tolist(),
                       default=[98178, 98125, 98028,98136,98074,98053,98003])
st.sidebar.markdown("""___""")
#------------------------------------------------------------------------------------------


# Filter Bedrooms
f_bedrooms = st.sidebar.selectbox('Valor maximo de bedrooms',
                                      sorted(set(df['bedrooms'].unique())),
                                 index=3 )
st.sidebar.markdown("""___""")

#------------------------------------------------------------------------------------------

# Filter bathrooms
f_bathrooms = st.sidebar.selectbox('Valor maximo de bathrooms',
                                      sorted(set(data['bathrooms'].unique())),index=3) 




# Filter Zipcode
#st.sidebar.subheader('Classifique a estação do ano')

f_season = st.sidebar.multiselect('Filtrar estação do ano', data['season'].unique(),default=['spring','summer'])


#------------------------------------------------------------------------------------------
f_waterview = st.sidebar.checkbox('Somente imóveis com vista para água')
#------------------------------------------------------------------------------------------


# Ligando os filtros aos dados 

# Filtro 

linhas_selecionadas = data['price'] < f_price

data = data.loc[linhas_selecionadas,:]

#------------------------------------------------------------------------------------------



linhas_selecionadas= data['date'] < f_date
data = data.loc[linhas_selecionadas,:]
#------------------------------------------------------------------------------------------


# Filtro do País
linhas_selecionadas = data['zipcode'].isin(zipcode_options)
data = data.loc[linhas_selecionadas,:]

#------------------------------------------------------------------------------------------

# Filtro bedrooms
linhas_selecionadas = data['bedrooms'] < f_bedrooms
data = data.loc[linhas_selecionadas,:]


#------------------------------------------------------------------------------------------

# Filtro bathrooms
linhas_selecionadas = data['bathrooms'] < f_bathrooms
data = data.loc[linhas_selecionadas,:]



#------------------------------------------------------------------------------------------
# Filtro do season
linhas_selecionadas = data['season'].isin(f_season)
data = data.loc[linhas_selecionadas,:]
#------------------------------------------------------------------------------------------

# House per water view

if f_waterview:
    data = data[data['waterfront'] == 1]
else:
    data = data.copy()

#------------------------------------------------------------------------------------------    






#=======================================
#  Layout NO STREAMLIT
#=======================================

st.title('Sugestão de compra ')

with st.container():
    
    df_sugestao = sugestao_compras(data)
    
    st.dataframe(df_sugestao)
    
    



with st.container():
    
    
    df_sugestao = sugestao_venda(df_sugestao)
    
    
    
    
    st.sidebar.subheader('Pressione o Botão se deseja comprar os imóveis selecionados🛒🧾')
    if st.sidebar.button('Comprar'):
        # Métricas de Vendas
        st.title('Tabela de imóveis comprados')
    
        with st.container():
            c1, c2, c3 ,c4= st.columns(4)

            with c1:
                c1.metric(label="💲Investimento", value=round(df_sugestao['price'].sum(),2))
            
        
            with c2:
                st.metric(label="💲 Soma do valor total com o lucro ", value= round(df_sugestao['price_sales'].sum(),2))
            
            
        
        
            with c3:
                st.metric(label="💲Lucro",value=round(df_sugestao['lucro'].sum(),2),delta= str(per(df_sugestao['price'].sum(),df_sugestao['price_sales'].sum()))+'%')
            
            
            
            with c4:
                st.metric(label='Número de imóveis comprados 🏠',value= df_sugestao['id'].count())
                    # Salvando os atributos filtrados
                    
            df_compra = df_sugestao[['id','date','price','lucro','price_season','price_sales']].copy().reset_index(drop=True)
        
            st.dataframe(df_compra,use_container_width=True)
            
            #----------------------------------------------------------------------------------------------------------------------------------------------------------            
            st.title('Mapa das localizações dos imóveis comprados')
            
            mapa = criacao_mapa(df_sugestao)
            
            folium_static(mapa, width=1024, height= 600)
            
           




  
        
        
        
        


    
    

    