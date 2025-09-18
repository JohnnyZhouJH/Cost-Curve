import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# PCB cost with different Arrangements
pcb_models = {
    "LH6": lambda x: 0.9812*x - 0.2134,
    "LH8": lambda x: 1.6676*x - 4.84,
    "LH10": lambda x: 1.958*x - 4.752
}

# Die cost with Chip sizes
die_model = lambda x: 0.0225*x**2 + 0.0413*x + 7.9703

# Streamlit UI
st.title("Total Cost Surface Viewer")

arr_choice = st.selectbox("Choose PCB Arrangement:", list(pcb_models.keys()))
pcb_min, pcb_max = st.slider("PCB size range:", 8, 12, (5, 15))
die_min, die_max = st.slider("Chip size range:", 1, 20, (1, 20))
density = st.slider("Resolution (grid points):", 20, 80, 40)

# Precompute meshgrid
pcb_vals = np.linspace(pcb_min, pcb_max, density)
die_vals = np.linspace(die_min, die_max, density)
PCB, DIE = np.meshgrid(pcb_vals, die_vals)

# Cost calculation
pcb_cost = pcb_models[arr_choice](PCB)
die_cost = die_model(DIE)
total_cost = pcb_cost + die_cost

# Find minimum point
min_idx = np.unravel_index(np.argmin(total_cost), total_cost.shape)
pcb_min_val, die_min_val, total_min_val = PCB[min_idx], DIE[min_idx], total_cost[min_idx]

# Draw figure
fig = go.Figure()

fig.add_trace(go.Surface(
    z=total_cost, x=PCB, y=DIE,
    colorscale="Viridis", opacity=0.9
))

# Add minimum point marker
if st.checkbox("Show minimum point", value=True):
    fig.add_trace(go.Scatter3d(
        x=[pcb_min_val], y=[die_min_val], z=[total_min_val],
        mode="markers+text",
        marker=dict(size=6, color="red"),
        text=[f"Min: {total_min_val:.2f}€\nPCB={pcb_min_val:.2f}, Die={die_min_val:.2f}"],
        textposition="top center"
    ))
    st.success(f"Minimum Cost Point: {total_min_val:.2f} € (PCB={pcb_min_val:.2f}, Die={die_min_val:.2f})")

# Only one chart (remove duplicate)
selected_points = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

# Show clicked point info
if selected_points:
    pt = selected_points[0]
    st.info(f"Clicked Point → PCB={pt['x']:.2f}, Die={pt['y']:.2f}, Cost={pt['z']:.2f} €")
