import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import json

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Panel · indie.",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = "https://vxkczsctgsxonxwjrfqe.supabase.co"
SUPABASE_KEY = "sb_publishable_i2aKMZLyZ6_9u7yRztf3KA_TkCOJqEc"

GITHUB_RAW = "https://raw.githubusercontent.com/IndieAgency/planning-indie-agency/main/"
BG_URL   = GITHUB_RAW + "FOTO%20PERFIL%20V3.png"
LOGO_URL = GITHUB_RAW + "IMAGOTIPO%20NEGRO.png"

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    [data-testid="stSidebar"] {{ background: #1a1a1a !important; }}
    [data-testid="stSidebar"] * {{ color: #fff !important; }}
    .activity-item {{
        background: #fafafa;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 3px solid #f06292;
    }}

    /* BITE ANIMATION OVERLAY */
    .bite-overlay {{
        position: fixed;
        inset: 0;
        z-index: 9999;
        pointer-events: none;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(249,168,212,0.15);
        animation: fadeInOut 1.4s ease forwards;
    }}
    .bite-top {{
        position: fixed;
        top: -120px;
        left: 50%;
        transform: translateX(-50%);
        width: 420px;
        height: 180px;
        background: #1a1a1a;
        border-radius: 0 0 50% 50%;
        animation: biteDown 0.55s cubic-bezier(.4,0,.2,1) 0.1s forwards;
        clip-path: polygon(
            0% 0%, 6% 0%, 6% 60%, 10% 100%, 14% 60%, 18% 0%,
            24% 0%, 24% 65%, 28% 100%, 32% 65%, 36% 0%,
            42% 0%, 42% 70%, 46% 100%, 50% 70%, 54% 0%,
            60% 0%, 60% 65%, 64% 100%, 68% 65%, 72% 0%,
            78% 0%, 78% 60%, 82% 100%, 86% 60%, 90% 0%,
            100% 0%
        );
    }}
    .bite-bottom {{
        position: fixed;
        bottom: -120px;
        left: 50%;
        transform: translateX(-50%);
        width: 420px;
        height: 180px;
        background: #1a1a1a;
        border-radius: 50% 50% 0 0;
        animation: biteUp 0.55s cubic-bezier(.4,0,.2,1) 0.1s forwards;
        clip-path: polygon(
            0% 100%, 6% 100%, 6% 40%, 10% 0%, 14% 40%, 18% 100%,
            24% 100%, 24% 35%, 28% 0%, 32% 35%, 36% 100%,
            42% 100%, 42% 30%, 46% 0%, 50% 30%, 54% 100%,
            60% 100%, 60% 35%, 64% 0%, 68% 35%, 72% 100%,
            78% 100%, 78% 40%, 82% 0%, 86% 40%, 90% 100%,
            100% 100%
        );
    }}
    @keyframes biteDown {{
        from {{ top: -120px; }}
        to {{ top: 0px; }}
    }}
    @keyframes biteUp {{
        from {{ bottom: -120px; }}
        to {{ bottom: 0px; }}
    }}
    @keyframes fadeInOut {{
        0% {{ opacity:0; }}
        20% {{ opacity:1; }}
        70% {{ opacity:1; }}
        100% {{ opacity:0; }}
    }}
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_clients():
    r = get_supabase().table("clients").select("*").execute()
    return r.data or []

def get_posts():
    r = get_supabase().table("posts").select("*").order("date", desc=True).execute()
    return r.data or []

def get_scripts():
    r = get_supabase().table("scripts").select("*").order("created_at", desc=True).execute()
    return r.data or []

def update_client(client_id, data):
    get_supabase().table("clients").update(data).eq("id", client_id).execute()

def delete_post_db(post_id):
    get_supabase().table("posts").delete().eq("id", post_id).execute()

def delete_script_db(script_id):
    get_supabase().table("scripts").delete().eq("id", script_id).execute()

# ── HELPERS ───────────────────────────────────────────────────────────────────
APPROVAL_LABELS = {
    "pendiente": "⏳ Pendiente",
    "aprobado": "✅ Aprobado",
    "cambios": "🔄 Con cambios"
}
STATUS_COLORS = {"Idea":"#f0f0f0","En redacción":"#fff9c4","Listo":"#c8e6c9","Publicado":"#bbdefb"}

def parse_notes(raw):
    if isinstance(raw, str):
        try: return json.loads(raw)
        except: return []
    return raw or []

def get_all_activity(posts, scripts):
    activity = []
    for p in posts:
        for n in parse_notes(p.get("notes")):
            activity.append({"autor":n.get("author","?"),"texto":n.get("text",""),
                "fecha":n.get("date",""),"tipo":"📅 Post","titulo":p.get("title","Sin título")})
    for s in scripts:
        for n in parse_notes(s.get("notes")):
            activity.append({"autor":n.get("author","?"),"texto":n.get("text",""),
                "fecha":n.get("date",""),"tipo":"📝 Guión","titulo":s.get("title","Sin título")})
    return sorted(activity, key=lambda x: x["fecha"], reverse=True)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def login_screen():
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, #f9a8d4 0%, #fde68a 100%);
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        inset: -80px;
        background-image: url('{BG_URL}');
        background-size: 52%;
        background-position: center center;
        background-repeat: no-repeat;
        opacity: 0.13;
        filter: blur(14px);
        -webkit-mask-image: radial-gradient(ellipse 55% 65% at 50% 50%, black 40%, transparent 100%);
        mask-image: radial-gradient(ellipse 55% 65% at 50% 50%, black 40%, transparent 100%);
        z-index: 0;
    }}
    [data-testid="stAppViewBlockContainer"] {{ background: transparent; position: relative; z-index: 1; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([2, 1, 2])
    with col:
        st.markdown("""
        <div style="text-align:center;margin-bottom:22px">
            <div style="font-size:2.2rem;font-weight:900;color:#1a1a1a;letter-spacing:-1px;line-height:1">
                indie.<sup style="font-size:0.9rem;font-weight:700;vertical-align:super;letter-spacing:0"> ®</sup>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            if st.button("Ingresar →", use_container_width=True, type="primary"):
                clients = get_clients()
                match = next((c for c in clients if c["username"]==username and c["password"]==password), None)
                if match and match["id"] == "admin":
                    # Show bite animation before login
                    st.markdown("""
                    <div class="bite-overlay">
                        <div class="bite-top"></div>
                        <div class="bite-bottom"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    import time
                    time.sleep(1.2)
                    st.session_state.logged_in = True
                    st.rerun()
                elif match:
                    st.error("Solo el usuario Admin puede acceder.")
                else:
                    st.error("Usuario o contraseña incorrectos.")

# ── PÁGINAS ───────────────────────────────────────────────────────────────────
def page_dashboard(clients, all_posts, all_scripts):
    st.markdown("# 📊 Dashboard General")
    st.markdown("---")
    total_comments = sum(len(parse_notes(p.get("notes"))) for p in all_posts + all_scripts)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("👥 Clientes", len(clients))
    c2.metric("📅 Posts", len(all_posts))
    c3.metric("✅ Publicados", sum(1 for p in all_posts if p.get("status")=="Publicado"))
    c4.metric("📝 Guiones", len(all_scripts))
    c5.metric("💬 Comentarios", total_comments)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Posts por estado")
        if all_posts:
            df = pd.Series([p.get("status","Idea") for p in all_posts]).value_counts().reset_index()
            df.columns = ["Estado","Cantidad"]
            fig = px.pie(df, names="Estado", values="Cantidad",
                         color_discrete_sequence=["#bbdefb","#c8e6c9","#fff9c4","#f0f0f0"])
            fig.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=280)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin posts todavía.")

    with col2:
        st.markdown("### Posts por plataforma")
        if all_posts:
            df = pd.Series([p.get("platform","instagram") for p in all_posts]).value_counts().reset_index()
            df.columns = ["Plataforma","Cantidad"]
            df["Plataforma"] = df["Plataforma"].map({"instagram":"📸 Instagram","linkedin":"💼 LinkedIn"}).fillna(df["Plataforma"])
            fig2 = px.bar(df, x="Plataforma", y="Cantidad",
                          color_discrete_map={"📸 Instagram":"#E1306C","💼 LinkedIn":"#0A66C2"}, color="Plataforma")
            fig2.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=280, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Actividad mensual")
    if all_posts:
        df2 = pd.DataFrame(all_posts)
        df2["date"] = pd.to_datetime(df2["date"], errors="coerce")
        df2 = df2.dropna(subset=["date"])
        df2["mes"] = df2["date"].dt.to_period("M").astype(str)
        monthly = df2.groupby("mes").size().reset_index(name="posts")
        fig3 = px.bar(monthly, x="mes", y="posts")
        fig3.update_traces(marker_color="#f06292")
        fig3.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=220)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Guiones por aprobación")
    if all_scripts:
        df3 = pd.Series([s.get("approval_status","pendiente") for s in all_scripts]).value_counts().reset_index()
        df3.columns = ["Estado","Cantidad"]
        df3["Estado"] = df3["Estado"].map(APPROVAL_LABELS).fillna(df3["Estado"])
        fig4 = px.bar(df3, x="Estado", y="Cantidad", color="Estado",
                      color_discrete_map={"⏳ Pendiente":"#fff9c4","✅ Aprobado":"#c8e6c9","🔄 Con cambios":"#ffccbc"})
        fig4.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=220, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

def page_posts(clients, all_posts):
    st.markdown("# 📅 Posts del Calendario")
    st.markdown("---")
    client_names = {c["id"]: c["name"] for c in clients}
    c1,c2,c3,c4 = st.columns(4)
    cf = c1.selectbox("Cliente", ["Todos"]+list(client_names.values()))
    sf = c2.selectbox("Estado", ["Todos","Idea","En redacción","Listo","Publicado"])
    pf = c3.selectbox("Plataforma", ["Todas","Instagram","LinkedIn"])
    se = c4.text_input("🔍 Buscar")

    filtered = all_posts
    if cf != "Todos":
        cid = next((c["id"] for c in clients if c["name"]==cf), None)
        if cid: filtered = [p for p in filtered if p["client_id"]==cid]
    if sf != "Todos": filtered = [p for p in filtered if p.get("status")==sf]
    if pf != "Todas": filtered = [p for p in filtered if p.get("platform")==pf.lower()]
    if se: filtered = [p for p in filtered if se.lower() in (p.get("title") or "").lower()]

    st.markdown(f"**{len(filtered)} posts encontrados**")
    for post in filtered:
        notes = parse_notes(post.get("notes"))
        plat_icon = "📸" if post.get("platform")=="instagram" else "💼"
        with st.expander(f"{plat_icon} **{post.get('title','Sin título')}** — {post.get('date','')} · {client_names.get(post.get('client_id'),'?')}"):
            c1,c2,c3 = st.columns([2,1,1])
            c1.markdown(f"**Estado:** {post.get('status','')}")
            c1.markdown(f"**Tipo:** {post.get('ctype','')}")
            if post.get("caption"): c1.markdown(f"**Caption:** {post.get('caption','')[:200]}")
            c2.markdown(f"**Comentarios:** 💬 {len(notes)}")
            if c3.button("🗑️ Eliminar", key=f"dp_{post['id']}"):
                delete_post_db(post["id"]); st.success("Eliminado."); st.rerun()
            if notes:
                st.markdown("**Comentarios:**")
                for n in notes:
                    st.markdown(f"<div class='activity-item'><strong>{n.get('author','?')}</strong> <span style='color:#aaa;font-size:0.8rem'>{n.get('date','')}</span><br/>{n.get('text','')}</div>", unsafe_allow_html=True)

def page_scripts(clients, all_scripts):
    st.markdown("# 📝 Guiones de Contenido")
    st.markdown("---")
    client_names = {c["id"]: c["name"] for c in clients}
    c1,c2,c3 = st.columns(3)
    cf = c1.selectbox("Cliente", ["Todos"]+list(client_names.values()))
    af = c2.selectbox("Aprobación", ["Todos","Pendiente","Aprobado","Con cambios"])
    se = c3.text_input("🔍 Buscar")

    filtered = all_scripts
    if cf != "Todos":
        cid = next((c["id"] for c in clients if c["name"]==cf), None)
        if cid: filtered = [s for s in filtered if s["client_id"]==cid]
    am = {"Pendiente":"pendiente","Aprobado":"aprobado","Con cambios":"cambios"}
    if af != "Todos": filtered = [s for s in filtered if s.get("approval_status")==am[af]]
    if se: filtered = [s for s in filtered if se.lower() in (s.get("title") or "").lower()]

    for script in filtered:
        aprov = script.get("approval_status","pendiente")
        notes = parse_notes(script.get("notes"))
        scenes = script.get("scenes") or []
        with st.expander(f"**{script.get('title','Sin título')}** — {APPROVAL_LABELS.get(aprov,aprov)} · {client_names.get(script.get('client_id'),'?')}"):
            c1,c2,c3 = st.columns([2,1,1])
            c1.markdown(f"**Tipo:** {script.get('ctype','')} · **Objetivo:** {script.get('objective','')}")
            if script.get("date"): c1.markdown(f"**Fecha:** {script.get('date')}")
            c2.markdown(f"**Escenas:** {len(scenes)}")
            c2.markdown(f"**Comentarios:** 💬 {len(notes)}")
            new_aprov = c3.selectbox("Estado", ["pendiente","aprobado","cambios"],
                index=["pendiente","aprobado","cambios"].index(aprov), key=f"ap_{script['id']}")
            if new_aprov != aprov and c3.button("Guardar", key=f"sap_{script['id']}"):
                get_supabase().table("scripts").update({"approval_status":new_aprov}).eq("id",script["id"]).execute()
                st.success("Actualizado."); st.rerun()
            if c3.button("🗑️ Eliminar", key=f"ds_{script['id']}"):
                delete_script_db(script["id"]); st.success("Eliminado."); st.rerun()
            if scenes:
                st.markdown("**Tabla Audio/Video:**")
                df = pd.DataFrame(scenes)
                df.index = [f"Escena {i+1}" for i in range(len(df))]
                st.dataframe(df, use_container_width=True)
            if notes:
                st.markdown("**Comentarios:**")
                for n in notes:
                    st.markdown(f"<div class='activity-item'><strong>{n.get('author','?')}</strong> <span style='color:#aaa;font-size:0.8rem'>{n.get('date','')}</span><br/>{n.get('text','')}</div>", unsafe_allow_html=True)

def page_activity(all_posts, all_scripts):
    st.markdown("# 💬 Actividad Reciente")
    st.markdown("---")
    activity = get_all_activity(all_posts, all_scripts)
    if not activity:
        st.info("No hay comentarios todavía.")
        return
    authors = pd.Series([a["autor"] for a in activity]).value_counts().reset_index()
    authors.columns = ["Usuario","Comentarios"]
    c1,c2 = st.columns([1,2])
    with c1:
        st.markdown("### Por usuario")
        st.dataframe(authors, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("### Distribución")
        fig = px.pie(authors, names="Usuario", values="Comentarios")
        fig.update_layout(margin=dict(t=10,b=0,l=0,r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    fa = st.selectbox("Filtrar por usuario", ["Todos"]+authors["Usuario"].tolist())
    shown = activity if fa=="Todos" else [a for a in activity if a["autor"]==fa]
    for item in shown:
        st.markdown(f"""<div class='activity-item'>
            <div style='display:flex;justify-content:space-between'>
                <div><strong>{item['autor']}</strong>
                <span style='background:#f0f0f0;border-radius:10px;padding:2px 8px;font-size:0.75rem;margin-left:8px'>{item['tipo']}</span>
                <span style='color:#666;font-size:0.85rem;margin-left:6px'>{item['titulo']}</span></div>
                <span style='color:#aaa;font-size:0.78rem'>{item['fecha']}</span>
            </div>
            <div style='color:#333;margin-top:4px'>{item['texto']}</div>
        </div>""", unsafe_allow_html=True)

def page_clients(clients):
    st.markdown("# 👥 Gestión de Clientes")
    st.markdown("---")
    st.info("Los clientes **solo pueden comentar** desde la app — no acceden a este panel.")
    for client in clients:
        with st.expander(f"**{client['name']}** — @{client['username']} {'🔑 Admin' if client['id']=='admin' else ''}"):
            c1,c2 = st.columns(2)
            with c1:
                nn = st.text_input("Nombre", value=client.get("name",""), key=f"n_{client['id']}")
                nu = st.text_input("Usuario", value=client.get("username",""), key=f"u_{client['id']}")
                np = st.text_input("Contraseña editor", value=client.get("password",""), key=f"p_{client['id']}", type="password")
                ng = st.text_input("Contraseña invitado", value=client.get("guest_password",""), key=f"g_{client['id']}", type="password")
            with c2:
                ni = st.text_input("Instagram @", value=client.get("instagram",""), key=f"i_{client['id']}")
                nl = st.text_input("LinkedIn @", value=client.get("linkedin",""), key=f"l_{client['id']}")
            if st.button("💾 Guardar", key=f"s_{client['id']}"):
                update_client(client["id"], {"name":nn,"username":nu,"password":np,"guest_password":ng,"instagram":ni,"linkedin":nl})
                st.success(f"✅ {nn} actualizado."); st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login_screen()
        return

    clients = get_clients()
    all_posts = get_posts()
    all_scripts = get_scripts()

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 12px">
            <img src="{LOGO_URL}" style="height:52px;filter:invert(1);opacity:0.95"/>
            <div style="font-size:1.05rem;font-weight:800;color:#fff;letter-spacing:-0.3px;margin-top:8px">
                indie.<sup style="font-size:0.5rem;font-weight:600;vertical-align:super"> ®</sup>
            </div>
            <div style="font-size:0.65rem;color:#555;letter-spacing:1px;text-transform:uppercase;margin-top:2px">Panel Admin</div>
        </div>
        <hr style="border-color:#2a2a2a;margin:4px 0 12px"/>
        """, unsafe_allow_html=True)
        page = st.radio("", ["📊 Dashboard","📅 Posts","📝 Guiones","💬 Actividad","👥 Clientes"])
        st.markdown("---")
        st.markdown(f"Posts: **{len(all_posts)}** · Guiones: **{len(all_scripts)}**")
        st.markdown(f"Clientes: **{len(clients)}**")
        st.markdown("---")
        if st.button("↩️ Cerrar sesión"):
            st.session_state.logged_in = False; st.rerun()

    if page == "📊 Dashboard": page_dashboard(clients, all_posts, all_scripts)
    elif page == "📅 Posts": page_posts(clients, all_posts)
    elif page == "📝 Guiones": page_scripts(clients, all_scripts)
    elif page == "💬 Actividad": page_activity(all_posts, all_scripts)
    elif page == "👥 Clientes": page_clients(clients)

if __name__ == "__main__":
    main()
