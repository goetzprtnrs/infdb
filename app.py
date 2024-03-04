import dash
from dash import html, dcc, callback, Output, Input 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import urllib.parse
import pandas as pd
from dash.dash_table import DataTable
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import geopandas as gpd
from shapely import wkt
from shapely.geometry import LineString
import numpy as np



# Define external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

# Definieren der Dash-App mit external_stylesheets
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

df_weichen = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2105-V_Stueckliste_Weichen.pickle')
df_bruecken = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2106-V_Stueckliste_Bruecken.pickle')
df_tunnel = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2108-V_Stueckliste_Tunnel.pickle')
df_stuetzbauwerke = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2110-V_Stueckliste_Stuetzbauwerke_Bauwerksklasse(BWK)3.pickle')
df_schallschutzwande = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2111-V_Stueckliste_Schallschutzwaende.pickle')
df_bahnubergange = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2112-V_Stueckliste_Bahnuebergaenge.pickle')
df_GSL = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/2022_2101-V_Gesamtstreckenliste(GSL).pickle')
df_ETCS = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/ETCS_heute_und_geplant.pickle')
df_Traffic = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/StrNr_Average_Anual_Traffic_Flow.pickle')
df_HLK_Zeitraum = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/StrNr_HLK_Zeitraum.pickle')
df_br = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/20240229_Matching_Bruecken_vClean.pickle')
df_bu = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/20240229_Matching_2112-V_Stueckliste_Bahnuebergaenge_vClean.pickle')
df_tu = pd.read_pickle('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/20240229_Matching_Tunnel_vClean.pickle')


# HLK-Klarnamen je Streckennummer
hlk_timetable = pd.read_csv('https://raw.githubusercontent.com/goetzprtnrs/infdb/main/data/StrNr_HLK_Zeitraum2.csv', encoding = "'latin-1", sep=";")
streckennummern_listen = hlk_timetable['Streckennummer'].apply(lambda x: [int(num) for num in x.split(',')] if ',' in x else [int(x)]).tolist()
hlk_timetable = hlk_timetable.assign(Streckennummern_Liste=streckennummern_listen)
hlk_dict = dict(zip(hlk_timetable["HLK Name"], hlk_timetable["Streckennummern_Liste"]))



pio.renderers.default = 'browser'

# Mapbox Access Token setzen (ersetzen Sie dies durch Ihr tatsächliches Mapbox Access Token)
mapbox_access_token = 'pk.eyJ1IjoiYW5ka29jaDkzIiwiYSI6ImNsMTZiNnU4dTE5MzQzY3MwZnV1NjVqOGoifQ.ZxCDeRkr59lifDEm4PIWQA'


# GeoDataFrame
df_tu = df_tu[df_tu['geometry'].notna()]
df_tu['geometry'] = df_tu['geometry'].apply(wkt.loads)
df_tu_geo = gpd.GeoDataFrame(df_tu, geometry='geometry')

# Daten manipulieren
df_GSL = df_GSL.groupby(by=['STR_NR']).agg({'LAENGE':'sum', 
                                             'VON_KM':'min',
                                             'BIS_KM':'max', 
                                             'VON_KM_I':'min', 
                                             'BIS_KM_I':'max', 
                                             'EIU': 'first', 
                                             'REGION':'first', 
                                             'NETZ':'first', 
                                             'STR_KURZNAME':'first', 
                                             'STR_KM_ANF':'min', 
                                             'STR_KM_END':'max',
                                             'ISK_NETZ':'first', 
                                             'BAHNNUTZUNG':'first', 
                                             'BETREIBERART':'min'}).reset_index()

df_GSL = df_GSL.merge(df_ETCS, on='STR_NR', how='outer')
df_GSL = df_GSL.merge(df_Traffic, on='STR_NR', how='outer')
df_GSL = df_GSL.merge(df_HLK_Zeitraum, on='STR_NR', how='outer')

# Count der Anlagen etc. 

df_count = df_GSL['STR_NR'].reset_index()
df_count['STR_NR'] = df_count['STR_NR'].astype(str)

count_weichen = df_weichen.groupby('STR_NR').size().reset_index()
count_weichen['STR_NR'] = count_weichen['STR_NR'].astype(str)
count_weichen = count_weichen.rename(columns={0: '#Weichen'})

count_bruecken = df_bruecken.groupby('STR_NR').size().reset_index()
count_bruecken['STR_NR'] = count_bruecken['STR_NR'].astype(str)
count_bruecken = count_bruecken.rename(columns={0: '#Bruecken'})

count_tunnel = df_tunnel.groupby('STR_NR').size().reset_index()
count_tunnel['STR_NR'] = count_tunnel['STR_NR'].astype(str)
count_tunnel = count_tunnel.rename(columns={0: '#Tunnel'})

