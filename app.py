import streamlit as st
import subprocess
import json
import time
import urllib.parse
import pandas as pd
from playwright.sync_api import sync_playwright
from io import StringIO

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
# 🎨 VISUAL (estilo NEXUS / dark + cyan)
# ============================================================
st.set_page_config(
    page_title="PHOENIX LEADS AI",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', system-ui, sans-serif !important;
}

/* Fundo */
.stApp {
  background: #06080f !important;
}
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(6, 182, 212, 0.07), transparent),
    radial-gradient(ellipse 50% 40% at 100% 100%, rgba(14, 165, 233, 0.04), transparent);
  pointer-events: none;
  z-index: 0;
}

/* Esconde chrome padrão */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }

/* Texto */
h1, h2, h3, h4, p, span, label, .stMarkdown {
  color: #e2e8f0 !important;
}
.stCaption, small { color: #64748b !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
  background: rgba(15, 23, 42, 0.85) !important;
  border: 1px solid rgba(51, 65, 85, 0.7) !important;
  color: #e2e8f0 !important;
  border-radius: 10px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: rgba(34, 211, 238, 0.5) !important;
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.08) !important;
}

/* Botões primários */
.stButton > button {
  background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
  color: #ecfeff !important;
  border: 1px solid rgba(34, 211, 238, 0.3) !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  box-shadow: 0 2px 12px rgba(6, 182, 212, 0.18) !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
  box-shadow: 0 4px 20px rgba(6, 182, 212, 0.28) !important;
  transform: translateY(-1px);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.8);
}
.stTabs [data-baseweb="tab"] {
  color: #64748b !important;
  background: transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #22d3ee !important;
  border-bottom: 2px solid #22d3ee !important;
}

/* Expander / cards */
.streamlit-expanderHeader {
  background: rgba(12, 18, 32, 0.8) !important;
  border: 1px solid rgba(30, 41, 59, 0.8) !important;
  border-radius: 12px !important;
  color: #e2e8f0 !important;
}
div[data-testid="stExpander"] {
  background: rgba(12, 18, 32, 0.55) !important;
  border: 1px solid rgba(30, 41, 59, 0.7) !important;
  border-radius: 14px !important;
}

/* Info boxes */
div[data-testid="stAlert"] {
  background: rgba(12, 18, 32, 0.7) !important;
  border: 1px solid rgba(51, 65, 85, 0.6) !important;
  border-radius: 12px !important;
}

