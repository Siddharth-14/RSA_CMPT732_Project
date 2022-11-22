import dash                     # pip install dash
from dash.dependencies import Input, Output
from dash import dcc, html
import plotly.express as px     # pip install plotly==5.2.2

import pandas as pd             # pip install pandas
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(__name__, server = server, external_stylesheets=external_stylesheets, suppress_callback_exceptions= True)
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://bgmfqpvaznkong:28dd0e1b6da38e2e47bd8b33f72169c233264c732c26c2b9b88bf7c7d21bd819@ec2-35-173-91-114.compute-1.amazonaws.com:5432/d8nf5i3c87jp03"

with server.app_context():
    db = SQLAlchemy(app.server)
    df = pd.read_sql_table("cleaned_data", con = db.engine)

app.layout = html.Div([
    html.H1("Analytics Dashboard of Vancover Police Department (Dash Plotly)", style={
            "textAlign": "center"}),
    html.Hr(),
    html.P("Choose Year:"),
    html.Div(html.Div([
        dcc.Dropdown(id='crime-type', clearable=False,
                     value=2003,
                     options=[{'label': x, 'value': x} for x in
                              df.sort_values(by=['year'])["year"].unique()]),
    ], className="two columns"), className="row"),

    html.Div(id="output-div", children=[]),
])


@app.callback(Output(component_id="output-div", component_property="children"),
              Input(component_id="crime-type", component_property="value"),
              )
def make_bars(animal_chosen):
    # HISTOGRAM
    df_hist = df[df["year"] == animal_chosen]
    fig_hist = px.histogram(df_hist, y="type", text_auto=True,
                            title="Total Number of Crime By Type")
    fig_hist.update_yaxes(categoryorder="total ascending")

    # HISTOGRAM
    fig_strip = px.histogram(df_hist, x="neighbourhood",
                             text_auto=True, title="Total Crime By Neighbourhood")
    fig_strip.update_xaxes(categoryorder="total descending")

    # HISTOGRAM
    df_line_stacked = df_hist.groupby(
        ["type", "neighbourhood"]).size().reset_index(name="count")
    fig_stacked = px.bar(df_line_stacked, x="neighbourhood", y="count",
                         color="type", title="Stacked Type of Crime by Neighbourhood")

    # # SUNBURST
    # df_sburst = df.dropna(subset=['chip_status'])
    # df_sburst = df_sburst[df_sburst["intake_type"].isin(
    #     ["STRAY", "FOSTER", "OWNER SURRENDER"])]
    # fig_sunburst = px.sunburst(
    #     df_sburst, path=["animal_type", "intake_type", "chip_status"])

    # # Empirical Cumulative Distribution
    # df_ecdf = df[df["animal_type"].isin(["DOG", "CAT"])]
    # fig_ecdf = px.ecdf(df_ecdf, x="animal_stay_days", color="animal_type")

    # # LINE CHART
    df_line = df_hist.groupby(["month"]).size().reset_index(name="count")
    fig_line_month = px.line(df_line, x="month", y="count",
                             markers=True, text="count", title="Total Crime By Month")
    fig_line_month.update_traces(textposition="bottom right")

    # # LINE CHART
    df_line = df_hist.groupby(["hour"]).size().reset_index(name="count")
    fig_line_hour = px.line(df_line, x="hour", y="count",
                            markers=True, text="count", title="Total Crime By Hour")
    fig_line_hour.update_traces(textposition="bottom right")

    return [
        html.Div([
            html.Div([dcc.Graph(figure=fig_hist)], className="six columns"),
            html.Div([dcc.Graph(figure=fig_strip)], className="six columns"),
        ], className="row"),
        # html.H2("All Animals", style={"textAlign": "center"}),
        # html.Hr(),
        # html.Div([
        #     html.Div([dcc.Graph(figure=fig_sunburst)],
        #              className="six columns"),
        #     html.Div([dcc.Graph(figure=fig_ecdf)], className="six columns"),
        # ], className="row"),
        html.Div([
            html.Div([dcc.Graph(figure=fig_stacked)],
                     className="twelve columns"),
        ], className="row"),
        html.Div([
            html.Div([dcc.Graph(figure=fig_line_month)],
                     className="twelve columns"),
        ], className="row"),
        html.Div([
            html.Div([dcc.Graph(figure=fig_line_hour)],
                     className="twelve columns"),
        ], className="row"),
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