count_stuetzbauwerke = df_stuetzbauwerke.groupby('STR_NR').size().reset_index()
count_stuetzbauwerke['STR_NR'] = count_stuetzbauwerke['STR_NR'].astype(str)
count_stuetzbauwerke = count_stuetzbauwerke.rename(columns={0: '#Stuezbauwerke'})

count_schallschutzwaende = df_schallschutzwande.groupby('STR_NR').size().reset_index()
count_schallschutzwaende['STR_NR'] = count_schallschutzwaende['STR_NR'].astype(str)
count_schallschutzwaende = count_schallschutzwaende.rename(columns={0: '#Schallschutzwaende'})

count_bahnuebergaenge = df_bahnubergange.groupby('STR_NR').size().reset_index()
count_bahnuebergaenge['STR_NR'] = count_bahnuebergaenge['STR_NR'].astype(str)
count_bahnuebergaenge = count_bahnuebergaenge.rename(columns={0: '#Bahnuebergaenge'})

df_count = df_count.merge(count_weichen, on = 'STR_NR',  how='outer')
df_count = df_count.merge(count_bruecken, on = 'STR_NR',  how='outer')
df_count = df_count.merge(count_tunnel, on = 'STR_NR',  how='outer')
df_count = df_count.merge(count_stuetzbauwerke, on = 'STR_NR',  how='outer')
df_count = df_count.merge(count_schallschutzwaende, on = 'STR_NR',  how='outer')
df_count = df_count.merge(count_bahnuebergaenge, on = 'STR_NR',  how='outer')
df_count = df_count.fillna(0)



# Seitenbeschreibungen
page_descriptions = {
    'HLK-Generalsanierung': html.Div([
        html.P([html.Strong("Informationen zu HLK-Generalsanierungen:")]),
        html.Ul([
            html.Li("Informationen zu den 40 HLK-Generalsanierungen"),
            html.Li("Auswahl und Analyse einzelner Projekte über Dropdown-Menü"),
            html.Li("Details zu Strecken und Anlagen"),
            html.Li("Geographische Visualisierung von Lage und Ausdehnung auf Karte")
        ])
    ]),
    'Analyse Infrastruktur-Bestandsdaten': html.Div([
        html.P([html.Strong("Die Analyse von Infrastruktur-Bestandsdaten ermöglicht:")]),
        html.Ul([
            html.Li("Auswertung von Details zu Strecken und Anlagen"),
            html.Li("Tabellarische und geographische Darstellung")
        ]),
        
    ]),
    'Geo-Visualisierung': html.Div([
        html.P([html.Strong("Geographische Darstellung von")]),
        html.Ul([
            html.Li("Brücken"),
            html.Li("Tunnel"),
            html.Li("Bahnübergänge"),
        ]),
        
    ]),
    'Personenbahnhöfe': html.Div([
        html.P([html.Strong("Zukünftig Informationen zu:")]),
        html.Ul([
            html.Li("Eigenschaften von Personenbahnhöfen"),
            html.Li("Bahnsteiglänge und Barrierefreiheit"),
            html.Li("Daten zu Zukunftsbahnhöfen"),
            html.Li("Details zu Bahnsteiglänge und Barrierefreiheit"),
            html.Li("Informationen zu Zukunftsbahnhöfen"),
        ])
    ])
}



# Funktion zum Erstellen von Karten
def create_card(number, title):
    title_url = urllib.parse.quote(title)
    card_content = dbc.CardBody(
        [
            html.H3(number, className="card-title", style={'color': '#00ffff', 'marginRight': '15px','fontSize': '40px'}),
            html.P(title, className="card-text", style={'fontSize': '20px'}),
        ],
        style={'display': 'flex', 'alignItems': 'center'}
    )

    return html.Div(
        dcc.Link(
            dbc.Card(
                card_content,
                color="light",
                inverse=False,
                style={
                    "width": "95%", 
                    'height': '100px',  # Erhöhte Höhe der Karte
                    'margin': '10px auto', 
                    'textDecoration': 'none',
                    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)'  # Schatten-Effekt
                }
            ),
            href=f'/{title_url}',
            style={'textDecoration': 'none', 'color': 'inherit'}
        ),
        style={'width': '100%'}
    )



# Reusable function for creating styled headings

def create_styled_heading(text, include_search=False, include_extra_text=False):
    search_box = dbc.Input(
        id='search-box',
        type='text',
        placeholder='Datenbank durchsuchen...',
        size="lg",
        className="mb-3"
    ) if include_search else None
    
    extra_text = html.P("im Aufbau befindend", style={'color': '#ff0000', 'fontSize': '20px', 'textAlign': 'center'}) if include_extra_text else None

    return dbc.Card(
        dbc.CardBody(
            [
                html.H1(text, className="card-title text-center", style={'color': '#ffffff'}),
                search_box,
                html.H1('Prototyp', className="card-title text-center", style={'color': '#ff0000', 'fontSize': '20px'}),
                extra_text  # Fügt den zusätzlichen Text mittig hinzu, wenn include_extra_text True ist
            ]
        ),
        className="mb-3",
        style={
            'background': 'linear-gradient(180deg, #003366 0%, #000033 100%)',
            'color': '#fff',
            'borderRadius': '15px',
        }
    )


