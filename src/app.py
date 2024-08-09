import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from pages import ModDatosLogisticos

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], use_pages=True,suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([

    dbc.NavbarSimple(
            children=[
                dbc.NavItem(
                    dbc.NavLink(
                        [
                            html.Div(page["name"], className="ms-2"),
                        ],
                        href=page["path"],
                        active="exact",
                    )
                )
                for page in dash.page_registry.values()
            ],
            brand="Transpor-T",
            brand_href="/Panel1",
            color="primary",
            dark=True
        ),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)