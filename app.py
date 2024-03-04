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
test_dict = dict(zip(hlk_timetable["HLK Name"], hlk_timetable["Streckennummern_Liste"]))



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



# Seitenbeschreibungen
page_descriptions = {
    'HLK-Auswertung': 'Mit der HLK-Auswertung haben sie Überblick über 40 HLK Generalsanierungen. Diese können mit einem Dropdown Menü ausgewählt und ausgewertet werden. So stehen Ihnen Informationen zu den Anlagen und Strecken zu Verfügung, welche geographisch visualisiert werden.',
    'Inspektor Infrastruktur-Bestandsdaten': 'Mit dem Inspektor Infrastruktur-Bestandsdaten können Sie sich Details zu Strecken und Anlagen sowohl tabellarisch als auch geographisch anzeigen lassen.',
    'Geo-Visualisierung': 'Die Geo-Visualisierung ermöglicht die geographische Visualisierung von Anlagen.',
    'Personenbahnhöfe': 'Hier erhalten Sie Informationen über Personenbahnhöfe und deren Eigenschaften. Zu diesen zählen Bahnsteiglänge und Barrierefreiheit sowie Informationen zu Zukunftsbahnhöfen.'
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
        if title == 'Inspektor Infrastruktur-Bestandsdaten':
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

                # Tabelle für df_GSL
                DataTable(
                    id='table-df_GSL',
                    columns=[{'name': i, 'id': i} for i in df_GSL.columns],
                    data=df_GSL.head(1).to_dict('records'),
                    style_table={'overflowX': 'auto', 'height': '90px', 'marginTop': '40px'},  # Festlegen der Höhe mit Scrollbar
                    style_data_conditional=[{'if': {'column_id': 'STR_NR'}, 'marginTop': '10px'}]  # Anpassen des Abstands des Sliders
                ),
                html.Div('Informationen zu Anlagen auf ausgewählter Strecke', style={'color': '#003366', 'textAlign': 'center', 'marginTop': '40px', 'marginBottom': '20px', 'fontSize': '24px'}),
                html.Div(children='Bitte wählen Sie einen Anlagentyp:', style={'padding': '10px'}),
                
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
                    labelStyle={'display': 'block'}
                ),
                
                # Tabelle für Datenausgabe
                DataTable(
                    id='table-content',
                    filter_action='native',
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Anpassen des Abstands
                    page_size=8,  # Anzeigen der obersten 8 Einträge pro Seite
                    page_action='native'  # Benutzerdefinierte Seitennavigation
                ),
                dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'} )
            ]
        if title == 'HLK-Auswertung':
            page_description = page_descriptions[title]
            page_content = html.P(page_description, className="mb-5")
            heading = create_styled_heading(title, include_search=False, include_extra_text=(title == "Personenbahnhöfe"))
            return [
                heading, page_content,
                html.Div('Strecken-Informationen', style={'color': '#003366', 'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '24px'}),
                # Eingabefeld für STR_NR-Filter
                html.Div([
                    html.Label('Wählen Sie einen Hochleistungskorridor (HLK) aus:'),
                dcc.Dropdown(
                    id='STR_NR-filter',
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
                    id='table-df_GSL',
                    columns=[{'name': i, 'id': i} for i in df_GSL.columns],
                    data=df_GSL.head(1).to_dict('records'),
                    style_table={'overflowX': 'auto', 'height': '90px', 'marginTop': '40px'},  # Festlegen der Höhe mit Scrollbar
                    style_data_conditional=[{'if': {'column_id': 'STR_NR'}, 'marginTop': '10px'}]  # Anpassen des Abstands des Sliders
                ),
                html.Div('Informationen zu Anlagen auf ausgewählter Strecke', style={'color': '#003366', 'textAlign': 'center', 'marginTop': '40px', 'marginBottom': '20px', 'fontSize': '24px'}),
                html.Div(children='Bitte wählen Sie einen Anlagentyp:', style={'padding': '10px'}),
                
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
                    labelStyle={'display': 'block'}
                ),
                
                # Tabelle für Datenausgabe
                DataTable(
                    id='table-content',
                    filter_action='native',
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Anpassen des Abstands
                    page_size=8,  # Anzeigen der obersten 8 Einträge pro Seite
                    page_action='native'  # Benutzerdefinierte Seitennavigation
                ),
                dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'} )
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
                    labelStyle={'display': 'block'}
                ),
                
                # Tabelle für Datenausgabe
                DataTable(
                    id='table-content',
                    filter_action='native',
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Anpassen des Abstands
                    page_size=8,  # Anzeigen der obersten 8 Einträge pro Seite
                    page_action='native'  # Benutzerdefinierte Seitennavigation
                ),
                dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'} )
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
    hover_text_bu = df_bu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BAUFORM: {row['BAUFORM']}<br>UEB_WACH_ART: {row['UEB_WACH_ART']}<br>ZUGGEST: {row['ZUGGEST']}", axis=1)

    # Für Brücken (df_br)
    hover_text_br = df_br_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BR_BEZ: {row['BR_BEZ']}<br>BAUART: {row['BAUART']}<br>ZUST_KAT: {row['ZUST_KAT']}", axis=1)

    # Für Tunnel (df_tu)
    #hover_text_tu = df_tu_new.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)



    fig = go.Figure()
    

    # Datainklusion 1

    fig.add_trace(go.Scattermapbox(
        lat=df_bu_new['breite'],
        lon=df_bu_new['länge'],
        mode='markers',
        marker=dict(size=5, color='#AAD228'),
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
        marker=dict(size=5, color='#006587'),
        hoverinfo='text',
        hovertext=hover_text_br,
        name='Brücken',
        showlegend=True,
    ))

    # Datainklusion 3 

    lons = []
    lats = []
    hover_texts = []

    for index, row in df_tu_new.iterrows():
        x, y = row['geometry'].xy
        lons.extend(x.tolist() + [None])  # Add None at the end of each line string
        lats.extend(y.tolist() + [None])  # Add None at the end of each line string
        # Add hover text for each segment
        hover_texts.extend([f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}"] * len(x))
        # No need to add None again at the end since it's already added with coordinates

    # Add a single trace for all tunnel line segments
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=lons,
        lat=lats,
        hovertext=hover_texts,
        hoverinfo="text",
        line=dict(color='#969696', width=5),
        name='Tunnel',  # Give a name to this trace for the legend,
        showlegend=True,
    ))



    # Continue with updating the layout and showing the figure as before
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center={"lat": 51.1657, "lon": 10.4515},
            zoom=5.5,
            style='outdoors'
        ),
        showlegend=True,
        title={
            'text': "Geoplot der DB Bahnübergänge, Brücken und Tunnel",
            'font': {'color': '#003366', 'size': 24},
            'x': 0.5, # Mittig ausrichten
            'xanchor': 'center', # Ankerpunkt für x-Achse
            'y': 0.95, # 5% vom oberen Rand der Grafik
            'yanchor': 'top', # Ankerpunkt für y-Achse
        }
    )


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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
