# Structuration du projet HiveAssets

## 1. Présentation du projet
**HiveAssets** est une application web développée en python avec la librairie **Bottle**.  
Elle permet de lister, rechercher et visualiser des fichiers de différents types (modèles 3D, textures, etc.).  

Le projet repose sur ces trois fichiers python :
- `main.py`
- `constants.py`
- `config.py`

---

## 2. Description des fichiers

### `main.py`
Ce fichier est le **cœur** du projet. Il contient :
- **Les librairies nécessaires** : librairies utilisées (Bottle, Pillow, etc.).
- **Les fonctions principales** :
  - `creer_scanfile()` : Création du fichier de scan s'il n'existe pas.
  - `lire_cachefile()` : Lecture du fichier de cache.
  - `modifier_cachefile(cle, valeur)` : Modification du fichier de cache.
  - `liste_des_fichiers()` : Génération d'une liste des fichiers à scanner.
- **La gestion du serveur** : Démarrage de l'application avec `run(host="localhost", port="8080")`.
- **Les routes du serveur** : Fonctionnalités accessibles via l’interface web :
  - **Routes visuelles :**
    - `/` : Page d'accueil.
    - `/recherche` : Recherche de fichiers.
    - `/settings` : Configuration des paramètres utilisateur.
  - **Routes d'opérations en arrière plan**
    - `/texturesfiles/<path:path>/<filename>` : Récupération des fichiers textures.
    - `/texturespreview/<path:path>/<filename>` : Génération des aperçus de textures.
    - `/openfileonsystem/<path:path>/<filename>` : Ouverture d'un fichier dans l'explorateur.

---

### `constants.py`
Ce fichier définit **les variables** utilisées dans le projet.  
On y retrouve :
- `TYPES_DE_FICHIERS` : Contiens les types de fichiers pris en charge par le programme.
- `ASSETS_TYPES` : Contiens les types d'assets actuellements pris en charge par le programme.
- `DONNEES_SCAN` : Données de base pour le fichier de scan.
- `DONNEES_CACHE` : Données de base pour le cache.

---

### `config.py`
Ce fichier gère **les préférences de l'utilisateur**.  
Il contient :
- **Des fonctions pour manipuler la configuration** :
  - `verif_fichier_config()` : Vérification du fichier de configuration du logiciel.
  - `lire_config()` : Chargement de la configuration.
  - `modifier_config(cle, valeur)` : Modification d’un paramètre.

---

## 3. Fonctionnement global
1. **Démarrage** : `main.py` initialise le projet en vérifiant l’existence des fichiers de configuration.
2. **Scan des fichiers** : `liste_des_fichiers()` récupère les fichiers à afficher depuis le fichier de configuration.
3. **Interface web** :
   - L’utilisateur accède à l’application via son navigateur (`localhost:8080`).
   - Il peut rechercher des fichiers, les visualiser, modifier les paramètres, etc.
4. **Gestion des fichiers** :
   - Les fichiers sont stockés et organisés selon les constantes définies dans `constants.py`.
   - Les préférences utilisateurs sont sauvegardées dans `config.py`.

---

## 4. Conclusion
Le projet est structuré de manière modulaire :
- **`main.py`** : Gestion du serveur et des routes.
- **`constants.py`** : Définition des constantes.
- **`config.py`** : Configuration du projet.

En suivant cette documentation, il est possible de **reprendre et modifier facilement le projet** pour l’adapter à de nouveaux besoins.

---
