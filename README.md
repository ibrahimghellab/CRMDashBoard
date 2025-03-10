# 📊 Tableau de Bord de Service

## 📝 Description

Ce projet est une application web interactive développée avec **Dash** et **Plotly** qui permet de visualiser et analyser les données de commandes de service à partir de fichiers Excel. L'application comprend différentes fonctionnalités, notamment l'affichage de tableaux interactifs, des graphiques dynamiques et des statistiques clés sur les commandes.

## 🚀 Fonctionnalités

- 📂 **Téléchargement de fichier Excel** : Permet de charger un fichier contenant les données des commandes.
- 📊 **Tableau de bord** : Présente des KPI clés et des graphiques analytiques.
- 🔎 **Suivi des commandes** : Liste les commandes nécessitant une attention particulière avec des codes couleur pour identifier les urgences.
- 🎛️ **Filtres dynamiques** : Possibilité de filtrer les données par période et par statut.
- 📈 **Graphiques interactifs** : Utilisation de **Plotly** pour générer des visualisations détaillées.

## 🛠️ Technologies utilisées

- 🐍 **Python**
- 🎨 **Dash**
- 📊 **Plotly**
- 📑 **Pandas**
- 🖥️ **HTML/CSS**

## ⚙️ Installation

### ❌ Si pas d'exécutable :

1. 📥 Cloner ce dépôt :
   ```sh
   git clone https://github.com/votre-repo/tableau-de-bord-service.git
   cd tableau-de-bord-service
   ```
2. 📦 Installer les dépendances :
   ```sh
   pip install -r requirements.txt
   ```
3. ▶️ Lancer l'application :
   ```sh
   python final.py
   ```
4. 🌐 Ouvrir un navigateur et accéder à :
   ```
   http://127.0.0.1:8050
   ```

### ✅ Si exécutable :

1. ▶️ Lancer l'application :
   ```sh
   ./final.exe
   ```
2. 🌐 Ouvrir un navigateur et accéder à :
   ```
   http://127.0.0.1:8050
   ```
3. 📂 Charger un fichier Excel respectant la structure ci-dessous.

## 📑 Structure du fichier Excel

Le fichier Excel doit contenir au minimum les colonnes suivantes :

- 🔢 **Order No.**
- 🏢 **Customer Name**
- 👨‍🔧 **Service Technician**
- 🏷️ **Model**
- 📌 **Order Status**
- 📅 **Created At**
- ✅ **Approved Date**
- ⏳ **Task Completed Date**
- 🎯 **Order Completed Date**
- ⏳ **Waiting for PO At**
- ⚙️ **In Work At**
- 🔧 **Wf. Part At(H)**
- ⛔ **Suspension At**

## 🤝 Contributions

Les contributions sont les bienvenues ! Merci de créer une branche et soumettre une **pull request** avec vos améliorations.


