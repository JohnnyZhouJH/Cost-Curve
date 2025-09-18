import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# =============== 模型 ===============
pcb_models = {
    "LH6":  lambda x: 0.9812*x - 0.2134,
    "LH8":  lambda x: 1.6676*x - 4.84,
    "LH10": lambda x: 1.958*x - 4.752
}
die_model = lambda y: 0.0225*y**2 + 0.0413*y + 7.9703

# =============== UI ===============
st.title("💰 Total Cost Surface Viewer")
arr_choice = st.selectbox("选择 PCB Arrangement:", list(pcb_models.keys()))
pcb_min, pcb_max = st.slider("PCB size 范围:", 5, 20, (5, 20))
die_min, die_max = st.slider("Die size 范围:", 1, 10, (1, 10))
density = st.slider("曲面分辨率 (网格点数):", 20, 80, 40)
show_min = st.checkbox("显示最小点", value=True)

# =============== 计算（带缓存） ===============
@st.cache_data(show_spinner=False)
def compute_grid(arr_key, pmin, pmax, dmin, dmax, n):
    px = np.linspace(pmin, pmax, n)
    dy = np.linspace(dmin, dmax, n)
    PCB, DIE = np.meshgrid(px, dy)
    pcb_cost = pcb_models[arr_key](PCB)
    die_cost = die_model(DIE)
    total = pcb_cost + die_cost
    # 最小点
    idx = np.unravel_index(np.argmin(total), total.shape)
    return PCB, DIE, total, (PCB[idx], DIE[idx], total[idx])

PCB, DIE, TOTAL, (pcb_min_val, die_min_val, total_min_val) = compute_grid(
    arr_choice, pcb_min, pcb_max, die_min, die_max, density
)

# =============== 组图（Surface + 可点击点云） ===============
fig = go.Figure()

# 1) surface（美观）
fig.add_trace(go.Surface(
    x=PCB, y=DIE, z=TOTAL,
    colorscale="Viridis", opacity=0.9,
    showscale=True, name="Total cost surface",
    hovertemplate="PCB=%{x:.2f}<br>Die=%{y:.2f}<br>Cost=%{z:.2f}<extra></extra>"
))

# 2) 点云（用于点击 & 兜底可见性）
fig.add_trace(go.Scatter3d(
    x=PCB.ravel(), y=DIE.ravel(), z=TOTAL.ravel(),
    mode="markers",
    marker=dict(size=2, color=TOTAL.ravel(), colorscale="Viridis", opacity=0.25),
    name="Clickable points",
    hovertemplate="PCB=%{x:.2f}<br>Die=%{y:.2f}<br>Cost=%{z:.2f}<extra></extra>"
))

# 3) 最小点
if show_min:
    fig.add_trace(go.Scatter3d(
        x=[pcb_min_val], y=[die_min_val], z=[total_min_val],
        mode="markers+text",
        marker=dict(size=6, color="red"),
        text=[f"Min: {total_min_val:.2f}€\nPCB={pcb_min_val:.2f}, Die={die_min_val:.2f}"],
        textposition="top center",
        name="Minimum"
    ))
    st.success(f"✅ 最小成本点: {total_min_val:.2f} € (PCB={pcb_min_val:.2f}, Die={die_min_val:.2f})")

fig.update_layout(
    scene=dict(
        xaxis_title="PCB size",
        yaxis_title="Die size",
        zaxis_title="Total cost (€)"
    ),
    title=f"Total Cost Surface (Arrangement {arr_choice})",
    height=700
)

# =============== 仅渲染一张图，并监听点击 ===============
selected = plotly_events(
    fig, click_event=True, hover_event=False,
    override_height=700, override_width="100%"
)

# =============== 点击信息（安全取值） ===============
if selected:
    pt = selected[0]
    x_sel = pt.get("x", None)
    y_sel = pt.get("y", None)
    z_sel = pt.get("z", None)
    if (x_sel is not None) and (y_sel is not None):
        # 没有 z 就按模型计算
        if z_sel is None:
            z_sel = pcb_models[arr_choice](x_sel) + die_model(y_sel)
        st.info(f"📍 点击点 → PCB={x_sel:.2f}, Die={y_sel:.2f}, Cost={z_sel:.2f} €")
