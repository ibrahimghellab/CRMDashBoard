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
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    
    # Afficher les colonnes pour vérifier si elles existent
    print(df.columns)
    
    return df

@app.callback(
    Output('output-table', 'children'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def update_table(contents):
    df = parse_contents(contents)
    
    # Vérification des colonnes requises
    required_columns = ['Order No.', 'Customer Name', 'Service Technician', 'Model', 'Order Status','Created At', 'Approved Date', 
                        'Task Completed Date', 'Order Completed Date', 'Waiting for PO At', 'In Work At', 
                        'Wf. Part At(H)', 'Suspension At']
    
    # Vérifier si des colonnes manquent
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return html.Div(f"Colonnes manquantes : {', '.join(missing_columns)}")
    
    # Ajouter des colonnes manquantes si nécessaire
    if 'Order Completed Date' not in df.columns:
        df['Order Completed Date'] = pd.NaT  # Ajouter une colonne vide si elle manque
    
    # Convertir les colonnes de date en format datetime
    date_columns = ['Created At', 'Approved Date', 'Task Completed Date', 'Order Completed Date', 
                    'Waiting for PO At', 'In Work At', 'Wf. Part At(H)', 'Suspension At']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    today = datetime.today()
    
    def color_code(row):
        today = datetime.today().date()  # Utilisation de .date() pour obtenir uniquement la date sans l'heure
        if(row["Order Status"] == "Waiting for Inspection"):
            return 'green'
        
        #Order Complete
        if pd.notna(row['Order Completed Date']):
            completed_date_days = (today - row['Order Completed Date'].date()).days  # .date() pour ignorer l'heure
            if completed_date_days >= 30:
                return 'red'
            elif completed_date_days >= 15:
                return 'orange'
            else:
                return ''
        # Task Completed
        if pd.notna(row['Task Completed Date']):
            task_completed_days = (today - row['Task Completed Date'].date()).days  # .date() pour ignorer l'heure
            if task_completed_days >= 30:
                return 'red'
            elif task_completed_days >= 15:
                return 'orange'
            else:
                return ''
         # In Work
        if pd.notna(row['In Work At']):
            in_work_days = (today - row['In Work At'].date()).days 
            print(f"In work days : {in_work_days} Date : {row['In Work At'].date()}")
            if in_work_days >= 14:
                return 'red'
            elif in_work_days >= 7:
                return 'orange'
            else:
                return ''
        #Suspension for reasons
        if pd.notna(row['Suspension At']):
            suspention_date_days = (today - row['Suspension At'].date()).days  # .date() pour ignorer l'heure
            if suspention_date_days >= 30:
                return 'red'
            elif suspention_date_days >= 15:
                return 'orange'
            else:
                return ''
       
        # Waiting for Part
        if pd.notna(row['Wf. Part At(H)']):
            waiting_part_days = (today - row['Wf. Part At(H)'].date()).days  # .date() pour ignorer l'heure
            if waiting_part_days >= 14:
                return 'red'
            elif waiting_part_days >= 7:
                return 'orange'
            else:
                return ''

        #Waiting for PO 
        if pd.notna(row['Waiting for PO At']):
            waiting_for_po_date_days = (today - row['Waiting for PO At'].date()).days  # .date() pour ignorer l'heure
            if waiting_for_po_date_days >= 30:
                return 'red'
            elif waiting_for_po_date_days >= 15:
                return 'orange'
            else:
                return ''
        




        # Created
        if pd.notna(row['Created At']):
            created_date_days = (today - row['Created At'].date()).days  # .date() pour ignorer l'heure
            if created_date_days >= 30:
                return 'red'
            elif created_date_days >= 15:
                return 'orange'
            else:
                return ''
       

        
        
        
        
        
        return ''

    df['Color'] = df.apply(color_code, axis=1)
    
    # Filtrer pour exclure "Order Completed" et les lignes vides
    df_filtered = df[df.get('Order Completed Date').isna()]  # Utiliser get() pour éviter KeyError
    
    # Sélectionner les colonnes pertinentes
    df_filtered = df_filtered[['Order No.', 'Customer Name', 'Service Technician', 'Model','Order Status', 
                               'Created At', 'Approved Date', 'Task Completed Date', 'Waiting for PO At', 
                               'In Work At', 'Wf. Part At(H)', 'Suspension At', 'Color']]
    
    # Formater les dates pour affichage
    for col in date_columns:
        if col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].dt.strftime('%d %B %Y')
    
    return dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in df_filtered.columns if col != 'Color'],
        data=df_filtered.to_dict('records'),
        style_data_conditional=[
            {
                'if': {'filter_query': '{Color} = "red"'},
                'backgroundColor': 'red',
                'color': 'white'
            },
            {
                'if': {'filter_query': '{Color} = "orange"'},
                'backgroundColor': 'orange',
                'color': 'black'
            }
        ]
    )

if __name__ == '__main__':
    app.run_server(debug=True)
