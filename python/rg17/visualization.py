import plotly
import plotly.plotly as py
from plotly.graph_objs import *

import networkx as nx
from .evaluate_toplist import *

def show_graph(pair_occs_df, key_words, snapshot_ids, score_limit=None):
    edges = get_toplist_with_max_scores(pair_occs_df,key_words,snapshot_ids)[["word_1","word_2","occ_score"]]
    edges = edges.sort_values("occ_score")
    node_color_map = edges.groupby("word_2")["occ_score"].mean()
    for key_w in key_words:
        node_color_map[key_w] = 0.0
    if score_limit != None:
        edges = edges[edges["occ_score"] > score_limit]
    # If mention is bi-directional than this information is lost
    G = nx.Graph()
    G.add_weighted_edges_from(edges.as_matrix(),weight="occ_score")
    spring_layout = nx.spring_layout(G,iterations=100,weight="occ_score")
    draw_with_plotly(G, spring_layout, key_words, node_color_map, snapshot_id=snapshot_ids)
    
def show_multiple_snapshots(pair_occs_df, key_words, snapshot_ids, score_limit=None):
    for snapshot_id in snapshot_ids:
        print(snapshot_id)
        if isinstance(snapshot_id, list):
            show_graph(pair_occs_df, key_words, snapshot_id, score_limit=score_limit)
        else:
            show_graph(pair_occs_df, key_words, [snapshot_id], score_limit=score_limit)
    if isinstance(snapshot_ids[0], list):
        merged_time_stamps = []
        for ts_list in snapshot_ids:
            merged_time_stamps += ts_list
        merged_time_stamps = list(set(merged_time_stamps))
    else:
        merged_time_stamps = snapshot_ids
    show_graph(pair_occs_df, key_words, merged_time_stamps, score_limit=score_limit)

### Plotly ###

def draw_with_plotly(SP, SP_layout, queried_nodes, node_color_map, snapshot_id=None):
    edge_trace = Scatter(
    x=[],
    y=[],
    line=Line(
        width=1.0,
        color='#888',
        #color=[]#,
        #autocolorscale=True,
        #text=[],
        #colorscale='YIGnBu'   
    ),
    hoverinfo='none',
    mode='lines')

    #edge_color, edge_info = [], []
    for edge in SP.edges(data=True):
        x0, y0 = list(SP_layout[edge[0]])
        x1, y1 = list(SP_layout[edge[1]])
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]
        #print(edge[2]['occ_score'])
        #edge_color += ["#4286f4" if edge[2]['occ_score'] < 1.1 else "#f44542"]#[edge[2]['occ_score']]
        #edge_trace['line']['text'] += ["%.3f" % edge[2]['occ_score']]
        #edge_trace['text'] += [edge[2]]
    #print(edge_color)
    #edge_trace['line']['color'] = edge_color
    #edge_trace['line']['text'] = edge_info
    
    node_trace = Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=Marker(
            showscale=True,
            colorscale='YIGnBu',
            reversescale=True,
            opacity=1.0,
            color=[],
            size=[],
            line=dict(width=2))
    )
    
    for node in SP.nodes():
        x, y = list(SP_layout[node])
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        mean_occ_val = node_color_map[node] if node in node_color_map else 0.0
        node_trace['text'].append(str(node) + ": %0.3f" % mean_occ_val)
        node_trace['marker']['color'].append(mean_occ_val)
        node_trace['marker']['size'].append(20 if node in queried_nodes else 15)
    
    
    fig = Figure(data=Data([edge_trace, node_trace]),
                 layout=Layout(
                    width=1500,
                    height=800,
                    title='<br>%s' % snapshot_id if snapshot_id != None else "",
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
    """
    if snapshot_id != None:
        py.iplot(fig, filename='combined_occurences_%s' % snapshot_id)
    else:
        py.iplot(fig, filename='combined_occurences')
    """
    if snapshot_id != None:
        plotly.offline.iplot(fig, filename='combined_occurences_%s' % snapshot_id)
    else:
        plotly.offline.iplot(fig, filename='combined_occurences')
    