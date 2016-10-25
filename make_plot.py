import json
import arrow
import plotly
from plotly.tools import FigureFactory as FF
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Bar
import plotly.graph_objs as go
from collections import defaultdict

if __name__ == '__main__':
    with open('plot/AC_DC.json','r') as min:
        acdc = json.load(min)
    mdict = {}
    for member in acdc['member_points']:
        p = member['member']
        if mdict.get(p,None) is None:
            mdict[p] = {}
        if mdict[p].get('x',None) is None:
            mdict[p]['x'] =  []
        if mdict.get('y',None) is None:
            mdict[p]['y'] = []

        mdict[p]['x'].append(arrow.get(member['t'], 'YYYYMMDD').year)
        mdict[p]['y'].append(member['member'])
        mdict[p]['x'].append(arrow.get(member['f'], 'YYYYMMDD').year)
        mdict[p]['y'].append(member['member'])

    traces = []
    for member, xy in mdict.items():
        traces.append(go.Scatter(
            x=xy['x'],
            y=xy['y']
        ))

    # layout = go.Layout(
    #     xaxis=dict(
    #         showline=True,
    #         showgrid=False,
    #         showticklabels=True,
    #         linecolor='rgb(204, 204, 204)',
    #         linewidth=2,
    #         autotick=False,
    #         ticks='outside',
    #         tickcolor='rgb(204, 204, 204)',
    #         tickwidth=2,
    #         ticklen=5,
    #         tickfont=dict(
    #             family='Arial',
    #             size=12,
    #             color='rgb(82, 82, 82)',
    #         ),
    #     ),
    #     yaxis=dict(
    #         showgrid=False,
    #         zeroline=False,
    #         showline=False,
    #         showticklabels=False,
    #     ),
    #     autosize=False,
    #     margin=dict(
    #         autoexpand=False,
    #         l=100,
    #         r=20,
    #         t=110,
    #     ),
    #     showlegend=False,
    # )

    fig = go.Figure(data=traces)
    plotly.offline.plot(fig, filename='it.html')



