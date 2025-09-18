import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# ===============================
# PCB cost models
# ===============================
pcb_models = {
    "LH6": lambda x: 0.9812*x - 0.2134,
    "LH8": lambda x: 1.6676*x - 4.84,
    "LH10": lambda x: 1.958*x - 4.752
}

# Die cost model
die_model = lambda x: 0.0225*x**2 + 0.0413*x + 7.9703

# ===============================
# Streamlit UI
# ===============================
st.title("💰 Total Cost Surface Viewer")

arr_choice = st.selectbox("选择 PCB Arrangement:", list(pcb_models.keys()))
pcb_min, pcb_max = st.slider("PCB size 范围:", 5, 20, (5, 20))
die_min, die_max = st.slider("Die size 范围:", 1, 10, (1, 10))
density = st.slider("曲面分辨率 (网格点数):", 20, 80, 40)

# ===============================
# 生成网格并计算
# ===============================
pcb_vals = np.linspace(pcb_min, pcb_max, density)
die_vals = np.linspace(die_min, die_max, density)
PCB, DIE = np.meshgrid(pcb_vals, die_vals)

pcb_cost = pcb_models[arr_choice](PCB)
die_cost = die_model(DIE)
total_cost = pcb_cost + die_cost

# 找最小点
min_idx = np.unravel_index(np.argmin(total_cost), total_cost.shape)
pcb_min_val, die_min_val, total_min_val = PCB[min_idx], DIE[min_idx], total_cost[min_idx]

# ===============================
# 绘制曲面
# ===============================
fig = go.Figure()

fig.add_trace(go.Surface(
    z=total_cost, x=PCB, y=DIE,
    colorscale="Viridis", opacity=0.9
))

# 可选：显示最小点
if st.checkbox("显示最小点", value=True):
    fig.add_trace(go.Scatter3d(
        x=[pcb_min_val], y=[die_min_val], z=[total_min_val],
        mode="markers+text",
        marker=dict(size=6, color="red"),
        text=[f"Min: {total_min_val:.2f}€\nPCB={pcb_min_val:.2f}, Die={die_min_val:.2f}"],
        textposition="top center"
    ))
    st.success(f"✅ 最小成本点: {total_min_val:.2f} € (PCB={pcb_min_val:.2f}, Die={die_min_val:.2f})")

fig.update_layout(
    scene=dict(
        xaxis_title="PCB size",
        yaxis_title="Die size",
        zaxis_title="Total cost (€)"
    ),
    title=f"Total Cost Surface (Arrangement {arr_choice})",
    autosize=True,
    height=700
)

# ===============================
# 始终显示曲面图
# ===============================
st.plotly_chart(fig, use_container_width=True)

# ===============================
# 监听点击事件
# ===============================
selected_points = plotly_events(fig, click_event=True, hover_event=False)

# ===============================
# 点击点信息
# ===============================
if selected_points:
    pt = selected_points[0]
    x_sel = pt.get("x")
    y_sel = pt.get("y")

    # 如果没有 z，就自己算
    if "z" in pt:
        z_sel = pt["z"]
    else:
        pcb_c = pcb_models[arr_choice](x_sel)
        die_c = die_model(y_sel)
        z_sel = pcb_c + die_c

    st.info(f"📍 点击点 → PCB={x_sel:.2f}, Die={y_sel:.2f}, Cost={z_sel:.2f} €")
