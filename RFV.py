import numpy as np 
import pandas as pd
import streamlit as st
from datetime import datetime
import os

os.makedirs('./output', exist_ok=True)

st.set_page_config(page_title = 'RFV clientes',
        layout="wide",
        initial_sidebar_state='expanded'
    )

@st.cache_data()
def convert_df(df):
    return df.to_csv(index = False).encode('utf-8')

@st.cache_data()
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output , engine='xlsxwriter')
    df.to_excel(writer, index = False , sheet_name = 'Sheet 1')
    writer.save()
    processed_data = output.getvalue()
    
    return processed_data

def recencia_class(x, r, q_dict):
    """Classifica como melhor o menor quartil 
       x = valor da linha,
       r = recencia,
       q_dict = quartil dicionario   
    """
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'


def freq_val_class(x, fv, q_dict):
    """Classifica como melhor o maior quartil 
       x = valor da linha,
       fv = frequencia ou valor,
       q_dict = quartil dicionario   
    """
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'

def main():
    # Configuração inicial da página da aplicação
    
    # Título principal da aplicação
    st.write("""# RFV 
             
             significa recência, frequência, valor e é utilizado para segmentação de clientes baseado no comportamento de compras dos clientes e agrupa eles em clusters parecidos. Utilizando esse tipo de agrupamento podemos realizar ações de marketing e CRM melhores direcionadas, ajudando assim na personalização do conteúdo e até a retenção de clientes.

                Para cada cliente é preciso calcular cada uma das componentes abaixo:

                Recência (R): Quantidade de dias desde a última compra.
                Frequência (F): Quantidade total de compras no período.
                Valor (V): Total de dinheiro gasto nas compras do período.
                E é isso que iremos fazer abaixo.""")
    
    st.markdown("---")
    
    st.sidebar.write("## Suba o arquivo")
    data_file1 = st.sidebar.file_uploader("Marketing clientes" , type = ['csv' , 'xlsx'])

    if (data_file1 is not None):

        st.write("## Recência (R)")

        df_compras = pd.read_csv(r"C:\Users\g_abi\OneDrive\Documentos\Data Science\Data Science EBAC\Módulo 31  - RFV Deploy\Atividade 1\input\dados_input 1.csv",

                                parse_dates=['DiaCompra'])

        dia_atual = datetime(2021, 12, 9)
        st.write("Dia máximo na base de dados", dia_atual)

        st.write("Quantos dias faz desde a última compra?")



        df_recencia = df_compras.groupby(by='ID_cliente',
                                        as_index=False)['DiaCompra'].max()
        df_recencia.columns = ['ID_cliente', 'DiaUltimaCompra']
        df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(
            lambda x: (dia_atual - x).days)
        st.write(df_recencia.head())

        df_recencia.drop('DiaUltimaCompra', axis=1, inplace=True)

        st.write("## Frequência (F)")

        df_frequencia = df_compras[['ID_cliente', 'CodigoCompra'
                                    ]].groupby('ID_cliente').count().reset_index()
        df_frequencia.columns = ['ID_cliente', 'Frequencia']
        st.write(df_frequencia.head())

        st.write("## Valor (R)")

        df_valor = df_compras[['ID_cliente', 'ValorTotal'
                            ]].groupby('ID_cliente').sum().reset_index()
        df_valor.columns = ['ID_cliente', 'Valor']
        st.write(df_valor.head())

        st.write("## Tabela final")
        df_RF = df_recencia.merge(df_frequencia, on='ID_cliente')
        df_RFV = df_RF.merge(df_valor, on='ID_cliente')
        df_RFV.set_index('ID_cliente', inplace=True)

        st.write(df_RFV.head())

        st.write("## Segmentação por RFV")


        quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])
        quartis.to_dict()
        st.write(quartis)


        st.write("## Tabela após criação do grupos")
        df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class,
                                                        args=('Recencia', quartis))
        df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class,
                                                        args=('Frequencia', quartis))
        df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class,
                                                    args=('Valor', quartis))

        df_RFV['RFV_Score'] = (df_RFV.R_quartil + df_RFV.F_quartil +
                            df_RFV.V_quartil)
        
        st.write(df_RFV.head())

        st.write("## Quantidade de clientes por grupos")
        st.write(df_RFV['RFV_Score'].value_counts())

        
        st.write("## Clientes com menor recência, maior frequência e maior valor")
        st.write(df_RFV[df_RFV['RFV_Score'] == 'AAA'].sort_values('Valor',
                                                        ascending=False).head(10))

        st.write("### Ações de marketing/CRM")

        dict_acoes = {
            'AAA':
            'Enviar cupons de desconto, Pedir para indicar nosso produto pra algum amigo, Ao lançar um novo produto enviar amostras grátis pra esses.',
            'DDD':
            'Churn! clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'DAA':
            'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'CAA':
            'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar'
        }

        df_RFV['acoes de marketing/crm'] = df_RFV['RFV_Score'].map(dict_acoes)
        st.write(df_RFV)

        df_RFV.to_excel('./output/RFV.xlsx')

if __name__ == '__main__':
	main()