# House_Rocket
This repository contains files and script to build a company strategy dashboard.

# 1. Descrição do problema de negócio:

A House Rocket é uma empresa fictícia que trabalha com a compra e venda de imóveis. A equipe de negócio da empresa precisa decidir quais são as melhores opções de imóveis para compra. Devido a grande quantidade de imóveis no portfólio e da quantidade de atributos que cada imóvel possui, é demandada uma análise mais criteriosa e técnica. Porém, realizar o trabalho manualmente é muito demorado e pode levar a decisões precipitadas. Deste modo, é necessária a realização de um projeto para avaliar quais são as melhores estratégias para que a empresa consiga escolher bons imóveis para a compra, aumentando o seu faturamento.

# 2. Questões de negócio:

2.1. Quais são os imóveis que a House Rocket deveria comprar?

2.2. Uma vez comprados os imóveis, qual o melhor momento para vendê-los e por qual preço?

# 3. Base de dados e descrição dos atributos:

# 3.1. Dados disponíveis em: https://www.kaggle.com/harlfoxem/housesalesprediction/discussion/207885.

# 3.2. Descrição dos atributos (colunas):

|Columns|Description|
| --- | --- |
|'id':| código do imóvel|.
|'date':| data em que o imóvel foi vendido.|
|'price':| preço de venda do imóvel.|
|'bedrooms':|quantidade de quartos.|
|'bathrooms': |quantidade de banheiros.|
|'sqft_living': |tamanho interno do imóvel em ft.|
|'sqft_lot': |tamanho do lote em ft.|
|'floors': |quantidade de andares.|
|'waterfront': |se possui vista para o mar (1) ou não (0).|
|'view': |qualidade da vista (0 até 4).|
|'condition': |condição do imóvel (1 até 5).|
|'grade': |qualidade do design e da construção (1 até 13).|
|'sqft_above': |tamanho do andar superior (ou do único andar).|
|'sqft_basement': |tamanho do andar inferior (porão).|
|'yr_built': |ano de construção do imóvel.|
|'yr_renovated': |ano de reforma do imóvel (se reformado).|
|'zipcode': |localidade.|
|'lat': |latitude.|
|'long': |longitude.|
|'sqft_living15': |tamanho interno do imóvel em ft dos 15 vizinhos mais próximos.|
|'sqft_lot15': |tamanho do lote em ft dos 15 vizinhos mais próximos.|


# 4. Premissas de negócio:

# 4.1 Premissas
 - Date é referente ao dia que o imóvel foi disponibilizado para venda.
 - Assumimos que Ids duplicados são imóveis reavaliados. Portando mantemos os atualizados
 Consideramos que o valor "33" na variavel "bedrooms", houve um erro de digitação. Portando mudamos para "3".
 - Imóveis no qual o ano de renovação é igual a 0 é considerado que não houve reforma.
 - Podem haver erros de digitação em alguns registros que devem ser tratados/removidos durante a limpeza dos dados.

# 4.2. Foram criados novos atributos para a análise:


'floors_h7': Derivada da coluna Floors. Onde a coluna floors_h7 recebe os valores; menor ou igual a 1 é considerado 'house', diferente disso recebe o valor 'more_floors'.

'porao': Derivada da coluna m2_basement. Onde a coluna porao recebe os valores; sem_porao ou com_porao

'yr_construction': Derivada da coluna yr_built. Onde a coluna yr_construction recebe os imóveis do periodo 1900 - 1954 a 1955 - 2015.

'is_waterfront': indica se o imóvel possui vista para o mar ('is_waterfront' == com_vista) ou não ('is_waterfront' == sem_vista).

'dormitory_type': Derivada da coluna bedrooms. Onde a coluna nova recebe os seguintes valores; studio, apartament, house.

'year': retorna o ano do imóvel de acordo com a coluna 'date'.

'month': retorna o mês do imóvel de acordo com a coluna 'date'.

'year_week'; Derivada da coluna date. Onde a coluna nova recebe a semana e o ano.

'month_year'': retorna o ano e o mês do imóvel de acordo com a coluna 'date'.

'season': Derivada da coluna month. onde a colina season recebe os seguintes valores; winter, spring, summer, autumn.


# 5. Estrategia da solução:

# 5.1 Ferramentas utilizadas:

Python 3.10.8;
PyCharm Community;
Jupyter Notebook;
Streamlit.
# 5.2 Produto final:

Relatório 'purchase_recommendations.csv' com sugestões de compra de imóveis;
Relatório 'selling_recommendations.csv' com sugestões de preço de venda de imóveis e momento de venda de imóveis;
Utilizando o framework Streamlit Cloud para visualização,localização dos imóveis com o mapa interativo e exploração dos dados.Na janela Overview podemos realizar pesquisas através dos filtros, analisar as métricas dos imóveis.

# 5.3 Planejamento para a criação do relatório de sugestão de compra dos imóveis:

- Foram coletados os dados e aplicadas as premissas de negócio.
- Os imóveis estão com duas condições pre estabelecidas para compra.
   1. O preço do imóvel tem que ser a baixo do valor mediano da sua região.
   2. As condições dos imóveis deve estar maior ou igual a 3.
   
- Para que a experiencia seja agradável, proporcionamos filtros interativos, assim o time de negócio poderar realizar sua proprias pesquisas.
- Os imóveis foram agrupados de acordo com a sua localidade por meio da coluna 'zipcode'.
- Foram determinadas as medianas dos preços para cada localidade.

# 5.4 Planejamento para a criação do relatório de sugestão de venda dos imóveis:

- Os imóveis foram agrupados de acordo com a sua localidade e sazonalidade.

- Foram determinadas as medianas dos preços para cada localidade e sazonalidade.

- Foi criado um novo atributo: 'price_sales'
'price_sales': representa o preço pelo qual os imóveis devem ser vendidos. Imóveis com preço abaixo do preço da mediana são vendidos pelo preço de compra acrescido de 30%, imóveis com imóveis com preço acima da mediana são vendidos pelo preço de compra acrescido de 10%.


# 6.1. Hipóteses:
Nossas hipóteses são totalmente interativas atráves dos dois filtros; Data e Preço.
Dessa forma o time de negócio consegue ter uma autonomia melhor na toma de decisão.

Seguem as Hipóteses:

- Hipótese 1: Imóveis no ano de construção menor que 1955, são 50% mais baratos na média.

- Hipótese 2: Imóveis com vista para água, são 30 % mais caros, na média.

- Hipóteses 3: Imóveis sem porão, são -20% desvalorizados comparando com imóveis com porão.

- Hipótese 4: Imóveis tipo casa são 30% mais em conta do que imóveis com mais de 1 andar.

# 7. Resultados financeiros:
Como fizemos algo mais inderativo para o time de negó
cio. O resultado financeiro vária conforme as buscas pelos filtros.

# 8. Conclusão:
Não só buscamos responder as perguntas do time de negócio, como deixamos o projeto o mais interativo possível.
Com esse painel de métricas, vamos poder explorar ainda mais e assim ter uma tomada de decisão com base nas pesquisas do time de negócio.

# 9.Próximo passos:
- Aplicação de mais filtros.
- Novas hipóteses.
- Implementar o modelo de negócio.
