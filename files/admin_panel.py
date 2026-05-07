import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, date
import json

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Admin · Planning Indie Agency",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = "https://vxkczsctgsxonxwjrfqe.supabase.co"
SUPABASE_KEY = "sb_publishable_i2aKMZLyZ6_9u7yRztf3KA_TkCOJqEc"

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #1a1a1a; }
    [data-testid="stSidebar"] * { color: #fff !important; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1.5px solid #ebebeb;
        text-align: center;
    }
    .metric-num { font-size: 2rem; font-weight: 700; color: #1a1a1a; }
    .metric-label { font-size: 0.8rem; color: #888; margin-top: 4px; }
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .activity-item {
        background: #fafafa;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 3px solid #6c5ce7;
    }
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_clients():
    sb = get_supabase()
    r = sb.table("clients").select("*").execute()
    return r.data or []

def get_posts(client_id=None):
    sb = get_supabase()
    q = sb.table("posts").select("*")
    if client_id:
        q = q.eq("client_id", client_id)
    r = q.order("date", desc=True).execute()
    return r.data or []

def get_scripts(client_id=None):
    sb = get_supabase()
    q = sb.table("scripts").select("*")
    if client_id:
        q = q.eq("client_id", client_id)
    r = q.order("created_at", desc=True).execute()
    return r.data or []

def update_client(client_id, data):
    sb = get_supabase()
    sb.table("clients").update(data).eq("id", client_id).execute()

def delete_post_db(post_id):
    sb = get_supabase()
    sb.table("posts").delete().eq("id", post_id).execute()

def delete_script_db(script_id):
    sb = get_supabase()
    sb.table("scripts").delete().eq("id", script_id).execute()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def login_screen():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 📅 Panel Admin")
        st.markdown("**Planning Indie Agency**")
        st.markdown("---")
        username = st.text_input("Usuario", placeholder="admin")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        if st.button("Ingresar →", use_container_width=True, type="primary"):
            clients = get_clients()
            match = next((c for c in clients if c["username"] == username and c["password"] == password), None)
            if match and match["id"] == "admin":
                st.session_state.logged_in = True
                st.session_state.admin_user = match
                st.rerun()
            elif match:
                st.error("Solo el usuario Admin puede acceder a este panel.")
            else:
                st.error("Usuario o contraseña incorrectos.")

# ── HELPERS ───────────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "Idea": "#f0f0f0",
    "En redacción": "#fff9c4",
    "Listo": "#c8e6c9",
    "Publicado": "#bbdefb"
}
STATUS_TEXT = {
    "Idea": "#777",
    "En redacción": "#795548",
    "Listo": "#2e7d32",
    "Publicado": "#1565c0"
}
APPROVAL_LABELS = {
    "pendiente": "⏳ Pendiente",
    "aprobado": "✅ Aprobado",
    "cambios": "🔄 Con cambios"
}
APPROVAL_COLORS = {
    "pendiente": "#fff9c4",
    "aprobado": "#c8e6c9",
    "cambios": "#ffccbc"
}

def get_all_activity(posts, scripts):
    """Recolecta toda la actividad reciente (comentarios) de posts y guiones."""
    activity = []
    for p in posts:
        notes = p.get("notes")
        if isinstance(notes, str):
            try: notes = json.loads(notes)
            except: notes = []
        for n in (notes or []):
            activity.append({
                "autor": n.get("author", "?"),
                "texto": n.get("text", ""),
                "fecha": n.get("date", ""),
                "tipo": "📅 Post",
                "titulo": p.get("title", "Sin título"),
                "id": p.get("id")
            })
    for s in scripts:
        notes = s.get("notes")
        if isinstance(notes, str):
            try: notes = json.loads(notes)
            except: notes = []
        for n in (notes or []):
            activity.append({
                "autor": n.get("author", "?"),
                "texto": n.get("text", ""),
                "fecha": n.get("date", ""),
                "tipo": "📝 Guión",
                "titulo": s.get("title", "Sin título"),
                "id": s.get("id")
            })
    return sorted(activity, key=lambda x: x["fecha"], reverse=True)

# ── PÁGINAS ───────────────────────────────────────────────────────────────────

def page_dashboard(clients, all_posts, all_scripts):
    st.markdown("# 📊 Dashboard General")
    st.markdown("---")

    total_clients = len(clients)
    total_posts = len(all_posts)
    total_published = sum(1 for p in all_posts if p.get("status") == "Publicado")
    total_scripts = len(all_scripts)
    total_approved = sum(1 for s in all_scripts if s.get("approval_status") == "aprobado")
    total_comments = sum(
        len(json.loads(p["notes"]) if isinstance(p.get("notes"), str) else (p.get("notes") or []))
        for p in all_posts + all_scripts
    )

    # Métricas principales
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("👥 Clientes", total_clients)
    with c2:
        st.metric("📅 Posts totales", total_posts)
    with c3:
        st.metric("✅ Publicados", total_published)
    with c4:
        st.metric("📝 Guiones", total_scripts)
    with c5:
        st.metric("💬 Comentarios", total_comments)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📈 Posts por estado")
        if all_posts:
            status_counts = pd.Series([p.get("status", "Idea") for p in all_posts]).value_counts().reset_index()
            status_counts.columns = ["Estado", "Cantidad"]
            colors = [STATUS_COLORS.get(s, "#f0f0f0") for s in status_counts["Estado"]]
            fig = px.pie(status_counts, names="Estado", values="Cantidad",
                        color_discrete_sequence=["#bbdefb","#c8e6c9","#fff9c4","#f0f0f0"])
            fig.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=280)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin posts todavía.")

    with col_right:
        st.markdown("### 📱 Posts por plataforma")
        if all_posts:
            plat_counts = pd.Series([p.get("platform", "instagram") for p in all_posts]).value_counts().reset_index()
            plat_counts.columns = ["Plataforma", "Cantidad"]
            plat_counts["Plataforma"] = plat_counts["Plataforma"].map({"instagram": "📸 Instagram", "linkedin": "💼 LinkedIn"}).fillna(plat_counts["Plataforma"])
            fig2 = px.bar(plat_counts, x="Plataforma", y="Cantidad",
                         color="Plataforma",
                         color_discrete_map={"📸 Instagram": "#E1306C", "💼 LinkedIn": "#0A66C2"})
            fig2.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=280, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sin posts todavía.")

    # Posts por mes
    st.markdown("### 📆 Actividad mensual")
    if all_posts:
        df_posts = pd.DataFrame(all_posts)
        df_posts["date"] = pd.to_datetime(df_posts["date"], errors="coerce")
        df_posts = df_posts.dropna(subset=["date"])
        df_posts["mes"] = df_posts["date"].dt.to_period("M").astype(str)
        monthly = df_posts.groupby("mes").size().reset_index(name="posts")
        fig3 = px.bar(monthly, x="mes", y="posts", labels={"mes": "Mes", "posts": "Posts"})
        fig3.update_traces(marker_color="#6c5ce7")
        fig3.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=220)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sin datos de fechas todavía.")

    # Guiones por estado
    st.markdown("### 📝 Guiones por estado de aprobación")
    if all_scripts:
        aprov_counts = pd.Series([s.get("approval_status", "pendiente") for s in all_scripts]).value_counts().reset_index()
        aprov_counts.columns = ["Estado", "Cantidad"]
        aprov_counts["Estado"] = aprov_counts["Estado"].map(APPROVAL_LABELS).fillna(aprov_counts["Estado"])
        fig4 = px.bar(aprov_counts, x="Estado", y="Cantidad",
                     color="Estado",
                     color_discrete_map={
                         "⏳ Pendiente": "#fff9c4",
                         "✅ Aprobado": "#c8e6c9",
                         "🔄 Con cambios": "#ffccbc"
                     })
        fig4.update_layout(margin=dict(t=20,b=0,l=0,r=0), height=220, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Sin guiones todavía.")


def page_posts(clients, all_posts):
    st.markdown("# 📅 Posts del Calendario")
    st.markdown("---")

    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        client_names = {c["id"]: c["name"] for c in clients}
        client_filter = st.selectbox("Cliente", ["Todos"] + list(client_names.values()))
    with col2:
        status_filter = st.selectbox("Estado", ["Todos"] + ["Idea", "En redacción", "Listo", "Publicado"])
    with col3:
        plat_filter = st.selectbox("Plataforma", ["Todas", "Instagram", "LinkedIn"])
    with col4:
        search = st.text_input("🔍 Buscar", placeholder="Título del post...")

    # Filtrar
    filtered = all_posts
    if client_filter != "Todos":
        cid = next((c["id"] for c in clients if c["name"] == client_filter), None)
        if cid:
            filtered = [p for p in filtered if p["client_id"] == cid]
    if status_filter != "Todos":
        filtered = [p for p in filtered if p.get("status") == status_filter]
    if plat_filter != "Todas":
        filtered = [p for p in filtered if p.get("platform") == plat_filter.lower()]
    if search:
        filtered = [p for p in filtered if search.lower() in (p.get("title") or "").lower()]

    st.markdown(f"**{len(filtered)} posts encontrados**")
    st.markdown("---")

    if not filtered:
        st.info("No hay posts que coincidan con los filtros.")
        return

    for post in filtered:
        client_name = client_names.get(post.get("client_id"), "?")
        status = post.get("status", "Idea")
        platform = post.get("platform", "instagram")
        plat_icon = "📸" if platform == "instagram" else "💼"
        notes = post.get("notes")
        if isinstance(notes, str):
            try: notes = json.loads(notes)
            except: notes = []
        n_comments = len(notes or [])

        with st.expander(f"{plat_icon} **{post.get('title','Sin título')}** — {post.get('date','')} · {client_name}"):
            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                st.markdown(f"**Estado:** {status}")
                st.markdown(f"**Tipo:** {post.get('ctype','')}")
                if post.get("caption"):
                    st.markdown(f"**Caption:** {post.get('caption','')[:200]}")
                if post.get("hashtags"):
                    st.markdown(f"**Hashtags:** `{post.get('hashtags','')[:100]}`")
            with c2:
                st.markdown(f"**Plataforma:** {plat_icon} {platform.capitalize()}")
                st.markdown(f"**Comentarios:** 💬 {n_comments}")
            with c3:
                if st.button("🗑️ Eliminar", key=f"del_post_{post['id']}"):
                    delete_post_db(post["id"])
                    st.success("Post eliminado.")
                    st.rerun()

            if n_comments > 0:
                st.markdown("**Comentarios:**")
                for note in (notes or []):
                    st.markdown(f"""
                    <div class='activity-item'>
                        <strong>{note.get('author','?')}</strong>
                        <span style='color:#aaa;font-size:0.8rem;margin-left:8px'>{note.get('date','')}</span><br/>
                        {note.get('text','')}
                    </div>
                    """, unsafe_allow_html=True)


def page_scripts(clients, all_scripts):
    st.markdown("# 📝 Guiones de Contenido")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        client_names = {c["id"]: c["name"] for c in clients}
        client_filter = st.selectbox("Cliente", ["Todos"] + list(client_names.values()))
    with col2:
        aprov_filter = st.selectbox("Aprobación", ["Todos", "Pendiente", "Aprobado", "Con cambios"])
    with col3:
        search = st.text_input("🔍 Buscar guión", placeholder="Título...")

    filtered = all_scripts
    if client_filter != "Todos":
        cid = next((c["id"] for c in clients if c["name"] == client_filter), None)
        if cid:
            filtered = [s for s in filtered if s["client_id"] == cid]
    aprov_map = {"Pendiente": "pendiente", "Aprobado": "aprobado", "Con cambios": "cambios"}
    if aprov_filter != "Todos":
        filtered = [s for s in filtered if s.get("approval_status") == aprov_map[aprov_filter]]
    if search:
        filtered = [s for s in filtered if search.lower() in (s.get("title") or "").lower()]

    st.markdown(f"**{len(filtered)} guiones encontrados**")
    st.markdown("---")

    if not filtered:
        st.info("No hay guiones que coincidan.")
        return

    for script in filtered:
        client_name = client_names.get(script.get("client_id"), "?")
        aprov = script.get("approval_status", "pendiente")
        aprov_label = APPROVAL_LABELS.get(aprov, aprov)
        notes = script.get("notes")
        if isinstance(notes, str):
            try: notes = json.loads(notes)
            except: notes = []
        n_comments = len(notes or [])
        scenes = script.get("scenes") or []

        with st.expander(f"**{script.get('title','Sin título')}** — {aprov_label} · {client_name}"):
            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                st.markdown(f"**Tipo:** {script.get('ctype','')}")
                st.markdown(f"**Objetivo:** {script.get('objective','')}")
                if script.get("date"):
                    st.markdown(f"**Fecha estimada:** {script.get('date')}")
                if script.get("needs"):
                    st.markdown(f"**Necesidades:** {script.get('needs','')[:150]}")
            with c2:
                st.markdown(f"**Escenas:** {len(scenes)}")
                st.markdown(f"**Comentarios:** 💬 {n_comments}")
            with c3:
                # Cambiar estado de aprobación
                new_aprov = st.selectbox(
                    "Cambiar estado",
                    ["pendiente", "aprobado", "cambios"],
                    index=["pendiente","aprobado","cambios"].index(aprov),
                    key=f"aprov_{script['id']}"
                )
                if new_aprov != aprov:
                    if st.button("Guardar estado", key=f"save_aprov_{script['id']}"):
                        sb = get_supabase()
                        sb.table("scripts").update({"approval_status": new_aprov}).eq("id", script["id"]).execute()
                        st.success("Estado actualizado.")
                        st.rerun()
                if st.button("🗑️ Eliminar", key=f"del_script_{script['id']}"):
                    delete_script_db(script["id"])
                    st.success("Guión eliminado.")
                    st.rerun()

            if len(scenes) > 0:
                st.markdown("**Tabla Audio/Video:**")
                df_scenes = pd.DataFrame(scenes)
                df_scenes.index = [f"Escena {i+1}" for i in range(len(df_scenes))]
                st.dataframe(df_scenes, use_container_width=True)

            if n_comments > 0:
                st.markdown("**Comentarios:**")
                for note in (notes or []):
                    st.markdown(f"""
                    <div class='activity-item'>
                        <strong>{note.get('author','?')}</strong>
                        <span style='color:#aaa;font-size:0.8rem;margin-left:8px'>{note.get('date','')}</span><br/>
                        {note.get('text','')}
                    </div>
                    """, unsafe_allow_html=True)


def page_activity(all_posts, all_scripts):
    st.markdown("# 💬 Actividad Reciente")
    st.markdown("*Todos los comentarios dejados por usuarios en posts y guiones*")
    st.markdown("---")

    activity = get_all_activity(all_posts, all_scripts)

    if not activity:
        st.info("No hay comentarios todavía.")
        return

    # Resumen por autor
    authors = pd.Series([a["autor"] for a in activity]).value_counts().reset_index()
    authors.columns = ["Usuario", "Comentarios"]
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 👤 Actividad por usuario")
        st.dataframe(authors, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("### 📊 Distribución")
        fig = px.pie(authors, names="Usuario", values="Comentarios")
        fig.update_layout(margin=dict(t=10,b=0,l=0,r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(f"### 📋 Todos los comentarios ({len(activity)})")

    filter_author = st.selectbox("Filtrar por usuario", ["Todos"] + list(authors["Usuario"].tolist()))
    shown = activity if filter_author == "Todos" else [a for a in activity if a["autor"] == filter_author]

    for item in shown:
        st.markdown(f"""
        <div class='activity-item'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px'>
                <div>
                    <strong>{item['autor']}</strong>
                    <span style='background:#f0f0f0;border-radius:10px;padding:2px 8px;font-size:0.75rem;margin-left:8px'>{item['tipo']}</span>
                    <span style='color:#666;font-size:0.85rem;margin-left:6px'>{item['titulo']}</span>
                </div>
                <span style='color:#aaa;font-size:0.78rem'>{item['fecha']}</span>
            </div>
            <div style='color:#333;font-size:0.9rem'>{item['texto']}</div>
        </div>
        """, unsafe_allow_html=True)


def page_clients(clients):
    st.markdown("# 👥 Gestión de Clientes")
    st.markdown("---")

    st.info("⚠️ Desde acá podés editar contraseñas y datos. Los clientes **solo pueden comentar** — no tienen acceso al panel admin.")

    for client in clients:
        with st.expander(f"**{client['name']}** — @{client['username']} {'🔑 Admin' if client['id']=='admin' else ''}"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Nombre", value=client.get("name",""), key=f"name_{client['id']}")
                new_user = st.text_input("Usuario", value=client.get("username",""), key=f"user_{client['id']}")
                new_pass = st.text_input("Contraseña editor", value=client.get("password",""), key=f"pass_{client['id']}", type="password")
                new_guest = st.text_input("Contraseña invitado", value=client.get("guest_password",""), key=f"guest_{client['id']}", type="password")
            with col2:
                new_ig = st.text_input("Instagram @", value=client.get("instagram",""), key=f"ig_{client['id']}")
                new_li = st.text_input("LinkedIn @", value=client.get("linkedin",""), key=f"li_{client['id']}")
                st.markdown(f"**Color:** <span style='background:{client.get('color','#6c5ce7')};padding:4px 12px;border-radius:6px;color:white'>{client.get('color','#6c5ce7')}</span>", unsafe_allow_html=True)

            if st.button("💾 Guardar cambios", key=f"save_{client['id']}"):
                update_client(client["id"], {
                    "name": new_name,
                    "username": new_user,
                    "password": new_pass,
                    "guest_password": new_guest,
                    "instagram": new_ig,
                    "linkedin": new_li
                })
                st.success(f"✅ {new_name} actualizado correctamente.")
                st.rerun()

# ── MAIN APP ──────────────────────────────────────────────────────────────────
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_screen()
        return

    # Cargar datos
    clients = get_clients()
    all_posts = get_posts()
    all_scripts = get_scripts()

    # Sidebar
    with st.sidebar:
        st.markdown("## 📅 Planning Indie")
        st.markdown("**Panel de Administración**")
        st.markdown("---")
        page = st.radio("Navegación", [
            "📊 Dashboard",
            "📅 Posts",
            "📝 Guiones",
            "💬 Actividad",
            "👥 Clientes",
        ])
        st.markdown("---")
        st.markdown(f"**Posts:** {len(all_posts)}")
        st.markdown(f"**Guiones:** {len(all_scripts)}")
        st.markdown(f"**Clientes:** {len(clients)}")
        st.markdown("---")
        if st.button("↩️ Cerrar sesión"):
            st.session_state.logged_in = False
            st.rerun()

    # Routing
    if page == "📊 Dashboard":
        page_dashboard(clients, all_posts, all_scripts)
    elif page == "📅 Posts":
        page_posts(clients, all_posts)
    elif page == "📝 Guiones":
        page_scripts(clients, all_scripts)
    elif page == "💬 Actividad":
        page_activity(all_posts, all_scripts)
    elif page == "👥 Clientes":
        page_clients(clients)

if __name__ == "__main__":
    main()
