import dash
from dash import html, dcc, callback, Output, Input 
import dash_core_components as dcc
import dash_html_components as html
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

# Initialize the Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Beispiel-Datensätze einlesen
df_weichen = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2105-V_Stueckliste_Weichen.xlsx')
df_bruecken = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2106-V_Stueckliste_Bruecken.xlsx')
df_tunnel = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2108-V_Stueckliste_Tunnel.xlsx')
df_stuetzbauwerke = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2110-V_Stueckliste_Stuetzbauwerke_Bauwerksklasse(BWK)3.xlsx')
df_schallschutzwande = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2111-V_Stueckliste_Schallschutzwaende.xlsx')
df_bahnubergange = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2112-V_Stueckliste_Bahnuebergaenge.xlsx')
df_GSL = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/2022_2101-V_Gesamtstreckenliste(GSL).xlsx')
df_ETCS = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/ETCS_heute_und_geplant.xlsx')
df_Traffic = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/StrNr_Average_Anual_Traffic_Flow.xlsx')
df_HLK_Zeitraum = pd.read_excel('C:/Users/viktor.schumann/OneDrive - goetzpartners/Desktop/Python/data/StrNr_HLK_Zeitraum.xlsx')

# Pfad zu den Excel-Dateien
file_path_bu = r'C:\Users\viktor.schumann\OneDrive - goetzpartners\Desktop\Python\data\20240229_Matching_2112-V_Stueckliste_Bahnuebergaenge_vClean.xlsx'
file_path_br = r'C:\Users\viktor.schumann\OneDrive - goetzpartners\Desktop\Python\data\20240229_Matching_Brücken_vClean.xlsx'
file_path_tu = r'C:\Users\viktor.schumann\OneDrive - goetzpartners\Desktop\Python\data\20240229_Matching_Tunnel_vClean.xlsx'


df_bu = pd.read_excel(file_path_bu)
df_br = pd.read_excel(file_path_br)
df_tu = pd.read_excel(file_path_tu)

df_bu_dropdown = pd.read_excel(file_path_bu)


df_bu = df_bu[df_bu['STR_NR']==4010]
df_br = df_br[df_br['STR_NR']==4010]
df_tu = df_tu[df_tu['STR_NR']==4010]

pio.renderers.default = 'browser'

# Mapbox Access Token setzen (ersetzen Sie dies durch Ihr tatsächliches Mapbox Access Token)
mapbox_access_token = 'pk.eyJ1IjoiYW5ka29jaDkzIiwiYSI6ImNsMTZiNnU4dTE5MzQzY3MwZnV1NjVqOGoifQ.ZxCDeRkr59lifDEm4PIWQA'



# Erstellen der Figur
fig = go.Figure()

