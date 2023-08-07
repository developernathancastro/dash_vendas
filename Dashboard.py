import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide' )

def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return  f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)           #usuário vai inputar valores da minha lista criada acima

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'região':regiao.lower(), 'ano':ano}   ##colocando região em dicionario e transformando região em letra minuscula
response  = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')    ##transformando data de coluna do dataframe

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]  #filtra com os dados da filtro vendedores e traz no df dados somente os dados selecionados na lista


##Tabelas

#Tabelas de receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()        #agrupando compra por estado e trazendo a soma
receita_estados = dados.drop_duplicates(subset='Local da compra')               #removendo dados duplicados com base na coluna do estado da compra
receita_estados = receita_estados [['Local da compra', 'lat','lon']].merge(receita_estados.reset_index(), on= 'Local da compra', suffixes=('_local', '_total')).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].sum().reset_index() #colocando data da compra como index do dataframe   #agrupando por meses da colna  Data da Compra
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year  #armazenando informação de ano em nova coluna
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name() #armazenando informação do mês em nova coluna com seu respectivo nome

receita_categorias =  dados.groupby('Categoria do Produto') [['Preço']].sum().sort_values('Preço', ascending=False) #agrupando a receita por categoria e ordenando de forma decrescente o valor

#Tabelas de quantidade de vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

#Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count' ])) #agrupando dados dos vendedores e somando e contando receita


#Gráficos

fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat_local',
                                  lon= 'lon_total',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                hover_name='Local da compra',
                                  hover_data = {'lat_local': False, 'lon_total': False},
                                  title= 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers=True, #Identifica pontos nos meses
                            range_y=(0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita') #alterando nome do eixo y para receita

fig_receita_estados = px.bar(receita_estados.head(), #mostrando somente os 5 estados com maior receita
                             x= 'Local da compra',
                             y = 'Preço',
                             text_auto=True, #colocando o valor em cima de cada coluna
                            title= 'Top estados(Receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')#alterando nome do eixo y para receita

fig_receita_categorias = px.bar(receita_categorias,      #Não precisei passar o x e y devido a tabela ter soemnte duas informações(colunas)
                                text_auto=True,
                                title = 'Receita por categoria')

### Gráficos vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                     lat = 'lat',
                     lon= 'lon',
                     scope = 'south america',
                     #fitbounds = 'locations',
                     template='seaborn',
                     size = 'Preço',
                     hover_name ='Local da compra',
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_mensal = px.line(vendas_mensal,
              x = 'Mes',
              y='Preço',
              markers = True,
              range_y = (0,vendas_mensal.max()),
              color = 'Ano',
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

##Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), '$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de Vendas',formata_numero(dados['Preço'].count()))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), '$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de Vendas',formata_numero(dados['Preço'].count()))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart( fig_vendas_categorias,use_container_width=True)

with aba3:
    qtde_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), '$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores),
        x = 'sum',
        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores).index,
        text_auto = True,
        title = f'Top {qtde_vendedores} vendedores (Receita)')
        st.plotly_chart(fig_receita_vendedores)


    with coluna2:
        st.metric('Quantidade de Vendas',formata_numero(dados['Preço'].count()))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtde_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(
                                         qtde_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtde_vendedores} vendedores (Quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores, use_container_width = True)

#st.dataframe(dados)












#documentação streamlit: https://docs.streamlit.io/library/api-reference

#executar comando no terminal: streamlit run Dashboard.py