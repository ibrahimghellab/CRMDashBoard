import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Custom CSS for better styling
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap']

# Initialize the app
app = dash.Dash(__name__, 
                suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets)

# Variable pour stocker les données du fichier Excel
df = pd.DataFrame()

# Custom styles
COLORS = {
    'background': '#f8f9fa',
    'text': '#212529',
    'primary': '#0275d8',
    'success': '#5cb85c',
    'danger': '#d9534f',
    'warning': '#f0ad4e',
    'light': '#f7f7f7',
    'dark': '#343a40',
}

# Styles for the layout
CONTENT_STYLE = {
    'margin-left': '2rem',
    'margin-right': '2rem',
    'padding': '2rem',
    'backgroundColor': COLORS['background'],
}

# Styles for cards
CARD_STYLE = {
    'boxShadow': '0 4px 6px 0 rgba(0, 0, 0, 0.1)',
    'backgroundColor': 'white',
    'borderRadius': '10px',
    'padding': '20px',
    'margin-bottom': '20px',
}

# Disposition de l'application avec un design amélioré
app.layout = html.Div(style={'fontFamily': 'Roboto', 'backgroundColor': COLORS['background'], 'minHeight': '100vh'}, children=[
    html.Div(style={'backgroundColor': COLORS['primary'], 'padding': '20px', 'color': 'white'}, children=[
        html.H1("Tableau de Bord de Service", style={'textAlign': 'center', 'fontWeight': '500'}),
        html.P("Analyse et suivi des commandes de service", style={'textAlign': 'center', 'opacity': '0.8'})
    ]),
    
    html.Div(style=CONTENT_STYLE, children=[
        html.Div(style=CARD_STYLE, children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.I(className="fas fa-file-excel", style={'fontSize': '42px', 'color': COLORS['primary']}),
                    html.Div('Glissez ou', style={'margin': '10px'}),
                    html.Button('Sélectionnez un fichier Excel', 
                               style={
                                   'backgroundColor': COLORS['primary'],
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '10px 15px',
                                   'borderRadius': '5px',
                                   'cursor': 'pointer'
                               })
                ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'height': '200px'}),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'backgroundColor': COLORS['light'],
                    'border': f'2px dashed {COLORS["primary"]}',
                    'padding': '70px 0'
                },
                multiple=False
            ),
            html.Div(id='upload-status', style={'marginTop': '10px', 'textAlign': 'center'})
        ]),
        
        dcc.Tabs(
            id="tabs",
            value='tab1',
            style={
                'borderBottom': f'1px solid {COLORS["light"]}',
                'padding': '6px',
                'fontWeight': 'bold'
            },
            colors={
                "border": COLORS['light'],
                "primary": COLORS['primary'],
                "background": "#f9f9f9"
            },
            children=[
                dcc.Tab(
                    label='Tableau de Bord',
                    value='tab1',
                    style={'borderBottom': f'1px solid {COLORS["light"]}', 'padding': '10px'},
                    selected_style={'borderTop': f'3px solid {COLORS["primary"]}', 'padding': '10px'}
                ),
                dcc.Tab(
                    label='Commandes à Suivre',
                    value='tab2',
                    style={'borderBottom': f'1px solid {COLORS["light"]}', 'padding': '10px'},
                    selected_style={'borderTop': f'3px solid {COLORS["primary"]}', 'padding': '10px'}
                )
            ]
        ),
        html.Div(id='tabs-content', style={'padding': '20px 0'}),
        
        # Conteneurs pour les dropdowns qui seront peuplés plus tard
        html.Div([
            html.Div(id='dropdown-container', children=[
                dcc.Dropdown(id='period-dropdown', style={'display': 'none'}),
                dcc.Dropdown(id='date-dropdown', style={'display': 'none'})
            ]),
            html.Div(id='free-chargeable-graph-container')
        ], style={'display': 'none'})
    ])
])

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    return df

