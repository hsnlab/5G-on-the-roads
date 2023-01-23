import dash_bootstrap_components as dbc
import pandas
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output
from itertools import product
from os import path

targets = {"Tw": "Waiting time [s]", "I": "Information value"}
parameters = {"D": "Diameter [km]", "Tt": "Trigger time [s]", "B": "Bandwidth [Mb/s]"}

colums = {targets["Tw"]: "waiting_time",
          targets["I"]: "info_value"}

results = {"dir": "results",
           "file-prefix": "result_wt0.1",
           parameters["D"]: {
               "prefix": "d",
               "values": [500, 1000, 2000, 4000]},
           parameters["Tt"]: {
               "prefix": "tt",
               "values": [1000, 10000, 100000]},
           parameters["B"]: {
               "prefix": "bw",
               "values": [10, 100, 1000]},
           "dataframes": {},
           "plots": {}}

def get_cols_rows(parameter):
    cols = []
    rows = []
    if parameter == parameters["D"]:
        cols = [f"{y[0]}, {y[1]}" for y in list(product(
            [f"Tt={int(x/1000)} s" for x in results[parameters["Tt"]]["values"]],
            [f"B={x} Mb/s" for x in results[parameters["B"]]["values"]]))]
        rows = [x/1000 for x in results[parameter]["values"]]
    elif parameter == parameters["Tt"]:
        cols = [f"{y[0]}, {y[1]}" for y in list(product(
            [f"D={x/1000} km" for x in results[parameters["D"]]["values"]],
            [f"B={x} Mb/s" for x in results[parameters["B"]]["values"]]))]
        rows = [x/1000 for x in results[parameter]["values"]]
    elif parameter == parameters["B"]:
        cols = [f"{y[0]}, {y[1]}" for y in list(product(
            [f"Tt={int(x/1000)} s" for x in results[parameters["Tt"]]["values"]],
            [f"D={x/1000} km" for x in results[parameters["D"]]["values"]]))]
        rows = results[parameter]["values"]
    return (cols, rows)

for parameter in parameters.values():
    cols, rows = get_cols_rows(parameter)
    for target in targets.values():
        name = f"{parameter} {target}"
        results["dataframes"][name] = pandas.DataFrame(index=rows, columns=cols)

for d in results[parameters["D"]]["values"]:
    d_infix = f"{results[parameters['D']]['prefix']}{d}"
    for t in results[parameters["Tt"]]["values"]:
        t_infix = f"{d_infix}{results[parameters['Tt']]['prefix']}{t}"
        for b in results[parameters["B"]]["values"]:
            b_infix = f"{t_infix}{results[parameters['B']]['prefix']}{b}"
            df = pandas.read_csv(
                path.join(".", results["dir"],
                          f"{results['file-prefix']}{b_infix}.csv"))

            tw = round(df[colums[targets["Tw"]]].mean()/1000, 4)
            i =  round(df[colums[targets["I"]]].mean(), 4)

            results["dataframes"][f"{parameters['D']} {targets['Tw']}"].at[
                d/1000, f"Tt={int(t/1000)} s, B={b} Mb/s"] = tw

            results["dataframes"][f"{parameters['D']} {targets['I']}"].at[
                d/1000, f"Tt={int(t/1000)} s, B={b} Mb/s"] = i

            
            results["dataframes"][f"{parameters['Tt']} {targets['Tw']}"].at[
                t/1000, f"D={d/1000} km, B={b} Mb/s"] = tw

            results["dataframes"][f"{parameters['Tt']} {targets['I']}"].at[
                t/1000, f"D={d/1000} km, B={b} Mb/s"] = i


            results["dataframes"][f"{parameters['B']} {targets['Tw']}"].at[
                b, f"Tt={int(t/1000)} s, D={d/1000} km"] = tw

            results["dataframes"][f"{parameters['B']} {targets['I']}"].at[
                b, f"Tt={int(t/1000)} s, D={d/1000} km"] = i

            
for parameter in parameters.values():
    cols, rows = get_cols_rows(parameter)
    for target in targets.values():
        name = f"{parameter} {target}"
        log_y = False
        log_x = True
        range_y = [0, 0.4]
        range_x = []
        if target == targets["Tw"]:
            log_y = True
            range_y = [0.5, 130]
        if parameter == parameters["D"]:
            log_x = False
            range_x = [0, 4.5]
        elif parameter == parameters["Tt"]:
            range_x = [0.9, 110]
        elif parameter == parameters["B"]:
            range_x = [9, 1100]
        
        results["plots"][name] = px.line(
            results["dataframes"][name],
            labels={"index": parameter,
                    "value": target,
                    "variable": "System parameters:"},
            log_x=log_x,
            log_y=log_y,
            y=cols,
            range_x=range_x,
            range_y=range_y,
            title=f"Effect on the {target}")
        
def navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=[dbc.NavItem(dbc.NavLink("Diameter",
                                              href=f"/{results[parameters['D']]['prefix']}")),
                      dbc.NavItem(dbc.NavLink("Trigger time",
                                              href=f"/{results[parameters['Tt']]['prefix']}")),
                      dbc.NavItem(dbc.NavLink("Uplink bandwidth",
                                              href=f"/{results[parameters['B']]['prefix']}"))],
            brand="5G on the roads: optimizing the latency of federated analysis in vehicular edge networks (NOMS'23)",
            brand_href="/d",
            color="dark",
            dark=True)])

    return layout

def dimeter_layout():
    return html.Div([
        html.H4('Effects of changing the diameter'),
        html.H5('Legend:'),
        html.H6('Tt: trigger time [s]'),
        html.H6('B: bandwidth [Mb/s]'),
        html.Div(children=[
            dcc.Graph(figure=results["plots"][f"{parameters['D']} {targets['Tw']}"],
                      style={'display': 'inline-block'}),
            dcc.Graph(figure=results["plots"][f"{parameters['D']} {targets['I']}"],
                      style={'display': 'inline-block'})])])

def trigger_time_layout():
    return html.Div([
        html.H4('Effects of changing the trigger time'),
        html.H5('Legend:'),
        html.H6('D: diameter [km]'),
        html.H6('B: bandwidth [Mb/s]'),
        html.Div(children=[
            dcc.Graph(figure=results["plots"][f"{parameters['Tt']} {targets['Tw']}"],
                      style={'display': 'inline-block'}),
            dcc.Graph(figure=results["plots"][f"{parameters['Tt']} {targets['I']}"],
                      style={'display': 'inline-block'})])])

def bandwidth_layout():
    return html.Div([
        html.H4('Effects of changing the uplink bandwidth'),
        html.H5('Legend:'),
        html.H6('Tt: trigger time [s]'),
        html.H6('D: diameter [km]'),
        html.Div(children=[
            dcc.Graph(figure=results["plots"][f"{parameters['B']} {targets['Tw']}"],
                      style={'display': 'inline-block'}),
            dcc.Graph(figure=results["plots"][f"{parameters['B']} {targets['I']}"],
                      style={'display': 'inline-block'})])])

colorscales = px.colors.named_colorscales()

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP], 
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar(), 
    html.Div(id='page-content', children=[])])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == f"/{results[parameters['D']]['prefix']}":
        return dimeter_layout()
    if pathname == f"/{results[parameters['Tt']]['prefix']}":
        return trigger_time_layout()
    if pathname == f"/{results[parameters['B']]['prefix']}":
        return bandwidth_layout()
    else:
        return dimeter_layout()


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
