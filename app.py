import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA PROFISSIONAL ---
st.set_page_config(
    page_title="MAXTRACK SHIELD // PRO", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- IDÊNTICO À IDENTIDADE VISUAL EXECUTIVA (FONTE E CORES PREMIUM) ---
st.markdown("""
    <style>
    /* Fundo profundamente escuro e textos nítidos */
    .stApp { background-color: #030712; color: #FFFFFF; }
    
    /* Barra lateral corporativa azul escuro sutil */
    [data-testid="stSidebar"] { 
        background-color: #090d16; 
        border-right: 1px solid #1e293b; 
    }
    
    /* Títulos robustos e limpos */
    h1, h2, h3 { 
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif; 
        font-weight: 700; 
        letter-spacing: -0.5px;
    }
    
    /* Estilização dos Cards Superiores de Métricas (Idênticos ao Layout 2.0) */
    .metric-card {
        background-color: #0c111d;
        border-left: 4px solid #00E5FF;
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #ffffff !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
    }

    /* Botões executivos modernos */
    div.stButton > button {
        background-color: #0f172a; color: #00E5FF; border: 1px solid #00E5FF; border-radius: 6px;
        padding: 8px 16px; font-weight: 600; width: 100%; transition: all 0.2s;
    }
    div.stButton > button:hover { 
        background-color: #00E5FF; color: #030712; box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }
    
    /* Histórico em Cards Limpos e Elegantes */
    .activity-card {
        background-color: #0c111d; 
        border: 1px solid #1e293b; 
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 15px;
    }
    .activity-header {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    .activity-tag { color: #00FF66; font-weight: 700; font-size: 0.9rem; }
    .activity-hours { color: #00E5FF; font-weight: 600; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM BANCO DE DADOS (GOOGLE SHEETS) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="0s")
    df['Data'] = pd.to_datetime(df['Data'])
except Exception as e:
    st.error("Erro ao conectar ao banco de dados Google Sheets. Verifique as credenciais.")
    df = pd.DataFrame(columns=["Data", "Atividade", "Horas", "Impacto"])

# --- BARRA LATERAL DE OPERAÇÕES ---
st.sidebar.markdown("<h2 style='color: #ffffff; margin-bottom: 20px;'>🛡️ SHIELD // PRO</h2>", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size:0.9rem; color:#94a3b8; font-weight:bold; margin-bottom:5px;'>🔒 Autenticação</p>", unsafe_allow_html=True)
senha = st.sidebar.text_input("Acesso do Usuário:", type="password", label_visibility="collapsed")

if senha == "maxtrack2026":
    modo_editor = True
    st.sidebar.success("MODO CONFIGURAÇÃO ATIVO")
else:
    modo_editor = False
    if senha != "":
        st.sidebar.error("Acesso restrito para leitura.")

st.sidebar.write("---")

st.sidebar.markdown("<p style='font-size:0.9rem; color:#94a3b8; font-weight:bold; margin-bottom:5px;'>📅 Filtro de Exibição</p>", unsafe_allow_html=True)
if not df.empty:
    df['Mes_Ano'] = df['Data'].dt.strftime('%m/%Y')
    opcoes_mes = ["Ver Todos"] + sorted(df['Mes_Ano'].unique(), reverse=True)
else:
    opcoes_mes = ["Ver Todos", datetime.now().strftime('%m/%Y')]

mes_selecionado = st.sidebar.selectbox("Filtrar por período:", opcoes_mes, label_visibility="collapsed")

# Formulário de Cadastro Clínico e Organizado
if modo_editor:
    st.sidebar.write("---")
    st.sidebar.markdown("<p style='font-size:0.9rem; color:#00E5FF; font-weight:bold; margin-bottom:5px;'>🚀 Registrar Nova Demanda</p>", unsafe_allow_html=True)
    with st.sidebar.form(key="form_cadastro_v2", clear_on_submit=True):
        nova_data = st.date_input("Data de Execução", datetime.now())
        nova_ativ = st.text_area("O que foi feito? (Atividade)")
        nova_hora = st.number_input("Horas Investidas", min_value=0.5, max_value=24.0, step=0.5, value=1.0)
        novo_impacto = st.text_area("Resultado / Impacto no Negócio")
        
        btn_salvar = st.form_submit_button("PUBLICAR ATIVIDADE")
        
        if btn_salvar and nova_ativ and novo_impacto:
            if nova_data.month == 5 and nova_data.year == 2026:
                st.sidebar.error("⚠️ Mês consolidado no sistema.")
            else:
                nova_linha = pd.DataFrame({
                    "Data": [nova_data.strftime('%Y-%m-%d')],
                    "Atividade": [nova_ativ],
                    "Horas": [nova_hora],
                    "Impacto": [novo_impacto]
                })
                df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
                conn.update(data=df_atualizado)
                st.sidebar.success("Lançado no Sheets com sucesso!")
                st.rerun()

# --- PAINEL CORPORATIVO CENTRAL ---
st.markdown("<h1 style='color: #ffffff; margin-bottom: 2px;'>📊 Análise de Produtividade Operacional</h1>", unsafe_allow_html=True)
if mes_selecionado != "Ver Todos":
    st.markdown(f"<p style='color: #94a3b8; font-size: 0.95rem;'>Visualização focada no período de referência: <b>{mes_selecionado}</b></p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem;'>Exibindo histórico consolidado de todo o período disponível</p>", unsafe_allow_html=True)

st.write("---")

if not df.empty:
    if mes_selecionado == "Ver Todos":
        df_filtrado = df.sort_values(by="Data")
    else:
        df_filtrado = df[df['Mes_Ano'] == mes_selecionado].sort_values(by="Data")
else:
    df_filtrado = pd.DataFrame()

if df_filtrado.empty:
    st.info("Aguardando sincronização de registros com a base de dados Google Sheets...")
else:
    # --- 1. SEÇÃO DE METRIC CARDS HORIZONTAIS (ESTILO 2.0) ---
    total_atividades = len(df_filtrado)
    total_horas = df_filtrado['Horas'].sum()
    
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Volume de Entregas</div>
                <div class="metric-value">{total_atividades} Atividades</div>
            </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        # Formata bonitinho se tiver quebrado em meia hora (ex: 36h 30min)
        horas_int = int(total_horas)
        minutos = int((total_horas - horas_int) * 60)
        tempo_str = f"{horas_int}h {minutos}min" if minutos > 0 else f"{horas_int}h"
        
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #00FF66;">
                <div class="metric-label">Carga Horária Dedicada</div>
                <div class="metric-value">{tempo_str}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #a855f7;">
                <div class="metric-label">Status da Sincronização</div>
                <div class="metric-value">Banco Nuvem 100%</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- 2. SEÇÃO DE GRÁFICOS GERENCIAIS ACUMULADOS POR MÊS ---
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 15px;'>Esforço Mensal Consolidado</h3>", unsafe_allow_html=True)
    
    NOMES_MESES = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    df_mes = df_filtrado.copy()
    df_mes['Num_Mes'] = df_mes['Data'].dt.month
    df_mes['Mês'] = df_mes['Num_Mes'].map(NOMES_MESES)
    
    # Agrupamento e Ordenação
    df_grafico_mensal = df_mes.groupby(['Num_Mes', 'Mês'])['Horas'].sum().reset_index()
    df_grafico_mensal = df_grafico_mensal.sort_values(by='Num_Mes')
    df_grafico_mensal = df_grafico_mensal.set_index('Mês')
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("<p style='color: #00E5FF; font-size: 0.9rem; font-weight: bold; margin-bottom: 10px;'>📊 Total de Horas Mensais (Distribuição Absoluta)</p>", unsafe_allow_html=True)
        st.bar_chart(df_grafico_mensal[['Horas']], use_container_width=True)
        
    with g_col2:
        st.markdown("<p style='color: #00FF66; font-size: 0.9rem; font-weight: bold; margin-bottom: 10px;'>📈 Curva de Desempenho e Ritmo no Período</p>", unsafe_allow_html=True)
        st.line_chart(df_grafico_mensal[['Horas']], use_container_width=True)

    st.write("---")

    # --- 3. HISTÓRICO EM DOCUMENTOS CORPORATIVOS SLICK ---
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 20px;'>📋 Histórico Técnico de Atividades</h3>", unsafe_allow_html=True)
    df_lista = df_filtrado.sort_values(by="Data", ascending=False)
    
    for index, row in df_lista.iterrows():
        try:
            data_formatada = row['Data'].strftime('%d/%m/%Y')
        except:
            data_formatada = str(row['Data'])

        st.markdown(f"""
            <div class="activity-card">
                <div class="activity-header">
                    <span class="activity-tag">📅 ENTREGA REGISTRADA EM: {data_formatada}</span>
                    <span class="activity-hours">⏱️ ESFORÇO: {row['Horas']}h</span>
                </div>
                <p style="margin-top: 5px; color: #e2e8f0;"><b>🔹 Descrição Executiva:</b> {row['Atividade']}</p>
                <p style="margin-bottom: 0; color: #94a3b8;"><b>🎯 Retorno Estratégico:</b> {row['Impacto']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if modo_editor:
            if hasattr(row['Data'], 'month') and row['Data'].month == 5 and row['Data'].year == 2026:
                st.warning("🔒 Histórico consolidado institucional.")
            else:
                if st.button(f"Remover Registro #{index}", key=f"del_{index}"):
                    df_deletado = df.drop(index)
                    conn.update(data=df_deletado)
                    st.success("Removido com sucesso do banco central!")
                    st.rerun()
