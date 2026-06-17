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

# Inicializar ou carregar o arquivo de dados
DATA_FILE = "dados_shield.csv"
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
    except:
        df = pd.DataFrame(columns=["Data", "Atividade", "Horas", "Impacto"])
else:
    df = pd.DataFrame(columns=["Data", "Atividade", "Horas", "Impacto"])

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
    opcoes_mes = sorted(df['Mes_Ano'].unique(), reverse=True)
else:
    opcoes_mes = [datetime.now().strftime('%m/%Y')]

mes_selecionado = st.sidebar.selectbox("Selecione o mês de referência:", opcoes_mes)

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
            # Trava para impedir lançamentos retroativos em Maio (Apenas Junho/2026 em diante)
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
                df.to_csv(DATA_FILE, index=False)
                st.sidebar.success("Atividade registrada com sucesso!")
                st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("📊 Histórico de Atividades")

# Filtrar dados da tela pelo mês selecionado
if not df.empty:
    df_filtrado = df[df['Mes_Ano'] == mes_selecionado].sort_values(by="Data", ascending=False)
else:
    df_filtrado = pd.DataFrame()

if df_filtrado.empty:
    st.info(f"Nenhuma atividade registrada para o período {mes_selecionado}.")
else:
    # Métricas rápidas no topo
    total_atividades = len(df_filtrado)
    total_horas = df_filtrado['Horas'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Atividades no Mês", f"{total_atividades}")
    col2.metric("Total de Horas Dedicadas", f"{total_horas}h")
    
    st.write("---")
    
    # Listagem de Atividades
    for index, row in df_filtrado.iterrows():
        st.markdown(f"""
            <div class="card-atividade">
                <h4>📅 Data: {row['Data'].strftime('%d/%m/%Y')}</h4>
                <p><b>O que foi feito? (Atividade):</b><br>{row['Atividade']}</p>
                <p><b>Horas Gastas:</b> {row['Horas']}h</p>
                <p><b>Impacto Estratégico:</b><br>{row['Impacto']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão de Exclusão (SÓ APARECE SE O MODO EDITOR ESTIVER ATIVADO)
        if modo_editor:
            # Impedir exclusão de registros de Maio
            if row['Data'].month == 5 and row['Data'].year == 2026:
                st.warning("🔒 Registros de Maio não podem ser excluídos.")
            else:
                if st.button(f"🗑️ Excluir Lançamento #{index}", key=f"del_{index}"):
                    df = df.drop(index)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Registro excluído!")
                    st.rerun()