footer = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                        html.Img(src=app.get_asset_url('bmdv_logo.png'), style={'width': 'auto', 'height': '140px', 'marginBottom': '20px'}),
                        xs=12, sm=12, md=4, lg=4, xl=4,
                        className="mb-3 d-flex justify-content-center"
),

                dbc.Col(
                    [
                        html.H2('Optimierung des Schienen Datenmanagements', style={'fontWeight': 'bold', 'fontSize': '1.25em'}),
                        html.P("Funktionsfähiger Prototyp einer Datenbank für die zentrale Bündelung von Infrastruktur-Bestandsdaten", style={'fontSize': '0.9em'}),
                        html.P("Zielstellung:", style={'fontWeight': 'bold', 'marginTop': '20px'}),
                        html.Ul([
                            html.Li("SSOT: Verbesserte Qualitätskontrolle und konsistente Informationen", style={'fontSize': '0.9em'}),
                            html.Li("Reduzierter Zeitaufwand für Datenabfrage und -verarbeitung", style={'fontSize': '0.9em'}),
                            html.Li("Transparenz über vorhandene Daten", style={'fontSize': '0.9em'})
                        ]),
                        html.P("Verknüpfung diverser Datenquellen in zentraler Datenbank", style={'fontSize': '0.9em'})
                    ],
                    xs=12, sm=12, md=4, lg=4, xl=4,
                    className="mb-3"
                ),
                dbc.Col(
                    
                    [
                        html.H2('Datenquellen', style={'fontWeight': 'bold', 'fontSize': '1.25em'}),
                        html.Img(src=app.get_asset_url('infrago_logo.png'), style={'width': '20%', 'marginBottom': '15px'}),
                        html.Img(src=app.get_asset_url('mobilithek_logo.png'), style={'width': '20%', 'marginBottom': '15px'}),
                        html.Img(src=app.get_asset_url('EBA-Logo.png'), style={'width': '20%', 'marginBottom': '15px'}),
                        html.Img(src=app.get_asset_url('openstreetmap_logo.png'), style={'width': '20%', 'marginBottom': '15px'}),
                        html.Img(src=app.get_asset_url('umweltbundesamt_logo.png'), style={'width': '20%', 'marginBottom': '15px'})
                    ],
                    xs=12, sm=12, md=4, lg=4, xl=4,
                    className="mb-3 d-flex flex-column align-items-center"
                )
            ],
            justify="around"
        )
    ],
    fluid=True,
    className="footer mt-5",
    style={'backgroundColor': '#f8f9fa', 'padding': '40px 20px', 'borderTop': '1px solid #dee2e6'}
)


# Navbar
navbar = dbc.NavbarSimple(
    brand="Startseite",
    brand_href="/",
    color="light",  # Setzt die Navbar auf eine helle (weiße) Farbe
    dark=False,  # Stellt sicher, dass die Textfarbe nicht automatisch auf weiß gesetzt wird
    className="mt-4",  # Fügt Abstand oben hinzu
    style={'backgroundColor': 'white'},  # Stellt sicher, dass die Navbar weiß ist
    brand_style={'color': '#003366'}  # Dunkelblaue Schriftfarbe für "Demo Anwendung"
)





# Layout
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        navbar,
        dbc.Row(
            [
                dbc.Col(id='page-content', width=12)
            ]
        ),
        footer
    ],
    fluid=True,
)


