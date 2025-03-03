import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io
import plotly.express as px
from datetime import datetime

# Initialize the app with suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Variable pour stocker les données du fichier Excel
df = pd.DataFrame()

# Disposition de l'application - include empty dropdowns in initial layout
app.layout = html.Div([
    html.H1("Dashboard", style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Télécharger un fichier Excel'),
        multiple=False
    ),
    dcc.Tabs(id="tabs", value='tab1', children=[
        dcc.Tab(label='Onglet 1', value='tab1'),
        dcc.Tab(label='Onglet 2', value='tab2')
    ]),
    html.Div(id='tabs-content'),
    
    # Add empty containers for dropdowns that will be populated later
    html.Div([
        html.Div(id='dropdown-container', children=[
            dcc.Dropdown(id='period-dropdown', style={'display': 'none'}),
            dcc.Dropdown(id='date-dropdown', style={'display': 'none'})
        ]),
        html.Div(id='free-chargeable-graph-container')
    ], style={'display': 'none'})  # Hide this initially
])

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    
    # Afficher les colonnes pour vérifier si elles existent
    print(df.columns)
    
    return df


@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('upload-data', 'contents')]
)
def update_tab(tab, contents):
    global df  # Utilisation de la variable globale pour stocker les données

    # Vérifier si le fichier n'a pas été téléchargé
    if not contents:
        return html.Div("Veuillez télécharger un fichier Excel.")
    
    # Décoder et lire le fichier Excel
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        # Lire le fichier Excel avec pandas
        df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return html.Div(f"Erreur lors du traitement du fichier: {e}")

    # Vérification que le fichier a bien des données
    if df.empty:
        return html.Div("Le fichier Excel est vide.")

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
    df_filtered = df[df.get('Order Completed Date').isna() & (df['Color']!= '')]  # Utiliser get() pour éviter KeyError
    print(df_filtered['Color'])
    
    # Sélectionner les colonnes pertinentes
    df_filtered = df_filtered[['Order No.', 'Customer Name', 'Service Technician', 'Model','Order Status', 
                               'Created At', 'Approved Date', 'Task Completed Date', 'Waiting for PO At', 
                               'In Work At', 'Wf. Part At(H)', 'Suspension At', 'Color']]
    
    # Formater les dates pour affichage
    for col in date_columns:
        if col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].dt.strftime('%d %B %Y')
    
    # Création des graphiques pour l'onglet 1 (adapté du premier code)
    graphs = []
    
    # Vérifier si les colonnes nécessaires pour les graphiques existent
    graph_columns = {
        'order_type': 'Order Type',
        'order_status': 'Order Status',
        'total_net_value': 'Total net value',
        'product_line': 'Product Line',
        'warranty_status': 'Warranty Status',
        'free_chargeable': 'Free/Chargeable',
        'created_date': 'Created Date'  # Colonne pour le filtre par date
    }
    
    existing_columns = {key: col for key, col in graph_columns.items() if col in df.columns}
    
    # Graphique des types de commandes
    if 'order_type' in existing_columns:
        order_type_counts = df[existing_columns['order_type']].value_counts()
        order_type_fig = px.pie(values=order_type_counts.values, names=order_type_counts.index,
                                title="Répartition des types de commandes", hole=0.3)
        graphs.append(dcc.Graph(figure=order_type_fig))
    
    # Graphique des statuts de commandes
    if 'order_status' in existing_columns:
        order_status_counts = df[existing_columns['order_status']].value_counts()
        status_fig = px.pie(values=order_status_counts.values, names=order_status_counts.index,
                            title="Répartition des statuts des commandes", hole=0.3)
        
        # Calcul de la somme totale si la colonne Total net value existe
        total_orders = df.shape[0]
        total_sum_text = ""
        if 'total_net_value' in existing_columns:
            total_sum = df[existing_columns['total_net_value']].sum()
            total_sum_text = f"Somme totale des {total_orders} commandes: {total_sum:.2f} €"
        
        status_div = html.Div([
            dcc.Graph(figure=status_fig),
            html.P(total_sum_text, style={'textAlign': 'center', 'margin-top': '10px'}),
            html.P(f"Nombre total de commandes: {total_orders}", style={'textAlign': 'center', 'margin-top': '10px'})
        ])
        graphs.append(status_div)
    
    # Graphique des produits
    if 'product_line' in existing_columns:
        product_values = df[existing_columns['product_line']].value_counts().to_dict()
        product_fig = px.pie(values=list(product_values.values()), names=list(product_values.keys()),
                            title="Nombres de produits par nom", hole=0.3)
        graphs.append(dcc.Graph(figure=product_fig))
    
    # Graphique de garantie
    if 'warranty_status' in existing_columns:
        garanty_values = df[existing_columns['warranty_status']].value_counts()
        garanty_fig = px.bar(x=garanty_values.index, y=garanty_values.values, 
                             labels={'x': 'Equipements', 'y': 'Garantie'},
                             title="Statut de garantie")
        graphs.append(dcc.Graph(figure=garanty_fig))
    
    # Filtre par date pour le graphique Free/Chargeable
    if 'free_chargeable' in existing_columns and 'created_date' in existing_columns:
        # Convertir les dates si ce n'est pas déjà fait
        if not pd.api.types.is_datetime64_any_dtype(df[existing_columns['created_date']]):
            df[existing_columns['created_date']] = pd.to_datetime(df[existing_columns['created_date']])
        
        # Options de période
        period_options = [
            {'label': 'Mois', 'value': 'month'},
            {'label': 'Trimestre', 'value': 'quarter'},
            {'label': 'Année', 'value': 'year'}
        ]
        
        # Préparer les options de date
        date_dropdown_div = html.Div([
            html.H4("Filtrer Free/Chargeable par période"),
            html.Div([
                dcc.Dropdown(
                    id='period-dropdown',
                    options=period_options,
                    value='month',  # Par défaut : mois
                    clearable=False,
                    style={'width': '40%', 'margin-top': '10px', 'margin-right': '20px'}
                ),
                dcc.Dropdown(
                    id='date-dropdown',
                    style={'width': '40%', 'margin-top': '10px'}
                )
            ], style={'display': 'flex'}),
            html.Div(id='free-chargeable-graph-container', style={'margin-top': '20px'})
        ])
        
        graphs.append(date_dropdown_div)
    elif 'free_chargeable' in existing_columns:
        # Si pas de colonne date mais Free/Chargeable existe
        free_chargeable_counts = df[existing_columns['free_chargeable']].value_counts()
        free_chargeable_fig = px.pie(values=free_chargeable_counts.values, names=free_chargeable_counts.index,
                                     title="Répartition Free/Chargeable", hole=0.3)
        graphs.append(dcc.Graph(figure=free_chargeable_fig))
    
    # Graphique des pannes et casses si la colonne Description existe
    if 'Description' in df.columns:
        panne_count = df[df['Description'].str.contains('panne', case=False, na=False)].shape[0]
        casse_count = df[df['Description'].str.contains('casse', case=False, na=False)].shape[0]
        
        fault_data = pd.DataFrame({'Type': ['Panne', 'Casse'], 'Nombre': [panne_count, casse_count]})
        fault_fig = px.bar(fault_data, x='Type', y='Nombre', title='Nombre de pannes et de casses')
        graphs.append(dcc.Graph(figure=fault_fig))
    
    # Une fois que le fichier est téléchargé, afficher les onglets
    if tab == 'tab1':
        return html.Div([
            html.H3("Analyse de données"),
            html.Div([
                html.P(f"Nombre de lignes dans le fichier: {len(df)}"),
                # Ajout des graphiques dans l'onglet 1
                html.Div(graphs)
            ])
        ])
    elif tab == 'tab2':
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
            ],
            sort_action='native'
        )

