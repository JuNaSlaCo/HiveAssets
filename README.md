# HiveAssets
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

HiveAssets est un gestionnaire d'assets (textures, modèles, etc.) permettant d'organiser et de centraliser divers fichiers multimédias.

## Installation et Utilisation

### Versions et Releases
Les versions compilées de HiveAssets sont disponibles dans la section **Releases** du dépôt GitHub. Vous pouvez les télécharger directement et les exécuter sans installation supplémentaire.

Si vous souhaitez modifier le programme ou explorer son fonctionnement, vous pouvez télécharger l'archive du code source directement depuis GitHub.

## Installation pour le Développement

### Prérequis
Avant de commencer, assurez-vous d'avoir installé :
- **Node.js** (version recommandée : LTS)
- **Python 3.10 ou plus**
- **pip** et **virtualenv** (pour l'environnement Python)

### 1. Cloner le Dépôt
```sh
git clone https://github.com/JuNaSlaCo/HiveAssets.git
cd HiveAssets
```

### 2. Installation des Dépendances

#### Côté Serveur Python
Le serveur est basé sur **Bottle** et se trouve dans le dossier `bottle_server`.
```sh
cd bottle_server
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```
Le fichier principal est `server.py` :
- Il contient toutes les routes web du serveur ainsi que la logique des scans de fichiers.
- Le fichier `constants.py` regroupe toutes les variables globales.
- Le fichier `config.py` contient toutes les fonctions de configuration du serveur.

Vous pouvez visualiser le serveur en tapant `localhost:5069` dans votre navigateur.

Pour construire le serveur, exécutez :
```sh
build_tools/build_server.bat
```

#### Côté Interface Electron
L'interface utilisateur repose sur **Electron.js**. Pour installer les dépendances :
```sh
npm install
```
Le fichier principal **`main.js`** gère l'initialisation de l'application et la communication avec le serveur Bottle.
Le fichier **`loader.html`** permet d'afficher un écran de chargement en attendant que le serveur soit prêt.

### 3. Lancer l'Application en Mode Développement

#### Démarrer le Serveur Bottle
```sh
cd bottle_server
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
python server.py
```

#### Démarrer l'Application Electron
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

## Commandes npm du projet

- **npm start** : permet de lancer l'application electron
- **npm build** : Permet de construire le projet
- **npm run publish** : Permet de publier le projet sur votre repository GitHub (il faut modifier les informations dans `package.json`)
## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/NaweDev"><img src="https://avatars.githubusercontent.com/u/96984101?v=4?s=100" width="100px;" alt="Nawe_Dev"/><br /><sub><b>Nawe_Dev</b></sub></a><br /><a href="https://github.com/JuNaSlaCo/HiveAssets/commits?author=NaweDev" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Cocoagneau"><img src="https://avatars.githubusercontent.com/u/201631272?v=4?s=100" width="100px;" alt="Cocoagneau"/><br /><sub><b>Cocoagneau</b></sub></a><br /><a href="#ideas-Cocoagneau" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Slayjojo"><img src="https://avatars.githubusercontent.com/u/201461005?v=4?s=100" width="100px;" alt="Slayjojo"/><br /><sub><b>Slayjojo</b></sub></a><br /><a href="#ideas-Slayjojo" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ju-78"><img src="https://avatars.githubusercontent.com/u/201461159?v=4?s=100" width="100px;" alt="Ju-78"/><br /><sub><b>Ju-78</b></sub></a><br /><a href="#ideas-Ju-78" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td align="center" size="13px" colspan="7">
        <img src="https://raw.githubusercontent.com/all-contributors/all-contributors-cli/1b8533af435da9854653492b1327a23a4dbd0a10/assets/logo-small.svg">
          <a href="https://all-contributors.js.org/docs/en/bot/usage">Add your contributions</a>
        </img>
      </td>
    </tr>
  </tfoot>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!