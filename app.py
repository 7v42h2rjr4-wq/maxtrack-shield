import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página - Interface de Alta Performance
st.set_page_config(page_title="MAXTRACK SHIELD // PERFORMANCE", layout="wide", initial_sidebar_state="expanded")

# Estilização Cyberpunk/Neon de alto contraste
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #020612; border-right: 2px solid #00E5FF; }
    h1, h2, h3, h4 { color: #00E5FF !important; font-family: 'Segoe UI', Roboto, sans-serif; font-weight: 800; }
    p, span, label { color: #FFFFFF !important; }
    div.stButton > button {
        background-color: #001A24; color: #00E5FF; border: 2px solid #00E5FF; border-radius: 6px;
        font-weight: bold; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2); transition: all 0.3s;
    }
    div.stButton > button:hover { background-color: #00E5FF; color: #000000; box-shadow: 0 0 20px #00E5FF; }
    .card-atividade {
        background-color: #010A15; border: 1px solid #00FF66; border-radius: 8px; 
        padding: 18px; margin-bottom: 15px; box-shadow: 3px 3px 12px rgba(0, 255, 102, 0.1);
    }
    .card-data { color: #00FF66 !important; font-weight: bold; font-size: 1.1em; }
    [data-testid="stMetricLabel"] { font-size: 1.1rem !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO DO ARQUIVO COM MEMÓRIA CACHEADA (SESSION STATE) ---
if 'dados_backup' not in st.session_state:
    CANDIDATOS = [
        "Maxtrack_Shield/dados_shield.csv",
        "maxtrack_shield/dados_shield.csv",
        "dados_shield.csv",
        "Maxtrack_Shield/dados_shield_recuperado.csv"
    ]
    
    DATA_FILE = "dados_shield.csv"
    df_inicial = pd.DataFrame(columns=["Data", "Atividade", "Horas", "Impacto"])
    
    for caminho in CANDIDATOS:
        if os.path.exists(caminho):
            DATA_FILE = caminho
            try:
                temp_df = pd.read_csv(caminho, sep=';')
                if 'Data' not in temp_df.columns or temp_df.shape[1] < 3:
                    temp_df = pd.read_csv(caminho, sep=',')
                if 'Data' in temp_df.columns:
                    df_inicial = temp_df
                    df_inicial['Data'] = pd.to_datetime(df_inicial['Data'])
                    break
            except:
                continue
                
    st.session_state['dados_backup'] = df_inicial
    st.session_state['caminho_arquivo'] = DATA_FILE

# Recupera o DataFrame ativo da memória estável
df = st.session_state['dados_backup']
DATA_FILE = st.session_state['caminho_arquivo']

# --- BARRA LATERAL ---
st.sidebar.title("🛡️ SHIELD // PRO")

st.sidebar.subheader("🔒 Autenticação")
senha = st.sidebar.text_input("Senha de Editor:", type="password")

if senha == "maxtrack2026":
    modo_editor = True
    st.sidebar.success("MODO CONFIGURAÇÃO ATIVO")
else:
    modo_editor = False
    if senha != "":
        st.sidebar.error("Acesso de Leitura.")
    else:
        st.sidebar.info("Modo Visualização (Gestão)")

st.sidebar.subheader("📅 Período")
if not df.empty:
    df['Mes_Ano'] = df['Data'].dt.strftime('%m/%Y')
    opcoes_mes = ["Ver Todos"] + sorted(df['Mes_Ano'].unique(), reverse=True)
else:
    opcoes_mes = ["Ver Todos", datetime.now().strftime('%m/%Y')]

mes_selecionado = st.sidebar.selectbox("Selecione o período:", opcoes_mes)

# Formulário de Cadastro conectado à Memória Ativa
if modo_editor:
    st.sidebar.subheader("🚀 Novo Registro")
    with st.sidebar.form(key="form_cadastro", clear_on_submit=True):
        nova_data = st.date_input("Data", datetime.now())
        nova_ativ = st.text_area("Atividade Realizada")
        nova_hora = st.number_input("Horas Dedicadas", min_value=0.5, max_value=24.0, step=0.5, value=1.0)
        novo_impacto = st.text_area("Impacto no Negócio")
        
        btn_salvar = st.form_submit_button("🔥 PUBLICAR AGORA")
        
        if btn_salvar and nova_ativ and novo_impacto:
            if nova_data.month == 5 and nova_data.year == 2026:
                st.sidebar.error("⚠️ Registros de Maio consolidados.")
            else:
                novo_registro = pd.DataFrame({
                    "Data": [pd.to_datetime(nova_data)],
                    "Atividade": [nova_ativ],
                    "Horas": [nova_hora],
                    "Impacto": [novo_impacto]
                })
                # Atualiza na memória do Session State na mesma hora
                st.session_state['dados_backup'] = pd.concat([df, novo_registro], ignore_index=True)
                
                # Tenta gravar em arquivo por segurança (se o servidor permitir)
                try:
                    st.session_state['dados_backup'].to_csv(DATA_FILE, index=False, sep=';')
                except:
                    pass
                    
                st.sidebar.success("Registrado na memória!")
                st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("⚡ DASHBOARD DE PRODUTIVIDADE EM TEMPO REAL")
st.write("---")

if not df.empty:
    if mes_selecionado == "Ver Todos":
        df_filtrado = df.sort_values(by="Data")
    else:
        df_filtrado = df[df['Mes_Ano'] == mes_selecionado].sort_values(by="Data")
else:
    df_filtrado = pd.DataFrame()

if df_filtrado.empty:
    st.info("Aguardando sincronização de dados...")
else:
    # 1. KPIs Impactantes
    total_atividades = len(df_filtrado)
    total_horas = df_filtrado['Horas'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color: #00E5FF !important; margin-bottom:0;'>Volume de Entregas</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color: #00E5FF !important; font-size: 3.5rem; margin-top:0;'>{total_atividades}</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='color: #00FF66 !important; margin-bottom:0;'>Carga Horária Total</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color: #00FF66 !important; font-size: 3.5rem; margin-top:0;'>{total_horas}h</h1>", unsafe_allow_html=True)
    
    st.write("---")
    
    # 2. SEÇÃO DE GRÁFICOS - MENSAL CONSOLIDADO
    st.subheader("📊 Mapeamento Acumulado Mensal")
    
    NOMES_MESES = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    df_mes = df_filtrado.copy()
    df_mes['Num_Mes'] = df_mes['Data'].dt.month
    df_mes['Mês'] = df_mes['Num_Mes'].map(NOMES_MESES)
    
    df_grafico_mensal = df_mes.groupby(['Num_Mes', 'Mês'])['Horas'].sum().reset_index()
    df_grafico_mensal = df_grafico_mensal.sort_values(by='Num_Mes')
    df_grafico_mensal = df_grafico_mensal.set_index('Mês')
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("<p style='color: #00E5FF; font-weight: bold;'>⚡ Total de Horas Dedicadas por Mês (Barras)</p>", unsafe_allow_html=True)
        st.bar_chart(df_grafico_mensal[['Horas']], use_container_width=True)
        
    with g_col2:
        st.markdown("<p style='color: #00FF66; font-weight: bold;'>📈 Evolução Comparativa Mensal (Linhas)</p>", unsafe_allow_html=True)
        st.line_chart(df_grafico_mensal[['Horas']], use_container_width=True)
    
    st.write("---")
    
    # 3. LISTAGEM EM FORMATO CARDS NEON
    st.subheader("📋 Histórico Executivo de Atividades")
    df_lista = df_filtrado.sort_values(by="Data", ascending=False)
    
    for index, row in df_lista.iterrows():
        try:
            data_formatada = row['Data'].strftime('%d/%m/%Y')
        except:
            data_formatada = str(row['Data'])

        st.markdown(f"""
            <div class="card-atividade">
                <span class="card-data">📅 DATA DA ENTREGA: {data_formatada}</span>
                <p style="margin-top: 10px;"><b>🔹 Descrição da Atividade:</b><br>{row['Atividade']}</p>
                <p><b>⏱️ Tempo Alocado:</b> <span style="color: #00E5FF; font-weight:bold;">{row['Horas']} horas</span></p>
                <p style="margin-bottom: 0;"><b>🎯 Impacto Gerado:</b><br>{row['Impacto']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if modo_editor:
            if hasattr(row['Data'], 'month') and row['Data'].month == 5 and row['Data'].year == 2026:
                st.warning("🔒 Histórico consolidado.")
            else:
                if st.button(f"🗑️ APAGAR REGISTRO #{index}", key=f"del_{index}"):
                    st.session_state['dados_backup'] = df.drop(index)
                    try:
                        st.session_state['dados_backup'].to_csv(DATA_FILE, index=False, sep=';')
                    except:
                        pass
                    st.success("Removido!")
                    st.rerun()