# Callback pour mettre à jour le statut du téléchargement
@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-data', 'contents')]
)
def update_upload_status(contents):
    if contents:
        return html.Div([
            html.I(className="fas fa-check-circle", style={'color': COLORS['success'], 'marginRight': '10px'}),
            "Fichier chargé avec succès"
        ], style={'color': COLORS['success']})
    return ""

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('upload-data', 'contents')]
)
def update_tab(tab, contents):
    global df  # Utilisation de la variable globale pour stocker les données

    # Vérifier si le fichier n'a pas été téléchargé
    if not contents:
        return html.Div([
            html.Div(
                html.Img(src='/assets/upload_icon.png', style={'width': '100px', 'opacity': '0.3'}),
                style={'textAlign': 'center', 'marginTop': '50px'}
            ),
            html.H3("Veuillez télécharger un fichier Excel pour commencer",
                   style={'textAlign': 'center', 'color': COLORS['text'], 'opacity': '0.7', 'fontWeight': '400'})
        ])
    
    # Décoder et lire le fichier Excel
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        # Lire le fichier Excel avec pandas
        df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'fontSize': '48px', 'color': COLORS['danger']}),
            html.H4(f"Erreur lors du traitement du fichier: {e}", style={'color': COLORS['danger']})
        ], style={'textAlign': 'center', 'marginTop': '30px'})

    # Vérification que le fichier a bien des données
    if df.empty:
        return html.Div([
            html.I(className="fas fa-file-excel", style={'fontSize': '48px', 'color': COLORS['warning']}),
            html.H4("Le fichier Excel est vide.", style={'color': COLORS['warning']})
        ], style={'textAlign': 'center', 'marginTop': '30px'})

    df = parse_contents(contents)
    
    # Vérification des colonnes requises
    required_columns = ['Order No.', 'Customer Name', 'Service Technician', 'Model', 'Order Status','Created At', 'Approved Date', 
                        'Task Completed Date', 'Order Completed Date', 'Waiting for PO At', 'In Work At', 
                        'Wf. Part At(H)', 'Suspension At']
    
    # Vérifier si des colonnes manquent
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return html.Div([
            html.I(className="fas fa-table", style={'fontSize': '48px', 'color': COLORS['warning']}),
            html.H4("Données incomplètes", style={'color': COLORS['warning']}),
            html.P(f"Colonnes manquantes : {', '.join(missing_columns)}", style={'color': COLORS['text']})
        ], style={'textAlign': 'center', 'marginTop': '30px', 'padding': '20px', 'backgroundColor': '#fff8e1', 'borderRadius': '10px'})
    
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
        today = datetime.today().date()
        
        # Order Complete
        if pd.notna(row['Order Completed Date']):
            completed_date_days = (today - row['Order Completed Date'].date()).days
            if completed_date_days >= 30:
                return 'red'
            elif completed_date_days >= 15:
                return 'orange'
            else:
                return ''
        # Task Completed
        if pd.notna(row['Task Completed Date']):
            task_completed_days = (today - row['Task Completed Date'].date()).days
            if task_completed_days >= 30:
                return 'red'
            elif task_completed_days >= 15:
                return 'orange'
            else:
                return ''
        # In Work
        if pd.notna(row['In Work At']):
            in_work_days = (today - row['In Work At'].date()).days
            if in_work_days >= 14:
                return 'red'
            elif in_work_days >= 7:
                return 'orange'
            else:
                return ''
        # Suspension for reasons
        if pd.notna(row['Suspension At']):
            suspention_date_days = (today - row['Suspension At'].date()).days
            if suspention_date_days >= 30:
                return 'red'
            elif suspention_date_days >= 15:
                return 'orange'
            else:
                return ''
        # Waiting for Part
        if pd.notna(row['Wf. Part At(H)']):
            waiting_part_days = (today - row['Wf. Part At(H)'].date()).days
            if waiting_part_days >= 14:
                return 'red'
            elif waiting_part_days >= 7:
                return 'orange'
            else:
                return ''
        # Waiting for PO 
        if pd.notna(row['Waiting for PO At']):
            waiting_for_po_date_days = (today - row['Waiting for PO At'].date()).days
            if waiting_for_po_date_days >= 30:
                return 'red'
            elif waiting_for_po_date_days >= 15:
                return 'orange'
            else:
                return ''
        # Created
        if pd.notna(row['Created At']):
            created_date_days = (today - row['Created At'].date()).days
            if created_date_days >= 30:
                return 'red'
            elif created_date_days >= 15:
                return 'orange'
            else:
                return ''
        return ''

    df['Color'] = df.apply(color_code, axis=1)
    
    # Filtrer pour exclure "Order Completed" et les lignes vides
    df_filtered = df[df['Order Completed Date'].isna() & (df['Color'] != '') & (df['Order Status'] != "Cancelled")]

    
    # Sélectionner les colonnes pertinentes
    df_filtered = df_filtered[['Order No.', 'Customer Name', 'Service Technician', 'Model','Order Status', 
                               'Created At', 'Approved Date', 'Task Completed Date', 'Waiting for PO At', 
                               'In Work At', 'Wf. Part At(H)', 'Suspension At', 'Color']]
    
    # Formater les dates pour affichage
    for col in date_columns:
        if col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].dt.strftime('%d %B %Y')
    
    # Création des graphiques pour l'onglet 1 (adapté du premier code)
    # Vérifier si les colonnes nécessaires pour les graphiques existent
    graph_columns = {
        'order_type': 'Order Type',
        'order_status': 'Order Status',
        'total_net_value': 'Total net value',
        'product_line': 'Product Line',
        'warranty_status': 'Warranty Status',
        'free_chargeable': 'Free/Chargeable',
        'created_date': 'Created Date'
    }
    
    existing_columns = {key: col for key, col in graph_columns.items() if col in df.columns}

    # Une fois que le fichier est téléchargé, afficher les onglets
    if tab == 'tab1':
        # Compteurs pour KPIs
        total_orders = len(df)
        pending_orders = len(df[~df["Order Status"].isin(["Order Complete", "Order Approved", "Task Complete"])])
        urgent_orders = len(df_filtered[df_filtered['Color'] == 'red'])
        warning_orders = len(df_filtered[df_filtered['Color'] == 'orange'])
        
        # Obtenir les statistiques sur les statuts des dossier
        order_status_counts = df['Order Status'].value_counts()
        
        # Préparation des données pour le tableau détaillé des dossiers
        if 'total_net_value' in existing_columns:
            status_data = df.groupby('Order Status').agg({
                'Order No.': 'count',
                existing_columns['total_net_value']: 'sum'
            }).reset_index()
            status_data.columns = ['Statut', 'Nombre', 'Valeur (€)']
            status_data['Valeur (€)'] = status_data['Valeur (€)'].round(2)
        else:
            status_data = df.groupby('Order Status').agg({
                'Order No.': 'count'
            }).reset_index()
            status_data.columns = ['Statut', 'Nombre']
        
        # Créer les KPI cards
        kpi_cards = html.Div([
            
            html.Div(className='row', style={'display': 'flex', 'flexWrap': 'wrap', 'margin': '0 -10px'}, children=[
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '200px'}, children=[
                    html.Div(style={**CARD_STYLE, 'backgroundColor': COLORS['primary'], 'color': 'white'}, children=[
                        html.H2(total_orders, style={'textAlign': 'center', 'margin': '0', 'fontSize': '42px'}),
                        html.P("Total des commandes", style={'textAlign': 'center', 'margin': '5px 0 0 0', 'opacity': '0.8'})
                    ])
                ]),
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '200px'}, children=[
                    html.Div(style={**CARD_STYLE, 'backgroundColor': COLORS['success'], 'color': 'white'}, children=[
                        html.H2(pending_orders, style={'textAlign': 'center', 'margin': '0', 'fontSize': '42px'}),
                        html.P("Commandes en cours", style={'textAlign': 'center', 'margin': '5px 0 0 0', 'opacity': '0.8'})
                    ])
                ]),
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '200px'}, children=[
                    html.Div(style={**CARD_STYLE, 'backgroundColor': COLORS['warning'], 'color': 'white'}, children=[
                        html.H2(warning_orders, style={'textAlign': 'center', 'margin': '0', 'fontSize': '42px'}),
                        html.P("Attention requise", style={'textAlign': 'center', 'margin': '5px 0 0 0', 'opacity': '0.8'})
                    ])
                ]),
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '200px'}, children=[
                    html.Div(style={**CARD_STYLE, 'backgroundColor': COLORS['danger'], 'color': 'white'}, children=[
                        html.H2(urgent_orders, style={'textAlign': 'center', 'margin': '0', 'fontSize': '42px'}),
                        html.P("Commandes urgentes", style={'textAlign': 'center', 'margin': '5px 0 0 0', 'opacity': '0.8'})
                    ])
                ])
            ])
        ])
        
        # Nouveau tableau pour détailler les statuts des commandes
        status_detail_card = html.Div(style={**CARD_STYLE, 'marginTop': '20px'}, children=[
            html.H3("Total des dossiers", style={'margin-top': '0', 'marginBottom': '20px', 'color': COLORS['dark']}),
            html.Div(style={'overflowX': 'auto'}, children=[
                dash_table.DataTable(
                    data=status_data.to_dict('records'),
                    columns=[{'name': col, 'id': col, 'type': 'numeric' if col != 'Statut' else 'text'} for col in status_data.columns],
                    style_header={
                        'backgroundColor': COLORS['light'],
                        'fontWeight': 'bold',
                        'border': f'1px solid {COLORS["light"]}',
                        'textAlign': 'center',
                    },
                    style_cell={
                        'textAlign': 'center',
                        'padding': '10px',
                        'fontFamily': 'Roboto',
                    },
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'Statut'},
                            'textAlign': 'left',
                            'fontWeight': 'bold',
                        },
                        {
                            'if': {'column_id': 'Nombre'},
                            'width': '120px',
                        },
                        {
                            'if': {'column_id': 'Valeur (€)'},
                            'width': '150px',
                        }
                    ],
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgba(0, 0, 0, 0.05)',
                        }
                    ],
                )
            ])
        ])
        
        # Créer les graphiques
        graphs = []
        
        # Première rangée de graphiques
        row1 = html.Div(className='row', style={'display': 'flex', 'flexWrap': 'wrap', 'margin': '20px -10px'}, children=[])
        
        # Graphique des types de commandes
        if 'order_type' in existing_columns:
            order_type_counts = df[existing_columns['order_type']].value_counts()
            order_type_fig = px.pie(
                values=order_type_counts.values, 
                names=order_type_counts.index,
                title="Types de commandes",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            order_type_fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(t=40, b=40, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            row1.children.append(
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '400px'}, children=[
                    html.Div(style=CARD_STYLE, children=[
                        dcc.Graph(figure=order_type_fig, config={'displayModeBar': False})
                    ])
                ])
            )
        
        # Graphique des statuts de commandes
        if 'order_status' in existing_columns:
            order_status_counts = df[existing_columns['order_status']].value_counts()
            
            # Calculer la valeur totale pour chaque statut si la colonne 'total_net_value' existe
            if 'total_net_value' in existing_columns:
                total_value_by_status = df.groupby(existing_columns['order_status'])[existing_columns['total_net_value']].sum()
                labels = [f"{status}" 
                        for status, count in order_status_counts.items()]
            else:
                labels = [f"{status} - {count} commandes" for status, count in order_status_counts.items()]
            
            status_fig = px.pie(
                values=order_status_counts.values, 
                names=labels,  # Utiliser les labels personnalisés
                title="Statuts des commandes",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )


            status_fig.update_layout(
                legend=dict(orientation="h", y=-5, xanchor="center", x=0.5),
                margin=dict(t=40, b=40, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # Calcul de la somme totale si la colonne Total net value existe
            total_sum_text = ""
            if 'total_net_value' in existing_columns:
                total_sum = df[existing_columns['total_net_value']].sum()
                total_sum_text = f"{total_sum:.2f} €"
            
            row1.children.append(
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '400px'}, children=[
                    html.Div(style=CARD_STYLE, children=[
                        dcc.Graph(figure=status_fig, config={'displayModeBar': False}),
                        html.Div(style={'textAlign': 'center', 'marginTop': '10px'}, children=[
                            html.Strong("Valeur totale: ", style={'marginRight': '5px', 'fontSize': '16px'}),
                            html.Span(total_sum_text, style={'fontSize': '16px', 'color': COLORS['primary']})
                        ]) if total_sum_text else None
                    ])
                ])
            )
        
        graphs.append(row1)
        
        # Deuxième rangée de graphiques
        row2 = html.Div(className='row', style={'display': 'flex', 'flexWrap': 'wrap', 'margin': '0 -10px'}, children=[])
        
        # Graphique des produits
        if 'product_line' in existing_columns:
            product_values = df[existing_columns['product_line']].value_counts().to_dict()
            
            # Utiliser un graphique à barres horizontales au lieu d'un camembert pour plus de clarté
            product_fig = px.bar(
                x=list(product_values.values()),
                y=list(product_values.keys()),
                orientation='h',
                title="Répartition des produits",
                color_discrete_sequence=[COLORS['primary']]
            )
            product_fig.update_layout(
                xaxis_title="Nombre de commandes",
                yaxis_title="",
                margin=dict(t=40, b=20, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            row2.children.append(
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '400px'}, children=[
                    html.Div(style=CARD_STYLE, children=[
                        dcc.Graph(figure=product_fig, config={'displayModeBar': False})
                    ])
                ])
            )
        
        # Graphique de garantie
        if 'warranty_status' in existing_columns:
            garanty_values = df[existing_columns['warranty_status']].value_counts()
            
            # Camembert stylisé pour le statut de garantie
            garanty_fig = px.pie(
                values=garanty_values.values, 
                names=garanty_values.index,
                title="Statut de garantie",
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            garanty_fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(t=40, b=40, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            row2.children.append(
                html.Div(className='col', style={'flex': '1', 'padding': '10px', 'minWidth': '400px'}, children=[
                    html.Div(style=CARD_STYLE, children=[
                        dcc.Graph(figure=garanty_fig, config={'displayModeBar': False})
                    ])
                ])
            )
        
        graphs.append(row2)
        
        # Section Free/Chargeable avec filtres améliorés
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
            
            filter_section = html.Div(className='row', style={'margin': '20px 0'}, children=[
                html.Div(style=CARD_STYLE, children=[
                    html.H4("Analyse Free/Chargeable par période", style={'margin-top': '0', 'marginBottom': '20px', 'color': COLORS['dark']}),
                    html.Div(style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}, children=[
                        html.Label("Période:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='period-dropdown',
                            options=period_options,
                            value='month',
                            clearable=False,
                            style={'width': '200px', 'marginRight': '20px'}
                        ),
                        html.Label("Date:", style={'marginRight': '10px', 'marginLeft': '20px', 'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='date-dropdown',
                            style={'width': '200px'}
                        )
                    ]),
                    html.Div(id='free-chargeable-graph-container', style={'marginTop': '20px'})
                ])
            ])
            
            graphs.append(filter_section)
        
        return html.Div([
            kpi_cards,
            status_detail_card,  # Nouveau tableau des statuts de commandes
            html.Div(graphs)
        ])
        
    elif tab == 'tab2':
        return html.Div(style={**CARD_STYLE, 'overflowX': 'auto'}, children=[  # Garder le défilement horizontal si nécessaire
            html.H3("Commandes à suivre", style={'margin-top': '0', 'marginBottom': '20px', 'color': COLORS['dark']}),
            html.P(f"{len(df_filtered)} commandes nécessitent votre attention", 
                style={'marginBottom': '20px', 'fontStyle': 'italic', 'color': COLORS['text']}),
            
            dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in df_filtered.columns if col != 'Color'],
                data=df_filtered.to_dict('records'),
                style_header={
                    'backgroundColor': COLORS['light'],
                    'fontWeight': 'bold',
                    'border': f'1px solid {COLORS["light"]}',
                    'borderRadius': '3px',
                    'padding': '15px 5px',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px 5px',
                    'fontFamily': 'Roboto',
                    'fontSize': '13px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgba(0, 0, 0, 0.05)',
                    },
                    {
                        'if': {
                            'filter_query': '{Color} = "red"'
                        },
                        'backgroundColor': 'rgba(255, 0, 0, 0.1)', 
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{Color} = "orange"'
                        },
                        'backgroundColor': 'rgba(255, 165, 0, 0.1)',
                    }
                ],
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                style_table={'minWidth': '100%'},
            )
        ])

