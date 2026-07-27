import streamlit as st
import subprocess
import os
import json
import time
import urllib.parse
import pandas as pd
from playwright.sync_api import sync_playwright

# ============================================================
# 🎨 CSS EMBUTIDO (NÃO PRECISA DE ARQUIVO EXTERNO)
# ============================================================
st.set_page_config(page_title="Phoenix Leads AI", page_icon="🦅", layout="wide")

css_futurista = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, .stApp {
    background: linear-gradient(145deg, #0a0a12 0%, #12121f 40%, #1a1a2e 100%) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    color: #e5e7eb !important;
    min-height: 100vh;
}

.glass, .stAlert, .stInfo, .stSuccess, .stWarning, .stException,
.element-container, .stMarkdown, .stDataFrame, .stTabs [data-baseweb="tab-panel"] {
    background: rgba(26, 26, 46, 0.78) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(0, 245, 255, 0.12) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
}

h1, h2, h3, h4, h5, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-weight: 700 !important;
    color: #f0f0f0 !important;
    text-shadow: 0 0 12px rgba(0, 245, 255, 0.25) !important;
    letter-spacing: -0.02em !important;
}

h1 {
    font-size: 2.5rem !important;
    background: linear-gradient(135deg, #00f5ff, #a855f7) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-shadow: none !important;
}

h2 {
    color: #00f5ff !important;
    border-bottom: 1px solid rgba(0, 245, 255, 0.2) !important;
    padding-bottom: 0.3rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00f5ff22, #a855f722) !important;
    border: 1px solid rgba(0, 245, 255, 0.4) !important;
    color: #00f5ff !important;
    border-radius: 50px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.15) !important;
    backdrop-filter: blur(6px) !important;
}