/* Cards de lead */
.lead-card {
  background: rgba(12, 18, 32, 0.72);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 41, 59, 0.85);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  margin-bottom: 0.35rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.lead-card:hover {
  border-color: rgba(34, 211, 238, 0.28);
  box-shadow: 0 8px 28px rgba(0,0,0,0.35);
}
.lead-card h4 {
  margin: 0 0 0.45rem 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #f1f5f9 !important;
}
.lead-card p {
  margin: 0.2rem 0;
  font-size: 0.82rem;
  color: #94a3b8 !important;
}
.badge {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  padding: 0.18rem 0.5rem;
  border-radius: 4px;
  margin-top: 0.35rem;
}
.badge-ok { background: rgba(34,211,238,0.12); color: #22d3ee; border: 1px solid rgba(34,211,238,0.22); }
.badge-warn { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.22); }
.badge-bad { background: rgba(251,113,133,0.12); color: #fb7185; border: 1px solid rgba(251,113,133,0.22); }

/* Progress */
.stProgress > div > div {
  background: linear-gradient(90deg, #0891b2, #22d3ee) !important;
}

/* Download button */
.stDownloadButton > button {
  background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
  color: #ecfeff !important;
  border: 1px solid rgba(34, 211, 238, 0.3) !important;
  border-radius: 10px !important;
}

/* Título */
.phoenix-title {
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: #f8fafc !important;
  margin-bottom: 0.15rem;
}
.phoenix-sub {
  font-size: 0.95rem;
  color: #94a3b8 !important;
  font-weight: 300;
  margin-bottom: 1.25rem;
}
.section-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔍 ANÁLISE DE SITE
# ============================================================
def analisar_site(url):
    if not url or url == "Não informado":
        return "❌ Sem Site"
    u = url.lower()
    if "instagram.com" in u: return "📸 Instagram"
    if "facebook.com" in u: return "👥 Facebook"
    if "youtube.com" in u: return "▶️ YouTube"
    if "tiktok.com" in u: return "🎵 TikTok"
    if "linkedin.com" in u: return "💼 LinkedIn"
    if "linktr.ee" in u or "biolinky" in u: return "🔗 Linktree/Bio"
    if "wa.me" in u or "api.whatsapp" in u: return "💬 WhatsApp"
    return "✅ Site Próprio"

def badge_class(status):
    if not status: return "badge-warn"
    if "✅" in status: return "badge-ok"
    if "❌" in status or "Sem Site" in status: return "badge-bad"
    return "badge-warn"

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
                    barra_progresso.progress((i + 1) / max(len(urls_locais), 1))

                site_coletado = "Não informado"
                links = page.locator('//a[@data-item-id="authority"]').all()
                if links:
                    site_coletado = links[0].get_attribute('href') or "Não informado"

                botoes = page.locator('//button[contains(@data-item-id, "phone:tel:")]').all()
                telefone = (
                    botoes[0].get_attribute('data-item-id').replace('phone:tel:', '').strip()
                    if botoes else "Não informado"
                )

                status_site = analisar_site(site_coletado)

                leads.append({
                    "id": i + 1,
                    "empresa": nome,
                    "telefone": telefone,
                    "status_site": status_site,
                    "link_coletado": site_coletado,
                    "link": url_local,
                })
            except Exception:
                continue

        browser.close()
    return leads

# ============================================================
# ⭐ LISTA DE INTERESSE
# ============================================================
def _chave_lead(lead):
    return lead.get("link") or f"{lead.get('empresa', '')}|{lead.get('telefone', '')}"

def adicionar_a_lista(lead):
    chave = _chave_lead(lead)
    existentes = {_chave_lead(l) for l in st.session_state["lista_interesse"]}
    if chave not in existentes:
        st.session_state["lista_interesse"].append({
            "empresa": lead.get("empresa", ""),
            "telefone": lead.get("telefone", ""),
            "status_site": lead.get("status_site", ""),
            "link_coletado": lead.get("link_coletado", ""),
            "link": lead.get("link", ""),
        })
        return True
    return False

def remover_da_lista(chave):
    st.session_state["lista_interesse"] = [
        l for l in st.session_state["lista_interesse"] if _chave_lead(l) != chave
    ]

def lead_esta_na_lista(lead):
    chave = _chave_lead(lead)
    return any(_chave_lead(l) == chave for l in st.session_state["lista_interesse"])

def exportar_lista_csv():
    if not st.session_state["lista_interesse"]:
        return None
    df = pd.DataFrame(st.session_state["lista_interesse"])
    colunas = ["empresa", "telefone", "status_site", "link_coletado", "link"]
    df = df[[c for c in colunas if c in df.columns]]
    buf = StringIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()

# ============================================================
# 🥷 API FLUTTER
# ============================================================
params = st.query_params
if "api" in params and "nicho" in params and "cidade" in params:
    resultado = extrair_leads(
        f"{params['nicho']} em {params['cidade']}",
        int(params.get("limite", 10)),
    )
    st.text(json.dumps({"status": "sucesso", "dados": resultado}, ensure_ascii=False))
    st.stop()

# ============================================================
# 🖥️ ESTADO
# ============================================================
if "leads_salvos" not in st.session_state:
    st.session_state["leads_salvos"] = pd.DataFrame()
if "lead_selecionado" not in st.session_state:
    st.session_state["lead_selecionado"] = None
if "lista_interesse" not in st.session_state:
    # migra carrinho antigo se existir
    if "carrinho_leads" in st.session_state and st.session_state["carrinho_leads"]:
        st.session_state["lista_interesse"] = st.session_state["carrinho_leads"]
    else:
        st.session_state["lista_interesse"] = []

# ============================================================
# 🖥️ UI
# ============================================================
aba1, aba2, aba3 = st.tabs([
    "🦅 Mineração Phoenix",
    "🤖 Construtor de Site",
    "💬 Prospectar Cliente",
])

# ---- ABA 1 ----
with aba1:
    st.markdown('<p class="phoenix-title">🦅 PHOENIX LEADS AI</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="phoenix-sub">Extraia leads do Google Maps com análise de presença digital</p>',
        unsafe_allow_html=True,
    )

    qtd = len(st.session_state["lista_interesse"])
    with st.expander(f"⭐ Lista de Interesse ({qtd})", expanded=qtd > 0):
        if qtd == 0:
            st.caption("Nenhum lead na lista ainda. Adicione a partir dos resultados abaixo.")
        else:
            st.markdown(f"**{qtd} lead(s)** — permanecem mesmo após nova mineração.")
            for i, item in enumerate(st.session_state["lista_interesse"]):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                with c1:
                    st.write(f"**{item['empresa']}**")
                with c2:
                    st.write(item["telefone"])
                with c3:
                    st.write(item["status_site"])
                with c4:
                    if st.button("🗑️", key=f"rm_lista_{i}", help="Remover"):
                        remover_da_lista(_chave_lead(item))
                        st.rerun()

            st.write("")
            col_a, col_b = st.columns([2, 1])
            with col_a:
                csv_data = exportar_lista_csv()
                if csv_data:
                    st.download_button(
                        "📥 Exportar Lista em CSV",
                        data=csv_data,
                        file_name=f"phoenix_lista_interesse_{qtd}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
            with col_b:
                if st.button("🧹 Limpar Lista", use_container_width=True):
                    st.session_state["lista_interesse"] = []
                    st.rerun()

    st.write("")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        termo = st.text_input("🔎 Nicho / Profissão", "Barbearia")
    with col2:
        cidade = st.text_input("📍 Cidade", "São Paulo")
    with col3:
        limite = st.number_input("📊 Limite", min_value=5, max_value=100, value=10)

    if st.button("🚀 Minerar Agora", use_container_width=True):
        barra = st.progress(0)
        status = st.empty()
        dados = extrair_leads(f"{termo} em {cidade}", limite, status_texto=status, barra_progresso=barra)
        status.text("✅ Mineração concluída!")
        if dados:
            st.session_state["leads_salvos"] = pd.DataFrame(dados)
            st.success(f"🎯 {len(dados)} leads encontrados! (Lista de Interesse intacta)")
        else:
            st.warning("Nenhum lead encontrado. Ajuste os termos.")

    if not st.session_state["leads_salvos"].empty:
        df = st.session_state["leads_salvos"]
        st.write("---")
        st.subheader("🎯 Leads encontrados")

        faltando = [r.to_dict() for _, r in df.iterrows() if not lead_esta_na_lista(r.to_dict())]
        if faltando:
            if st.button(
                f"➕ Adicionar todos os {len(faltando)} à Lista de Interesse",
                use_container_width=True,
            ):
                n = sum(1 for l in faltando if adicionar_a_lista(l))
                st.success(f"✅ {n} lead(s) adicionados!")
                st.rerun()

        cols = st.columns(3)
        for idx, (_, row) in enumerate(df.iterrows()):
            lead = row.to_dict()
            na = lead_esta_na_lista(lead)
            bc = badge_class(lead.get("status_site", ""))
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="lead-card">
                  <h4>{lead['empresa']}</h4>
                  <p>📞 {lead['telefone']}</p>
                  <span class="badge {bc}">{lead['status_site']}</span>
                  <p style="margin-top:0.5rem;font-size:0.75rem;opacity:0.7;">🔗 {str(lead.get('link_coletado',''))[:38]}…</p>
                </div>
                """, unsafe_allow_html=True)

                if na:
                    st.caption("✅ Na Lista de Interesse")
                    if st.button("🗑️ Remover", key=f"rm_card_{idx}", use_container_width=True):
                        remover_da_lista(_chave_lead(lead))
                        st.rerun()
                else:
                    if st.button("➕ Lista de Interesse", key=f"add_card_{idx}", use_container_width=True):
                        if adicionar_a_lista(lead):
                            st.rerun()

        st.write("---")
        st.markdown("### 🔍 Detalhes do lead")
        opcoes = {f"[{r['status_site']}] — {r['empresa']}": r for _, r in df.iterrows()}
        escolhido = st.selectbox("Selecione um lead", list(opcoes.keys()))
        info = opcoes[escolhido]
        lead_dict = info.to_dict() if hasattr(info, "to_dict") else dict(info)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.info(f"**🏢 Empresa**\n\n{lead_dict['empresa']}")
        with c2:
            st.info(f"**📱 Telefone**\n\n{lead_dict['telefone']}")
        with c3:
            st.info(f"**🌐 Status**\n\n{lead_dict['status_site']}")

        st.markdown(f"[Abrir no Google Maps]({lead_dict['link']})")
        st.caption(f"Link cadastrado: {lead_dict['link_coletado']}")

        if lead_esta_na_lista(lead_dict):
            st.caption("✅ Já está na Lista de Interesse")
        else:
            if st.button("➕ Adicionar à Lista de Interesse", key="add_detalhe", use_container_width=True):
                if adicionar_a_lista(lead_dict):
                    st.rerun()

        if st.button("🚀 Usar no Construtor / WhatsApp", use_container_width=True):
            st.session_state["lead_selecionado"] = lead_dict
            st.success("Lead ativo. Vá nas abas Construtor ou Prospectar.")

# ---- ABA 2 ----
with aba2:
    st.markdown('<p class="phoenix-title">🤖 Construtor de Site</p>', unsafe_allow_html=True)
    lead = st.session_state["lead_selecionado"]
    if lead is None:
        st.info("Selecione um lead na Mineração e clique em **Usar no Construtor / WhatsApp**.")
    else:
        st.success(f"**{lead['empresa']}** · {lead['status_site']}")
        tem_site = "✅" in lead.get("status_site", "")
        arg = (
            "possui um site, mas pode ser otimizado para conversão"
            if tem_site
            else f"não tem página profissional (só '{lead['link_coletado']}')"
        )
        st.markdown(f"""
**Diagnóstico:** A empresa **{lead['empresa']}** {arg}.

**Foco:** transformar busca local em agendamento via **{lead['telefone']}**.
""")
        prompt = f"""Escreva um prompt para o Vibe Code criar um site para {lead['empresa']} ({lead['status_site']}, link: {lead['link_coletado']}).

Dados:
- Nome: {lead['empresa']}
- Telefone: {lead['telefone']}
- Situação web: {lead['status_site']}

Diretrizes:
1. Landing page de alta conversão
2. Seções: Hero, Serviços, Prova Social, Contato
3. Botões de ação para WhatsApp: {lead['telefone']}
"""
        st.code(prompt, language="text")

# ---- ABA 3 ----
with aba3:
    st.markdown('<p class="phoenix-title">💬 Prospecção WhatsApp</p>', unsafe_allow_html=True)
    lead = st.session_state["lead_selecionado"]
    if lead is None:
        st.info("Selecione um lead na Mineração e clique em **Usar no Construtor / WhatsApp**.")
    else:
        st.markdown(f"Abordagem para **{lead['empresa']}**")
        num = "".join(filter(str.isdigit, lead["telefone"]))
        if num and not num.startswith("55"):
            num = "55" + num

        status = lead.get("status_site", "")
        if "Instagram" in status:
            gatilho = "Notei que vocês usam o Instagram como página principal. Funciona pra conteúdo, mas perde quem busca no Google querendo site rápido com agendamento."
        elif "Sem Site" in status:
            gatilho = "Notei que vocês ainda não têm site cadastrado pra quem encontra vocês na internet."
        elif "Linktree" in status or "WhatsApp" in status:
            gatilho = "Notei que vocês usam só agregador de links. Isso limita a autoridade pra quem busca no Google."
        else:
            gatilho = "Analisei a presença de vocês no mapa e montei uma proposta de site focado em mais agendamentos."

        copy = f"""Olá, tudo bem? Sou especialista em positioning digital e encontrei o perfil da *{lead['empresa']}* no Google.

{gatilho} Montei um protótipo de site moderno, focado em conversão e integrado ao WhatsApp ({lead['telefone']}).

Posso te enviar o link desse layout, sem compromisso, pra você ver o que acha?"""

        st.text_area("Copy pronta", value=copy, height=220)
        link = f"https://wa.me/{num}?text={urllib.parse.quote(copy)}"
        st.markdown(
            f'<a href="{link}" target="_blank" style="display:inline-block;padding:0.7rem 1.2rem;background:linear-gradient(135deg,#0891b2,#0e7490);color:#ecfeff;border-radius:10px;text-decoration:none;font-weight:500;border:1px solid rgba(34,211,238,0.3);">💬 Abrir no WhatsApp</a>',
            unsafe_allow_html=True,
        )