import pandas as pd

from datetime import datetime

import streamlit as st
import folium 
import plotly.express as px
import locale
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st. set_page_config(page_title= 'Overview',page_icon='📊',layout="wide")

def localizacao_map(data):

            mapa = folium.Map(max_bounds=True)

            marker_cluster = MarkerCluster().add_to(mapa)


            for index,location_info in data.iterrows():
                id_imovel= location_info["id"]
                date = location_info["date"]
                zipcode = location_info["zipcode"]
                price = location_info["price"]
                bedrooms = location_info["bedrooms"]
                m2_living = location_info["m2_living"]



                html = "<p><strong>{}</strong></p>"
                html += "<p>Date:{}"
                html += "<p>Zipcode: {},00"
                html += "<p>Price: {},00 "
                html += "<br />Bedrooms: {}"
                html += "<br />m2_living: {}"
                html = html.format(id_imovel,date,zipcode,price,bedrooms,m2_living)

                popup = folium.Popup(
                    folium.Html(html, script=True),
                    max_width=500,
                )

                folium.Marker([location_info['lat'], 
                               location_info['long']],
                               popup=popup).add_to(marker_cluster)



            marker_cluster = MarkerCluster().add_to(mapa)
            return mapa



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

# House per water view

if f_waterview:
    data = data[data['waterfront'] == 1]
else:
    data = data.copy()
    
    
#=======================================
#  Layout NO STREAMLIT
#=======================================

st.title(' Overview - House Rocket')


st.title(""" Informações dos imóveis cadastrados no APP""")

tab1,tab2,tab3,tab4 = st.tabs(["Visão Overview ", "Exploração e Análise de Dados","Visão Price","Análise de preço ao longo do tempo"])

with tab1:


    with st.container():

        col1,col2,col3,col4= st.columns(4)

        data_metric = df.copy()


        with col1:
            metricas_id = data_metric.loc[:,'id'].nunique()
            col1.metric('Imóveis Cadastrados', metricas_id)




        with col2:
            vista_agua = (data_metric.loc[data_metric['waterfront'] == 1,'id']
                      .nunique())
            col2.metric('Imóveis Com Vista Para Água',vista_agua)


        with col3:
            tipo_casa = (data_metric.loc[data_metric['dormitory_type']=='house', 'id']
                         .nunique())

            col3.metric('Imóveis Tipo Casa',tipo_casa)


        with col4:
            price_median = data_metric.loc[:,'price'].median()

            col4.metric('Mediana do preço', price_median)

        st.dataframe(data)

    with st.container():

        st.title('Mapa das localizações dos imóveis')
        st.caption('⬅️ Filtre quais tipos de imóvel quer visualizar')
        mapa = localizacao_map(data)
        
        
        folium_static(mapa, width=1024, height= 600)

    
with tab2:
    df1 = df.copy()
    
    tab2.title('Exploração e Análise de Dados')
    tab2.subheader('Distribuição de Frequencia📊')
    
    
    #-------------------------------------------
    # GRAFICO DA QUANTIDADE DE IMOVEL POR NUMERO DE QUARTO
    
    bedrooms = df1[['id','bedrooms']].groupby('bedrooms').count().reset_index()

    
    fig = px.bar(bedrooms,x='bedrooms', y='id',color='bedrooms',
                labels = {'id': 'Quantidade de Imóvel', 'bedrooms':'Quartos'})
    fig.update_layout(title_text='Quantidade de Imóveis por Número de Quartos',title_font_size=20)


    tab2.plotly_chart(fig,use_container_width=True)
    tab2.markdown("""___""")
    

    
    # -------------------------------------------
    #GRAFICO DA QUANTIDADE DE IMOVEL POR ANDARES
    
    floors = df1[['id','floors']].groupby('floors').count().reset_index()

    
   
    fig = px.bar(floors,x='floors', y='id',color='floors',
                labels = {'id': 'Quantidade de Imóvel', 'floors':'Andares'})
    fig.update_layout(title_text='Quantidade de Imóveis por Andares',title_font_size=20)
    tab2.plotly_chart(fig,use_container_width=True)
    tab2.markdown("""___""")




    # -------------------------------------------
    # GRAFICO DA QUANTIDADE DE IMOVEL COM E SEM VISTA PARA AGUA 
    waterfront = df1[['id','is_waterfront']].groupby('is_waterfront').count().reset_index()
    

    fig = px.bar(waterfront,x='is_waterfront', y='id',color='is_waterfront',
                labels = {'id': 'Quantidade de Imóvel', 'is_waterfront':'Andares'})
    fig.update_layout(title_text='Quantidade de imóveis com e sem vista para água',title_font_size=20)
    tab2.plotly_chart(fig,use_container_width=True)
    

    

    
