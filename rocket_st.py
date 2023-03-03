
import pandas as pd

from datetime import datetime

import streamlit as st

import plotly.express as px
import locale


st.set_page_config(layout='wide')
pd.set_option('display.float_format', lambda x: '%.2f' % x)




@st.cache(allow_output_mutation=True)
# Function

def get_data(path):
    data = pd.read_csv(path)


    return data



def per (val1,val2):
    perc = round(100 * (val2 - val1) / val1, 2)
    return perc


@st.cache(allow_output_mutation=True)
def convert_currency(currency):
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
    return locale.currency(currency, grouping=True)


def set_feature(data):
    # Removendo ids duplicados e permanecendo os mais recentes
    data = data.drop_duplicates(subset=['id'], keep='last').reset_index(drop=True)

    # Entendemos que o valor 33 foi um erro de digitação
    data.loc[data['bedrooms'] == 33, 'bedrooms'] = 3

    # Convert object to  date
    data['date'] = pd.to_datetime(data['date'])

    # Criando variavel apartir do ANO da variavel DATE
    data['year'] = pd.to_datetime(data['date']).dt.year

    # Criando variavel apartir do YEAR e MONTH da vairavel DATE.
    # Usaremos na hipotese 8
    data['month_year'] = data['date'].dt.strftime('%Y-%m')

    # Criando variavel apartir da semana do ano
    data['year_week'] = pd.to_datetime(data['date']).dt.strftime('%Y-%U')

    # Criando variavel apartir do MONTH da variavel DATE.
    # Usaremos na hípotese 9?
    data['month'] = pd.to_datetime(data['date']).dt.month

    # Alterando variável bathrooms de float para int
    data['bathrooms'] = data['bathrooms'].astype('int64')

    data['floors'] = data['floors'].astype('int64')
    # 3.077.2608
    # Converting variable to square meters
    data['sqft_living'] = data['sqft_living']* 0.3048
    data['sqft_above'] = data['sqft_above'] * 0.3048
    data['sqft_lot'] = data['sqft_lot'] * 0.3048
    data['sqft_basement'] = data['sqft_basement'] * 0.3048

    # renomeando colunas
    data.rename(columns={'sqft_living': 'm2_living',
                         'sqft_above': 'm2_above',
                         'sqft_lot': 'm2_lot',
                         'sqft_basement': 'm2_basement'}, inplace=True)

    # Criando variavel Ano de Construção e guardando os valores de acordo com a condição
    # Usaremos na hipotese1
    data['yr_construction'] = data['yr_built'].apply(lambda x: '1900 - 1954 ' if x <= 1954 else '1955 - 2015')

    # Transformando valor 'com_porao' e 'sem_porao'
    # Usaremos para a hipotese 3
    data['porao'] = data['m2_basement'].apply(lambda x: 'sem_porao' if x == 0 else 'com_porao')

    # Transformando o valor da variavel floors em 'house' e 'house_more_floors'
    data['floors_h7'] = data['floors'].apply(lambda x: 'house' if x <= 1 else 'more_floors')

    # Classificando estilo de casas por quantidades de quartos
    data['dormitory_type'] = data['bedrooms'].apply(lambda x: 'studio' if x == 1 else
    'apartament' if x == 2 else
    'house')

    # Modificando valor 0 e 1. Para "sem_vista" e "com_vista"
    # Usaremos na hipotese 2,8 e 9
    data['is_waterfront'] = data['waterfront'].apply(lambda x: 'com_vista' if x == 1 else 'sem_vista')

    # Criando a coluna de estação
    data['season'] = data['month'].apply(
        lambda x: 'winter' if (x == 12 or x <= 2) else 'spring' if (3 <= x < 6) else 'summer' if (6 <= x <= 8) else
        'Autumn')





    return data


