import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import io
import base64
from datetime import datetime

# Initialisation de l'application Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File'),
        multiple=False
    ),
    html.Div(id='output-table')
])

def parse_contents(contents):
    if not contents:
        return None  # Si aucun fichier n'est uploadé, retourner None
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    return df

@app.callback(
    Output('output-table', 'children'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def update_table(contents):
    df = parse_contents(contents)
    if df is None:
        return html.Div("Aucun fichier chargé.")
    
    # Conversion des colonnes de dates
    date_columns = ['Created At', 'Approved Date', 'Task Completed Date', 'Order Completed Date', 
                    'Waiting for PO At', 'In Work At', 'Wf. Part At(H)', 'Suspension At']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Filtrer les données
    df_filtered = df[df.get('Order Completed Date').isna()]
    
    # Ajout d'un tri interactif
    return dash_table.DataTable(
        columns=[
            {'name': col, 'id': col} for col in df_filtered.columns
        ],
        data=df_filtered.to_dict('records'),
        sort_action='native',  # Active le tri interactif
        page_size=10  # Ajoute la pagination
    )

if __name__ == '__main__':
    app.run_server(debug=True)