with tab3:
    
        
    
    tab3.title('Mediana de preço por Atributos ' )
    tab3.subheader('Visão de Planejamento📊')
    
    price_bedrooms = df1[['price','bedrooms']].groupby('bedrooms').median().reset_index().round(2)

    
    fig = px.bar(price_bedrooms,x='bedrooms',y='price',
                  color='price',labels = {'bedrooms': 'Quantidade Quartos', 'price':'Prec'})
    fig.update_layout(title_text='Mediana de preço por quartos',title_font_size=20)
    tab3.plotly_chart(fig,use_container_width=True)
    tab3.markdown("""___""")


    # -------------------------------------------
    floors = df1[['price', 'floors']].groupby('floors').median().reset_index().round(2)
    
    fig = px.bar(floors, x='floors',y='price',
                 color='price',labels = {'floors': 'Quantidade andares', 'price':'Preço'})
    fig.update_layout(title_text='Mediana de preço por Andares',title_font_size=20)
    tab3.plotly_chart(fig,use_container_width=True)  
    tab3.markdown("""___""")
    # -------------------------------------------
    
    
    waterfront = df1[['price','is_waterfront']].groupby('is_waterfront').median().reset_index().round(2)
    fig = px.bar(waterfront, x='is_waterfront',y='price',
                 color='price',labels = {'price': 'Preço', 'is_waterfront':'Com e sem vista para água'})
    fig.update_layout(title_text='Mediana de preços dos imóveis com vista e sem vista para água',title_font_size=20)
    tab3.plotly_chart(fig,use_container_width=True)  
    tab3.markdown("""___""")
    
    

    # -------------------------------------------
    bathrooms = df1[['price','bathrooms']].groupby('bathrooms').median().reset_index().round(2)
    
    
    
    fig = px.bar(bathrooms, x='bathrooms',y='price',
                 color='price',labels = {'price': 'Preço', 'bathrooms':'Banheiro'})
    fig.update_layout(title_text='Mediana de preços dos imóveis por quantidades de banheiros',title_font_size=20)
    tab3.plotly_chart(fig,use_container_width=True)  
    tab3.markdown("""___""")
    
    


with tab4:
    tab4.title('Análise de preço ao longo do tempo📈')
    tab4.subheader('Visão Estratégica📊')



    # -------------------------------------------
    by_month_year = df1[['price', 'month_year']].groupby('month_year').median().reset_index()
    fig = px.line(by_month_year, x='month_year',y='price')
    fig.update_layout(title_text='Variação Do Preço Por Mês',title_font_size=20)
    tab4.plotly_chart(fig,use_container_width=True)
    tab4.markdown("""___""")

    # -------------------------------------------
    by_year = df1[['price', 'yr_built']].groupby('yr_built').median().reset_index()
    
    fig = px.line(by_year, x='yr_built',y='price')
    fig.update_layout(title_text='Variação Do Preço Por Ano De Construção',title_font_size=20)
    tab4.plotly_chart(fig,use_container_width=True)
    tab4.markdown("""___""")
    
    
    # -------------------------------------------
    by_day = df1[['price', 'date']].groupby('date').median().reset_index()
    fig = px.line(by_day, x='date',y='price')
    fig.update_layout(title_text='Variação Do Preço Por Dia',title_font_size=20)
    tab4.plotly_chart(fig,use_container_width=True)
    
    
   


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

        