def company_view(tab1):
    with tab1:
        st.title('House Rocket🏡‍🚀')
        st.image('https://www.gouache.fr/images-donnees/fiches/articles/images/champ___4/locauxcommerciaux6.jpg',
                 width=1000)
        st.subheader('O que a empresa faz:')
        st.markdown('House Rocket é uma plataforma fictícia de compras e vendas de imóveis')
        st.subheader('Objetivo da empresa:')
        st.markdown(
            'Gerar insights através da análise e manipulação dos dados para auxiliar na tomada de decisão pelo time de negócio.')
        st.markdown("""
                    ## **1. Negócio**
                    O CEO da House Rocket deseja que sua equipe de cientistas de dados usem os seus conhecimentos em análise e manipulação de dados.
                    Para encontrar as melhores oportunidades de compras, visando na maximização. 

                    ### **1.1 Questões**
                    O CEO deixou para o Time de Dados as seguintes perguntas:

                    1. Quais são os imóveis que a House Rocket deveria comprar e por qual preço?
                    2. Uma vez a casa comprada, qual o melhor momento para vendê-las e por qual preço?
                """)
        st.markdown("""
        ### **1.2 Premissas**
        * Date é referente ao dia que o imóvel foi disponibilizado para venda.
        * Assumimos que Ids duplicados são imóveis reavaliados. Portando mantemos os atualizados
        * Consideramos que o valor "33" na variavel "bedrooms", houve um erro de digitação. Portando mudamos para "3".
        * Imóveis no qual o ano de renovação é igual a 0 é considerado que não houve reforma.
        * Podem haver erros de digitação em alguns registros que devem ser tratados/removidos durante a limpeza dos dados.""")
    return None

def validating_hi(data):



    # - Hipóteses 1: Imóveis no ano de construção menor que 1955, são 50% mais baratos na média.
    # AGRUPANDO E BUSCANDO A MÉDIA DO PREÇO
    df1 = data[['price', 'yr_construction']].groupby('yr_construction').mean().reset_index()
    df1['porcentagem'] = df1['price'].pct_change() * 100
    #______________________________________________________
    #______________________________________________________

    # - Hipóteses 2: Imóveis com vista para água, são 30% mais caros, na média.
    #  AGRUPANDO E BUSCANDO A MÉDIA DOS IMÓVEIS COM E SEM VISTA PARA ÁGUA
    df2 = data[['waterfront', 'price']].groupby('waterfront').mean().reset_index()
    df2['porcentagem'] = df2['price'].pct_change() * 100

    # ______________________________________________________
    # ______________________________________________________

    # - Hipóteses 3: Imóveis sem porão, são -20% desvalorizados comparando com imóveis com porão

    df3 = data[['porao', 'price']].groupby('porao', ).mean().reset_index()

    df3['porcentagem'] = df3['price'].pct_change() * 100

    # ______________________________________________________
    # ______________________________________________________

    df9 = data.loc[data['is_waterfront'] == 'com_vista'].copy()

    h9 = df9[['season', 'price']].groupby('season').mean().reset_index()
    aux = h9.loc[(h9['season'] == 'summer') | (h9['season'] == 'winter')].copy().reset_index(drop=True)

    aux['pct'] = aux['price'].pct_change() * 100





    return df1,df2,df3,aux

def plot_insights(df1,df2,df3,tab2,aux,convert_currency):
    tab2.title("Análise de Insights")

    c1,c2, = tab2.columns(2)
    c3,c4 = tab2.columns(2)




    # Criando as métricas
    #antes de 1955
    c1.subheader('🏠 Imóveis antes de 1955')
    c1.metric(label="💲 Preço médio",value=str(convert_currency(round(df1.iloc[0][1],2))))

    #antes de 1955
    c1.subheader('🏠 Imóveis depois de 1955')
    c1.metric(label="💲 Preço médio", value=str(convert_currency(round(df1.iloc[1][1],2))),delta=str(df1.iloc[1][2].round(2))+'%')


    # Plot
    c1.bar_chart(data=df1, x='yr_construction', y='price', use_container_width=True)

    #______________________________________________________
    # ______________________________________________________


    #Criando as métricas

    #Sem vista
    c2.subheader('🏠 Imóveis sem vista ')
    c2.metric(label="💲 Preço médio", value=str(convert_currency(round(df2.iloc[0][1],2))))

    #Com vista
    c2.subheader('🏠 Imóveis com vista ')
    c2.metric(label="💲 Preço médio", value=str(convert_currency(round(df2.iloc[1][1],2))),delta=(df2.iloc[1][2].round(2)))

    # Plot
    c2.bar_chart(data=df2, x='waterfront', y='price', use_container_width=True)

    # ______________________________________________________
    # ______________________________________________________

    #Criando as métricas
    # Com basement
    c3.subheader('🏠 Imóveis com basement ')
    c3.metric(label="💲 Preço médio", value=str(convert_currency(round(df3.iloc[0][1], 2))))

    # Sem basement
    c3.subheader('🏠 Imóveis sem basement ')
    c3.metric(label="💲 Preço médio", value=str(convert_currency(round(df3.iloc[1][1], 2))),
              delta=str(df3.iloc[1][2].round(2)) + '%')
    #Plot
    c3.bar_chart(data=df3, x='porao', y='price', use_container_width=True)

    # ______________________________________________________
    # ______________________________________________________

    # Criando as métricas
    c4.subheader('🏠🌡️ Summer ')
    c4.metric(label="💲 Preço médio", value=str(convert_currency(round(aux.iloc[0][1], 2))))

    # Sem basement
    c4.subheader('🏠🌡 Winter ')
    c4.metric(label="💲 Preço médio", value=str(convert_currency(round(aux.iloc[1][1], 2))),
              delta=str(aux.iloc[1][2].round(2)) + '%')

    # Plot
    c4.bar_chart(data=aux,x='season',y='price',use_container_width=True)




    return None

