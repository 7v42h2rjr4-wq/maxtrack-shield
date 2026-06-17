import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página com a paleta Maxtrack (Deep Navy)
st.set_page_config(page_title="MAXTRACK SHIELD // PRO", layout="wide", initial_sidebar_state="expanded")

# Estilização customizada para fundo preto e detalhes em azul petróleo/navy (Sem cinza)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #050C1A; border-right: 1px solid #0A1931; }
    h1, h2, h3, p, span { color: #FFFFFF !important; }
    div.stButton > button {
        background-color: #0A1931; color: #FFFFFF; border: 1px solid #15305B; border-radius: 4px;
    }
    div.stButton > button:hover { background-color: #15305B; border-color: #1E4687; }
    .card-atividade {
        background-color: #020813; border: 1px solid #0A1931; border-radius: 6px; padding: 15px; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE BUSCA DE ARQUIVO ULTRA-RESISTENTE ---
# Lista de caminhos possíveis para o Python testar no GitHub
CANDIDATOS = [
    "Maxtrack_Shield/dados_shield.csv",
    "maxtrack_shield/dados_shield.csv",
    "dados_shield.csv",
    "Maxtrack_Shield/dados_shield_recuperado.csv"
]

DATA_FILE = None
df = pd.DataFrame(columns=["Data", "Atividade", "Horas", "Impacto"])

# Procura o arquivo vivo em cada um dos caminhos
for caminho in CANDIDATOS:
    if os.path.exists(caminho):
        DATA_FILE = caminho
        try:
            # Tenta ler com o padrão ponto-e-vírgula do Excel brasileiro
            temp_df = pd.read_csv(caminho, sep=';')
            if 'Data' not in temp_df.columns or temp_df.shape[1] < 3:
                # Se falhar, tenta com vírgula normal
                temp_df = pd.read_csv(caminho, sep=',')
            
            if 'Data' in temp_df.columns:
                df = temp_df
                df['Data'] = pd.to_datetime(df['Data'])
                break # Arquivo encontrado e carregado com sucesso!
        except:
            continue

# Se nenhum foi achado, define o padrão na raiz para não quebrar
if DATA_FILE is None:
    DATA_FILE = "dados_shield.csv"

# --- BARRA LATERAL ---
st.sidebar.title("🛡️ MAXTRACK SHIELD")

# Trava de Segurança por Senha para Modo Editor
st.sidebar.subheader("🔒 Autenticação")
senha = st.sidebar.text_input("Digite a senha para editar/lançar:", type="password")

# Definição do modo (Apenas você sabe a senha 'maxtrack2026')
if senha == "maxtrack2026":
    modo_editor = True
    st.sidebar.success("Modo Editor Ativado!")
else:
    modo_editor = False
    if senha != "":
        st.sidebar.error("Senha incorreta. Modo Visualização Ativado.")
    else:
        st.sidebar.info("Modo Visualização (Apenas Leitura)")

# Filtro de Dashboard (Disponível para todos)
st.sidebar.subheader("📅 Filtro do Dashboard")
if not df.empty:
    df['Mes_Ano'] = df['Data'].dt.strftime('%m/%Y')
    opcoes_mes = ["Ver Todos"] + sorted(df['Mes_Ano'].unique(), reverse=True)
else:
    opcoes_mes = ["Ver Todos", datetime.now().strftime('%m/%Y')]

mes_selecionado = st.sidebar.selectbox("Selecione o período:", opcoes_mes)

# Formulário de Cadastro (SÓ APARECE SE O MODO EDITOR ESTIVER ATIVADO)
if modo_editor:
    st.sidebar.subheader("🚀 Registrar Atividade")
    with st.sidebar.form(key="form_cadastro", clear_on_submit=True):
        nova_data = st.date_input("Data da Atividade", datetime.now())
        nova_ativ = st.text_area("O que foi feito? (Atividade)")
        nova_hora = st.number_input("Horas Gastas", min_value=0.5, max_value=24.0, step=0.5, value=1.0)
        novo_impacto = st.text_area("Impacto Estratégico")
        
        btn_salvar = st.form_submit_button("Salvar Registro")
        
        if btn_salvar and nova_ativ and novo_impacto:
            # Trava para impedir lançamentos retroativos em Maio
            if nova_data.month == 5 and nova_data.year == 2026:
                st.sidebar.error("⚠️ Os registros de Maio/2026 foram consolidados e estão travados para edição.")
            else:
                novo_registro = pd.DataFrame({
                    "Data": [pd.to_datetime(nova_data)],
                    "Atividade": [nova_ativ],
                    "Horas": [nova_hora],
                    "Impacto": [novo_impacto]
                })
                df = pd.concat([df, novo_registro], ignore_index=True)
                df.to_csv(DATA_FILE, index=False, sep=';')
                st.sidebar.success("Atividade registrada com sucesso!")
                st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("📊 Histórico de Atividades")

# Filtrar dados da tela de acordo com a seleção (Ver Tudo ou Mês Específico)
if not df.empty:
    if mes_selecionado == "Ver Todos":
        df_filtrado = df.sort_values(by="Data", ascending=False)
    else:
        df_filtrado = df[df['Mes_Ano'] == mes_selecionado].sort_values(by="Data", ascending=False)
else:
    df_filtrado = pd.DataFrame()

if df_filtrado.empty:
    st.info("Buscando dados... Se o histórico não carregar, verifique se o arquivo .csv foi commitado corretamente no GitHub.")
else:
    # Métricas rápidas no topo
    total_atividades = len(df_filtrado)
    total_horas = df_filtrado['Horas'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Atividades Exibidas", f"{total_atividades}")
    col2.metric("Total de Horas Dedicadas", f"{total_horas}h")
    
    st.write("---")
    
    # Listagem de Atividades
    for index, row in df_filtrado.iterrows():
        try:
            data_formatada = row['Data'].strftime('%d/%m/%Y')
        except:
            data_formatada = str(row['Data'])

        st.markdown(f"""
            <div class="card-atividade">
                <h4>📅 Data: {data_formatada}</h4>
                <p><b>O que foi feito? (Atividade):</b><br>{row['Atividade']}</p>
                <p><b>Horas Gastas:</b> {row['Horas']}h</p>
                <p><b>Impacto Estratégico:</b><br>{row['Impacto']}</p>
            </div>
        """, unsafe_allow_html=True)
