import streamlit as st
import subprocess
import os
import json
import time
import urllib.parse
import pandas as pd
from playwright.sync_api import sync_playwright

# ============================================================
# 🎨 CARREGAR CSS PERSONALIZADO (style.css na mesma pasta)
# ============================================================
def carregar_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Arquivo style.css não encontrado. Usando tema padrão.")

carregar_css()

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
# 🔍 ANÁLISE DE SITE (agora com mais redes)
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
# 🦅 MOTOR DE EXTRAÇÃO (scraper)
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

        barra_lateral = page.locator('//div[@role="feed"]')
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
# 🥷 API PARA FLUTTER (se chamar com parâmetros)
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
# 🖥️ INTERFACE PRINCIPAL (com estilos CSS)
# ============================================================
st.set_page_config(page_title="Phoenix Leads AI", page_icon="🦅", layout="wide")

if 'leads_salvos' not in st.session_state:
    st.session_state['leads_salvos'] = pd.DataFrame()
if 'lead_selecionado' not in st.session_state:
    st.session_state['lead_selecionado'] = None

# MENU DE ABAS
aba1, aba2, aba3 = st.tabs(["🦅 Mineração Phoenix", "🤖 Construtor de Site (Vibe Code)", "💬 Prospectar Cliente"])

# ---- ABA 1: MINERADOR ----
with aba1:
    st.title("🦅 PHOENIX LEADS AI")
    st.markdown('<p class="subtitle">Extraia leads do Google Maps com análise de presença digital</p>', unsafe_allow_html=True)

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

        # Exibição em cards (mais bonito)
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

        # Gatilho personalizado
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