# Callback pour le graphique Free/Chargeable
@app.callback(
    [Output('date-dropdown', 'options'),
     Output('date-dropdown', 'value')],
    [Input('period-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_date_options(period_value, contents):
    if not contents or not period_value:
        return [], None
    
    # Décoder et lire le fichier Excel
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    
    # Vérifier si les colonnes nécessaires existent
    if 'Created Date' not in df.columns:
        return [], None
    
    # Convertir en datetime
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    
    # Générer les options en fonction de la période sélectionnée
    if period_value == 'month':
        # Format: "MM-YYYY"
        date_groups = df['Created Date'].dt.strftime('%m-%Y').unique()
        options = [{'label': datetime.strptime(date, '%m-%Y').strftime('%B %Y'), 'value': date} for date in date_groups if pd.notna(date)]
    elif period_value == 'quarter':
        # Format: "QX-YYYY"
        df['Quarter'] = 'Q' + df['Created Date'].dt.quarter.astype(str) + '-' + df['Created Date'].dt.year.astype(str)
        options = [{'label': quarter, 'value': quarter} for quarter in df['Quarter'].unique() if pd.notna(quarter)]
    else:  # year
        # Format: "YYYY"
        date_groups = df['Created Date'].dt.year.astype(str).unique()
        options = [{'label': year, 'value': year} for year in date_groups if pd.notna(year)]
    
    # Trier les options
    options = sorted(options, key=lambda x: x['value'])
    
    # Valeur par défaut: la période la plus récente
    default_value = options[-1]['value'] if options else None
    
    return options, default_value

@app.callback(
    Output('free-chargeable-graph-container', 'children'),
    [Input('date-dropdown', 'value'),
     Input('period-dropdown', 'value'),
     Input('upload-data', 'contents')]
)
def update_free_chargeable_graph(selected_date, period_value, contents):
    if not contents or not selected_date or not period_value:
        return html.Div("Sélectionnez une période et une date pour voir les données")
    
    # Décoder et lire le fichier Excel
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    
    # Vérifier si les colonnes nécessaires existent
    if 'Created Date' not in df.columns or 'Free/Chargeable' not in df.columns:
        return html.Div("Les colonnes 'Created Date' ou 'Free/Chargeable' sont manquantes dans le fichier")
    
    # Convertir en datetime
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    
    # Filtrer en fonction de la période sélectionnée
    if period_value == 'month':
        # Format attendu: "MM-YYYY"
        month, year = selected_date.split('-')
        mask = (df['Created Date'].dt.month == int(month)) & (df['Created Date'].dt.year == int(year))
        title = f"Répartition Free/Chargeable - {datetime.strptime(selected_date, '%m-%Y').strftime('%B %Y')}"
    elif period_value == 'quarter':
        # Format attendu: "QX-YYYY"
        quarter, year = selected_date.split('-')
        quarter_num = int(quarter[1])
        start_month = (quarter_num - 1) * 3 + 1
        end_month = quarter_num * 3
        mask = (df['Created Date'].dt.year == int(year)) & (df['Created Date'].dt.month >= start_month) & (df['Created Date'].dt.month <= end_month)
        title = f"Répartition Free/Chargeable - {selected_date}"
    else:  # year
        # Format attendu: "YYYY"
        mask = df['Created Date'].dt.year == int(selected_date)
        title = f"Répartition Free/Chargeable - Année {selected_date}"
    
    filtered_df = df[mask]
    
    # Si aucune donnée après filtrage
    if filtered_df.empty:
        return html.Div("Aucune donnée disponible pour cette période", 
                       style={'textAlign': 'center', 'padding': '20px', 'color': COLORS['text']})
    
    # Compter les valeurs Free/Chargeable
    free_chargeable_counts = filtered_df['Free/Chargeable'].value_counts()
    
    # Créer un graphique à secteurs
    fig = px.pie(
        names=free_chargeable_counts.index,
        values=free_chargeable_counts.values,
        title=title,
        color_discrete_sequence=px.colors.sequential.RdBu_r
    )
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(t=50, b=50, l=20, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Ajouter des statistiques sur la valeur si disponible
    stats_div = html.Div()
    if 'Total net value' in df.columns:
        total_value = filtered_df.groupby('Free/Chargeable')['Total net value'].sum().to_dict()
        stats_rows = []
        
        for category, count in free_chargeable_counts.items():
            value = total_value.get(category, 0)
            percentage = (count / free_chargeable_counts.sum()) * 100
            
            stats_rows.append(html.Tr([
                html.Td(category, style={'fontWeight': 'bold', 'padding': '8px'}),
                html.Td(f"{count} ({percentage:.1f}%)", style={'padding': '8px', 'textAlign': 'center'}),
                html.Td(f"{value:.2f} €", style={'padding': '8px', 'textAlign': 'right'})
            ]))
        
        
    
    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False}),
        stats_div
    ])

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=False)