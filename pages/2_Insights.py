import pandas as pd

from datetime import datetime

import streamlit as st
import folium 
import plotly.express as px
import locale
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import seaborn as sns

st. set_page_config(page_title= 'Visão Insights',page_icon='📉',layout="wide")

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

df = pd.read_csv('dataset/kc_house_data.csv')





df = transformation_clean(df)
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






    
#------------------------------------------------------------------------------------------


# Ligando os filtros aos dados 

# Filtro 

linhas_selecionadas = data['price'] < f_price

data = data.loc[linhas_selecionadas,:]

#------------------------------------------------------------------------------------------



linhas_selecionadas= data['date'] < f_date
data = data.loc[linhas_selecionadas,:]
#------------------------------------------------------------------------------------------



    
#=======================================
#  Layout NO STREAMLIT
#=======================================

st.title('Visão Insights📊 - House Rocket')



with st.container():
    st.markdown("""___""")
     
    st.caption('Hipótese 1: Imóveis no ano de construção menor que 1955, são 50% mais baratos na média')
    
    df1 = data[['price','yr_construction']].groupby('yr_construction').mean().reset_index()

    df1['porcentagem'] = df1['price'].pct_change()*100
    
    r = ''

    if df1.loc[0,'porcentagem'] > 50:
        r='verdadeira'
    
    else:
        r='falsa'
    
    
    fig = px.bar(df1, x = 'yr_construction', y='price',
                    text_auto='.2s',
                    color='price',
                    width=300,
                     height=500,
                labels = {'price': 'Preço', 'yr_construction':'Ano de construção'})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title_text='A hipótese é {:}. Imóveis construídos antes de 1955. São em média, {:.2f}% mais baratos que os demais anos '.format(r,df1.loc[1,'porcentagem']),title_font_size=20)

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""___""")
    

with st.container():
    #H2 IMOVEIS COM VISTA PARA AGUA, SAO 30 % MAIS CAROS, NA MEDIA.
    st.caption('Hipótese 2:  Imóveis com vista para água, são 30 % mais caros, na média.') 

    df2 = data[['waterfront','price']].groupby('waterfront').mean().reset_index()
    df2['porcentagem'] = df2['price'].pct_change()*100

    r = ''
    if df2.loc[1,'porcentagem'] >=30:
        r='Verdadeira'
    
    else:
        r='Falsa'

    fig = px.bar(df2,x = 'waterfront', y='price',color='price',
                labels = {'waterfront': 'Vista para água', 'price':'Preço'})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title_text='A hipótese é {:}. Imóveis com vista para água.São em média,{:.2f}% mais caros que os sem vista para água'.format(r,df2.loc[1,'porcentagem']),title_font_size=20)

    
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("""___""")
    
    
with st.container():
    st.caption('Hipóteses 3: Imóveis sem porão, são -20% desvalorizados comparando com imóveis com porão')
    df3 = data[['porao','price']].groupby('porao').mean().reset_index()

    df3['porcentagem'] = df3['price'].pct_change()*100



    r = ''
    if df3.loc[1,'porcentagem'] < -20:
        r='Verdadeira'
    
    else:
        r='Falsa'


    fig = px.bar(df3,x ='porao', y='price',color='price')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title_text='A hipótese é {:}. Imóveis sem porao. São em média, {:.2f}%  mais desvalorizados que os imóveis com porão'.format(r,df3.loc[1,'porcentagem']),title_font_size=20)

          
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("""___""")
    
    
    
with st.container():
    st.caption('Hipótese 4: Imóveis tipo casa são 30% mais em conta do que imóveis com mais de 1 andar')
    
    
    df4 = data[['price','floors_h7']].groupby('floors_h7').mean().reset_index()

    df4['pct'] = df4['price'].pct_change()*100

    result = ''
    if df4.loc[1, 'pct'] > 30:
        result = 'Verdadeira'
    else: 
        result = 'Falsa'

    
    fig = px.bar(df4, x='floors_h7', y='price',color='price')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title_text='A hipótese é {:}. Imóveis do tipo casa, são {:.2f}% mais baratos do que casa com mais de 1 andar.'.format(result, df4.loc[1,'pct']),title_font_size=20)
    
    
    st.plotly_chart(fig,use_container_width=True)
