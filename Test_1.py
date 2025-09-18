import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# ===============================
# 1. 定义 PCB cost 模型 (不同 arrangement)
# ===============================
pcb_models = {
    "LH8": lambda x: 0.9817*x - 0.2314,
    "LH9": lambda x: 1.6676*x - 4.84,
    "LH10": lambda x: -0.2842*x**3 + 8.635*x**2 - 91.58*x + 352.41
}

# ===============================
# 2. 定义 Die cost 模型
# ===============================
die_model = lambda die: 0.8225*die**2 + 0.4317*die + 2.9783

# ===============================
# 3. Streamlit 界面
# ===============================
st.title("💰 Total Cost Surface Viewer")

# Arrangement 下拉选择
arr_choice = st.selectbox("选择 PCB Arrangement:", list(pcb_models.keys()))

# 选择范围（可调节）
pcb_min, pcb_max = st.slider("PCB size 范围:", 5, 20, (5, 20))
die_min, die_max = st.slider("Die size 范围:", 1, 10, (1, 10))

# 网格密度
density = st.slider("曲面分辨率 (网格点数):", 20, 100, 50)

# ===============================
# 4. 计算网格数据
# ===============================
pcb_vals = np.linspace(pcb_min, pcb_max, density)
die_vals = np.linspace(die_min, die_max, density)
PCB, DIE = np.meshgrid(pcb_vals, die_vals)

pcb_cost = pcb_models[arr_choice](PCB)
die_cost = die_model(DIE)
total_cost = pcb_cost + die_cost

# ===============================
# 5. 找最小点
# ===============================
min_idx = np.unravel_index(np.argmin(total_cost), total_cost.shape)
pcb_min_val = PCB[min_idx]
die_min_val = DIE[min_idx]
total_min_val = total_cost[min_idx]

# ===============================
# 6. 绘制交互式 3D 曲面
# ===============================
fig = go.Figure()

# 曲面
fig.add_trace(go.Surface(
    z=total_cost, x=PCB, y=DIE, colorscale="Viridis", opacity=0.9
))

# 最小点
show_min = st.checkbox("显示最小点", value=True)
if show_min:
    fig.add_trace(go.Scatter3d(
        x=[pcb_min_val], y=[die_min_val], z=[total_min_val],
        mode="markers+text",
        marker=dict(size=6, color="red"),
        text=[f"Min: {total_min_val:.2f}€\nPCB={pcb_min_val:.2f}, Die={die_min_val:.2f}"],
        textposition="top center"
    ))

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

st.plotly_chart(fig, use_container_width=True)

selected_points = plotly_events(fig, click_event=True, hover_event=False)

if selected_points:
    pt = selected_points[0]
    x_sel = pt["x"]
    y_sel = pt["y"]
    z_sel = pt["z"]
    st.info(f"The Point You Clicked: PCB={x_sel:.2f}, Die={y_sel:.2f}, Cost={z_sel:.2f} €")
 
# ===============================
# 7. 显示最小点信息
# ===============================
if show_min:
    st.success(f"✅ 最小成本点: {total_min_val:.2f} € (PCB={pcb_min_val:.2f}, Die={die_min_val:.2f})")