def plot_estrategica(data,tab3):

    tab3.title('Exploração e Análise de Dados')
    tab3.subheader('Distribuição de Frequencia📊')
    c5,c6,c7 = tab3.columns(3)

    tab3.title('Média de preço por Atributos ' )
    tab3.subheader('Visão de Planejamento📊')
    c8,c9,c10, = tab3.columns(3)






    #-------------------------------------------
    df = data[['id','bedrooms']].groupby('bedrooms').count().reset_index()

    c5.caption('Quantidades de Imóveis por Número de Quartos🛏️️')
    c5.bar_chart(data=df,x='bedrooms',y='id')


    # -------------------------------------------
    df_floors = data[['id','floors']].groupby('floors').count().reset_index()

    c6.caption("Quantidades de Imóveis por Andares🏘️")
    c6.bar_chart(data=df_floors,x='floors',y='id')


    # -------------------------------------------
    df_waterfront = data[['id','is_waterfront']].groupby('is_waterfront').count().reset_index()
    c7.caption("Quantidades de Imóveis por Vista para Água🌉")
    c7.bar_chart(data=df_waterfront,x='is_waterfront',y='id')

    # -------------------------------------------
    # -------------------------------------------

    by_price = data[['price', 'bedrooms']].groupby('bedrooms').mean().reset_index().round(2)

    c8.caption("Média de preço por Quartos🛏️")
    c8.bar_chart(data=by_price, x='bedrooms', y='price')

    # -------------------------------------------
    by_floors = data[['price', 'floors']].groupby('floors').mean().reset_index().round(2)
    c9.caption('Média de preço por Andares🏘️')
    c9.bar_chart(data=by_floors, x='floors', y='price')

    # -------------------------------------------
    by_waterfront = data[['price','is_waterfront']].groupby('is_waterfront').mean().reset_index().round(2)
    c10.caption('Média de preços dos imóveis com vista e sem vista para água🌉')
    c10.bar_chart(data=by_waterfront, x='is_waterfront', y='price')
    # -------------------------------------------
    by_bathrooms = data[['price','bathrooms']].groupby('bathrooms').median().reset_index().round(2)
    tab3.caption('Média de preços dos imóveis por quantidades de banheiros🛁🚽')
    tab3.bar_chart(data=by_bathrooms, x='bathrooms', y='price')



    # -------------------------------------------
    # -------------------------------------------
    tab3.title('Análise de preço ao longo do tempo📈')
    tab3.subheader('Visão Estratégica📊')
    c11, c12, c13, = tab3.columns(3)


    # -------------------------------------------
    by_month_year = data[['price', 'month_year']].groupby('month_year').median().reset_index()
    c11.caption('Variação Do Preço Por Mês📈📅')
    c11.line_chart(data=by_month_year,x='month_year',y='price')
    # -------------------------------------------
    by_year = data[['price', 'yr_built']].groupby('yr_built').median().reset_index()
    c12.caption('Variação Do Preço Por Ano De Construção📈📅')
    c12.line_chart(data=by_year, x='yr_built',y='price')
    # -------------------------------------------
    by_day = data[['price', 'date']].groupby('date').median().reset_index()
    c13.caption('Variação Do Preço Por Dia📈📅')
    c13.line_chart(data=by_day,x='date',y='price')




    return None

