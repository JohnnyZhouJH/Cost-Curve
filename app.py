import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


# PCB cost with diffrent S-Cell sizes and with diffrent Arrangements

pcb_models = {
    "LH6": lambda x: 0.9812*x - 0.2134,
    "LH8": lambda x: 1.6676*x - 4.84,
    "LH10": lambda x: 1.958*x- 4.752
}

# Die cost with Chip sizes
die_model = lambda x: 0.0225*x**2 + 0.0413*x + 7.9703


# Streamlit
st.title("Total Cost Surface Viewer")

arr_choice = st.selectbox("Choose PCB Arrangement:", list(pcb_models.keys()))
pcb_min, pcb_max = st.slider("PCB size:", 5, 20, (5, 20))
die_min, die_max = st.slider("Chip size:", 1, 10, (1, 10))
density = st.slider("Resolution:", 20, 100, 50)

pcb_vals = np.linspace(pcb_min, pcb_max, density)
die_vals = np.linspace(die_min, die_max, density)
PCB, DIE = np.meshgrid(pcb_vals, die_vals)

pcb_cost = pcb_models[arr_choice](PCB)
die_cost = die_model(DIE)
total_cost = pcb_cost + die_cost

# Minimum Point
min_idx = np.unravel_index(np.argmin(total_cost), total_cost.shape)
pcb_min_val = PCB[min_idx]
die_min_val = DIE[min_idx]
total_min_val = total_cost[min_idx]

# Draw
fig = go.Figure()

fig.add_trace(go.Surface(
    z=total_cost, x=PCB, y=DIE, colorscale="Viridis", opacity=0.9
))

# Minimum Point
show_min = st.checkbox("Minimum Point Display", value=True)
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

if show_min:
    
    st.success(f"Minimum Cost Point: {total_min_val:.2f} € (PCB={pcb_min_val:.2f}, Die={die_min_val:.2f})")
