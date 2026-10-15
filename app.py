"""Interactive retail sales analytics dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import forecast_revenue, monthly_revenue, summarize
from src.data_loader import load_data, load_uploaded_data

DATA_PATH = Path(__file__).resolve().parent / "data" / "sample_data.csv"
PALETTE = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]

st.set_page_config(page_title="Ringkasan Penjualan", page_icon="🛒", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root { color-scheme: light; }
    .stApp, [data-testid="stAppViewContainer"] { background: #f4f7fb !important; }
    html, body, [class*="st-"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
    [data-testid="stHeader"] { background: rgba(244,247,251,.9); }
    .block-container { max-width: 1440px; padding: 2rem 2.5rem 3rem; }
    h1, h2, h3, p, label, span, small { color: #1e293b; }
    [data-testid="stCaptionContainer"] p { color: #475569 !important; }
    [data-testid="stMetric"] {
        background: #ffffff !important; border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important; padding: 20px 22px !important;
        box-shadow: 0 4px 6px -1px rgba(15,23,42,.10), 0 2px 4px -2px rgba(15,23,42,.08);
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] *,
    [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * {
        color: #1e293b !important; opacity: 1 !important;
    }
    [data-testid="stMetricLabel"] { font-weight: 600; }
    [data-testid="stMetricValue"] { font-weight: 700; }
    [data-testid="stTabs"] button { color: #334155 !important; font-weight: 600; }
    [data-testid="stDataFrame"] { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; }
    [data-testid="stDataFrame"] * { color: #1e293b !important; }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e2e8f0; }
    [data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
        background: #4f46e5 !important; border: 1px solid #4338ca !important;
        color: #fff !important; border-radius: 9px !important; font-weight: 600;
    }
    [data-testid="stButton"] button *, [data-testid="stDownloadButton"] button * { color: #fff !important; }
    [data-testid="stAlert"] { border-radius: 10px; }
    .help-card, .section-card {
        background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 16px 20px; color: #334155; margin: 10px 0 18px;
        box-shadow: 0 4px 6px -1px rgba(15,23,42,.07);
    }
    @media (max-width: 700px) { .block-container { padding: 1.25rem 1rem 2rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🛒 Ringkasan Penjualan")
st.caption("Lihat jumlah penjualan, produk yang paling laris, dan wilayah pembeli dalam satu tempat.")

with st.sidebar:
    st.header("Pilih Data")
    upload = st.file_uploader("Unggah file penjualan (CSV atau Excel)", type=["csv", "xlsx"], help="File perlu memiliki kolom date, product_category, revenue, units_sold, region, customer_type.")

try:
    if upload is not None:
        data = load_uploaded_data(upload)
        st.sidebar.success(f"File berhasil dibaca · {len(data):,} transaksi")
        if hasattr(st, "toast"):
            st.toast("Dataset eksternal berhasil dimuat", icon="✅")
    else:
        data = load_data(DATA_PATH)
        st.sidebar.info("Saat ini memakai data contoh. Unggah file sendiri untuk melihat hasilnya.")
except (FileNotFoundError, ValueError) as exc:
    st.error(f"Gagal memuat data: {exc}")
    st.stop()

with st.sidebar:
    st.divider()
    st.header("Saring Hasil")
    min_date, max_date = data["date"].min().date(), data["date"].max().date()
    dates = st.date_input("Tanggal transaksi", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    categories = st.multiselect("Jenis produk", sorted(data["product_category"].unique()), default=sorted(data["product_category"].unique()))
    regions = st.multiselect("Wilayah", sorted(data["region"].unique()), default=sorted(data["region"].unique()))

filtered = data.copy()
if isinstance(dates, (tuple, list)) and len(dates) == 2:
    filtered = filtered[filtered["date"].dt.date.between(dates[0], dates[1])]
filtered = filtered[filtered["product_category"].isin(categories) & filtered["region"].isin(regions)]
if filtered.empty:
    st.info("Tidak ada transaksi yang sesuai dengan filter. Ubah pilihan filter untuk melihat hasil.")
    st.stop()

st.markdown('<div class="help-card">📌 <b>Cara membaca:</b> Gunakan pilihan di sebelah kiri untuk menyaring tanggal, jenis produk, atau wilayah. Angka dan grafik di bawah akan ikut berubah.</div>', unsafe_allow_html=True)
kpis = summarize(filtered)
metric_cols = st.columns(3)
metric_cols[0].metric("Total Penjualan", f"${kpis['total_revenue']:,.2f}", help="Jumlah seluruh pendapatan dari transaksi yang sedang ditampilkan.")
metric_cols[1].metric("Produk Terjual", f"{kpis['total_units_sold']:,}", help="Jumlah unit produk yang terjual.")
metric_cols[2].metric("Rata-rata per Transaksi", f"${kpis['average_order_value']:,.2f}", help="Total penjualan dibagi jumlah transaksi.")

sales_tab, category_tab, region_tab, data_tab, report_tab = st.tabs(["📊 Ikhtisar", "🛍️ Jenis Produk", "📍 Wilayah", "📋 Daftar Transaksi", "⬇️ Unduh Laporan"])
layout = dict(template="plotly_white", color_discrete_sequence=PALETTE)


def style_chart(figure):
    """Apply shared layout settings after Plotly Express creates a chart."""
    return figure.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#1e293b", size=13),
        margin=dict(l=16, r=16, t=42, b=16),
        hoverlabel=dict(bgcolor="#0f172a", bordercolor="#334155", font=dict(color="#ffffff", family="Inter, sans-serif")),
        legend=dict(font=dict(color="#334155")),
    )


def clean_axes(figure):
    """Keep chart labels clear while removing distracting grid lines."""
    figure.update_xaxes(showgrid=False, zeroline=False, linecolor="#cbd5e1", tickfont=dict(color="#334155"))
    figure.update_yaxes(showgrid=False, zeroline=False, linecolor="#cbd5e1", tickfont=dict(color="#334155"))
    return figure

with sales_tab:
    st.subheader("Perubahan penjualan dari bulan ke bulan")
    st.caption("Grafik menunjukkan penjualan bulanan. Garis perkiraan membantu melihat kemungkinan arah penjualan berikutnya; ini bukan jaminan hasil.")
    monthly = monthly_revenue(filtered)
    try:
        forecast = forecast_revenue(filtered)
    except (ValueError, ImportError) as exc:
        forecast = pd.DataFrame(columns=["month", "revenue"])
        st.warning(f"Perkiraan belum tersedia: {exc}")
    actual = monthly[["month", "revenue"]].assign(series="Penjualan tercatat")
    plot_data = pd.concat([actual, forecast.assign(series="Perkiraan")], ignore_index=True) if not forecast.empty else actual
    figure = px.line(plot_data, x="month", y="revenue", color="series", markers=True, labels={"month": "Bulan", "revenue": "Penjualan ($)", "series": "Keterangan"}, **layout)
    st.plotly_chart(clean_axes(style_chart(figure)), use_container_width=True)

with category_tab:
    st.subheader("Penjualan untuk setiap jenis produk")
    st.caption("Bandingkan total penjualan antarjenis produk. Batang yang lebih panjang berarti penjualan lebih tinggi.")
    category_sales = filtered.groupby("product_category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    figure = px.bar(category_sales, x="product_category", y="revenue", color="product_category", labels={"product_category": "Jenis produk", "revenue": "Penjualan ($)"}, **layout)
    figure.update_traces(marker_line_width=0, marker_cornerradius=6, hovertemplate="%{x}<br>Penjualan: $%{y:,.2f}<extra></extra>")
    st.plotly_chart(clean_axes(style_chart(figure)), use_container_width=True)

with region_tab:
    st.subheader("Asal penjualan berdasarkan wilayah")
    st.caption("Setiap bagian lingkaran menunjukkan porsi penjualan dari satu wilayah.")
    region_sales = filtered.groupby("region", as_index=False)["revenue"].sum()
    figure = px.pie(region_sales, names="region", values="revenue", hole=0.48, color_discrete_sequence=PALETTE, template="plotly_white", labels={"region": "Wilayah", "revenue": "Penjualan ($)"})
    figure.update_traces(textfont=dict(color="#1e293b"), hovertemplate="%{label}<br>Penjualan: $%{value:,.2f}<extra></extra>")
    st.plotly_chart(style_chart(figure), use_container_width=True)

with data_tab:
    st.subheader("Transaksi yang sesuai pilihan")
    st.caption(f"Menampilkan {len(filtered):,} transaksi. Ubah saringan di sebelah kiri untuk mempersempit daftar.")
    st.dataframe(filtered.sort_values("date", ascending=False), use_container_width=True, hide_index=True)

with report_tab:
    st.subheader("Simpan data atau ringkasan")
    st.caption("Unduh daftar transaksi yang sudah disaring atau ringkasan angka penjualan untuk dibuka di aplikasi spreadsheet.")
    summary = pd.DataFrame([{
        "total_revenue": kpis["total_revenue"],
        "total_units_sold": kpis["total_units_sold"],
        "average_order_value": kpis["average_order_value"],
        "transaction_rows": len(filtered),
        "date_from": filtered["date"].min().date().isoformat(),
        "date_to": filtered["date"].max().date().isoformat(),
    }])
    export_col, summary_col = st.columns(2)
    export_col.download_button("⬇️ Unduh daftar transaksi (CSV)", filtered.to_csv(index=False).encode("utf-8-sig"), "daftar_transaksi.csv", "text/csv", use_container_width=True)
    summary_col.download_button("⬇️ Unduh ringkasan penjualan (CSV)", summary.to_csv(index=False).encode("utf-8-sig"), "ringkasan_penjualan.csv", "text/csv", use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)