# Update page content based on URL
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        heading = create_styled_heading('Zentrale Datenbank für Infrastruktur-Bestandsdaten', include_search=True)
        cards = [
            create_card(str(index + 1), title)
            for index, title in enumerate(page_descriptions)
        ]
        return [heading] + [dbc.Row(cards, justify="start")]
    else:
        # Decode the URL component back to the title
        title = urllib.parse.unquote(pathname[1:])
        if title == 'Analyse Infrastruktur-Bestandsdaten':
            page_description = page_descriptions[title]
            page_content = html.P(page_description, className="mb-5")
            heading = create_styled_heading(title, include_search=False, include_extra_text=(title == "Personenbahnhöfe"))
            return [
                heading, page_content,        
                html.Div('Strecken-Informationen', style={'color': '#003366', 'textAlign': 'center', 'marginBottom': '20px', 'fontSize': '24px'}),
                # Eingabefeld für STR_NR-Filter
                html.Div([
                    html.Label('Filtern Sie die STR_NR:'),
                    dcc.Input(
                        id='STR_NR-filter',
                        type='text',
                        placeholder='Geben Sie STR_NR ein',
                        value = '4010'
                    )
                ], style={'marginBottom': '40px'}),

                # Tabelle für df_GSL
                DataTable(
                    id='table-df_GSL',
                    columns=[{'name': i, 'id': i} for i in df_GSL.columns],
                    data=df_GSL.head(1).to_dict('records'),
                    style_table={'overflowX': 'auto', 'height': '90px', 'marginTop': '40px'},  # Festlegen der Höhe mit Scrollbar
                    style_data_conditional=[{'if': {'column_id': 'STR_NR'}, 'marginTop': '10px'}]  # Anpassen des Abstands des Sliders
                ),
                html.Div('Informationen zu Anlagen auf ausgewählter Strecke', style={'color': '#003366', 'textAlign': 'center', 'marginTop': '60px', 'marginBottom': '20px', 'fontSize': '24px'}),
                html.Div(children='Bitte wählen Sie einen Anlagentyp:'),
                
                # RadioItems für Datensatz-Auswahl
                dcc.RadioItems(
                    id='dataset-radio',
                    options=[
                        {'label': 'Weichen', 'value': 'df_weichen'},
                        {'label': 'Brücken', 'value': 'df_br'},
                        {'label': 'Tunnel', 'value': 'df_tunnel'},
                        {'label': 'Stützbauwerke', 'value': 'df_stuetzbauwerke'},
                        {'label': 'Schallschutzwände', 'value': 'df_schallschutzwande'},
                        {'label': 'Bahnübergänge', 'value': 'df_bahnubergange'}
                    ],
                    value='df_weichen',
                    labelStyle={'display': 'inline-block', 'margin-right': '15px'}
                ),
                
                # Tabelle für Datenausgabe
                DataTable(
                    id='table-content',
                    filter_action='native',
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Anpassen des Abstands
                    page_size=8,  # Anzeigen der obersten 8 Einträge pro Seite
                    page_action='native'  # Benutzerdefinierte Seitennavigation
                ),
                dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'} ),
                html.P([html.Strong("Zukünftige Features/Datenpunkte:")]),
                html.Ul([
                html.Li("Kennzahlen"),
                html.Li("Datendownload und -export"),
                html.Li("Automatisches Summieren"),
                html.Li("Speichern von Reports"),
                html.Li("Erweiterte geographische Visualisierung"),
                html.Li("Informationen zu weiteren Anlagen"),
        ])
                
            ]
        if title == 'HLK-Generalsanierung':
            page_description = page_descriptions[title]
            page_content = html.P(page_description, className="mb-5")
            heading = create_styled_heading(title, include_search=False, include_extra_text=(title == "Personenbahnhöfe"))
            return [
                heading, page_content,
                html.Div('Strecken-Informationen', style={'color': '#003366', 'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '24px'}),
                # Eingabefeld für HLK_STR_NR-Filter
                html.Div([
                    html.Label('Wählen Sie einen Hochleistungskorridor (HLK) aus:'),
                dcc.Dropdown(
                    id='HLK_STR_NR-filter',
                    options=[
                        {'label': str(num), 'value': str(num)} for num in hlk_timetable["HLK Name"].unique()
                    ],
                    placeholder='Wählen Sie einen HLK aus',
                    value='Frankfurt - Mannheim',  # Standardwert
                    clearable=True,  # Option zum Löschen der Auswahl
                )
                ], style={'marginBottom': '40px'}),

                # Tabelle für df_GSL
                DataTable(
                    id='table-df_GSL_HLK',
                    columns=[{'name': i, 'id': i} for i in df_GSL.columns],
                    data=df_GSL.head(1).to_dict('records'),
                    style_table={'overflowX': 'auto', 'marginTop': '40px'},  # Festlegen der Höhe mit Scrollbar
                    style_data_conditional=[{'if': {'column_id': 'STR_NR'}, 'marginTop': '10px'}]  # Anpassen des Abstands des Sliders
                ),
                html.Div('Informationen zu Anlagen auf ausgewählter Strecke', style={'color': '#003366', 'textAlign': 'center', 'marginTop': '40px', 'marginBottom': '20px', 'fontSize': '24px'}),
                html.Div(children='Bitte wählen Sie einen Anlagentyp:', style={'padding': '10px'}),
                
                # RadioItems für Datensatz-Auswahl
                dcc.RadioItems(
                    id='dataset-radio_HLK',
                    options=[
                        {'label': 'Weichen', 'value': 'df_weichen'},
                        {'label': 'Brücken', 'value': 'df_br'},
                        {'label': 'Tunnel', 'value': 'df_tunnel'},
                        {'label': 'Stützbauwerke', 'value': 'df_stuetzbauwerke'},
                        {'label': 'Schallschutzwände', 'value': 'df_schallschutzwande'},
                        {'label': 'Bahnübergänge', 'value': 'df_bahnubergange'}
                    ],
                    value='df_weichen',
                    labelStyle={'display': 'inline-block', 'margin-right': '15px'}
                ),
                
                # Tabelle für Datenausgabe
                DataTable(
                    id='table-content_HLK',
                    filter_action='native',
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Anpassen des Abstands
                    page_size=8,  # Anzeigen der obersten 8 Einträge pro Seite
                    page_action='native'  # Benutzerdefinierte Seitennavigation
                ),
                dcc.Graph(id='graph-content_HLK', style={'height': '80vh', 'width': '100%'} )
            ]
        if title == 'Geo-Visualisierung':
            page_description = page_descriptions[title]
            page_content = html.P(page_description, className="mb-5")
            heading = create_styled_heading(title, include_search=False, include_extra_text=(title == "Personenbahnhöfe"))
            return [
                heading, page_content,
                html.Div('Strecken-Informationen', style={'color': '#003366', 'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '24px'}),
                # Eingabefeld für STR_NR-Filter
                html.Div([
                    html.Label('Filtern Sie die STR_NR:'),
                    dcc.Input(
                        id='STR_NR-filter',
                        type='text',
                        placeholder='Geben Sie STR_NR ein',
                        value = '4010'
                    )
                ], style={'marginBottom': '40px'}),

                # RadioItems für Datensatz-Auswahl
                
                dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'} ),

                dcc.RadioItems(
                    id='dataset-radio',
                    options=[
                        {'label': 'Weichen', 'value': 'df_weichen'},
                        {'label': 'Brücken', 'value': 'df_br'},
                        {'label': 'Tunnel', 'value': 'df_tunnel'},
                        {'label': 'Stützbauwerke', 'value': 'df_stuetzbauwerke'},
                        {'label': 'Schallschutzwände', 'value': 'df_schallschutzwande'},
                        {'label': 'Bahnübergänge', 'value': 'df_bahnubergange'}
                    ],
                    value='df_weichen',
                    labelStyle={'display': 'inline-block', 'margin-right': '15px'}
                ),
                
                # Tabelle für Datenausgabe
                DataTable(
                    id='table-content',
                    filter_action='native',
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Anpassen des Abstands
                    page_size=8,  # Anzeigen der obersten 8 Einträge pro Seite
                    page_action='native'  # Benutzerdefinierte Seitennavigation
                ),
                html.P([html.Strong("Zukünftige Datenpunkte:")]),
                html.Ul([
                    html.Li("Gleise"),
                    html.Li("Weichen"),
                    html.Li("Energie"),
                    html.Li("Personenbahnhöfe")
                ])
                

            ]
        if title == 'Personenbahnhöfe':
            page_description = page_descriptions[title]
            page_content = html.P(page_description, className="mb-5")
            heading = create_styled_heading(title, include_search=False, include_extra_text=(title == "Personenbahnhöfe"))
            return [
                heading, page_content,
                dcc.Link('zurück zur Startseite', href='/', style={'color': '#003366'}),
                html.Div('Weitere Darstellungen in Arbeit', style={'color': '#003366', 'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '24px', 'marginTop': '100px'}),
            ]
        else:
            return html.Div([
                html.H1(title, style={'color': '#003366'}),
                dcc.Link('zurück zur Startseite', href='/', style={'color': '#003366'})
            ])


# Callback für die Aktualisierung der Tabelle basierend auf dem RadioItems-Wert und dem ausgewählten Datensatz
@app.callback(
    Output('table-content', 'columns'), 
    Output('table-content', 'data'),
    Output('graph-content', 'figure'),
    [Input('dataset-radio', 'value'),
     Input('STR_NR-filter', 'value')
     ]
   
)

def update_table(selected_dataset, STR_NR_filter):
    df = None
    if selected_dataset == 'df_weichen':
        df = df_weichen
    elif selected_dataset == 'df_br':
        df = df_br
    elif selected_dataset == 'df_tunnel':
        df = df_tunnel
    elif selected_dataset == 'df_stuetzbauwerke':
        df = df_stuetzbauwerke
    elif selected_dataset == 'df_schallschutzwande':
        df = df_schallschutzwande
    elif selected_dataset == 'df_bahnubergange':
        df = df_bahnubergange

    if STR_NR_filter:
        df = df[df['STR_NR'].astype(str).str.contains(STR_NR_filter)]

    columns = [{'name': i, 'id': i} for i in df.columns] if df is not None else []
    data = df.to_dict('records') if df is not None else []

    df_bu_new = df_bu[df_bu['STR_NR']==int(STR_NR_filter)]
    df_br_new = df_br[df_br['STR_NR']==int(STR_NR_filter)]
    df_tu_new = df_tu_geo[df_tu_geo['STR_NR']==int(STR_NR_filter)]

     # Für Bahnübergänge (df_bu)
    ### NEW# OLD hover_text_bu = df_bu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BAUFORM: {row['BAUFORM']}<br>UEB_WACH_ART: {row['UEB_WACH_ART']}<br>ZUGGEST: {row['ZUGGEST']}", axis=1)
    hover_text_bu = df_bu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>BAUFORM: {row['BAUFORM']}", axis=1)
    
    # Für Brücken (df_br)
    # OLD hover hover_text_br = df_br_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BR_BEZ: {row['BR_BEZ']}<br>BAUART: {row['BAUART']}<br>ZUST_KAT: {row['ZUST_KAT']}", axis=1)
    hover_text_br = df_br_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>BAUART: {row['BAUART']}<br>ZUST_KAT: {row['ZUST_KAT']}", axis=1)

    # Für Tunnel (df_tu)
    # OLD hover hover_text_tu = df_tu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)
    hover_text_tu = df_tu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>LAENGE: {row['LAENGE']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)


    fig = go.Figure()
    

    # Datainklusion 1

    fig.add_trace(go.Scattermapbox(
        lat=df_bu_new['breite'],
        lon=df_bu_new['länge'],
        mode='markers',
        marker=dict(size=7, color='#68DAFF'),
        hoverinfo='text',
        hovertext=hover_text_bu,
        name='Bahnübergänge',
        showlegend=True,
    ))
    
    # Datainklusion 2

    fig.add_trace(go.Scattermapbox(
        lat=df_br_new['GEOGR_BREITE'],
        lon=df_br_new['GEOGR_LAENGE'],
        mode='markers',
        marker=dict(size=7, color='#006587'),
        hoverinfo='text',
        hovertext=hover_text_br,
        name='Brücken',
        showlegend=True,
    ))

    # Datainklusion 3 

    lons = []
    lats = []
    hover_texts = []
    # COPY for later 
    for index, row in df_tu_new.iterrows():
        x, y = row['geometry'].xy
        lons.extend(x.tolist() + [None])  # Add None at the end of each line string
        lats.extend(y.tolist() + [None])  # Add None at the end of each line string
        # Add hover text for each segment
        hover_texts.extend(hover_text_tu)
            
            #[f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}"] * len(x))

    # Add a single trace for all tunnel line segments
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=lons,
        lat=lats,
        hovertext=hover_texts,
        hoverinfo="text",
        line=dict(color='#5496B8', width=7),
        name='Tunnel',  
        showlegend=True,
    ))
    # COPY for later 
    # Convert numpy arrays to pandas Series
    lats_series = pd.Series(lats)
    lons_series = pd.Series(lons)
    
    # Now, concatenate using pandas Series
    all_latitudes = pd.concat([lats_series, df_bu_new['breite'], df_br_new['GEOGR_BREITE']])
    all_longitudes = pd.concat([lons_series, df_bu_new['länge'], df_br_new['GEOGR_LAENGE']])
    
    # Calculate the mean of the latitudes and longitudes
    lat1 = np.mean(all_latitudes)
    lon1 = np.mean(all_longitudes)
    
    # Continue with updating the layout and showing the figure as before
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center={"lat": lat1, "lon": lon1},
            zoom=5.5,
            style='outdoors'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        title="Geoplot der DB Bahnübergänge, Brücken und Tunnel",
        title_font=dict(color='#003366', size=24),
        title_x=0.5,
        margin=dict(b=40),
    )

    
  # COPY for later 


    fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        center={"lat": lat1, "lon": lon1},
        zoom=9.0,
        style='outdoors'
    ),
    legend=dict(
        font=dict(
            size=20  
        )
    ),

    
    #Slider für Zoom
    
    sliders=[dict(
        active=4,
        currentvalue={
            "prefix": "Zoom: ",
            "visible": False,
            "xanchor": "right",
            "font": {
                "size": 20,
                "color": "black"
            }
        },
        pad={"t": 50},
        steps=[
            dict(method='relayout', args=['mapbox.zoom', 2], label = "Rauszoomen"),
            dict(method='relayout', args=['mapbox.zoom', 3], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 4], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 5], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 6], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 7], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 8], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 9], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 10], label = "Reinzoomen"),
        ],
        x=0.05,
        xanchor="left",
        len=0.9,
        y=-0.035,
        yanchor="bottom",
        bgcolor="#006587",  # Slider background color
        activebgcolor="#AAD228",  # Slider background color when active
        tickwidth=7,
        ticklen = 0,
        bordercolor="white",  # Slider border color
        borderwidth=2,  # Slider border width
        font=dict(size=15, color="#006587"),

    )],
    
   # Title-Bezeichnung
    
    showlegend=True,
    title_text="Geoplot der DB Bahnübergänge, Brücken und Tunnel",
    title_font=dict(size=24, color="#003366"),
    title_pad=dict(t=20, b=20),
    
    # Dropdown für Map-Ansicht
    updatemenus=[dict(
        buttons=[
            dict(args=[{"mapbox.style": "outdoors"}],
                 label="Outdoors",
                 method="relayout"),
            dict(args=[{"mapbox.style": "satellite"}],
                 label="Satellite",
                 method="relayout"),
            dict(args=[{"mapbox.style": "light"}],
                 label="Hell",
                 method="relayout"),
            dict(args=[{"mapbox.style": "dark"}],
                 label="Dunkel",
                 method="relayout"),
            dict(args=[{"mapbox.style": "streets"}],
                 label="Straße",
                 method="relayout"),
            dict(args=[{"mapbox.style": "satellite-streets"}],
                 label="Satellite mit Straßen",
                 method="relayout"),
        ],
        direction="down",
        pad={"r": 10, "t": 10},
        showactive=True,
        x=1,
        xanchor="right",
        y=1.1,
        yanchor="top",
        bgcolor="#001C4F",
        font=dict(size=15, color="white")  
    )]
)

