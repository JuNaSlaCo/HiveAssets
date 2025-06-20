#Projet : HiveAssets
#Auteurs : Judicaël Lenglet, Ewan Jannot, Joan Molle, Maël Pouvreau
from constants import *
from queue import Queue
from PIL import Image
from bottle import HTTPResponse, TEMPLATE_PATH
import json, os, threading, json, time, random, string

queue = Queue()
def verif_data_files(): 
    """
    Cette fonction vérifie si les dossiers du logiciel existent, 
    elle vérifie aussi si le fichier de configuration existe et est a jour, elle le met a jour si il manque des données. 
    """    
    os.makedirs(dossier_config, exist_ok=True)
    os.makedirs(cache_folder, exist_ok=True)
    os.makedirs(hdri_folder, exist_ok=True)
    os.makedirs(themes_folder, exist_ok=True)
    if not os.path.exists(fichier_config):
        with open(fichier_config, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    else:
        with open(fichier_config, "r+", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                json.dump(DEFAULT_CONFIG, f, indent=4)
                config = DEFAULT_CONFIG
        maj = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                maj = True
        if maj == True:
            with open(fichier_config, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print("Fichier de configuration mis a jour !")
    if not os.path.exists(fichier_cache): # Vérifie si le fichier de cache existe
        with open(fichier_cache, "w", encoding="utf-8") as f:
            json.dump(DONNEES_CACHE, f, indent=4)

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
                verif_data_files() # On vérifie tout les fichiers car ce n'est pas normal d'obtenir une erreur ici
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

if system == "Windows":
    import pythoncom
    from win32com.shell import shell

    def reveal_in_explorer(file_path):
        pythoncom.CoInitialize()
        
        file_path = os.path.abspath(file_path)
        folder_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        folder_pidl, _ = shell.SHILCreateFromPath(folder_path, 0)

        desktop = shell.SHGetDesktopFolder()
        folder = desktop.BindToObject(folder_pidl, None, shell.IID_IShellFolder)

        item_pidl = folder.ParseDisplayName(0, None, file_name)[1]

        shell.SHOpenFolderAndSelectItems(folder_pidl, (item_pidl,), 0)

def worker():
    while True:
        filepath, size, cache_part = queue.get()
        convertimage(filepath, size, cache_part)
        queue.task_done()

def loadlocale():
    global locale
    setlocale = lire_config().get("locale")
    print(os.path.join(locales_dir, f"{setlocale}.json"))
    with open(os.path.join(static_dir, "locales", f"{setlocale}.json"), "r", encoding="utf-8") as f:
        try:
            out = json.load(f)
        except json.JSONDecodeError as e:
            print(e)
        locale = out

def getlocale(loc):
    cache = locale
    for l in loc.split("."):
        cache = cache[l]
    return cache

def getlocales():
    locales = []
    if os.listdir(locales_dir) != "":
            for f in os.listdir(locales_dir):
                file_extension = f.lower().split(".")[-1]
                if file_extension == "json":
                    if os.path.isfile(os.path.join(locales_dir, f)):
                        locales.append(f.split(".")[0])
    return locales

# Cette fonction crée le fichier de scan si il n'existe pas
def creer_scanfile(): 
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(DONNEES_SCAN, f, indent=4)
    
# Cette fonction permet de lire le fichier de cache
def lire_cachefile():
    global modifoncache, cachecontent
    if os.path.exists(fichier_cache):
        if modifoncache:
            with open(fichier_cache, "r", encoding="utf-8") as f:
                try: 
                    out = json.load(f)
                except json.JSONDecodeError:
                    verif_data_files()
                    out = json.load(f)
                modifoncache = False
                cachecontent = out
                return cachecontent
        else:
            return cachecontent
    else:
        verif_data_files()
        return dict()

# Ces fonctions permettent de modifier le cache ainsi que le fichier de cache
def modifier_cachefile():
    global modifiercache, cachecontent, modifoncache
    with threading.Lock():
        time.sleep(5)
        if not os.path.exists(fichier_config):
            verif_data_files()
            with open(fichier_cache, "w", encoding="utf-8") as f:
                json.dump(cachecontent, f, indent=4)
        else :
            with open(fichier_cache, "w", encoding="utf-8") as f:
                json.dump(cachecontent, f, indent=4)
        modifiercache = False
        modifoncache = True

def modifier_cache(cle, valeur, mainkey):
    global modifiercache
    print(cle, valeur)
    cachecontent[mainkey].append({cle: valeur})
    if not modifiercache:
        modifiercache = True
        threading.Thread(target=modifier_cachefile, daemon=True).start()

# Cette fonction permet de convertir des images

def convertimage(filepath, size, cache_part):
    try:
        with Image.open(filepath) as i:
            i = i.convert("RGBA")

            if size != -1:
                if i.size[0] > size or i.size[1] > size:
                    i = i.resize((size, size))
                
            newname = ""
            cachelist = lire_cachefile().get(cache_part, [])

            while newname == "" or newname in cachelist:
                liste = random.choices(string.ascii_lowercase, k=10)
                for l in liste:
                    newname += l
            newname = (newname + ".png")

            cache_path = os.path.join(cache_folder, newname)

            i.save(cache_path, format="PNG")
            modifier_cache(filepath, newname, cache_part)

    except Exception as e:
        raise HTTPResponse((f"Erreur lors de la conversion {e}"), status=500)

"""
Cette fonction permet de faire une liste de tout les fichiers se trouvant dans les dossiers a scanner 
(Ces dossiers sont enregistrés dans le fichier de configuration)
:return: renvoit la liste des fichiers present dans le dossier
"""
def liste_des_fichiers():
    list = []
    for dir in lire_config().get("scan_directory", []):
        for chemin, dir, fichiers in os.walk(dir):
            for fichier in fichiers:
                file_extension = fichier.lower().split(".")[-1]
                file_name = fichier.rsplit(".", 1)[0]
                if TYPES_DE_FICHIERS.get(file_extension, "Unknown") != "Unknown" and lire_config().get("ignoreunknownfiles") == True:
                    list.append([file_name, TYPES_DE_FICHIERS.get(file_extension, "Unknown"), (chemin + "\\" + fichier)])
                elif lire_config().get("ignoreunknownfiles") == False:
                    list.append([file_name, TYPES_DE_FICHIERS.get(file_extension, "Unknown"), (chemin + "\\" + fichier)])
    return list

def liste_des_themes():
    dirs = []
    for rep in os.listdir(themes_folder):
        if os.path.isdir(os.path.join(themes_folder, rep)) and os.path.exists(os.path.join(themes_folder, rep, "home.html")):
            dirs.append(rep)
    return dirs

def set_theme():
    theme_path = "C:\\Users\\Freddy Studio\\.hiveasset\\themes\\Nawe theme\\"
    if theme_path not in TEMPLATE_PATH:
        TEMPLATE_PATH.insert(0, theme_path)
    print("Thème changé :  ", theme_path)