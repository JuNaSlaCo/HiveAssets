#Projet : HiveAssets
#Auteurs : Judicaël Lenglet, Ewan Jannot, Joan Molle, Maël Pouvreau
from constants import *
import json, os
def verif_fichier_config(): 
    """
    Cette fonction vérifie si les dossiers du logiciel existent, 
    elle vérifie aussi si le fichier de configuration existe et est a jour, elle le met a jour si il manque des données. 
    """    
    os.makedirs(dossier_config, exist_ok=True)
    os.makedirs(cache_folder, exist_ok=True)
    if not os.path.exists(fichier_config):
        with open(fichier_config, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    else:
        with open(fichier_config, "r+", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                json.dump(DEFAULT_CONFIG, f, indent=4)
                config = DEFAULT_CONFIG.copy()
        maj = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                maj = True
        if maj == True:
            with open(fichier_config, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print("Fichier de configuration mis a jour !")

def lire_config(): 
    """
    Cette fonction permet de lire le fichier de configuration
    :return: Renvoie le contenu du fichier de configuration, None si non trouvé
    """
    if os.path.exists(fichier_config):
        with open(fichier_config, "r", encoding="utf-8") as f:
            try: 
                out = json.load(f)
            except json.JSONDecodeError:
                verif_fichier_config()
                out = json.load(f)
            return out
    else:
        return None
    
def modifier_config(cle, valeur): 
    """
    Cette fonction permet de modifier le fichier de configuration
    """
    config = lire_config()
    if config is None:
        config = {}
    config[cle] = valeur
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)