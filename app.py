import streamlit as st
import subprocess
import os
import json

# ---- AUTO-INSTALAÇÃO DO BROWSER NA NUVEM ----
@st.cache_resource
def instalar_playwright_browsers():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        subprocess.run(["playwright", "install-deps"], check=False)
    except Exception as e:
        pass

instalar_playwright_browsers()

from playwright.sync_api import sync_playwright
import pandas as pd
import time
import urllib.parse
# Se estiver usando Streamlit, a forma mais brutal e eficaz é esta:
# Adicione isso logo após os seus imports:
def liberar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# Quando você devolver o JSON (lá na parte do seu código que faz o st.text(json.dumps...)),
# Tente forçar a resposta se o Streamlit permitir, ou simplesmente ignore
# o CORS no lado do Flutter como vou te mostrar abaixo.

# ---- FUNÇÃO PARA DISTINGUIR SITE REAL DE REDE SOCIAL ----
def analisar_site(url):
    if not url or url == "Não informado":
        return "❌ Sem Site"
    url_lower = url.lower()
    if "instagram.com" in url_lower: return "📸 Só Instagram"
    if "facebook.com" in url_lower: return "👥 Só Facebook"
    if "linktr.ee" in url_lower or "biolinky" in url_lower: return "🔗 Só Linktree/Bio"
    if "wa.me" in url_lower or "api.whatsapp" in url_lower: return "💬 Só Whats"
    return "✅ Possui Site"

# ---- MOTOR DO SCRAPER (ROBÔ) ----
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
                status_texto.text(
                    f"🔍 Encontrados {len(urls_locais)} de {max_resultados} resultados..."
                )

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
            # continua o restante do seu código...
            try:
                page.goto(url_local)
                page.wait_for_timeout(1500)
                nome = page.locator('//h1').inner_text() if page.locator('//h1').count() > 0 else "Sem nome"
                
                if status_texto: status_texto.text(f"🎯 Extraindo dados de: {nome}")
                if barra_progresso: barra_progresso.progress((i + 1) / len(urls_locais))
                
                site_coletado = "Não informado"
                links = page.locator('//a[@data-item-id="authority"]').all()
                if links: site_coletado = links[0].get_attribute('href')
                    
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
            except:
                continue
        browser.close()
    return leads

# =========================================================
# 🥷 SEGREDO DA API: SE O FLUTTER CHAMAR, DEVOLVE SÓ JSON
# =========================================================
params = st.query_params
if "api" in params and "nicho" in params and "cidade" in params:
    nicho_busca = params["nicho"]
    cidade_busca = params["cidade"]
    limite_busca = int(params.get("limite", 10))
    
    resultado_leads = extrair_leads(f"{nicho_busca} em {cidade_busca}", limite_busca)
    
    st.text(json.dumps({"status": "sucesso", "dados": resultado_leads}, ensure_ascii=False))
    st.stop() 

# =========================================================
# 🦅 INTERFACE ORIGINAL DO STREAMLIT (INTEIRA E SEM CORTES)
# =========================================================
st.set_page_config(page_title="Phoenix Leads AI", page_icon="🦅", layout="wide")

if 'leads_salvos' not in st.session_state:
    st.session_state['leads_salvos'] = pd.DataFrame()
if 'lead_selecionado' not in st.session_state:
    st.session_state['lead_selecionado'] = None

# MENU DE ABAS NATIVAS
aba1, aba2, aba3 = st.tabs(["🦅 Mineração Phoenix", "🤖 Construtor de Site Vibe Code", "💬 Prospectar Cliente"])