# COPY

    return columns, data, fig

# Callback für die Aktualisierung der df_GSL-Tabelle basierend auf dem STR_NR-Filter
@app.callback(
    Output('table-df_GSL', 'data'),
    [Input('STR_NR-filter', 'value')]
)
def update_table_df_GSL(STR_NR_filter):
    if STR_NR_filter:
        filtered_df_GSL = df_GSL[df_GSL['STR_NR'].astype(str).str.contains(STR_NR_filter)].head(1)
    else:
        filtered_df_GSL = df_GSL.head(1)
    data = filtered_df_GSL.to_dict('records')
    return data



### HLK

@app.callback(
    Output('table-df_GSL_HLK', 'data'),
    [Input('HLK_STR_NR-filter', 'value')]
)

def update_table_df_GSL_HLK(HLK_STR_NR_filter):

    ls_streckennummern = hlk_dict[HLK_STR_NR_filter]

    if HLK_STR_NR_filter:
        filtered_df_GSL = df_GSL[df_GSL['STR_NR'].isin(ls_streckennummern)]
        #df_GSL.head(5) #df_GSL[df_GSL['STR_NR'].astype(str).str.contains(STR_NR_filter)].head(1)
    else:
        filtered_df_GSL = df_GSL.head(1)
    data = filtered_df_GSL.to_dict('records')
    return data




