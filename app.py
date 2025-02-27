import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import base64
import io

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Disposition de l'application
app.layout = html.Div([
    html.H1("Dashboard", style={'textAlign': 'center'}),

    # Upload du fichier Excel
    dcc.Upload(
        id='upload-data',
        children=html.Button('Télécharger un fichier Excel'),
        multiple=False
    ),
    html.Div(id='alert-container', style={'color': 'red', 'font-weight': 'bold', 'display': 'none'}),
    # Zone pour afficher les graphiques
    html.Div(id='graphs-container'),

    # Dropdown pour choisir la période (mois, trimestre, année)
    html.Div([
        dcc.Dropdown(
            id='period-dropdown',
            options=[
                {'label': 'Mois', 'value': 'month'},
                {'label': 'Trimestre', 'value': 'quarter'},
                {'label': 'Année', 'value': 'year'}
            ],
            value='month',  # Par défaut : mois
            clearable=False,
            style={'width': '40%', 'margin-top': '20px'}
        ),
        # Dropdown pour choisir la date (mois, trimestre, année spécifique)
        dcc.Dropdown(id='date-dropdown', clearable=False, style={'width': '40%', 'margin-top': '20px'})
    ], id='date-selection-container', style={'display': 'none'}),  # Initialement caché

    # Graphique initial pour l'évolution du nombre d'appareils (tous produits)
    html.Div([
        dcc.Graph(id='initial-evolution-chart')
    ], id='initial-evolution-container', style={'display': 'none'}),

    # Navbar pour sélectionner un produit
    html.Div(id='product-navbar', style={'margin-top': '20px', 'display': 'flex', 'flex-wrap': 'wrap', 'gap': '10px'}),

    # Graphique pour l'évolution du nombre d'appareils par produit spécifique (après sélection)
    html.Div([
        dcc.Graph(id='product-evolution-chart')
    ], id='product-evolution-container', style={'margin-top': '20px', 'display': 'none'})
])

