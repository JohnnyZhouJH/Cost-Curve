import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# ===============================
# PCB cost models
# ===============================
pcb_models = {
    "LH6":  lambda pcb_size: 0.9812*pcb_size - 0.2134,
    "LH8":  lambda pcb_size: 1.6676*pcb_size - 4.84,
    "LH10": lambda pcb_size: 1.958*pcb_size - 4.752
}

# Die cost model
die_model = lambda die_size: 0.0225*die_size**2 + 0.0413*die_size + 7.9703

# ===============================
# Streamlit UI
# ===============================
st.title("💰 Total Cost Surface Viewer")

arr_choice = st.selectbox("选择 PCB Arrangement:", list(pcb_models.keys()))
pcb_min, pcb_max = st.slider("PCB size 范围:", 5, 20, (5, 20))
die_min, die_max = st.slider("Die size 范围:", 1, 10, (1, 10))
density = st.slider("曲面分辨率 (网格点数):", 20, 80, 40)
show_min = st.checkbox("显示最小点", value=True)

# ===============================
# 计算网格（带缓存）
# ===============================
@st.cache_data(show_spinner=False)
def compute_grid(arr_key, pmin, pmax, dmin, dmax, n):
    pcb_vals = np.linspace(pmin, pmax, n)
    die_vals = np.linspace(dmin, dmax, n)
    PCB, DIE = np.meshgrid(pcb_vals, die_vals)
    pcb_cost = pcb_models[arr_key](PCB)
    die_cost = die_model(DIE)
    total_cost = pcb_cost + die_cost
    # 最小点
    idx = np.unravel_index(np.argmin(total_cost), total_cost.shape)
    return PCB, DIE, total_cost, (PCB[idx], DIE[idx], total_cost[idx])

PCB, DIE, TOTAL, (pcb_min_val, die_min_val, total_min_val) = compute_grid(
    arr_choice, pcb_min, pcb_max, die_min, die_max, density
)

# ===============================
# 绘制曲面
# ===============================
fig = go.Figure()

# 曲面
fig.add_trace(go.Surface(
    z=TOTAL, x=PCB, y=DIE,
    colorscale="Viridis", opacity=0.9,
    showscale=True,
    hovertemplate="PCB=%{x:.2f}<br>Die=%{y:.2f}<br>Cost=%{z:.2f}<extra></extra>"
))

# 最小点
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

# ===============================
# 始终显示图（保证曲面不丢）
# ===============================
st.plotly_chart(fig, use_container_width=True)

# ===============================
# 点击事件监听（只捕获坐标）
# ===============================
selected_points = plotly_events(fig, click_event=True, hover_event=False)

# ===============================
# 显示点击点信息
# ===============================
if selected_points:
    pt = selected_points[0]
    x_sel = pt.get("x")
    y_sel = pt.get("y")
    z_sel = pt.get("z")

    # 如果缺少 z，就自己算
    if z_sel is None and (x_sel is not None and y_sel is not None):
        z_sel = pcb_models[arr_choice](x_sel) + die_model(y_sel)

    if (x_sel is not None) and (y_sel is not None) and (z_sel is not None):
        st.info(f"📍 点击点 → PCB={x_sel:.2f}, Die={y_sel:.2f}, Cost={z_sel:.2f} €")