# Callback pour mettre à jour les options de dates en fonction de la période sélectionnée
@app.callback(
    Output('date-dropdown', 'options'),
    [Input('period-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_date_options(period, contents):
    if not contents or not period:
        return []
    
    # Vérifier si la colonne Created Date existe
    created_date_col = 'Created Date'
    if created_date_col not in df.columns:
        return []
    
    # Convertir les dates si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df[created_date_col]):
        df[created_date_col] = pd.to_datetime(df[created_date_col])
    
    # Générer les options en fonction de la période
    if period == 'month':
        options = sorted(df[created_date_col].dt.strftime('%Y-%m').unique())
    elif period == 'quarter':
        options = sorted(df[created_date_col].dt.to_period('Q').astype(str).unique())
    elif period == 'year':
        options = sorted(df[created_date_col].dt.year.astype(str).unique())
    
    return [{'label': d, 'value': d} for d in options]

# Callback pour mettre à jour le graphique Free/Chargeable en fonction de la date sélectionnée
@app.callback(
    Output('free-chargeable-graph-container', 'children'),
    [Input('date-dropdown', 'value'),
     Input('period-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_free_chargeable_graph(selected_date, period, contents):
    if not contents or not selected_date or not period:
        return []
    
    # Vérifier si les colonnes nécessaires existent
    if 'Free/Chargeable' not in df.columns or 'Created Date' not in df.columns:
        return html.Div("Colonnes 'Free/Chargeable' ou 'Created Date' manquantes")
    
    # Convertir les dates si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df['Created Date']):
        df['Created Date'] = pd.to_datetime(df['Created Date'])
    
    # Filtrer les données selon la période sélectionnée
    if period == 'month':
        filtered_df = df[df['Created Date'].dt.strftime('%Y-%m') == selected_date]
    elif period == 'quarter':
        filtered_df = df[df['Created Date'].dt.to_period('Q').astype(str) == selected_date]
    elif period == 'year':
        filtered_df = df[df['Created Date'].dt.year.astype(str) == selected_date]
    
    # Créer le graphique Free/Chargeable avec les données filtrées
    free_chargeable_counts = filtered_df['Free/Chargeable'].value_counts()
    free_chargeable_fig = px.pie(
        values=free_chargeable_counts.values, 
        names=free_chargeable_counts.index,
        title=f"Répartition Free/Chargeable ({selected_date})", 
        hole=0.3
    )
    
    return dcc.Graph(figure=free_chargeable_fig)

if __name__ == '__main__':
    app.run_server(debug=True)