import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import zoneinfo

# 1. CONFIGURAÇÕES DE IDENTIDADE E ESTILIZAÇÃO PROTEGIDA (100% INTACTA)
st.set_page_config(page_title="MAXTRACK SHIELD // PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Arial&display=swap');
    
    .stApp, h1, h2, h3, p, label, button, .stSelectbox, .stTextInput, .stTextArea { 
        font-family: 'Arial', sans-serif !important;
    }
    
    .stMarkdown p, .stExpander details summary {
        font-family: 'Arial', sans-serif !important;
    }

    [data-testid="stIcon"], 
    .stExpander details summary svg,
    [class*="inner-icon"],
    span[class*="Icon"] {
        font-family: inherit !important;
    }
    
    .stApp { 
        background-color: #020617; 
    }
    
    h1, h2, h3, p, label, span, div { 
        color: #f8fafc !important; 
    }
    
    .stMetric { 
        background-color: #0f172a; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #38bdf8; 
    }
    </style>
""", unsafe_allow_html=True)

# FUNÇÃO AUXILIAR: Transforma horas decimais em formato amigável
def formatar_horas_relogio(horas_decimais):
    horas_inteiras = int(horas_decimais)
    minutos = int(round((horas_decimais - horas_inteiras) * 60))
    if horas_inteiras == 0:
        return f"{minutos}min"
    return f"{horas_inteiras}h {minutos:02d}min"

# 2. DIRECIONAMENTO E TRAVA DE DATA E HORA (FUSO HORÁRIO DE BRASÍLIA)
FUSO_BRASILIA = zoneinfo.ZoneInfo("America/Sao_Paulo")
agora_brasilia = datetime.datetime.now(FUSO_BRASILIA)
mes_atual_texto = agora_brasilia.strftime('%m/%Y')

# 3. CONTROLE DE ACESSO VIA URL (TRAVA DO GESTOR)
query_params = st.query_params
modo_leitor = query_params.get("view") == "gestor"

# 4. GARANTIA E PRESERVAÇÃO DO SEU HISTÓRICO ATUAL (.CSV)
DB_FILE = "dados_shield.csv"
PASTA_FOTOS = "evidencias"

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

if not os.path.exists(DB_FILE):
    df_vazio = pd.DataFrame(columns=["Data", "Hora_Registro", "Area", "Atividade", "Horas", "Impacto", "Imagem_Path"])
    df_vazio.to_csv(DB_FILE, index=False, sep=";")

# --- FUNÇÃO PARA APAGAR REGISTROS ---
def apagar_registro(id_registro):
    df_atual = pd.read_csv(DB_FILE, sep=";")
    foto_path = df_atual.loc[id_registro, "Imagem_Path"]
    if pd.notna(foto_path) and foto_path != "N/A" and os.path.exists(str(foto_path)):
        try:
            os.remove(str(foto_path))
        except Exception:
            pass
    df_atual = df_atual.drop(id_registro)
    df_atual.to_csv(DB_FILE, index=False, sep=";")
    st.rerun()

# --- CARREGAMENTO DO SEU HISTÓRICO EXISTENTE ---
try:
    df = pd.read_csv(DB_FILE, sep=";")
    if not df.empty and "Data" in df.columns:
        df['Datetime_Aux'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Mes_Ano_Aux'] = df['Datetime_Aux'].dt.strftime('%m/%Y')
    else:
        df['Mes_Ano_Aux'] = None
except Exception:
    df = pd.DataFrame(columns=["Data", "Hora_Registro", "Area", "Atividade", "Horas", "Impacto", "Imagem_Path", "Mes_Ano_Aux"])

# --- BARRA LATERAL ---
with st.sidebar:
    if modo_leitor:
        st.header("📋 Modo Visualização")
        st.caption("Acesso exclusivo para leitura de relatórios.")
    else:
        st.header("🚀 Registrar Atividade")
        st.markdown(f"**🕒 Horário de Brasília:** {agora_brasilia.strftime('%H:%M')}")
    st.divider()
    
    st.subheader("🔍 Filtro do Dashboard")
    lista_meses = [mes_atual_texto]
    if not df.empty and 'Mes_Ano_Aux' in df.columns:
        meses_detectados = df['Mes_Ano_Aux'].dropna().unique().tolist()
        for m in meses_detectados:
            if m not in lista_meses:
                lista_meses.append(m)
    
    mes_selecionado = st.selectbox("Exibir dados do mês:", lista_meses, index=0)
    st.divider()
    
    # SÓ MOSTRA O FORMULÁRIO SE NÃO FOR O GESTOR
    if not modo_leitor:
        with st.form("form_shield_pro_final", clear_on_submit=True):
            f_data = st.date_input("Data da Atividade", agora_brasilia.date(), format="DD/MM/YYYY")
            f_area = st.selectbox("Área / Projeto", ["Área Técnica", "Agendamento", "Validação", "Solicitação Supervisores", "Solicitação Coordenação", "Solicitação Pós-venda", "Entre outros"])
            f_task = st.text_area("O que você fez? (Atividade)")
            
            st.write("**Tempo Investido:**")
            c_hr, c_min = st.columns(2)
            with c_hr: f_horas_pures = st.selectbox("Horas", list(range(0, 25)), index=1)
            with c_min: f_minutos_pures = st.selectbox("Minutos", list(range(0, 61)), index=0)
                
            f_impact = st.text_area("Qual o valor disso? (Impacto Estratégico)")
            f_foto = st.file_uploader("Anexar Evidência (Imagem)", type=['png', 'jpg', 'jpeg'])
            
            btn_salvar = st.form_submit_button("SALVAR ATIVIDADE")
            
            if btn_salvar:
                horas_calculadas = f_horas_pures + (f_minutos_pures / 60.0)
                if horas_calculadas == 0:
                    st.error("❌ Por favor, insira um tempo válido.")
                else:
                    momento_salvamento = datetime.datetime.now(FUSO_BRASILIA)
                    caminho_final = "N/A"
                    
                    if f_foto:
                        timestamp = momento_salvamento.strftime("%Y%m%d_%H%M%S")
                        caminho_final = os.path.join(PASTA_FOTOS, f"{timestamp}_{f_foto.name}")
                        with open(caminho_final, "wb") as f:
                            f.write(f_foto.getbuffer())
                    
                    novo_item = {
                        "Data": f_data.strftime("%d/%m/%Y"),
                        "Hora_Registro": momento_salvamento.strftime("%H:%M"),
                        "Area": f_area,
                        "Atividade": f_task,
                        "Horas": horas_calculadas,
                        "Impacto": f_impact,
                        "Imagem_Path": caminho_final
                    }
                    
                    df_hist = pd.read_csv(DB_FILE, sep=";")
                    df_hist = pd.concat([df_hist, pd.DataFrame([novo_item])], ignore_index=True)
                    
                    if 'Datetime_Aux' in df_hist.columns: df_hist = df_hist.drop(columns=['Datetime_Aux'])
                    if 'Mes_Ano_Aux' in df_hist.columns: df_hist = df_hist.drop(columns=['Mes_Ano_Aux'])
                    
                    df_hist.to_csv(DB_FILE, index=False, sep=";")
                    st.success("✅ Atividade registrada!")
                    st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("📊 MAXTRACK SHIELD // PRO")
st.markdown(f"Visualização focada no período de referência: **{mes_selecionado}**")

if not df.empty and "Area" in df.columns and 'Mes_Ano_Aux' in df.columns:
    df_filtrado = df[df['Mes_Ano_Aux'] == mes_selecionado].copy()
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Atividades em {mes_selecionado}", len(df_filtrado))
    
    total_horas_decimais = df_filtrado['Horas'].sum() if 'Horas' in df_filtrado.columns else 0.0
    c2.metric(f"Horas no Mês", formatar_horas_relogio(total_horas_decimais))
    
    area_ativa = df_filtrado['Area'].mode()[0] if not df_filtrado['Area'].dropna().empty else "N/A"
    c3.metric("Demanda Crítica do Período", area_ativa)

    st.divider()

    if not df_filtrado.empty:
        col_dir, col_esq = st.columns(2)
        
        with col_dir:
            st.subheader("Esforço Mensal por Área (Horas)")
            if 'Horas' in df_filtrado.columns:
                fig_barra = px.bar(df_filtrado.groupby("Area")["Horas"].sum().reset_index(), 
                                   x="Area", y="Horas", color="Area", 
                                   template="plotly_dark", color_discrete_sequence=px.colors.sequential.Blues_r)
                fig_barra.update_layout(font_family="Arial")
                st.plotly_chart(fig_barra)

        with col_esq:
            st.subheader("Distribuição das Demandas")
            if 'Area' in df_filtrado.columns:
                fig_pizza = px.pie(df_filtrado, names="Area", hole=0.4, template="plotly_dark")
                fig_pizza.update_layout(font_family="Arial")
                st.plotly_chart(fig_pizza)
    else:
        st.info(f"Nenhuma atividade registrada ainda para o mês {mes_selecionado}.")

    st.divider()

    st.subheader(f"📑 Histórico Detalhado ({mes_selecionado})")
    
    if not df_filtrado.empty:
        for i in reversed(df_filtrado.index):
            row = df_filtrado.loc[i]
            hora_str = f" às {row['Hora_Registro']}" if "Hora_Registro" in df_filtrado.columns and pd.notna(row["Hora_Registro"]) and row["Hora_Registro"] != "N/A" else ""
            
            titulo_card = f"📌 {row['Data']}{hora_str} | {row['Area']}"
            
            with st.expander(titulo_card):
                col_txt, col_img = st.columns([2, 1])
                with col_txt:
                    st.write(f"**O que foi feito? (Atividade)**")
                    st.write(str(row['Atividade']))
                    
                    horas_formatadas = formatar_horas_relogio(float(row['Horas']))
                    st.write(f"**Horas Gastas:** {horas_formatadas}")
                    st.write(f"**Impacto Estratégico:** {row['Impacto']}")
                    
                    # SÓ MOSTRA O BOTÃO DE EXCLUIR SE NÃO FOR O GESTOR
                    if not modo_leitor:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"🗑️ Excluir Lançamento", key=f"del_shield_real_{i}"):
                            apagar_registro(i)
                            
                with col_img:
                    if "Imagem_Path" in df_filtrado.columns and pd.notna(row['Imagem_Path']) and row['Imagem_Path'] != "N/A" and os.path.exists(str(row['Imagem_Path'])):
                        st.image(str(row['Imagem_Path']), caption="Evidência Visual")
                    else:
                        st.warning("Sem evidência fotográfica.")
    else:
        st.write("Sem registros neste período.")
else:
    st.info("Aguardando lançamentos no histórico para gerar os gráficos.")
