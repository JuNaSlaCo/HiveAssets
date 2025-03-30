# HiveAssets

HiveAssets est un gestionnaire d'assets (textures, modèles, etc.) permettant d'organiser et de centraliser divers fichiers multimédias.

## Installation pour le développement

### Prérequis
Avant de commencer, assurez-vous d'avoir installé :
- **Node.js** (version recommandée : LTS)
- **Python 3**
- **pip** et **virtualenv** (pour l'environnement Python)

### 1. Cloner le dépôt
```sh
git clone https://github.com/JuNaSlaCo/HiveAssets.git
cd HiveAssets
```

### 2. Installation des dépendances
#### Côté Electron
```sh
npm install
```

#### Côté Serveur Python
```sh
cd bottle_server
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Lancer l'application en mode développement
#### Démarrer le serveur Bottle
```sh
cd bottle_server
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
python server.py
```

#### Démarrer l'application Electron
Dans un autre terminal :
```sh
npm start
```

## Compilation & Build
Des scripts de build sont fournis pour compiler l'application selon votre OS :
- **Windows** : `build_electron_win.bat`
- **Linux** : `build_electron_linux.bat` (non testé)
- **Mac** : `build_electron_mac.bat` (non testé)
- **Tous** : `build_electron_all.bat` (non testé)
- **Serveur** : `build_server.bat`

## Releases
Les versions compilées de HiveAssets sont disponibles dans la section **Releases** du dépôt GitHub.