# Callback pour charger les données, afficher les graphiques et gérer la sélection de période
@app.callback(
    [Output('graphs-container', 'children'),
     Output('date-selection-container', 'style'),
     Output('alert-container', 'children'),
     Output('alert-container', 'style'),
     Output('date-dropdown', 'options'),
     Output('product-navbar', 'children'),
     Output('initial-evolution-chart', 'figure'),
     [Input('upload-data', 'contents'),
     Input('period-dropdown', 'value'),
     Input('date-dropdown', 'value')]]
   
)
def load_file(contents, period, selected_date):
    if not contents:
        return "Veuillez télécharger un fichier Excel.", {'display': 'none'}, [], [], px.bar()

    # Décoder le fichier Excel téléchargé
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        # Lire le fichier Excel avec Pandas
        df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return f"Erreur lors du traitement du fichier: {e}", {'display': 'none'}, [], [], px.bar()

    # Vérification des colonnes nécessaires
    required_columns = ['Order Type', 'Order Status', 'Total net value', 'Model', 'Created Date', 'Product Line', 'Warranty Status', 'Free/Chargeable']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return f"Le fichier Excel ne contient pas les colonnes nécessaires: {', '.join(missing_columns)}", {'display': 'none'}, [], [], px.bar()

    # Vérifier que "Total net value" contient des valeurs numériques
    if not pd.api.types.is_numeric_dtype(df['Total net value']):
        return "La colonne 'Total net value' doit contenir des valeurs numériques.", {'display': 'none'}, [], [], px.bar()

    # Convertir les dates pour la gestion des périodes
    df['Created Date'] = pd.to_datetime(df['Created Date'])

    total_value = df[df['Order Status'] == "Task Complete"]['Total net value'].sum()
    alert_message = ""
    alert_style = {'display': 'none'}

    if total_value > 0:
        alert_message = f"Attention ! La somme d'argent pour 'Task Complete' est de {total_value:.2f} €."
        alert_style = {'color': 'red', 'font-weight': 'bold', 'display': 'block'}

    # Créer les graphiques de base (basés sur l'ensemble des données)
    order_type_counts = df['Order Type'].value_counts()
    order_type_fig = px.pie(values=order_type_counts.values, names=order_type_counts.index,
                            title="Répartition des types de commandes", hole=0.3)

    # Fonction pour générer le libellé avec le nombre de commandes et la somme d'argent
    def get_status_label(status):
        count = df[df['Order Status'] == status].shape[0]
        total_value = df[df['Order Status'] == status]['Total net value'].sum()
        return f"{status} ({count} commandes, {total_value:.2f} €)"


    

    # Créer le dictionnaire des statuts avec les libellés modifiés
    status_counts = {
        get_status_label("Order Approved"): df[df['Order Status'] == 'Order Approved'].shape[0],
        get_status_label("Task Complete"): df[df['Order Status'] == 'Task Complete'].shape[0],
        get_status_label("Waiting for Parts"): df[df['Order Status'] == 'Waiting for Parts'].shape[0],
        get_status_label("Suspension for Reasons"): df[df['Order Status'] == 'Suspension for Reasons'].shape[0],
        get_status_label("Waiting for PO"): df[df['Order Status'] == 'Waiting for PO'].shape[0],
        get_status_label("In Work"): df[df['Order Status'] == 'In Work'].shape[0],
        get_status_label("Waiting for Inspection"): df[df['Order Status'] == 'Waiting for Inspection'].shape[0],
        get_status_label("PO Received"): df[df['Order Status'] == 'PO Received'].shape[0],  # Ajout de PO Received
        get_status_label("Order Complete"): df[df['Order Status'] == 'Order Complete'].shape[0]  # Ajout de Order Complete
    }
    status_fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()),
                        title="Répartition des statuts des commandes", hole=0.3)

    product_values = df['Product Line'].value_counts().to_dict()
    product_fig = px.pie(values=list(product_values.values()), names=list(product_values.keys()),
                         title="Nombres de produits par nom", hole=0.3)

    garanty_values = df['Warranty Status'].value_counts()
    garanty_fig = px.bar(x=garanty_values.index, y=garanty_values.values, labels={'x': 'Equipements', 'y': 'Garantie'})

    # Obtenir les valeurs uniques pour la période sélectionnée
    if period == 'month':
        options = df['Created Date'].dt.strftime('%Y-%m').unique()
    elif period == 'quarter':
        options = df['Created Date'].dt.to_period('Q').astype(str).unique()
    elif period == 'year':
        options = df['Created Date'].dt.year.astype(str).unique()

    # Rendre les menus de sélection de période visibles
    style = {'display': 'block'} if period else {'display': 'none'}

    # Initialiser le graphique Free/Chargeable avec une valeur par défaut
    free_chargeable_fig = px.pie(values=[1], names=['No Data'], title="Répartition Free/Chargeable", hole=0.3)

    # Si une période et une date sont sélectionnées, filtrer les données pour Free/Chargeable uniquement
    if selected_date:
        if period == 'month':
            filtered_df = df[df['Created Date'].dt.strftime('%Y-%m') == selected_date]
        elif period == 'quarter':
            filtered_df = df[df['Created Date'].dt.to_period('Q').astype(str) == selected_date]
        elif period == 'year':
            filtered_df = df[df['Created Date'].dt.year.astype(str) == selected_date]

        # Mettre à jour le graphique Free/Chargeable avec les données filtrées
        free_chargeable_counts = filtered_df['Free/Chargeable'].value_counts()
        free_chargeable_fig = px.pie(values=free_chargeable_counts.values, names=free_chargeable_counts.index,
                                     title=f"Répartition Free/Chargeable ({selected_date})", hole=0.3)

    # Créer la navbar avec les boutons pour chaque produit
    product_navbar = [
        html.Button(
            f"{product} ({count})",
            id={'type': 'product-button', 'index': product},
            n_clicks=0,
            style={'margin': '5px', 'padding': '10px', 'border-radius': '5px', 'background-color': '#f0f0f0'}
        )
        for product, count in df['Product Line'].value_counts().items()
    ]

    # Créer le graphique d'évolution initial (tous produits)
    evolution_df = df.resample('ME', on='Created Date').size().reset_index(name='count')
    initial_evolution_fig = px.bar(
        evolution_df, 
        x='Created Date', 
        y='count', 
        title="Évolution du nombre d'appareils (tous produits)"
    )

    return [
        dcc.Graph(figure=order_type_fig),
        dcc.Graph(figure=status_fig),
        dcc.Graph(figure=product_fig),
        dcc.Graph(figure=garanty_fig),
        dcc.Graph(figure=free_chargeable_fig)  # Ajouter le nouveau graphique
    ], style, [{'label': d, 'value': d} for d in sorted(options)], product_navbar, initial_evolution_fig, alert_message, alert_style

# Callback pour mettre à jour le graphique d'évolution du produit sélectionné
@app.callback(
    [Output('product-evolution-chart', 'figure'),
     Output('product-evolution-container', 'style')],
    [Input({'type': 'product-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [Input('upload-data', 'contents')]
)
def update_product_evolution(n_clicks, contents):
    if not contents:
        return px.bar(), {'display': 'none'}

    # Vérifier si un bouton a été cliqué
    ctx = dash.callback_context
    if not ctx.triggered:
        return px.bar(), {'display': 'none'}
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Si le déclencheur est le téléchargement du fichier et non un bouton, retourner un graphique vide
    if button_id == 'upload-data':
        return px.bar(), {'display': 'none'}
    
    # Décoder le fichier Excel téléchargé
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))

    # Convertir les dates pour la gestion des périodes
    df['Created Date'] = pd.to_datetime(df['Created Date'])

    # Trouver le produit sélectionné
    product = eval(button_id)['index']

    # Filtrer les données pour le produit sélectionné
    filtered_df = df[df['Product Line'] == product]

    # Grouper par mois et compter le nombre d'appareils
    evolution_df = filtered_df.resample('ME', on='Created Date').size().reset_index(name='count')

    # Créer le graphique en barres
    fig = px.bar(evolution_df, x='Created Date', y='count', title=f"Évolution du nombre d'appareils pour {product}")
    return fig, {'display': 'block'}

if __name__ == '__main__':
    app.run_server(debug=True)