# ---- ABA 1: MINERADOR ----
with aba1:
    st.title("🦅 PHOENIX LEADS AI")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: termo = st.text_input("Nicho:", "Barbearia")
    with col2: cidade = st.text_input("Cidade:", "São Paulo")
    with col3: limite = st.number_input("Limite:", min_value=5, max_value=100, value=10)
    
    if st.button("(Minerar)", use_container_width=True):
        barra_p = st.progress(0)
        status_t = st.empty()
        
        lista_dados = extrair_leads(f"{termo} em {cidade}", limite, status_texto=status_t, barra_progresso=barra_p)
        status_t.text("✅ Mineração concluída com sucesso!")
        if lista_dados:
            st.session_state['leads_salvos'] = pd.DataFrame(lista_dados)
        else:
            st.warning("Nenhum lead encontrado.")

    if not st.session_state['leads_salvos'].empty:
        df_exibir = st.session_state['leads_salvos']
        st.write("---")
        st.subheader("🎯 Leads Encontrados (Com análise de Site)")
        
        df_bonito = df_exibir.rename(columns={
            "id": "ID", "empresa": "Empresa", "telefone": "Telefone", 
            "status_site": "Status do Site", "link_coletado": "Link Coletado"
        })
        st.dataframe(df_bonito[["ID", "Empresa", "Telefone", "Status do Site", "Link Coletado"]], use_container_width=True, hide_index=True)
        
        st.markdown("### 🔍 Seleção de Lead & Detalhes")
        opcoes_leads = {f"[{row['status_site']}] - {row['empresa']}": row for _, row in df_exibir.iterrows()}
        lead_chosen = st.selectbox("Clique em cima do lead desejado para abrir as informações:", list(opcoes_leads.keys()))
        
        info_lead = opcoes_leads[lead_chosen]
        st.write("---")
        st.markdown(f"#### 📋 Ficha Completa do Lead no Google Maps:")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.info(f"**Nome do Negócio:**\n{info_lead['empresa']}")
        with c2: st.info(f"**Telefone / WhatsApp:**\n{info_lead['telefone']}")
        with c3: st.info(f"**Diagnóstico de Página:**\n{info_lead['status_site']}")
        
        st.caption(f"**Link de Origem Cadastrado:** {info_lead['link_coletado']}")
        
        if st.button("🚀 Obter Resumo e Gerar Site", use_container_width=True):
            st.session_state['lead_selecionado'] = info_lead
            st.success(f"Dados filtrados! Os módulos de criação e abordagem já foram calibrados com o status desse cliente.")

# ---- ABA 2: CRIADOR DE SITE IA ----
with aba2:
    st.title("🤖 PHOENIX SITE BUILDER VIBE CODE")
    lead = st.session_state['lead_selecionado']
    
    if lead is None:
        st.info("Nenhum lead selecionado ainda. Vá na aba de 'Mineração Phoenix' e clique em 'Obter Resumo e Gerar Site'.")
    else:
        st.markdown(f"### 📋 Dados do Lead Ativo:")
        st.success(f"**Empresa:** {lead['empresa']} | **Status Atual:** {lead['status_site']}")
        
        with st.spinner("Montando o prompt cirúrgico para o Vibe Code..."):
            time.sleep(0.5)
            
            st.markdown("## 📜 1. Resumo Estratégico do Lead (IA)")
            argumento_ia = f"não possui nenhuma página profissional na web, dependendo apenas do link '{lead['link_coletado']}'" if "✅" not in lead['status_site'] else "possui um site, mas ele pode ser otimizado para conversão direta"
            
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

# ---- ABA 3: PROSPECTAR CLIENTE ----
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
            
        if "📸 Só Instagram" in lead['status_site']:
            gatilho_venda = "Notei que vocês usam o perfil do Instagram como página principal. O Instagram é ótimo para conteúdo, mas vocês acabam perdendo muitos clientes que buscam direto no Google e querem ver um site rápido, com valores ou botões de agendamento diretos."
        elif "❌ Sem Site" in lead['status_site']:
            gatilho_venda = "Notei que vocês ainda não têm um site ou página cadastrada para receber os clientes que acham vocês na internet."
        elif "🔗 Só Linktree" in lead['status_site'] or "💬" in lead['status_site']:
            gatilho_venda = "Notei que vocês usam apenas um agregador de links/botão direto na página de vocês. Isso limita um pouco a autoridade do negócio para quem busca direto pelo Google."
        else:
            gatilho_venda = "Estava analisando a presença digital de vocês no mapa e montei uma proposta de otimização para o site atual de vocês, focado em trazer mais agendamentos."

        copy_whatsapp = f"Olá, tudo bem? Sou especialista em positioning digital e encontrei o perfil da *{lead['empresa']}* no Google.\n\n{gatilho_venda} Eu montei um protótipo de site exclusivo e moderno, focado em alta conversão e integrado com o WhatsApp de vocês ({lead['telefone']}).\n\nPosso te enviar o link desse layout que desenhei, sem compromisso nenhum, para você dar uma olhada e ver o que acha?"
        
        st.markdown("#### 📝 Copy de Abordagem Personalizada:")
        st.text_area("Texto pronto:", value=copy_whatsapp, height=220)
        
        texto_url = urllib.parse.quote(copy_whatsapp)
        link_api_whatsapp = f"https://wa.me/{numero_limpo}?text={texto_url}"
        
        st.write("---")
        html_botao = f"""
        <a href="{link_api_whatsapp}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; text-align: center; padding: 15px; font-weight: bold; font-size: 16px; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                💬 Abrir Conversa e Fechar Cliente no WhatsApp
            </div>
        </a>
        """
        st.markdown(html_botao, unsafe_allow_html=True)