def test_apply(x):
    try:
        return float(x)
    except ValueError:
        return str(x)


@app.callback(
    Output('table-content_HLK', 'columns'), 
    Output('table-content_HLK', 'data'),
    Output('graph-content_HLK', 'figure'),
    [Input('dataset-radio_HLK', 'value'),
     Input('HLK_STR_NR-filter', 'value')
     ]
   
)

def update_table(selected_dataset, HLK_STR_NR_filter):
    df = None
    if selected_dataset == 'df_weichen':
        df = df_weichen
        df['STR_NR'] =  df['STR_NR'].apply(test_apply)
    elif selected_dataset == 'df_br':
        df = df_br
    elif selected_dataset == 'df_tunnel':
        df = df_tunnel
    elif selected_dataset == 'df_stuetzbauwerke':
        df = df_stuetzbauwerke
    elif selected_dataset == 'df_schallschutzwande':
        df = df_schallschutzwande
    elif selected_dataset == 'df_bahnubergange':
        df = df_bahnubergange

    ls_streckennummern = hlk_dict[HLK_STR_NR_filter]


    if HLK_STR_NR_filter:
        df = df[df['STR_NR'].isin(ls_streckennummern)]

    columns = [{'name': i, 'id': i} for i in df.columns] if df is not None else []
    data = df.to_dict('records') if df is not None else []

    df_bu_new = df_bu[df_bu['STR_NR'].isin(ls_streckennummern)]
    df_br_new = df_br[df_br['STR_NR'].isin(ls_streckennummern)]
    df_tu_new = df_tu_geo[df_tu_geo['STR_NR'].isin(ls_streckennummern)]

     # Für Bahnübergänge (df_bu)
    ### NEW# OLD hover_text_bu = df_bu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BAUFORM: {row['BAUFORM']}<br>UEB_WACH_ART: {row['UEB_WACH_ART']}<br>ZUGGEST: {row['ZUGGEST']}", axis=1)
    hover_text_bu = df_bu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>BAUFORM: {row['BAUFORM']}", axis=1)
    
    # Für Brücken (df_br)
    # OLD hover hover_text_br = df_br_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BR_BEZ: {row['BR_BEZ']}<br>BAUART: {row['BAUART']}<br>ZUST_KAT: {row['ZUST_KAT']}", axis=1)
    hover_text_br = df_br_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>BAUART: {row['BAUART']}<br>ZUST_KAT: {row['ZUST_KAT']}", axis=1)

    # Für Tunnel (df_tu)
    # OLD hover hover_text_tu = df_tu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)
    hover_text_tu = df_tu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>LAENGE: {row['LAENGE']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)


    fig = go.Figure()
    

    # Datainklusion 1

    fig.add_trace(go.Scattermapbox(
        lat=df_bu_new['breite'],
        lon=df_bu_new['länge'],
        mode='markers',
        marker=dict(size=7, color='#68DAFF'),
        hoverinfo='text',
        hovertext=hover_text_bu,
        name='Bahnübergänge',
        showlegend=True,
    ))
    
    # Datainklusion 2

    fig.add_trace(go.Scattermapbox(
        lat=df_br_new['GEOGR_BREITE'],
        lon=df_br_new['GEOGR_LAENGE'],
        mode='markers',
        marker=dict(size=7, color='#006587'),
        hoverinfo='text',
        hovertext=hover_text_br,
        name='Brücken',
        showlegend=True,
    ))

    # Datainklusion 3 

    lons = []
    lats = []
    hover_texts = []
    # COPY for later 
    for index, row in df_tu_new.iterrows():
        x, y = row['geometry'].xy
        lons.extend(x.tolist() + [None])  # Add None at the end of each line string
        lats.extend(y.tolist() + [None])  # Add None at the end of each line string
        # Add hover text for each segment
        hover_texts.extend(hover_text_tu)
            
            #[f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}"] * len(x))

    # Add a single trace for all tunnel line segments
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=lons,
        lat=lats,
        hovertext=hover_texts,
        hoverinfo="text",
        line=dict(color='#5496B8', width=7),
        name='Tunnel',  
        showlegend=True,
    ))
    # COPY for later 
    # Convert numpy arrays to pandas Series
    lats_series = pd.Series(lats)
    lons_series = pd.Series(lons)
    
    # Now, concatenate using pandas Series
    all_latitudes = pd.concat([lats_series, df_bu_new['breite'], df_br_new['GEOGR_BREITE']])
    all_longitudes = pd.concat([lons_series, df_bu_new['länge'], df_br_new['GEOGR_LAENGE']])
    
    # Calculate the mean of the latitudes and longitudes
    lat1 = np.mean(all_latitudes)
    lon1 = np.mean(all_longitudes)
    
    # Continue with updating the layout and showing the figure as before
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center={"lat": lat1, "lon": lon1},
            zoom=5.5,
            style='outdoors'
        ),
        showlegend=True,
        title="Geoplot der DB Bahnübergänge, Brücken und Tunnel",
        title_font=dict(color='#003366', size=24),
        title_x=0.5,
        margin=dict(b=40),
    )

    
  # COPY for later 


    fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        center={"lat": lat1, "lon": lon1},
        zoom=9.0,
        style='outdoors'
    ),
    legend=dict(
        font=dict(
            size=20  
        )
    ),

    
    #Slider für Zoom
    
    sliders=[dict(
        active=4,
        currentvalue={
            "prefix": "Zoom: ",
            "visible": False,
            "xanchor": "right",
            "font": {
                "size": 20,
                "color": "black"
            }
        },
        pad={"t": 50},
        steps=[
            dict(method='relayout', args=['mapbox.zoom', 2], label = "Rauszoomen"),
            dict(method='relayout', args=['mapbox.zoom', 3], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 4], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 5], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 6], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 7], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 8], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 9], label = ""),
            dict(method='relayout', args=['mapbox.zoom', 10], label = "Reinzoomen"),
        ],
        x=0.05,
        xanchor="left",
        len=0.9,
        y=-0.035,
        yanchor="bottom",
        bgcolor="#006587",  # Slider background color
        activebgcolor="#AAD228",  # Slider background color when active
        tickwidth=7,
        ticklen = 0,
        bordercolor="white",  # Slider border color
        borderwidth=2,  # Slider border width
        font=dict(size=15, color="#006587"),

    )],
    
   # Title-Bezeichnung
    
    showlegend=True,
    title_text="Geoplot der DB Bahnübergänge, Brücken und Tunnel",
    title_font=dict(size=24, color="#003366"),
    title_pad=dict(t=20, b=20),
    
    # Dropdown für Map-Ansicht
    updatemenus=[dict(
        buttons=[
            dict(args=[{"mapbox.style": "outdoors"}],
                 label="Outdoors",
                 method="relayout"),
            dict(args=[{"mapbox.style": "satellite"}],
                 label="Satellite",
                 method="relayout"),
            dict(args=[{"mapbox.style": "light"}],
                 label="Hell",
                 method="relayout"),
            dict(args=[{"mapbox.style": "dark"}],
                 label="Dunkel",
                 method="relayout"),
            dict(args=[{"mapbox.style": "streets"}],
                 label="Straße",
                 method="relayout"),
            dict(args=[{"mapbox.style": "satellite-streets"}],
                 label="Satellite mit Straßen",
                 method="relayout"),
        ],
        direction="down",
        pad={"r": 10, "t": 10},
        showactive=True,
        x=1,
        xanchor="right",
        y=1.1,
        yanchor="top",
        bgcolor="#001C4F",
        font=dict(size=15, color="white")  
    )]
)

# COPY

    return columns, data, fig







# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