# Für Bahnübergänge (df_bu)
hover_text_bu = df_bu.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>LAGE_KM: {row['LAGE_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BAUFORM: {row['BAUFORM']}<br>UEB_WACH_ART: {row['UEB_WACH_ART']}<br>ZUGGEST: {row['ZUGGEST']}", axis=1)

# Für Brücken (df_br)
hover_text_br = df_br.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>BR_BEZ: {row['BR_BEZ']}<br>BAUART: {row['BAUART']}<br>ZUST_KAT: {row['ZUST_KAT']}", axis=1)

# Für Tunnel (df_tu)
hover_text_tu = df_tu.apply(lambda row: f"REGION: {row['REGION']}<br>NETZ: {row['NETZ']}<br>STR_NR: {row['STR_NR']}<br>VON_KM: {row['VON_KM']}<br>BIS_KM: {row['BIS_KM']}<br>RIKZ: {row['RIKZ']}<br>RIL_100: {row['RIL_100']}<br>LAENGE: {row['LAENGE']}<br>ANZ_STR_GL: {row['ANZ_STR_GL']}<br>QUERSCHN: {row['QUERSCHN']}<br>BAUWEISE: {row['BAUWEISE']}", axis=1)

# GeoDataFrame
df_tu = df_tu[df_tu['geometry'].notna()]
df_tu['geometry'] = df_tu['geometry'].apply(wkt.loads)
df_tu_geo = gpd.GeoDataFrame(df_tu, geometry='geometry')



# Datainklusion 1
fig.add_trace(go.Scattermapbox(
    lat=df_bu['breite'],
    lon=df_bu['länge'],
    mode='markers',
    marker=dict(size=5, color='#AAD228'),
    hoverinfo='text',
    hovertext=hover_text_bu,
    name='Bahnübergänge'
))

# Datainklusion 2

fig.add_trace(go.Scattermapbox(
    lat=df_br['GEOGR_BREITE'],
    lon=df_br['GEOGR_LAENGE'],
    mode='markers',
    marker=dict(size=5, color='#006587'),
    hoverinfo='text',
    hovertext=hover_text_br,
    name='Brücken'
))

# Datainklusion 3 

lons = []
lats = []
hover_texts = []

for index, row in df_tu_geo.iterrows():
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
    name='Tunnel'  # Give a name to this trace for the legend
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
    title="Geoplot der DB Bahnübergänge, Brücken und Tunnel"
)

# Ende Plot



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

# Function to create cards with enhanced shadows
def create_card(number, title):
    # Convert title to URL-safe format
    title_url = urllib.parse.quote(title)
    return dcc.Link(
        html.Div(
            html.Div([
                html.H3(number, style={'fontSize': '60px', 'margin': '0', 'flexShrink': '0'}),
                html.P(title, style={'fontSize': '36px', 'margin': '0', 'marginLeft': '15px'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'start'}, className="card-body"),
            className="card",
            style={
                'borderRadius': '15px',
                'boxShadow': '2px 2px 3px 3px grey',
                'textAlign': 'left',
                'height': '80px',
                'marginBottom': '40px',
                'padding': '20px',
                'marginTop': '20px'
            }
        ),
        href=f'/{title_url}',
        style={'textDecoration': 'none', 'color': 'inherit'}
    )


# Reusable function for creating styled headings
def create_styled_heading(text, include_search=False):  # Add parameter
    return html.Div([
        html.Div([
            html.H1(text, style={'color': '#fff', 'marginBottom': '10px'}),
            # Search box (conditional)
            dcc.Input(
                id='search-box', 
                type='text', 
                placeholder='Datenbank durchsuchen...', 
                style={
                    'width': '85%',   
                    'backgroundColor': 'white',
                    'borderRadius': '5px',
                    'border': 'none',
                    'padding': '10px' 
                }
            ) if include_search else None  # Only include if needed
        ], style={'display': 'flex', 'flexDirection': 'column',  'alignItems': 'center', 'width': '100%'}),  
        html.Hr()
    ], style={
        'padding': '20px',
        'background': 'linear-gradient(180deg, #003366 0%, #000033 100%)',
        'color': '#fff',
        'borderRadius': '15px',
        'marginBottom': '20px'
    })




# Sidebar with Image, Link, Additional Text, and Logos
sidebar = html.Div([
    html.Div([
        html.Img(src=app.get_asset_url('bmdv_logo.png'), style={'width': '40%', 'display': 'block', 'marginBottom': '40px'}),
        html.H2('Optimierung des Schienen-Datenmanagements', style={'color': '#000', 'fontWeight': 'bold', 'textAlign': 'center', 'fontSize': '25px'})
    ], style={'padding': '10px', 'backgroundColor': '#D8D7D7'}),
    html.Hr(),
    html.Div([
        dcc.Link('Startseite', href='/', className='sidebar-link',
                 style={'display': 'block', 'textAlign': 'center', 'padding': '8px 16px', 'borderRadius': '15px',
                        'backgroundColor': '#fff', 'color': '#003366', 'margin': '0 auto'}),
    ], style={'paddingBottom': '20px'}),
    # Additional bulleted text under the "Startseite" button
    html.Div([
        html.P("Funktionsfähiger Prototyp einer Datenbank für die zentrale Bündelung von Infrastruktur-Bestandsdaten",
               style={'textAlign': 'left', 'marginBottom': '2em'}),
        html.P("Zielstellung:", style={'textAlign': 'left', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li("SSOT: Verbesserte Qualitätskontrolle und konsistente Informationen"),
            html.Li("Reduzierter Zeitaufwand für Datenabfrage und -verarbeitung"),
            html.Li("Transparenz über vorhandene Daten")
        ], style={'textAlign': 'left', 'paddingLeft': '20px', 'marginBottom': '2em'}),
        html.P("Verknüpfung diverser Datenquellen in zentraler Datenbank:", style={'textAlign': 'left'})
    ], style={'padding': '10px 0'}),
    # Logos
    html.Img(src=app.get_asset_url('infrago_logo.png'), style={'width': '30%', 'marginTop': '10px','display': 'block', 'margin': '0 auto', 'marginBottom': '15px'}),
    html.Img(src=app.get_asset_url('mobilithek_logo.png'), style={'width': '30%', 'marginTop': '10px', 'display': 'block', 'margin': '0 auto', 'marginBottom': '15px'}),
    html.Img(src=app.get_asset_url('EBA-Logo.png'), style={'width': '30%', 'marginTop': '10px', 'display': 'block', 'margin': '0 auto', 'marginBottom': '15px'}),
    html.Img(src=app.get_asset_url('openstreetmap_logo.png'), style={'width': '30%', 'marginTop': '10px', 'display': 'block', 'margin': '0 auto', 'marginBottom': '15px'}),
    html.Img(src=app.get_asset_url('umweltbundesamt_logo.png'), style={'width': '30%', 'marginTop': '10px', 'display': 'block', 'margin': '0 auto', 'marginBottom': '15px'}),
], className='sidebar-sticky', style={
    'padding': '20px',
    'width': '15%',
    'background': '#D8D7D7',
    'position': 'fixed',
    'height': '100%',
    'overflow': 'auto',
    'borderRadius': '15px',  # Add border radius
    'boxShadow': '2px 2px 3px 3px grey'  # Add box shadow
})

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,

    # Main content area with adjusted spacing
    html.Div(id='page-content', style={
        'marginLeft': '17%',
        'marginRight': '2%',
        'paddingTop': '5px',
        'paddingRight': '2%',
        'paddingLeft': '2%',
        'paddingBottom': '20px'
    })
], style={'fontFamily': 'sans-serif', 'height': '100vh'})

# Update page content based on URL
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return [
            # Image above the top bar
            html.Img(src=app.get_asset_url('bild_oben.png'), style={'width': '100%', 'display': 'block', 'marginBottom': '20px'}),

            create_styled_heading('Zentrale Datenbank für Infrastruktur-Bestandsdaten', include_search=True),  # Include the search box

            # Cards Container
            html.Div(className='container-fluid', children=[
                html.Div(className='row', children=[
                    html.Div(create_card('1', 'HLK-Auswertung'), className='col-lg-6 mb-3'),
                    html.Div(create_card('2', 'Inspektor Infrastruktur-Bestandsdaten'), className='col-lg-6 mb-3'),
                    html.Div(create_card('3', 'Geo-Visualisierung'), className='col-lg-6 mb-3'),
                    html.Div(create_card('4', 'Personenbahnhöfe'), className='col-lg-6 mb-3'),
                ])
            ])
        ]
    else:
        # Decode the URL component back to the title
        title = urllib.parse.unquote(pathname[1:])
        if title == 'Inspektor Infrastruktur-Bestandsdaten':
            return [
                create_styled_heading(title, include_search=False),
                dcc.Link('zurück zur Startseite', href='/', style={'color': '#003366'}),
                html.Div('Hier kann eine kurze Beschreibung stehen.', style={'color': '#003366', 'textAlign': 'center', 'marginBottom': '40px'}),
                # Eingabefeld für STR_NR-Filter
                html.Div([
                    html.Label('Filtern Sie die STR_NR:'),
                    dcc.Input(
                        id='STR_NR-filter',
                        type='text',
                        placeholder='Geben Sie STR_NR ein'
                    )
                ], style={'marginBottom': '40px'}),

                # Tabelle für df_GSL
                DataTable(
                    id='table-df_GSL',
                    columns=[{'name': i, 'id': i} for i in df_GSL.columns],
                    data=df_GSL.head(1).to_dict('records'),
                    style_table={'overflowX': 'auto', 'height': '200px', 'marginTop': '40px'},  # Festlegen der Höhe mit Scrollbar
                    style_data_conditional=[{'if': {'column_id': 'STR_NR'}, 'marginTop': '10px'}]  # Anpassen des Abstands des Sliders
                ),

                html.Div(children='Bitte wählen Sie einen Anlagentyp:', style={'padding': '10px'}),
                
                # RadioItems für Datensatz-Auswahl
                dcc.RadioItems(
                    id='dataset-radio',
                    options=[
                        {'label': 'Weichen', 'value': 'df_weichen'},
                        {'label': 'Brücken', 'value': 'df_bruecken'},
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
                dcc.Graph(figure = fig, style={'height': '80vh', 'width': '100%'})
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
    [Input('dataset-radio', 'value'),
     Input('STR_NR-filter', 'value')]
)
def update_table(selected_dataset, STR_NR_filter):
    df = None
    if selected_dataset == 'df_weichen':
        df = df_weichen
    elif selected_dataset == 'df_bruecken':
        df = df_bruecken
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

    return columns, data

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
