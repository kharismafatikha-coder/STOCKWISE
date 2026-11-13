import os
import math
import sqlite3
import html as _html
from datetime import date, datetime, timedelta, timezone

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="STOCKWISE | Dashboard", page_icon="📦", layout="wide")

# ---------- PALET ----------
GREEN = "#2F6B5B"
GREEN_DARK = "#1F3D36"
GOLD = "#D6A85F"
RED = "#D64545"
AMBER = "#E8A33D"
INK = "#1F2A27"
MUTED = "#6B7A76"
PALETTE = ["#2F6B5B", "#D6A85F", "#7FB5A5", "#E58F65", "#8E9AAF", "#B8D8C9"]

# ---------- WAKTU (WIB) ----------
NOW = datetime.now(timezone(timedelta(hours=7)))
DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
          "Agustus", "September", "Oktober", "November", "Desember"]
DATE_LABEL = f"{DAYS[NOW.weekday()]}, {NOW.day} {MONTHS[NOW.month - 1]} {NOW.year}"
GREETING = ("Selamat pagi" if NOW.hour < 11 else "Selamat siang" if NOW.hour < 15
            else "Selamat sore" if NOW.hour < 18 else "Selamat malam")

# ---------- STYLE ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp {{font-family: 'Poppins', sans-serif;}}
.stApp {{background: #F4F6F5; color: {INK};}}
.block-container {{padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1300px;}}
header[data-testid="stHeader"] {{background: transparent;}}

/* Sidebar */
[data-testid="stSidebar"] {{background: linear-gradient(180deg, {GREEN_DARK} 0%, #2E5A4F 100%);}}
[data-testid="stSidebar"] * {{color: #EAF3EF;}}
[data-testid="stSidebar"] hr {{border-color: rgba(255,255,255,.15);}}
[data-testid="stSidebar"] input {{background: rgba(255,255,255,.95); color: {INK} !important; border-radius: 10px;}}
[data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: 8px 12px; border-radius: 10px; margin-bottom: 2px; transition: .2s;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{background: rgba(255,255,255,.10);}}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.25); color: #EAF3EF;
}}
.brand {{font-size: 1.5rem; font-weight: 700; letter-spacing: .5px;}}
.brand-sub {{font-size: .8rem; opacity: .75; margin-top: -6px;}}

/* Hero */
.hero {{
    background: linear-gradient(120deg, {GREEN_DARK} 0%, {GREEN} 60%, #4C9A85 100%);
    border-radius: 20px; padding: 26px 32px; color: white; margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(47,107,91,.25); position: relative; overflow: hidden;
}}
.hero:after {{
    content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px;
    background: rgba(255,255,255,.08); border-radius: 50%;
}}
.hero .eyebrow {{font-size: .72rem; letter-spacing: 1.6px; font-weight: 600; opacity: .7; margin-bottom: 4px;}}
.hero h1 {{margin: 0; font-size: 1.9rem; font-weight: 700; color: white;}}
.hero p {{margin: 4px 0 0 0; opacity: .85; font-size: .95rem;}}
.hero .hero-sum {{margin-top: 12px; opacity: .95; font-size: .9rem; max-width: 760px;}}
.hero .chip {{
    display: inline-block; background: rgba(255,255,255,.18); padding: 3px 12px;
    border-radius: 999px; font-size: .75rem; margin: 0 6px 10px 0;
}}
.hero .chip.warn {{background: rgba(232,163,61,.35);}}
.hero .chip.bad {{background: rgba(214,69,69,.45);}}
.hero .chip.ok {{background: rgba(184,216,201,.30);}}

/* KPI */
.kpi {{
    background: white; border-radius: 16px; padding: 18px 20px;
    box-shadow: 0 4px 18px rgba(31,42,39,.06); border: 1px solid #EDF0EE;
    border-left: 6px solid var(--accent); height: 100%;
}}
.kpi .top {{display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;}}
.kpi .icon {{
    width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center;
    justify-content: center; font-size: 1.25rem; background: var(--soft); flex-shrink: 0;
}}
.kpi .label {{color: {MUTED}; font-size: .82rem; font-weight: 500; padding-top: 2px;}}
.kpi .value {{
    color: {INK}; font-size: clamp(1.25rem, 1.9vw, 1.7rem); font-weight: 700; line-height: 1.3;
    white-space: nowrap; margin-top: 2px;
}}
.kpi .note {{color: {MUTED}; font-size: .75rem; margin-top: 2px;}}

/* Kartu & judul seksi */
.section-title {{font-size: 1.1rem; font-weight: 600; color: {INK}; margin: 8px 0 10px 0;}}
.section-sub {{color: {MUTED}; font-size: .85rem; margin: -6px 0 12px 0;}}
.card {{
    background: white; border-radius: 16px; padding: 16px 18px;
    box-shadow: 0 4px 18px rgba(31,42,39,.06); border: 1px solid #EDF0EE;
}}
.alert {{
    border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; font-size: .9rem;
    background: var(--soft); border-left: 5px solid var(--accent); color: {INK};
}}
.badge {{
    display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .75rem;
    font-weight: 600; margin: 2px 4px 2px 0; background: var(--soft); color: var(--accent);
}}
[data-testid="stMetric"] {{
    background: white; border: 1px solid #EDF0EE; padding: 16px; border-radius: 14px;
    box-shadow: 0 4px 18px rgba(31,42,39,.05);
}}
[data-testid="stMetric"] * {{color: {INK} !important;}}
.stTabs [data-baseweb="tab"] {{font-weight: 600;}}
.stButton > button {{border-radius: 10px; font-weight: 600;}}
.small-muted {{color: {MUTED}; font-size: .88rem;}}

/* Panel notifikasi */
.notif {{
    background: white; border-radius: 16px; padding: 14px 16px; height: 100%;
    border: 1px solid #EDF0EE; border-top: 5px solid var(--accent);
    box-shadow: 0 4px 18px rgba(31,42,39,.06);
}}
.notif .n-head {{
    display: flex; justify-content: space-between; align-items: center;
    font-weight: 600; font-size: .95rem; margin-bottom: 8px;
}}
.notif .n-count {{
    background: var(--soft); color: var(--accent); border-radius: 999px;
    padding: 1px 10px; font-size: .8rem; font-weight: 700;
}}
.notif .n-item {{
    display: flex; justify-content: space-between; gap: 10px; padding: 7px 0;
    border-bottom: 1px dashed #E6EBE9; font-size: .88rem;
}}
.notif .n-item:last-of-type {{border-bottom: none;}}
.notif .n-meta {{color: var(--accent); font-weight: 600; white-space: nowrap;}}
.notif .n-empty {{color: {GREEN}; font-size: .88rem; padding: 8px 0;}}
.notif .n-foot {{
    margin-top: 8px; padding: 8px 10px; border-radius: 10px; background: var(--soft);
    font-size: .8rem; color: {INK};
}}

/* Aktivitas terbaru */
.act {{display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid #EFF2F1;}}
.act:last-child {{border-bottom: none;}}
.act-icon {{
    width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 1.05rem; flex-shrink: 0;
}}
.act-body {{flex: 1; font-size: .88rem; line-height: 1.4;}}
.act-qty {{font-weight: 600; color: {GREEN};}}
.act-sub {{color: {MUTED}; font-size: .78rem;}}
.act-time {{color: {MUTED}; font-size: .75rem; white-space: nowrap;}}
</style>
""", unsafe_allow_html=True)


# ---------- DATABASE (SQLite) ----------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockwise.db")
DATE_COLS = {"inventory": ("Tanggal masuk", "Kedaluwarsa")}


def db_save(name, df):
    out = df.copy()
    for c in DATE_COLS.get(name, ()):
        out[c] = pd.to_datetime(out[c]).dt.strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as con:
        out.to_sql(name, con, if_exists="replace", index=False)


def db_load(name):
    try:
        with sqlite3.connect(DB_PATH) as con:
            df = pd.read_sql(f"SELECT * FROM {name}", con)
    except Exception:
        return None
    for c in DATE_COLS.get(name, ()):
        df[c] = pd.to_datetime(df[c]).dt.date
    return df


def commit(key):
    db_save(key, st.session_state[key])


# ---------- DATA SIMULASI ----------
def default_inventory():
    t = date.today()
    return pd.DataFrame([
        {"Bahan": "Tepung terigu", "Kategori": "Bahan utama", "Stok": 18.0, "Satuan": "kg", "Stok minimum": 10.0, "Harga/satuan": 14000, "Tanggal masuk": t - timedelta(days=8), "Kedaluwarsa": t + timedelta(days=18), "Batch": "TR-001"},
        {"Bahan": "Gula pasir", "Kategori": "Bahan utama", "Stok": 7.0, "Satuan": "kg", "Stok minimum": 8.0, "Harga/satuan": 17000, "Tanggal masuk": t - timedelta(days=12), "Kedaluwarsa": t + timedelta(days=35), "Batch": "GP-002"},
        {"Bahan": "Telur", "Kategori": "Bahan utama", "Stok": 5.0, "Satuan": "kg", "Stok minimum": 4.0, "Harga/satuan": 29000, "Tanggal masuk": t - timedelta(days=2), "Kedaluwarsa": t + timedelta(days=6), "Batch": "TL-003"},
        {"Bahan": "Margarin", "Kategori": "Bahan tambahan", "Stok": 6.0, "Satuan": "kg", "Stok minimum": 3.0, "Harga/satuan": 32000, "Tanggal masuk": t - timedelta(days=5), "Kedaluwarsa": t + timedelta(days=12), "Batch": "MG-004"},
        {"Bahan": "Cokelat bubuk", "Kategori": "Bahan tambahan", "Stok": 3.0, "Satuan": "kg", "Stok minimum": 2.0, "Harga/satuan": 65000, "Tanggal masuk": t - timedelta(days=4), "Kedaluwarsa": t + timedelta(days=80), "Batch": "CB-005"},
        {"Bahan": "Susu cair", "Kategori": "Bahan tambahan", "Stok": 2.0, "Satuan": "liter", "Stok minimum": 4.0, "Harga/satuan": 18000, "Tanggal masuk": t - timedelta(days=1), "Kedaluwarsa": t + timedelta(days=4), "Batch": "SC-006"},
    ])


def default_sales():
    return pd.DataFrame({
        "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4", "Minggu 5", "Minggu 6"],
        "Brownies": [42, 48, 45, 55, 58, 62],
        "Bolu": [30, 34, 32, 38, 40, 43],
        "Nastar": [25, 28, 30, 27, 33, 36],
    })


def default_recipes():
    return pd.DataFrame([
        {"Produk": "Brownies", "Bahan": "Tepung terigu", "Kebutuhan/unit (kg)": 0.20},
        {"Produk": "Brownies", "Bahan": "Gula pasir", "Kebutuhan/unit (kg)": 0.15},
        {"Produk": "Brownies", "Bahan": "Telur", "Kebutuhan/unit (kg)": 0.10},
        {"Produk": "Brownies", "Bahan": "Cokelat bubuk", "Kebutuhan/unit (kg)": 0.08},
        {"Produk": "Bolu", "Bahan": "Tepung terigu", "Kebutuhan/unit (kg)": 0.18},
        {"Produk": "Bolu", "Bahan": "Gula pasir", "Kebutuhan/unit (kg)": 0.12},
        {"Produk": "Bolu", "Bahan": "Telur", "Kebutuhan/unit (kg)": 0.12},
    ])


def default_activity():
    def row(delta, jenis, bahan, jumlah, ket):
        return {"Waktu": (NOW - delta).strftime("%Y-%m-%d %H:%M"), "Jenis": jenis,
                "Bahan": bahan, "Jumlah": jumlah, "Keterangan": ket}
    return pd.DataFrame([
        row(timedelta(hours=1), "Bahan masuk", "Susu cair", "+2 liter", "Batch SC-006 diterima dari supplier"),
        row(timedelta(hours=3), "Produksi", "Brownies", "40 unit", "Bahan baku dikurangi dengan FEFO"),
        row(timedelta(hours=7), "Pembelian", "Gula pasir", "10 kg", "Pesanan dibuat ke supplier"),
        row(timedelta(days=1, hours=2), "Bahan keluar", "Tepung terigu", "-8 kg", "Penggunaan produksi · FEFO"),
        row(timedelta(days=2), "Perubahan stok", "Telur", "-0,5 kg", "Penyesuaian setelah stok opname"),
        row(timedelta(days=3), "Bahan masuk", "Telur", "+6 kg", "Batch TL-003 diterima dari supplier"),
    ])


def init_state(key, default_fn):
    if key not in st.session_state:
        df = db_load(key)
        if df is None:
            df = default_fn()
            db_save(key, df)
        st.session_state[key] = df


init_state("inventory", default_inventory)
init_state("sales", default_sales)
init_state("recipes", default_recipes)
init_state("activity", default_activity)


# ---------- HELPER ----------
def money(x):
    return "Rp{:,.0f}".format(x).replace(",", ".")


def num(x):
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",")


def days_left(d):
    if pd.isna(d):
        return 9999
    return (pd.to_datetime(d).date() - date.today()).days


def kpi(col, icon, label, value, note, accent, soft):
    col.markdown(f"""
<div class="kpi" style="--accent:{accent}; --soft:{soft};">
<div class="top"><div class="label">{label}</div><div class="icon">{icon}</div></div>
<div class="value">{value}</div>
<div class="note">{note}</div>
</div>""", unsafe_allow_html=True)


def alert(text, accent, soft):
    st.markdown(f'<div class="alert" style="--accent:{accent}; --soft:{soft};">{text}</div>',
                unsafe_allow_html=True)


def badges(items, accent, soft):
    return "".join(f'<span class="badge" style="--accent:{accent}; --soft:{soft};">{i}</span>' for i in items)


def title(text, sub=None):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def style_fig(fig, height=360):
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins, sans-serif", color=INK, size=12),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, title_text=""),
    )
    fig.update_xaxes(tickangle=0, automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def status_stok(r):
    return "Perlu beli" if r["Stok"] <= r["Stok minimum"] else "Aman"


def log_activity(jenis, bahan, jumlah, ket):
    row = pd.DataFrame([{"Waktu": NOW.strftime("%Y-%m-%d %H:%M"), "Jenis": jenis,
                         "Bahan": bahan, "Jumlah": jumlah, "Keterangan": ket}])
    st.session_state.activity = pd.concat([row, st.session_state.activity],
                                          ignore_index=True).head(200)
    commit("activity")


def rel_time(s):
    try:
        t = datetime.strptime(s, "%Y-%m-%d %H:%M")
    except Exception:
        return s
    mins = int((NOW.replace(tzinfo=None) - t).total_seconds() // 60)
    if mins < 1:
        return "baru saja"
    if mins < 60:
        return f"{mins} menit lalu"
    if mins < 60 * 24:
        return f"{mins // 60} jam lalu"
    if mins < 60 * 48:
        return "kemarin"
    return f"{mins // (60 * 24)} hari lalu"


def clean_inventory(df):
    df = df.copy()
    df = df[df["Bahan"].notna() & (df["Bahan"].astype(str).str.strip() != "")].reset_index(drop=True)
    tm = pd.to_datetime(df["Tanggal masuk"]).fillna(pd.Timestamp(date.today()))
    kd = pd.to_datetime(df["Kedaluwarsa"])
    missing = int(kd.isna().sum())
    kd = kd.fillna(pd.Timestamp(date.today() + timedelta(days=30)))
    df["Tanggal masuk"], df["Kedaluwarsa"] = tm.dt.date, kd.dt.date
    for c in ["Stok", "Stok minimum", "Harga/satuan"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["Satuan"] = df["Satuan"].fillna("kg")
    df["Kategori"] = df["Kategori"].fillna("Bahan utama")
    for i, r in df.iterrows():
        if pd.isna(r["Batch"]) or str(r["Batch"]).strip() == "":
            df.at[i, "Batch"] = f"{str(r['Bahan'])[:2].upper()}-{i + 1:03d}"
    return df, missing


def diff_inventory(old, new):
    o = old.drop_duplicates("Batch").set_index("Batch")
    n = new.drop_duplicates("Batch").set_index("Batch")
    logs = []
    for b in n.index:
        r = n.loc[b]
        if b not in o.index:
            logs.append(("Bahan masuk", r["Bahan"], f"+{num(r['Stok'])} {r['Satuan']}", f"Batch {b} ditambahkan"))
        else:
            d = r["Stok"] - o.loc[b, "Stok"]
            if abs(d) > 1e-9:
                logs.append(("Perubahan stok", r["Bahan"], f"{'+' if d > 0 else '-'}{num(abs(d))} {r['Satuan']}",
                             f"Batch {b}: {num(o.loc[b, 'Stok'])} → {num(r['Stok'])}"))
    for b in o.index:
        if b not in n.index:
            logs.append(("Perubahan stok", o.loc[b, "Bahan"], "-", f"Batch {b} dihapus"))
    return logs


def fefo_consume(bahan, qty):
    """Kurangi batch belum kedaluwarsa dengan tanggal terdekat terlebih dahulu."""
    df = st.session_state.inventory
    expiry = pd.to_datetime(df["Kedaluwarsa"]).dt.date
    idx = df[(df["Bahan"] == bahan) & (df["Stok"] > 0) & (expiry >= date.today())].sort_values("Kedaluwarsa").index
    remaining = float(qty)
    for i in idx:
        take = min(float(df.at[i, "Stok"]), remaining)
        df.at[i, "Stok"] = float(df.at[i, "Stok"]) - take
        remaining -= take
        if remaining <= 1e-9:
            break
    used = float(qty) - remaining
    if remaining > 1e-9:
        raise ValueError(f"Stok layak pakai {bahan} tidak mencukupi. Kekurangan {num(remaining)}.")
    commit("inventory")
    return used


def usable_stock(inv_df):
    """Jumlah stok yang masih layak digunakan; batch kedaluwarsa tidak dihitung."""
    expiry = pd.to_datetime(inv_df["Kedaluwarsa"]).dt.date
    valid = inv_df[expiry >= date.today()]
    if valid.empty:
        return pd.Series(dtype=float)
    return valid.groupby("Bahan")["Stok"].sum()


def production_summary(sales, recipes, inv_df):
    """Rekomendasi produksi dari prediksi penjualan (MA-3) + kebutuhan bahan baku."""
    stock = usable_stock(inv_df)
    unit = inv_df.drop_duplicates("Bahan").set_index("Bahan")["Satuan"]
    rows, need = [], {}
    for p in [c for c in sales.columns if c != "Minggu"]:
        v = pd.to_numeric(sales[p], errors="coerce").dropna()
        if v.empty:
            continue
        fc = float(v.tail(min(3, len(v))).mean())
        plan = int(math.ceil(fc))
        rec = recipes[recipes["Produk"] == p].dropna(subset=["Bahan"])
        if rec.empty:
            rows.append({"Produk": p, "Prediksi": fc, "Rencana (unit)": plan, "Maks. dari stok": None,
                         "Rekomendasi": "Resep belum ada — lengkapi di Produksi & BOM"})
            continue
        caps = []
        for _, r in rec.iterrows():
            per = float(r["Kebutuhan/unit (kg)"])
            if per > 0:
                caps.append(math.floor(float(stock.get(r["Bahan"], 0)) / per + 1e-9))
                need[r["Bahan"]] = need.get(r["Bahan"], 0) + per * plan
        maxp = min(caps) if caps else 0
        rekom = (f"Produksi {plan} unit" if maxp >= plan
                 else f"Bahan hanya cukup untuk {maxp} unit — beli bahan dulu")
        rows.append({"Produk": p, "Prediksi": fc, "Rencana (unit)": plan,
                     "Maks. dari stok": maxp, "Rekomendasi": rekom})
    mat = pd.DataFrame([
        {"Bahan": b, "Kebutuhan": q, "Stok": float(stock.get(b, 0)), "Satuan": unit.get(b, "kg"),
         "Selisih": float(stock.get(b, 0)) - q,
         "Status": "✅ Cukup" if float(stock.get(b, 0)) >= q else "⚠️ Kurang"}
        for b, q in need.items()])
    return pd.DataFrame(rows), mat


# ---------- OLAH DATA ----------
inv = st.session_state.inventory.copy()
inv["Nilai stok"] = inv["Stok"] * inv["Harga/satuan"]
inv["Sisa hari"] = inv["Kedaluwarsa"].apply(days_left)

low = inv[inv["Stok"] <= inv["Stok minimum"]]
expiring = inv[(inv["Sisa hari"] >= 0) & (inv["Sisa hari"] <= 7)].sort_values("Sisa hari")
expired = inv[inv["Sisa hari"] < 0].sort_values("Sisa hari")
attention = set(low["Bahan"]) | set(expiring["Bahan"]) | set(expired["Bahan"])

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown('<div class="brand">📦 STOCKWISE</div><div class="brand-sub">Less Waste, More Taste.</div>',
                unsafe_allow_html=True)
    st.write("")
    page = st.radio("MENU UTAMA", [
        "Dashboard", "Manajemen Stok", "FEFO & Kedaluwarsa",
        "Produksi & BOM", "Prediksi Permintaan"
    ])
    st.divider()
    st.caption("PROFIL USAHA")
    business_name = st.text_input("Nama usaha", "Dapur Pastry Kita")
    st.caption("Mode: Prototipe · Data tersimpan di stockwise.db")
    if st.button("↺ Reset ke data simulasi", use_container_width=True):
        try:
            os.remove(DB_PATH)
        except FileNotFoundError:
            pass
        for k in ["inventory", "sales", "recipes", "activity"]:
            st.session_state.pop(k, None)
        st.rerun()

# ---------- HERO ----------
if page == "Dashboard":
    chips = ""
    if len(low):
        chips += f'<span class="chip warn">🛒 {len(low)} perlu restock</span>'
    if len(expiring):
        chips += f'<span class="chip warn">⏳ {len(expiring)} segera kedaluwarsa</span>'
    if len(expired):
        chips += f'<span class="chip bad">🔴 {len(expired)} sudah kedaluwarsa</span>'
    if not chips:
        chips = '<span class="chip ok">✅ Semua aman</span>'
    if attention:
        summary = (f"Hari ini ada <b>{len(attention)} dari {inv['Bahan'].nunique()} jenis bahan</b> yang perlu perhatian. "
                   f"Nilai persediaan saat ini {money(inv['Nilai stok'].sum())}.")
    else:
        summary = f"Semua bahan dalam kondisi aman. Nilai persediaan saat ini {money(inv['Nilai stok'].sum())}."
    st.markdown(f"""
<div class="hero">
<div class="eyebrow">STOCKWISE WORKSPACE</div>
<span class="chip">📅 {DATE_LABEL}</span>{chips}
<h1>{GREETING}, {_html.escape(business_name)}!</h1>
<p>Kelola stok dan produksi lebih cerdas setiap hari.</p>
<p class="hero-sum">{summary}</p>
</div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class="hero">
<span class="chip">📅 {DATE_LABEL}</span>
<h1>{page}</h1>
<p>{_html.escape(business_name)} · Sistem perencanaan produksi dan persediaan bahan baku</p>
</div>""", unsafe_allow_html=True)

# ---------- DASHBOARD ----------
if page == "Dashboard":
    # 1) Kartu informasi
    total_stok = inv["Stok"].sum()
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "🧺", "Jenis bahan", f"{inv['Bahan'].nunique()}",
        f"Total stok {num(total_stok)} kg/liter · {len(attention)} perlu perhatian", GREEN, "#E3F0EC")
    kpi(c2, "💰", "Nilai persediaan", money(inv["Nilai stok"].sum()),
        "Stok × harga satuan", GOLD, "#FBF1DE")
    kpi(c3, "🛒", "Perlu restock", f"{len(low)} bahan",
        "Di bawah stok minimum" if len(low) else "Semua di atas minimum", RED, "#FBE5E5")
    kpi(c4, "⏳", "Segera kedaluwarsa", f"{len(expiring)} bahan",
        "Dalam 7 hari ke depan" + (f" · {len(expired)} sudah lewat" if len(expired) else ""), AMBER, "#FCEFD9")
    st.write("")

    # 2) Pusat perhatian (stok menipis / mendekati / sudah kedaluwarsa)
    title("Pusat perhatian", "Notifikasi persediaan berdasarkan stok minimum dan tanggal kedaluwarsa (FEFO).")

    def notif_card(col, icon, heading, rows, accent, soft, empty_msg, foot=""):
        body = "".join(rows) if rows else f'<div class="n-empty">✅ {empty_msg}</div>'
        foot_html = f'<div class="n-foot">{foot}</div>' if foot and rows else ""
        col.markdown(
            f'<div class="notif" style="--accent:{accent}; --soft:{soft};">'
            f'<div class="n-head"><span>{icon} {heading}</span><span class="n-count">{len(rows)}</span></div>'
            f'{body}{foot_html}</div>', unsafe_allow_html=True)

    def item(name, meta):
        return f'<div class="n-item"><span><b>{_html.escape(str(name))}</b></span><span class="n-meta">{meta}</span></div>'

    n1, n2, n3 = st.columns(3)
    low_rows = [item(r["Bahan"], f"{num(r['Stok'])} / {num(r['Stok minimum'])} {r['Satuan']}")
                for _, r in low.sort_values("Stok").iterrows()]
    notif_card(n1, "🛒", "Stok menipis", low_rows, RED, "#FBE5E5", "Semua stok di atas minimum",
               "Kurang dari stok minimum — pertimbangkan pembelian ulang.")
    exp_rows = [item(f"{r['Bahan']} ({r['Batch']})", f"sisa {r['Sisa hari']} hari") for _, r in expiring.iterrows()]
    first = expiring.iloc[0] if len(expiring) else None
    notif_card(n2, "⏳", "Mendekati kedaluwarsa", exp_rows, AMBER, "#FCEFD9", "Tidak ada bahan mendekati kedaluwarsa",
               f"<b>FEFO:</b> gunakan {first['Bahan']} lebih dulu." if first is not None else "")
    ex_rows = [item(f"{r['Bahan']} ({r['Batch']})", f"lewat {abs(r['Sisa hari'])} hari") for _, r in expired.iterrows()]
    notif_card(n3, "🔴", "Sudah kedaluwarsa", ex_rows, RED, "#FBE5E5", "Tidak ada bahan kedaluwarsa",
               "Pisahkan dan jangan dipakai produksi.")
    st.write("")

    # 3) Ringkasan produksi
    plan_df, mat_df = production_summary(st.session_state.sales, st.session_state.recipes, inv)
    title("Ringkasan produksi", "Rencana produksi dari prediksi penjualan (Moving Average 3 periode) dan kebutuhan bahan bakunya.")
    if plan_df.empty:
        st.info("Isi data penjualan di menu Prediksi Permintaan untuk melihat rekomendasi produksi.")
    else:
        short = int((mat_df["Status"] == "⚠️ Kurang").sum()) if not mat_df.empty else 0
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Produk direncanakan", len(plan_df))
        m2.metric("Total rencana produksi", f"{int(plan_df['Rencana (unit)'].sum())} unit")
        m3.metric("Jenis bahan dibutuhkan", len(mat_df))
        m4.metric("Bahan kurang", f"{short} bahan")

        pl, pr = st.columns([1.25, 1])
        with pl:
            st.dataframe(plan_df, use_container_width=True, hide_index=True, column_config={
                "Prediksi": st.column_config.NumberColumn("Prediksi", format="%.1f"),
                "Maks. dari stok": st.column_config.NumberColumn("Maks. dari stok", format="%d unit"),
                "Rekomendasi": st.column_config.TextColumn("Rekomendasi", width="large"),
            })
        with pr:
            if mat_df.empty:
                st.caption("Belum ada kebutuhan bahan karena resep produk belum diisi.")
            else:
                st.dataframe(mat_df, use_container_width=True, hide_index=True, column_config={
                    "Kebutuhan": st.column_config.NumberColumn(format="%.2f"),
                    "Stok": st.column_config.NumberColumn(format="%.2f"),
                    "Selisih": st.column_config.NumberColumn(format="%.2f"),
                })
        if not mat_df.empty:
            kurang = mat_df[mat_df["Selisih"] < 0]
            if len(kurang):
                alert("<b>Rekomendasi pembelian untuk rencana produksi:</b><br>" + badges(
                    [f"{r['Bahan']} +{num(abs(r['Selisih']))} {r['Satuan']}" for _, r in kurang.iterrows()],
                    RED, "#FBE5E5"), RED, "#FDF3F3")
            else:
                alert("✅ Stok bahan cukup untuk seluruh rencana produksi.", GREEN, "#EEF7F4")
    st.write("")

    # 4) Grafik
    title("Analisis persediaan dan penjualan", "Nilai stok, perbandingan stok aktual dengan batas minimum, dan tren permintaan produk.")
    left, right = st.columns([1.4, 1])
    with left:
        st.caption("Nilai persediaan per bahan")
        vs = inv.sort_values("Nilai stok", ascending=True)
        bar = go.Figure()
        for cat, colr in zip(vs["Kategori"].unique(), [GREEN, GOLD, "#7FB5A5", "#E58F65"]):
            sub = vs[vs["Kategori"] == cat]
            bar.add_trace(go.Bar(x=sub["Nilai stok"], y=sub["Bahan"], orientation="h", name=cat,
                                 marker=dict(color=colr, cornerradius=6),
                                 text=[money(v) for v in sub["Nilai stok"]], textposition="outside",
                                 cliponaxis=False, hovertemplate="%{y}: %{text}<extra></extra>"))
        bar.update_layout(barmode="overlay", yaxis=dict(categoryorder="array", categoryarray=vs["Bahan"].tolist()),
                          xaxis=dict(visible=False, range=[0, max(vs["Nilai stok"].max(), 1) * 1.3]))
        st.plotly_chart(style_fig(bar, 340), use_container_width=True)
    with right:
        st.caption("Komposisi nilai stok")
        pie = px.pie(inv, names="Bahan", values="Nilai stok", hole=.62, color_discrete_sequence=PALETTE)
        pie.update_traces(textinfo="percent", marker=dict(line=dict(color="white", width=2)))
        pie.add_annotation(text=f"<b>{money(inv['Nilai stok'].sum())}</b><br><span style='font-size:11px'>total</span>",
                           showarrow=False, font=dict(size=13), x=0.5, y=0.5, xref="paper", yref="paper")
        style_fig(pie, 340)
        pie.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
        st.plotly_chart(pie, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        st.caption("Stok aktual vs stok minimum")
        sv = inv.groupby("Bahan", sort=False).agg({"Stok": "sum", "Stok minimum": "max"}).reset_index()
        below = sv["Stok"] <= sv["Stok minimum"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=sv["Bahan"], y=sv["Stok"].where(~below), name="Stok aktual (aman)",
                             marker=dict(color=GREEN, cornerradius=6), offsetgroup="aktual"))
        fig.add_trace(go.Bar(x=sv["Bahan"], y=sv["Stok"].where(below), name="Stok aktual (di bawah minimum)",
                             marker=dict(color=RED, cornerradius=6), offsetgroup="aktual"))
        fig.add_trace(go.Bar(x=sv["Bahan"], y=sv["Stok minimum"], name="Stok minimum",
                             marker=dict(color=GOLD, cornerradius=6), offsetgroup="minimum"))
        fig.update_layout(barmode="group", bargap=.25, yaxis_title="Jumlah (kg/liter)")
        fig.update_xaxes(tickfont=dict(size=11))
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with g2:
        st.caption("Tren penjualan mingguan dan prediksi")
        sales_df = st.session_state.sales
        prods = [c for c in sales_df.columns if c != "Minggu"]
        fig = go.Figure()
        labels = sales_df["Minggu"].tolist()
        for i, p in enumerate(prods):
            y = pd.to_numeric(sales_df[p], errors="coerce")
            colr = PALETTE[i % len(PALETTE)]
            fig.add_trace(go.Scatter(x=labels, y=y, name=p, mode="lines+markers",
                                     line=dict(color=colr, width=3), legendgroup=p))
            v = y.dropna()
            if len(v) >= 2:
                fc = v.tail(min(3, len(v))).mean()
                fig.add_trace(go.Scatter(x=[labels[-1], "Prediksi"], y=[v.iloc[-1], fc], mode="lines+markers",
                                         line=dict(color=colr, width=2, dash="dot"),
                                         marker=dict(symbol="star", size=[0, 11]), legendgroup=p,
                                         showlegend=False, hovertemplate="Prediksi: %{y:.1f}<extra>" + p + "</extra>"))
        fig.update_layout(yaxis_title="Unit terjual")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    # 5) Aktivitas terbaru
    title("Aktivitas terbaru", "Riwayat bahan masuk, bahan keluar, perubahan stok, pembelian, dan produksi.")
    act = st.session_state.activity
    jenis_list = ["Semua"] + ["Bahan masuk", "Bahan keluar", "Perubahan stok", "Pembelian", "Produksi"]
    fcol, _ = st.columns([1, 3])
    pilih = fcol.selectbox("Filter aktivitas", jenis_list, label_visibility="collapsed")
    shown_act = act if pilih == "Semua" else act[act["Jenis"] == pilih]
    ACT_STYLE = {"Bahan masuk": ("📥", "#E3F0EC"), "Bahan keluar": ("📤", "#FCEFD9"),
                 "Perubahan stok": ("✏️", "#EEF1F0"), "Pembelian": ("🛒", "#FBF1DE"),
                 "Produksi": ("🏭", "#E3F0EC")}
    if shown_act.empty:
        st.caption("Belum ada aktivitas untuk filter ini.")
    else:
        rows_html = ""
        for _, r in shown_act.head(8).iterrows():
            ic, soft = ACT_STYLE.get(r["Jenis"], ("•", "#EEF1F0"))
            rows_html += (
                f'<div class="act"><div class="act-icon" style="background:{soft};">{ic}</div>'
                f'<div class="act-body"><b>{_html.escape(str(r["Jenis"]))}</b> · {_html.escape(str(r["Bahan"]))} '
                f'<span class="act-qty">{_html.escape(str(r["Jumlah"]))}</span>'
                f'<div class="act-sub">{_html.escape(str(r["Keterangan"]))}</div></div>'
                f'<div class="act-time">{rel_time(r["Waktu"])}</div></div>')
        st.markdown(f'<div class="card">{rows_html}</div>', unsafe_allow_html=True)
        with st.expander("Lihat semua riwayat"):
            st.dataframe(shown_act, use_container_width=True, hide_index=True)
    st.write("")

    # 6) Ringkasan persediaan
    title("Ringkasan persediaan")
    summary_df = inv.copy()
    summary_df["Level stok"] = (summary_df["Stok"] / summary_df["Stok minimum"].replace(0, pd.NA)).astype(float).fillna(0)
    summary_df["Status"] = summary_df.apply(status_stok, axis=1)
    st.dataframe(
        summary_df[["Bahan", "Stok", "Satuan", "Stok minimum", "Level stok", "Kedaluwarsa", "Sisa hari", "Status"]],
        use_container_width=True, hide_index=True,
        column_config={
            "Level stok": st.column_config.ProgressColumn("Level stok", min_value=0, max_value=3, format="%.1f×"),
            "Sisa hari": st.column_config.NumberColumn("Sisa hari", format="%d hari"),
        })

# ---------- MANAJEMEN STOK ----------
elif page == "Manajemen Stok":
    title("Catat transaksi stok", "Setiap transaksi otomatis masuk ke Aktivitas terbaru di Dashboard.")
    names = sorted(st.session_state.inventory["Bahan"].dropna().unique().tolist())
    t1, t2, t3 = st.tabs(["📥 Bahan masuk", "📤 Bahan keluar (FEFO)", "🛒 Pembelian"])

    if not names:
        st.warning("Tambahkan bahan pada tabel di bawah terlebih dahulu.")
    else:
        with t1:
            with st.form("f_in", clear_on_submit=True):
                a, b = st.columns(2)
                bahan = a.selectbox("Bahan", names, key="in_b")
                qty = b.number_input("Jumlah masuk", min_value=0.1, value=1.0, step=0.5, key="in_q")
                c, d = st.columns(2)
                harga = c.number_input("Harga/satuan (0 = pakai harga terakhir)", min_value=0, value=0, step=500, key="in_h")
                exp = d.date_input("Tanggal kedaluwarsa", value=date.today() + timedelta(days=14), key="in_e")
                if st.form_submit_button("Simpan bahan masuk", type="primary"):
                    cur = st.session_state.inventory
                    last = cur[cur["Bahan"] == bahan].iloc[-1]
                    prefix = str(last["Batch"]).split("-")[0] if "-" in str(last["Batch"]) else bahan[:2].upper()
                    n = len(cur) + 1
                    while f"{prefix}-{n:03d}" in set(cur["Batch"].astype(str)):
                        n += 1
                    code = f"{prefix}-{n:03d}"
                    new = pd.DataFrame([{
                        "Bahan": bahan, "Kategori": last["Kategori"], "Stok": float(qty), "Satuan": last["Satuan"],
                        "Stok minimum": last["Stok minimum"], "Harga/satuan": harga or last["Harga/satuan"],
                        "Tanggal masuk": date.today(), "Kedaluwarsa": exp, "Batch": code}])
                    st.session_state.inventory = pd.concat([cur, new], ignore_index=True)
                    commit("inventory")
                    log_activity("Bahan masuk", bahan, f"+{num(qty)} {last['Satuan']}", f"Batch {code} diterima")
                    st.toast(f"{bahan} +{num(qty)} {last['Satuan']} tercatat (batch {code}).")
                    st.rerun()
        with t2:
            with st.form("f_out", clear_on_submit=True):
                a, b, c = st.columns(3)
                bahan = a.selectbox("Bahan", names, key="out_b")
                qty = b.number_input("Jumlah keluar", min_value=0.1, value=1.0, step=0.5, key="out_q")
                alasan = c.selectbox("Alasan", ["Penggunaan produksi", "Rusak/terbuang", "Lainnya"], key="out_a")
                if st.form_submit_button("Simpan bahan keluar", type="primary"):
                    cur = st.session_state.inventory
                    avail = cur.loc[cur["Bahan"] == bahan, "Stok"].sum()
                    unit = cur.loc[cur["Bahan"] == bahan, "Satuan"].iloc[0]
                    if qty > avail:
                        st.error(f"Stok {bahan} hanya {num(avail)} {unit}.")
                    else:
                        fefo_consume(bahan, qty)
                        log_activity("Bahan keluar", bahan, f"-{num(qty)} {unit}", f"{alasan} · diambil dengan FEFO")
                        st.toast(f"{bahan} -{num(qty)} {unit} tercatat.")
                        st.rerun()
        with t3:
            with st.form("f_buy", clear_on_submit=True):
                a, b, c = st.columns(3)
                bahan = a.selectbox("Bahan", names, key="buy_b")
                qty = b.number_input("Jumlah dipesan", min_value=0.1, value=5.0, step=0.5, key="buy_q")
                supplier = c.text_input("Supplier / catatan", key="buy_s")
                if st.form_submit_button("Catat pembelian", type="primary"):
                    cur = st.session_state.inventory
                    unit = cur.loc[cur["Bahan"] == bahan, "Satuan"].iloc[0]
                    log_activity("Pembelian", bahan, f"{num(qty)} {unit}",
                                 "Pesanan dibuat" + (f" ke {supplier}" if supplier else ""))
                    st.toast("Pembelian tercatat. Catat di tab Bahan masuk saat barang tiba.")
                    st.rerun()

    st.write("")
    title("Data bahan baku")
    st.info("Ubah data langsung pada tabel. Tanggal kedaluwarsa dicatat per batch agar FEFO dapat diterapkan.")
    edited = st.data_editor(
        st.session_state.inventory, num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "Stok": st.column_config.NumberColumn(min_value=0, step=0.1),
            "Stok minimum": st.column_config.NumberColumn(min_value=0, step=0.1),
            "Harga/satuan": st.column_config.NumberColumn(format="Rp%d"),
            "Tanggal masuk": st.column_config.DateColumn(),
            "Kedaluwarsa": st.column_config.DateColumn(),
        })
    if st.button("💾 Simpan perubahan stok", type="primary"):
        cleaned, missing = clean_inventory(edited)
        for jenis, bahan, jumlah, ket in diff_inventory(st.session_state.inventory, cleaned):
            log_activity(jenis, bahan, jumlah, ket)
        st.session_state.inventory = cleaned
        commit("inventory")
        if missing:
            st.warning(f"{missing} batch tanpa tanggal kedaluwarsa diisi otomatis 30 hari dari hari ini.")
        st.success("Data persediaan berhasil diperbarui.")
        st.rerun()

    st.write("")
    title("Rekomendasi pembelian sederhana")
    data = st.session_state.inventory.copy()
    data["Kekurangan"] = (data["Stok minimum"] - data["Stok"]).clip(lower=0)
    purchase = data[data["Kekurangan"] > 0][["Bahan", "Stok", "Stok minimum", "Kekurangan", "Satuan"]]
    if purchase.empty:
        st.success("Belum ada bahan yang perlu ditambah berdasarkan stok minimum.")
    else:
        st.dataframe(purchase, use_container_width=True, hide_index=True)

# ---------- FEFO ----------
elif page == "FEFO & Kedaluwarsa":
    st.markdown('<div class="card">FEFO (<i>First Expired, First Out</i>) mengutamakan bahan dengan tanggal kedaluwarsa paling dekat.</div>',
                unsafe_allow_html=True)
    st.write("")
    fefo = st.session_state.inventory.copy()
    fefo["Sisa hari"] = fefo["Kedaluwarsa"].apply(days_left)
    fefo = fefo.sort_values(["Bahan", "Kedaluwarsa"])
    fefo["Status"] = fefo["Sisa hari"].apply(
        lambda x: "🔴 Kedaluwarsa" if x < 0 else ("🟠 Segera habis masa simpan" if x <= 7 else "🟢 Aman"))

    title("Sisa masa simpan per batch")
    f = fefo.sort_values("Sisa hari")
    fig = go.Figure(go.Bar(
        x=f["Sisa hari"], y=f["Bahan"] + " (" + f["Batch"].astype(str) + ")", orientation="h",
        marker=dict(color=[RED if d < 0 else AMBER if d <= 7 else GREEN for d in f["Sisa hari"]], cornerradius=6),
        text=[f"{d} hari" for d in f["Sisa hari"]], textposition="outside", cliponaxis=False))
    fig.update_xaxes(range=[min(0, f["Sisa hari"].min()) - 5, max(f["Sisa hari"].max(), 1) * 1.15])
    st.plotly_chart(style_fig(fig, 320), use_container_width=True)

    title("Detail batch")
    st.dataframe(fefo[["Bahan", "Batch", "Stok", "Satuan", "Kedaluwarsa", "Sisa hari", "Status"]],
                 use_container_width=True, hide_index=True)

    title("Urutan penggunaan")
    shown = False
    for bahan, group in fefo.groupby("Bahan"):
        group = group.sort_values("Kedaluwarsa")
        if len(group) > 1:
            shown = True
            st.markdown(f"**{bahan}:** " + " → ".join(group["Batch"].astype(str).tolist()))
    if not shown:
        st.caption("Belum ada bahan dengan lebih dari satu batch.")
    st.caption("Catatan: setiap penerimaan bahan di Manajemen Stok → Bahan masuk otomatis menjadi batch baru.")

# ---------- PRODUKSI / BOM ----------
elif page == "Produksi & BOM":
    tab1, tab2 = st.tabs(["📋 Data resep (BOM)", "🏭 Perencanaan produksi"])

    with tab1:
        rec_edit = st.data_editor(st.session_state.recipes, num_rows="dynamic",
                                  use_container_width=True, hide_index=True)
        if st.button("💾 Simpan resep"):
            st.session_state.recipes = rec_edit
            commit("recipes")
            st.success("Data resep disimpan.")
            st.rerun()

    with tab2:
        products = sorted(st.session_state.recipes["Produk"].dropna().unique().tolist())
        if products:
            c1, c2 = st.columns(2)
            selected = c1.selectbox("Pilih produk", products)
            target = c2.number_input("Target produksi (unit)", min_value=1, value=50, step=5)
            req = st.session_state.recipes[st.session_state.recipes["Produk"] == selected].copy()
            req["Total kebutuhan"] = req["Kebutuhan/unit (kg)"] * target

            inv_now = st.session_state.inventory.copy()
            inv_now["Kedaluwarsa"] = pd.to_datetime(inv_now["Kedaluwarsa"]).dt.date
            inv_now = inv_now[inv_now["Kedaluwarsa"] >= date.today()]
            stock = (inv_now.groupby("Bahan", as_index=False)
                     .agg(Stok=("Stok", "sum"), Satuan=("Satuan", "first")))
            check = req.merge(stock, on="Bahan", how="left")
            check["Status"] = check.apply(
                lambda r: "✅ Stok cukup" if pd.notna(r["Stok"]) and r["Stok"] >= r["Total kebutuhan"]
                else "⚠️ Perlu pengadaan", axis=1)

            ok = (check["Status"].str.contains("cukup")).sum()
            m1, m2, m3 = st.columns(3)
            m1.metric("Jenis bahan dibutuhkan", len(check))
            m2.metric("Stok mencukupi", f"{ok} bahan")
            m3.metric("Perlu pengadaan", f"{len(check) - ok} bahan")

            title(f"Kebutuhan vs stok untuk {target} unit {selected}")
            comp = check.melt(id_vars="Bahan", value_vars=["Total kebutuhan", "Stok"],
                              var_name="Jenis", value_name="Jumlah")
            fig = px.bar(comp, x="Bahan", y="Jumlah", color="Jenis", barmode="group",
                         color_discrete_sequence=[GOLD, GREEN])
            fig.update_traces(marker_cornerradius=6)
            st.plotly_chart(style_fig(fig, 320), use_container_width=True)

            title("Pemeriksaan kecukupan stok")
            st.dataframe(check[["Bahan", "Total kebutuhan", "Stok", "Satuan", "Status"]],
                         use_container_width=True, hide_index=True)

            if st.button("🏭 Catat produksi & kurangi stok (FEFO)", type="primary",
                         disabled=bool(ok < len(check))):
                for _, r in check.iterrows():
                    fefo_consume(r["Bahan"], r["Total kebutuhan"])
                log_activity("Produksi", selected, f"{target} unit", "Bahan baku dikurangi otomatis dengan FEFO")
                st.toast(f"Produksi {target} unit {selected} tercatat.")
                st.rerun()
            if ok < len(check):
                st.caption("Tombol aktif setelah seluruh bahan mencukupi.")
        else:
            st.warning("Tambahkan data resep terlebih dahulu.")

# ---------- PREDIKSI ----------
elif page == "Prediksi Permintaan":
    st.markdown('<div class="card">Peramalan permintaan dengan <b>Moving Average</b>. Ganti data dengan catatan penjualan usaha.</div>',
                unsafe_allow_html=True)
    st.write("")
    with st.expander("✏️ Edit data penjualan", expanded=False):
        sales = st.data_editor(st.session_state.sales, num_rows="dynamic", use_container_width=True, hide_index=True)
        if st.button("💾 Simpan data penjualan"):
            st.session_state.sales = sales
            commit("sales")
            st.success("Data penjualan disimpan.")
            st.rerun()

    product_cols = [c for c in st.session_state.sales.columns if c != "Minggu"]
    if product_cols:
        c1, c2 = st.columns(2)
        chosen = c1.selectbox("Produk yang dianalisis", product_cols)
        values = pd.to_numeric(st.session_state.sales[chosen], errors="coerce").dropna()
        if len(values) >= 3:
            window = c2.slider("Periode Moving Average", 2, max(3, min(6, len(values))), min(3, len(values)))
        else:
            window = 2
        if len(values) >= window:
            forecast = values.tail(window).mean()
            a, b, c = st.columns(3)
            a.metric("Prediksi periode berikutnya", f"{forecast:.1f} unit")
            b.metric("Rata-rata historis", f"{values.mean():.1f} unit")
            c.metric("Penjualan terakhir", f"{values.iloc[-1]:.0f} unit",
                     delta=f"{values.iloc[-1] - values.iloc[-2]:+.0f}" if len(values) > 1 else None)

            labels = st.session_state.sales["Minggu"].tolist()
            sales_vals = pd.to_numeric(st.session_state.sales[chosen], errors="coerce")
            ma = sales_vals.rolling(window).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=labels, y=sales_vals, name="Penjualan", mode="lines+markers",
                                     line=dict(color=GREEN, width=3), fill="tozeroy",
                                     fillcolor="rgba(47,107,91,.10)"))
            fig.add_trace(go.Scatter(x=labels, y=ma, name=f"MA({window})", mode="lines",
                                     line=dict(color=GOLD, width=3, dash="dot")))
            fig.add_trace(go.Scatter(x=["Prediksi"], y=[forecast], name="Prediksi", mode="markers",
                                     marker=dict(color=RED, size=14, symbol="star")))
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)
            st.caption(f"Rumus: MA({window}) = jumlah penjualan {window} periode terakhir ÷ {window}. Hasil dibulatkan sesuai kebutuhan produksi.")
        else:
            st.warning("Data belum cukup untuk periode Moving Average yang dipilih.")

st.divider()
st.caption("STOCKWISE · Prototipe akademik. Data awal merupakan data simulasi, bukan data usaha nyata.")