def sugestao_buy(data,tab4,per,convert_currency):


    # ------------------------------------------------------------------------------------------------
    # mediana de price per zipcode
    zipcode_median = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()

    # juntei a variavel com o dataframe e troquei o nome da variavel
    data = pd.merge(data, zipcode_median, on='zipcode', how='inner')



    data.rename(columns={'price_y': 'price_median_zip'}, inplace=True)

    # fiz a condição de compra e nao compra / que pode ser feita com lambda tambem

    for i in range(len(data)):
        if (data.loc[i, 'price_x'] < data.loc[i, 'price_median_zip']) & (data.loc[i, 'condition'] >= 3):
            data.loc[i, 'status'] = 'compra'

        else:
            data.loc[i, 'status'] = 'nao_compra'
    ## ----------------------------------------------------------------------------------------





    # Carregando apenas os dados com compra

    df = data.loc[data['status']=='compra'].copy().reset_index(drop=True)

    #----------------------------------------------------------------------------------------------------------------
    # 1.Agrupando os dados por região, para diminuir a influencia de preço por região
    # 2. Buscar a mediana por região. Porque podem ter outliers
    # 3. Agrupando por season para eliminar a sazonalidade

    price_season = df[['price_x', 'zipcode', 'season']].groupby(['zipcode', 'season']).median().reset_index()

    # Trocando o nome da coluna (price)
    price_season.columns = ['zipcode', 'season', 'price_season']

    # Combinando o price_season com o Data
    df = pd.merge(df, price_season, on=['zipcode', 'season'], how='inner')
    ## ----------------------------------------------------------------------------------------


    # 1. Fazendo percentual de lucro pela coluna 'price_season'.
    # Na qual essa coluna elimina o fator região e isola a estação do ano


    df['price_sales'] = df.apply(lambda x: (x['price_x'] * 1.1)

    if (x['price_x'] >= x['price_season'])

    else (x['price_x'] * 1.3), axis=1)

    # Fiz o preço de venda menos o de compra, para saber o lucro
    # O imposto não está colocado na soma.
    df['lucro'] = df['price_sales'] - df['price_x']


    # ------------------------------------------------------------------------------------------------
    # Filter Price
    st.sidebar.subheader('Classifiquem os atributos desejadas ')
    st.sidebar.caption('Se fizer seleção de atributos, esses são obrigatórios (Price_x,Price_sales,Lucro,Lat,Long,ID)')
    f_attributes = st.sidebar.multiselect('Filtrar Colunas', df.columns)
    # ------------------------------------------------------------------------------------------


    # Filter Zipcode
    #st.sidebar.subheader('Classifiquem as regiões desejadas')
    f_zipcode = st.sidebar.multiselect('Filtrar CEP', df['zipcode'].unique())
    # ------------------------------------------------------------------------------------------


    # Filter Bedrooms
    f_bedrooms = st.sidebar.selectbox('Valor maximo de bedrooms',
                                      sorted(set(df['bedrooms'].unique())))
    #------------------------------------------------------------------------------------------


    # Filter bathrooms
    f_bathrooms = st.sidebar.selectbox('Valor maximo de bathrooms',
                                      sorted(set(df['bathrooms'].unique())))

    # ------------------------------------------------------------------------------------------

    # Filter Zipcode
    #st.sidebar.subheader('Classifique a estação do ano')

    f_season = st.sidebar.multiselect('Filtrar estação do ano', df['season'].unique())
    # ------------------------------------------------------------------------------------------

    # Filter Floors

    f_floors = st.sidebar.selectbox('Valor maximo de floors',
                                       sorted(set(df['floors'].unique())))

    # ------------------------------------------------------------------------------------------

    # Filter M2_LIVING
    m2_living_min = int(df['m2_living'].min())
    m2_living_max = int(df['m2_living'].max())
    m2_living_avg = int(df['m2_living'].mean())

    f_living = st.sidebar.slider('Selecione até o M2 living desejado',
                      m2_living_min,
                      m2_living_max,
                      m2_living_avg)

    #------------------------------------------------------------------------------------------

    # Filter M2_LIVING
    m2_lot_min = int(df['m2_lot'].min())
    m2_lot_max = int(df['m2_lot'].max())
    m2_lot_avg = int(df['m2_lot'].mean())

    f_lot = st.sidebar.slider('Selecione até o M2 lot desejado',
                             m2_lot_min,
                             m2_lot_max,
                             m2_lot_avg)






    # ------------------------------------------------------------------------------------------
    price_min = int(df['price_x'].min())
    price_max = int(df['price_x'].max())
    price_avg = int(df['price_x'].mean())

    st.sidebar.subheader('Selecionem o valor ')
    f_price = st.sidebar.slider('Price',
                                     price_min,
                                     price_max,
                                     price_avg)
    # ------------------------------------------------------------------------------------------

    # filters Date
    st.sidebar.subheader('Selecionem a data ')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    min_date = datetime.strptime(df['date'].min(), '%Y-%m-%d')
    max_date = datetime.strptime(df['date'].max(), '%Y-%m-%d')

    f_date = st.sidebar.slider('Date', min_date, max_date, max_date)

    df['date'] = pd.to_datetime(df['date'])
    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------

    #  filter Attributes

    if f_lot:
        df = df.loc[df['m2_lot'] < f_lot]


    if f_attributes ==[]:
        f_attributes = df.columns


    if f_price :
        f_price = df['price_x'] < f_price


    if f_zipcode != []:
        df = df.loc[df['zipcode'].isin(f_zipcode)]

    if f_bedrooms:
        df= df.loc[df['bedrooms'] < f_bedrooms]
    if f_bathrooms:
        df= df.loc[df['bathrooms'] < f_bathrooms]

    if f_season:
        df = df.loc[df['season'].isin(f_season)]

    if f_floors:
        df = df.loc[df['floors'] == f_floors]

    if f_living:
        df= df.loc[df['m2_living'] < f_living]



    if f_date:
        df= df.loc[df['date'] < f_date]





    ## ------------------------------------------------------------------------------------------------
    tab4.title('Exposição de Imóveis🏘️')


    tab4.dataframe(df[f_attributes][f_price])

    # ----------------------------------------------s----------------------------------------------



    st.sidebar.subheader('Pressione o Botão se deseja comprar os imóveis selecionados🛒🧾')
    if st.sidebar.button('Comprar'):


        # Métricas de Vendas
        tab4.title('Tabela de Imóveis Vendidos💲🏠 ')

        # Salvando os atributos filtrados

        tab4.dataframe(df[f_attributes][f_price])

        df_compra =df[f_attributes][f_price].copy()

        # Plot dos imóveis escolhidos




        c15, c16, c17 ,c18= tab4.columns(4)

        # Criando medidores dos imóveis comprados
        c15.metric(label="💲Investimento", value=convert_currency(round(df_compra['price_x'].sum(),2)))
        c16.metric(label="💲 Soma do valor total com o lucro ", value= convert_currency(round(df_compra['price_sales'].sum(),1)))
        c17.metric(label="💲Lucro",value=convert_currency(round(df_compra['lucro'].sum(),2)),delta= str(per(df_compra['price_x'].sum(),df_compra['price_sales'].sum()))+'%')
        c18.metric(label='Número de imóveis comprados 🏠',value= df_compra['id'].count())


        # Plot Map
        tab4.title('Localização dos Imóveis🗺️')
        houses = df[f_attributes][f_price].copy()



        fig = px.scatter_mapbox(houses,
                                hover_data=['price_x', 'price_sales', 'lucro'],
                                lat='lat',
                                lon='long',
                                size='price_x',
                                color_continuous_scale=px.colors.diverging.PuOr,
                                size_max=15,
                                zoom=10)

        fig.update_layout(mapbox_style="open-street-map")

        fig.update_layout(height=600, margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
        tab4.plotly_chart(fig)



    return None


if __name__ == '__main__':
    path = '/Users/natanferreiralima/repos_mac/house_rocket/datasets/kc_house_data.csv'
    data = get_data(path)


    # Transformation
    data = set_feature(data)
    df1,df2,df3,aux= validating_hi(data)
    tab1,tab2,tab3,tab4 = st.tabs([" Company Vision📋 ","Insights📉💡" ,"Visão Estratégica 🧠","📥 Sugestão de Compra"])


    company_view(tab1)
    validating_hi(data)
    plot_insights(df1,df2,df3,tab2,aux,convert_currency)
    plot_estrategica(data,tab3)
    sugestao_buy(data,tab4,per,convert_currency)








