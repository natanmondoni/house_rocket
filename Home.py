import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='📊',
    layout='wide')


image_path = ('houserocket.png')
image = Image.open( image_path)


st.sidebar.image(image)


st.title('House Rocket🏡‍🚀')
        
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
* Podem haver erros de digitação em alguns registros que devem ser tratados/removidos durante a limpeza dos dados.



### Ask for Help
    
- https://www.linkedin.com/in/natã-ferreira-lima-13300193/""")
