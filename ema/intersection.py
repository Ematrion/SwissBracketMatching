import plotly.graph_objects as go
import numpy as np

from ema.coverings import FLAT, STAR
from ema.completebipartite import cmap


colors = cmap.colors

# Node mapping to colors
node_colors = {
    'F1': colors[0],  # type:ignore
    'F2': colors[1],  # type:ignore
    'F3': colors[2],  # type:ignore
    
    'S1': colors[0],  # type:ignore
    'S2': colors[1],  # type:ignore
    'S3': colors[2],  # type:ignore
}


# Define node positions
left_x = 1
left_y = [3, 2, 1]  # F1, F2, F3
right_x = 3
right_y = [3, 2, 1]  # S1, S2, S3


def edges():
    # Find common pairs and build edge data
    edge_data = []
    for i, flat_key in enumerate(['F1', 'F2', 'F3']):
        for j, star_key in enumerate(['S1', 'S2', 'S3']):
            flat_pairs = set(FLAT[flat_key])
            star_pairs = set(STAR[star_key])
            common = flat_pairs & star_pairs
            
            if common:
                pair = list(common)[0]  # Should be exactly one common pair
                label = f"{pair}"
                color1 = node_colors[flat_key]
                color2 = node_colors[star_key]
                edge_data.append((i, j, color1, color2, label))
    return edge_data

def color_gradient(fig, edge_data):
    # Draw edges with gradient effect
    for i, j, color1, color2, label in edge_data:
        n_segments = 50
        x_vals = np.linspace(left_x, right_x, n_segments)
        y_vals = np.linspace(left_y[i], right_y[j], n_segments)
        
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Create gradient colors
        for k in range(n_segments - 1):
            t = k / (n_segments - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            
            color = f'rgb({r},{g},{b})'
            
            fig.add_trace(go.Scatter(
                x=[x_vals[k], x_vals[k+1]], 
                y=[y_vals[k], y_vals[k+1]],
                mode='lines',
                line=dict(color=color, width=6),
                hovertemplate=f'<b>{label}</b><extra></extra>',
                showlegend=False,
                opacity=0.9
            ))

def draw_nodes(fig, right_labels, left_labels):
    # Draw left nodes (FLAT)
    for i, label in enumerate(left_labels):
        color = node_colors[label]
        fig.add_trace(go.Scatter(
            x=[left_x],
            y=[left_y[i]],
            mode='markers+text',
            marker=dict(size=60, color=color, line=dict(color='#333', width=3)),
            text=[label],
            textposition='middle center',
            textfont=dict(size=12, color='white', family='Arial Black'),
            hoverinfo='skip',
            showlegend=False
        ))

    # Draw right nodes (STAR)
    for i, label in enumerate(right_labels):
        color = node_colors[label]
        fig.add_trace(go.Scatter(
            x=[right_x],
            y=[right_y[i]],
            mode='markers+text',
            marker=dict(size=60, color=color, line=dict(color='#333', width=3)),
            text=[label],
            textposition='middle center',
            textfont=dict(size=12, color='white', family='Arial Black'),
            hoverinfo='skip',
            showlegend=False
        ))


def intersection_graph_STAR_FLAT():
    left_labels = ['F1', 'F2', 'F3']
    right_labels = ['S1', 'S2', 'S3']
    edge_data = edges()
    fig = go.Figure()
    
    color_gradient(fig, edge_data)
    draw_nodes(fig, right_labels, left_labels)

    fig.update_layout(
        title=dict(
            text='The intersection graph of two distinct 1-factorizations of K₃,₃ begets K₃,₃<br><sub>Hover over edges to common pair labels</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, family='Arial Black')
        ),
        xaxis=dict(
            range=[0.5, 3.5],
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[0.5, 3.5],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            scaleanchor='x',
            scaleratio=1
        ),
        plot_bgcolor='white',
        width=800,
        height=600,
        hovermode='closest',
        margin=dict(l=50, r=50, t=100, b=50)
    )
    return fig