.stButton > button:hover {
    transform: scale(1.04) !important;
    background: linear-gradient(135deg, #00f5ff44, #a855f744) !important;
    border-color: #00f5ff !important;
    box-shadow: 0 0 30px rgba(0, 245, 255, 0.3) !important;
    color: #ffffff !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: rgba(10, 10, 18, 0.7) !important;
    border: 1px solid rgba(0, 245, 255, 0.25) !important;
    border-radius: 12px !important;
    color: #e5e7eb !important;
    padding: 10px 16px !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    backdrop-filter: blur(4px) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div:focus-within,
.stTextArea > div > div > textarea:focus {
    border-color: #00f5ff !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.2) !important;
    outline: none !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(26, 26, 46, 0.6) !important;
    backdrop-filter: blur(8px) !important;
    padding: 6px 10px !important;
    border-radius: 60px !important;
    border: 1px solid rgba(0, 245, 255, 0.1) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 40px !important;
    padding: 8px 24px !important;
    font-weight: 500 !important;
    color: #9ca3af !important;
    transition: all 0.2s ease !important;
    font-size: 0.9rem !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #00f5ff22, #a855f722) !important;
    color: #00f5ff !important;
    border: 1px solid rgba(0, 245, 255, 0.4) !important;
    box-shadow: 0 0 25px rgba(0, 245, 255, 0.15) !important;
}

.card {
    background: rgba(26, 26, 46, 0.6) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(0, 245, 255, 0.15) !important;
    border-radius: 16px !important;
    padding: 18px !important;
    margin-bottom: 16px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

.card:hover {
    transform: translateY(-5px) !important;
    border-color: rgba(0, 245, 255, 0.5) !important;
    box-shadow: 0 8px 40px rgba(0, 245, 255, 0.15) !important;
}

.card h4 {
    color: #00f5ff !important;
    font-weight: 600 !important;
    margin-top: 0 !important;
    text-shadow: 0 0 10px rgba(0, 245, 255, 0.2) !important;
}

.card p {
    color: #d1d5db !important;
    font-size: 0.95rem !important;
}

.whatsapp-button {
    display: inline-block;
    background: linear-gradient(135deg, #25D36633, #00ff9d33) !important;
    border: 1px solid #00ff9d66 !important;
    color: #00ff9d !important;
    padding: 16px 28px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 60px !important;
    text-decoration: none !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 25px rgba(0, 255, 157, 0.2) !important;
    width: 100% !important;
    backdrop-filter: blur(6px) !important;
}

.whatsapp-button:hover {
    background: linear-gradient(135deg, #25D36655, #00ff9d55) !important;
    border-color: #00ff9d !important;
    transform: scale(1.02) !important;
    box-shadow: 0 0 45px rgba(0, 255, 157, 0.4) !important;
    color: #ffffff !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00f5ff, #a855f7) !important;
    border-radius: 20px !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.3) !important;
}

.stAlert, .stInfo, .stSuccess, .stWarning {
    background: rgba(26, 26, 46, 0.7) !important;
    backdrop-filter: blur(6px) !important;
    border-left: 4px solid #00f5ff !important;
    border-radius: 12px !important;
    color: #e5e7eb !important;
}

.stSuccess { border-left-color: #00ff9d !important; }
.stWarning { border-left-color: #eab308 !important; }
.stError { border-left-color: #ef4444 !important; }

.stDataFrame {
    background: rgba(26, 26, 46, 0.5) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(0, 245, 255, 0.1) !important;
    overflow: hidden !important;
}
.stDataFrame table {
    background: transparent !important;
    color: #d1d5db !important;
}
.stDataFrame thead tr th {
    background: rgba(0, 245, 255, 0.08) !important;
    color: #00f5ff !important;
    font-weight: 600 !important;
    border-bottom: 1px solid rgba(0, 245, 255, 0.2) !important;
}
.stDataFrame tbody tr:hover {
    background: rgba(0, 245, 255, 0.05) !important;
}

a {
    color: #a855f7 !important;
    text-decoration: none !important;
    transition: color 0.2s ease !important;
}
a:hover {
    color: #00f5ff !important;
    text-shadow: 0 0 12px rgba(0, 245, 255, 0.3) !important;
}

.stCodeBlock, .stMarkdown pre {
    background: rgba(10, 10, 18, 0.8) !important;
    border: 1px solid rgba(0, 245, 255, 0.15) !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: #a855f7 !important;
}

footer { visibility: hidden !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1a1a2e; }
::-webkit-scrollbar-thumb { background: #00f5ff44; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: #00f5ff88; }

.stSelectbox label { color: #9ca3af !important; font-weight: 500 !important; }

.stTextArea textarea {
    background: rgba(10, 10, 18, 0.7) !important;
    border: 1px solid rgba(0, 245, 255, 0.2) !important;
    color: #e5e7eb !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

.stInfo {
    background: rgba(0, 245, 255, 0.06) !important;
    border-left: 4px solid #00f5ff !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
}

@media (max-width: 768px) {
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        border-radius: 20px !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 6px 14px !important;
        font-size: 0.8rem !important;
    }
}
</style>
"""
st.markdown(css_futurista, unsafe_allow_html=True)

# ============================================================
# 🚀 AUTO-INSTALAÇÃO DO PLAYWRIGHT
# ============================================================
@st.cache_resource
def instalar_playwright_browsers():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        subprocess.run(["playwright", "install-deps"], check=False)
    except Exception:
        pass
instalar_playwright_browsers()

# ============================================================
# 🔍 ANÁLISE DE SITE
# ============================================================
def analisar_site(url):
    if not url or url == "Não informado":
        return "❌ Sem Site"
    url_lower = url.lower()
    if "instagram.com" in url_lower: return "📸 Instagram"
    if "facebook.com" in url_lower: return "👥 Facebook"
    if "youtube.com" in url_lower: return "▶️ YouTube"
    if "tiktok.com" in url_lower: return "🎵 TikTok"
    if "linkedin.com" in url_lower: return "💼 LinkedIn"
    if "linktr.ee" in url_lower or "biolinky" in url_lower: return "🔗 Linktree/Bio"
    if "wa.me" in url_lower or "api.whatsapp" in url_lower: return "💬 WhatsApp"
    return "✅ Site Próprio"

# ============================================================
# 🦅 MOTOR DE EXTRAÇÃO
# ============================================================
def extrair_leads(busca, max_resultados, status_texto=None, barra_progresso=None):
    leads = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.google.com/maps/search/{busca.replace(' ', '+')}"

        if status_texto:
            status_texto.text("🦅 Phoenix decolando... Acessando o Google Maps.")

        page.goto(url)
        page.wait_for_timeout(4000)

        urls_locais = set()
        tentativas_sem_novos = 0

        while len(urls_locais) < max_resultados and tentativas_sem_novos < 5:
            if status_texto:
                status_texto.text(f"🔍 Encontrados {len(urls_locais)} de {max_resultados} resultados...")

            page.mouse.wheel(0, 12000)
            page.wait_for_timeout(2000)

            locais = page.locator('//a[contains(@href, "/maps/place/")]').all()
            antes = len(urls_locais)

            for local in locais:
                href = local.get_attribute("href")
                if href:
                    urls_locais.add(href)

            if len(urls_locais) == antes:
                tentativas_sem_novos += 1
            else:
                tentativas_sem_novos = 0

        urls_locais = list(urls_locais)[:max_resultados]

        for i, url_local in enumerate(urls_locais):
            try:
                page.goto(url_local)
                page.wait_for_timeout(1500)
                nome = page.locator('//h1').inner_text() if page.locator('//h1').count() > 0 else "Sem nome"

                if status_texto:
                    status_texto.text(f"🎯 Extraindo dados de: {nome}")
                if barra_progresso:
                    barra_progresso.progress((i + 1) / len(urls_locais))

                site_coletado = "Não informado"
                links = page.locator('//a[@data-item-id="authority"]').all()
                if links:
                    site_coletado = links[0].get_attribute('href')

                botoes = page.locator('//button[contains(@data-item-id, "phone:tel:")]').all()
                telefone = botoes[0].get_attribute('data-item-id').replace('phone:tel:', '').strip() if botoes else "Não informado"

                status_site = analisar_site(site_coletado)

                leads.append({
                    "id": i+1,
                    "empresa": nome,
                    "telefone": telefone,
                    "status_site": status_site,
                    "link_coletado": site_coletado,
                    "link": url_local
                })
            except Exception:
                continue

        browser.close()
    return leads

# ============================================================
# 🥷 API PARA FLUTTER
# ============================================================
params = st.query_params
if "api" in params and "nicho" in params and "cidade" in params:
    nicho_busca = params["nicho"]
    cidade_busca = params["cidade"]
    limite_busca = int(params.get("limite", 10))
    resultado_leads = extrair_leads(f"{nicho_busca} em {cidade_busca}", limite_busca)
    st.text(json.dumps({"status": "sucesso", "dados": resultado_leads}, ensure_ascii=False))
    st.stop()

# ============================================================
# 🖥️ INTERFACE PRINCIPAL
# ============================================================
if 'leads_salvos' not in st.session_state:
    st.session_state['leads_salvos'] = pd.DataFrame()
if 'lead_selecionado' not in st.session_state:
    st.session_state['lead_selecionado'] = None

aba1, aba2, aba3 = st.tabs(["🦅 Mineração Phoenix", "🤖 Construtor de Site (Vibe Code)", "💬 Prospectar Cliente"])

# ---- ABA 1: MINERADOR ----
with aba1:
    st.title("🦅 PHOENIX LEADS AI")
    st.markdown('<p style="font-size:1.1rem; color:#9ca3af; margin-top:-0.5rem;">Extraia leads do Google Maps com análise de presença digital</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        termo = st.text_input("🔎 Nicho / Profissão:", "Barbearia")
    with col2:
        cidade = st.text_input("📍 Cidade:", "São Paulo")
    with col3:
        limite = st.number_input("📊 Limite:", min_value=5, max_value=100, value=10)

    if st.button("🚀 Minerar Agora", use_container_width=True):
        barra_p = st.progress(0)
        status_t = st.empty()

        lista_dados = extrair_leads(f"{termo} em {cidade}", limite, status_texto=status_t, barra_progresso=barra_p)
        status_t.text("✅ Mineração concluída com sucesso!")

        if lista_dados:
            st.session_state['leads_salvos'] = pd.DataFrame(lista_dados)
            st.success(f"🎯 {len(lista_dados)} leads encontrados e salvos!")
        else:
            st.warning("Nenhum lead encontrado. Tente ajustar os termos.")

    if not st.session_state['leads_salvos'].empty:
        df_exibir = st.session_state['leads_salvos']
        st.write("---")
        st.subheader("🎯 Leads Encontrados")

        # Cards em 3 colunas
        cols = st.columns(3)
        for idx, (_, row) in enumerate(df_exibir.iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="card">
                    <h4>{row['empresa']}</h4>
                    <p><strong>📞 Telefone:</strong> {row['telefone']}</p>
                    <p><strong>🌐 Status:</strong> {row['status_site']}</p>
                    <p><small>🔗 {row['link_coletado'][:40]}...</small></p>
                </div>
                """, unsafe_allow_html=True)

        st.write("---")
        st.markdown("### 🔍 Seleção de Lead & Detalhes")
        opcoes_leads = {f"[{row['status_site']}] - {row['empresa']}": row for _, row in df_exibir.iterrows()}
        lead_chosen = st.selectbox("Clique no lead para abrir as informações:", list(opcoes_leads.keys()))

        info_lead = opcoes_leads[lead_chosen]

        st.write("---")
        st.markdown(f"#### 📋 Ficha Completa do Lead no Google Maps")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.info(f"**🏢 Nome do Negócio:**\n{info_lead['empresa']}")
        with c2:
            st.info(f"**📱 Telefone / WhatsApp:**\n{info_lead['telefone']}")
        with c3:
            st.info(f"**📊 Diagnóstico de Página:**\n{info_lead['status_site']}")

        st.write("---")
        st.markdown(f"**🔗 Acesso Rápido ao Google Maps:** [Clique para abrir o perfil da empresa]({info_lead['link']})")
        st.caption(f"**Link de Origem Cadastrado:** {info_lead['link_coletado']}")

        if st.button("🚀 Obter Resumo e Gerar Site", use_container_width=True):
            st.session_state['lead_selecionado'] = info_lead
            st.success("✅ Dados filtrados! Vá para a aba 'Construtor de Site'.")

# ---- ABA 2: CRIADOR DE SITE ----
with aba2:
    st.title("🤖 PHOENIX SITE BUILDER (VIBE CODE)")
    lead = st.session_state['lead_selecionado']

    if lead is None:
        st.info("Nenhum lead selecionado ainda. Vá na aba 'Mineração Phoenix' e clique em 'Obter Resumo e Gerar Site'.")
    else:
        st.markdown(f"### 📋 Dados do Lead Ativo:")
        st.success(f"**Empresa:** {lead['empresa']} | **Status Atual:** {lead['status_site']}")

        with st.spinner("Montando o prompt cirúrgico para o Vibe Code..."):
            time.sleep(0.5)

            st.markdown("## 📜 1. Resumo Estratégico do Lead (IA)")
            argumento_ia = (f"não possui nenhuma página profissional na web, dependendo apenas do link '{lead['link_coletado']}'"
                            if "✅" not in lead['status_site']
                            else "possui um site, mas ele pode ser otimizado para conversão direta")

            resumo_ia = f"""
            * **Diagnóstico Digital:** A empresa **{lead['empresa']}** {argumento_ia}. Isso afasta os clientes que buscam um serviço sério ou imediato no Google desktop/mobile.
            * **Ponto de Conversão Crítico:** Criar um ambiente focado em transformar a busca local em agendamento rápido via {lead['telefone']}.
            """
            st.markdown(resumo_ia)
            st.write("---")

            st.markdown("## 💻 2. Prompt Estruturado para o Vibe Code")
            prompt_vibe_code = f"""Escreva um prompt que eu possa usar no software Vibe Code para criar um site atraente para uma empresa chamada {lead['empresa']}, que atualmente está classificada como {lead['status_site']} (Link cadastrado: {lead['link_coletado']}). Com esta informação:

[informações do google maps]
- Nome do Negócio: {lead['empresa']}
- Telefone/Contato: {lead['telefone']}
- Situação Web Atual: {lead['status_site']} (Link: {lead['link_coletado']})

[Diretrizes do Site que a IA deve seguir no Vibe Code]:
1. Crie uma landing page profissional de altíssima conversão, muito superior a perfis de redes sociais comuns ou linktrees.
2. Monte seções nítidas: Hero Section (Apresentação impactante), Serviços oferecidos, Prova Social/Depoimentos e Rodapé com dados de contato.
3. Fixe botões flutuantes e de ação direcionando direto para o WhatsApp de atendimento: {lead['telefone']}.
"""
            st.code(prompt_vibe_code, language="text")

# ---- ABA 3: PROSPECTAR ----
with aba3:
    st.title("💬 PROSPECÇÃO ATIVA VIA WHATSAPP")
    lead = st.session_state['lead_selecionado']

    if lead is None:
        st.info("Nenhum lead selecionado. Escolha um cliente na primeira aba para habilitar o disparador.")
    else:
        st.markdown(f"### ⚡ Preparando Abordagem para: **{lead['empresa']}**")

        numero_limpo = "".join(filter(str.isdigit, lead['telefone']))
        if len(numero_limpo) > 0 and not numero_limpo.startswith("55"):
            numero_limpo = "55" + numero_limpo

        if "📸 Instagram" in lead['status_site']:
            gatilho_venda = "Notei que vocês usam o perfil do Instagram como página principal. O Instagram é ótimo para conteúdo, mas vocês acabam perdendo muitos clientes que buscam direto no Google e querem ver um site rápido, com valores ou botões de agendamento diretos."
        elif "❌ Sem Site" in lead['status_site']:
            gatilho_venda = "Notei que vocês ainda não têm um site ou página cadastrada para receber os clientes que acham vocês na internet."
        elif "🔗 Linktree/Bio" in lead['status_site'] or "💬 WhatsApp" in lead['status_site']:
            gatilho_venda = "Notei que vocês usam apenas um agregador de links/botão direto na página de vocês. Isso limita um pouco a autoridade do negócio para quem busca direto pelo Google."
        else:
            gatilho_venda = "Estava analisando a presença digital de vocês no mapa e montei uma proposta de otimização para o site atual de vocês, focado em trazer mais agendamentos."

        copy_whatsapp = f"""Olá, tudo bem? Sou especialista em positioning digital e encontrei o perfil da *{lead['empresa']}* no Google.

{gatilho_venda} Eu montei um protótipo de site exclusivo e moderno, focado em alta conversão e integrado com o WhatsApp de vocês ({lead['telefone']}).

Posso te enviar o link desse layout que desenhei, sem compromisso nenhum, para você dar uma olhada e ver o que acha?"""

        st.markdown("#### 📝 Copy de Abordagem Personalizada:")
        st.text_area("Texto pronto:", value=copy_whatsapp, height=220)

        texto_url = urllib.parse.quote(copy_whatsapp)
        link_api_whatsapp = f"https://wa.me/{numero_limpo}?text={texto_url}"

        st.write("---")
        st.markdown(f"""
        <a href="{link_api_whatsapp}" target="_blank" class="whatsapp-button">
            💬 Abrir Conversa e Fechar Cliente no WhatsApp
        </a>
        """, unsafe_allow_html=True)