import os, json, platform, random, string
from bottle import route, run, template, request, static_file
from PIL import Image
from urllib.parse import unquote, quote

# Définition des variables

system = platform.system()
dossier_config = os.path.join(os.path.expanduser("~"), ".hiveasset")
fichier_config = os.path.join(dossier_config, "config.json")
fichier_scan = os.path.join(dossier_config, "scan.json")
fichier_cache = os.path.join(dossier_config, "cache.json")
cache_folder = os.path.join(dossier_config, "cache")
TYPES_DE_FICHIERS = { # Ici est défini tout les fichiers qui sont pris en charge par le logiciel
    "jpg": "Texture",
    "jpeg": "Texture",
    "png": "Texture",
    "tif": "Texture",
    "tiff": "Texture",
    "bmp": "Texture",
    "tga": "Texture",
    "dds": "Texture",
    "exr": "Texture",
    "svg": "Texture",
    "obj": "Mesh",
    "fbx": "Mesh",
    "stl": "Mesh",
    "ply": "Mesh",
    "gltf": "Mesh",
    "glb": "Mesh",
    "dae": "Mesh",
}
DEFAULT_CONFIG = { # Ici est défini la configuration par défaut du logiciel
        "os": system,
        "scan_directory": [],
        "3Dviewerhdrname": "BaseHDR.hdr",
        "ignoreunknownfiles": True,
        "openwebpageonload": True,
        "filter_texturessizes": ["128 x 128", "256 x 256", "512 x 512", "1024 x 1024", "2048 x 2048"]
}
DONNEES_SCAN = { # Ici est défini la configuration du fichier de scan, il n'est pas utile pour le moment
    "Textures" : [],
    "Mesh" : [],
    "Unknown" : []
}
ASSETS_TYPES = ["Textures", "Models"] # Ici est défini le type d'assets qui peut s'afficher dqns les filtres, n'est pas utile pour le moment
DONNEES_CACHE = { # Ici est défini le fichier servant de cache au logiciel, il garde en mémoire les textures non compatibles avec les navigateurs qui ont étés converties par le programme afin de les afficher correctement.
    "cache" : [],
    "preview_cache": []
}

# Définition des fonctions

def verif_fichier_config(): # Cette fonction vérifie si les dossiers du logiciel existent, elle vérifie aussi si le fichier de configuration existe et est a jour, elle le met a jour si il manque des données. 
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

def creer_scanfile(): # Cette fonction crée le fichier de scan si il existe pas
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(DONNEES_SCAN, f, indent=4)

def lire_config(): # Cette fonction permet de lire le fichier de configuration
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
    
def lire_cachefile(): # Cette fonction permet de lire le fichier de cache
    if os.path.exists(fichier_cache):
        with open(fichier_cache, "r", encoding="utf-8") as f:
            try: 
                out = json.load(f)
            except json.JSONDecodeError:
                verif_fichier_config()
                out = json.load(f)
            return out
    else:
        return None
    
def modifier_config(cle, valeur): # Cette fonction permet de modifier le fichier de configuration
    config = lire_config()
    if config is None:
        config = {}
    config[cle] = valeur
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def modifier_cachefile(cle, valeur): # Cette fonction permet de modifier le fichier de cache
    cache = lire_cachefile()
    if cache is None:
        cache = {}
    cache[cle] = valeur
    with open(fichier_cache, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

def liste_des_fichiers(): # Cette fonction permet de faire une liste de tout les fichiers se trouvant dans les dossiers a scanner (Ces dossiers sont enregistrés dans le fichier de configuration)
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

# Autre code

verif_fichier_config()
if not os.path.exists(fichier_cache): # Vérifie si le fichier de cache existe
        with open(fichier_cache, "w", encoding="utf-8") as f:
            json.dump(DONNEES_CACHE, f, indent=4)
if lire_config().get("openwebpageonload") == True: # Ouvre la page du navigateur si la configuration l'autorise
    if system == "Windows": # Execute une commande différente en fonction de l'os installé sur la machine
        os.system("start http://localhost:8080")
    else :
        os.system("open http://localhost:8080")

# Définition des routes

@route('/')
def home():
    return template("home.html", liste_des_fichiers = liste_des_fichiers(), files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)

@route('/recherche', method=['POST'])
def recherche():
    file_list = liste_des_fichiers()
    search_query = request.forms.get('search_query') # recupere ce qui est taper dans le formulaire
    if not search_query: # si il n'y a pas de recherche ou que le fichier rechercher n'existe pas
        # ca sort tout les trucs qu'il y a
        return template("home.html", liste_des_fichiers = file_list, files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)
    else:
        fich_trouv=[] # sinon ca cree une liste
        for f in file_list:# boucle d'explo
            if search_query.lower() in f[0].lower():# si la recherche en minuscule est dans le fichier ca l'apprend a la 
                # liste et a la fin ca sort juste la liste
                fich_trouv.append(f)
        if fich_trouv == []:
            fich_trouv = file_list
        return template("home.html", liste_des_fichiers = fich_trouv, files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)

@route('/model_loader_iframe/<type>/<path:path>/<filename>')
def model_loader_iframe(type, path, filename):
    path = unquote(path)
    filename = unquote(filename)
    file_path = os.path.join(path, filename).replace("\\", "/")
    hdr = lire_config().get("3Dviewerhdrname", "")
    if not os.path.exists(os.path.join("static/3dviewer/hdr/", hdr)):
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
    if type == "Texture":
        texture = file_path
        model = ""
    else:
        texture = ""
        model = file_path
    typef = type
    return template("model_loader.html", hdr = hdr, model = quote(model), texture = quote(texture), typef = typef)

@route('/settings', method=["GET", "POST"])
def settings():
    hdrs = []
    environmentos = lire_config().get("os", None)
    try:
        if os.listdir("./static/3dviewer/hdr") != "":
            for f in os.listdir("./static/3dviewer/hdr"):
                file_extension = f.lower().split(".")[-1]
                if file_extension == "hdr" or file_extension == "hdri":
                    if os.path.isfile(os.path.join("./static/3dviewer/hdr", f)):
                        hdrs.append(f)
    except FileNotFoundError as e:
        hdrs = []
        print("Erreur :", e)
    hdr = lire_config().get("3Dviewerhdrname", "")
    if hdr not in hdrs:
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
    ignoreunknownfiles = lire_config().get("ignoreunknownfiles", True)
    openwebpageonload = lire_config().get("openwebpageonload", True)
    dirconfig = list(lire_config().get("scan_directory", []))
    iuf = "checked"
    owpol = "checked"

    action = request.forms.get("action")

    if action == "add_repertoire":
        repertoire = str(request.forms.get("repertoire"))
        repertoire = repertoire.replace('"', '').replace("'", '')
        if repertoire not in dirconfig and repertoire != "":
            dirconfig.append(repertoire)
            modifier_config("scan_directory", dirconfig)
    
    elif action == "del_repertoire":
        delete = request.forms.get("dir_delete")
        if delete and delete in dirconfig:
            dirconfig.remove(delete)
            modifier_config("scan_directory", dirconfig)

    elif action == "remove_hdr":
        modifier_config("3Dviewerhdrname", "")
        hdr = ""

    elif action == "save_options":
        returnignoreunknownfiles = request.forms.get("ignoreunknownfiles", False)
        modifier_config("ignoreunknownfiles", bool(returnignoreunknownfiles == 'True'))
        ignoreunknownfiles = lire_config().get("ignoreunknownfiles", True)
        returnopenwebpageonload = request.forms.get("openwebpageonload", False)
        modifier_config("openwebpageonload", bool(returnopenwebpageonload == 'True'))
        openwebpageonload = lire_config().get("openwebpageonload", True)

        hdrselect = request.forms.get("select_hdr")
        if hdrselect and hdrselect in hdrs:
            modifier_config("3Dviewerhdrname", hdrselect)
            hdr = lire_config().get("3Dviewerhdrname", None)

    if ignoreunknownfiles == False:
        iuf = ""
    if openwebpageonload == False:
        owpol = ""
    
    return template("settings.html", scan_dir = dirconfig, os = environmentos, hdrs = hdrs, hdr = hdr, iuf = iuf, owpol = owpol)

@route('/texturesfiles/<path:path>/<filename>')
def textures_files(path, filename):
    path = unquote(path)
    filename = unquote(filename)
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        return "Fichier introuvable", 404
    for l in lire_cachefile().get("preview_cache", None):
        if file_path in l:
            for k, v in l.items():
                if not os.path.exists(v):
                    break
                else:
                    return static_file(v, root=cache_folder)
        
    extension = filename.lower().split('.')[-1]
    types = ["tif", "tiff", "tga", "dds", "exr"]

    if extension in types:
        try:
            with Image.open(file_path) as i:
                i = i.convert("RGBA")
                
                newname = ""
                cachelist = lire_cachefile().get("preview_cache")

                while newname == "" or newname in cachelist:
                    liste = random.choices(string.ascii_lowercase, k=10)
                    for l in liste:
                        newname += l
                newname = (newname + ".png")

                cache_path = os.path.join(cache_folder, newname)

                old_cache = list(lire_cachefile().get("preview_cache"))
                old_cache.append({file_path: cache_path})

                i.save(cache_path, format="PNG")
                modifier_cachefile("preview_cache", old_cache)

                return static_file(newname, root=cache_folder)
            
        except Exception as e:
            return "Erreur {e}", 500

    return static_file(filename, root=path)

# Route vers les dossiers contenus dans static

@route('/static/<path:path>/<filename>')
def server_static(path, filename):
    return static_file(filename, root=('./static/' + path))

# Route pour les previews des textures sur la page web

@route('/texturespreview/<path:path>/<filename>')
def textures_preview(path, filename):
    file_path = os.path.join(path, filename).replace("\\", "/")

    if not os.path.exists(file_path):
        return "Fichier introuvable", 404
    for l in lire_cachefile().get("cache", None):
        if file_path in l:
            for k, v in l.items():
                if not os.path.exists(v):
                    break
                else:
                    return static_file(v, root=cache_folder)
        
    extension = filename.lower().split('.')[-1]
    types = ["tif", "tiff", "tga", "dds", "exr"]

    if extension in types:
        try:
            with Image.open(file_path) as i:
                i = i.convert("RGBA")

                if i.size[0] > 128 or i.size[1] > 128:
                    i = i.resize((128, 128))
                
                newname = ""
                cachelist = lire_cachefile().get("cache")

                while newname == "" or newname in cachelist:
                    liste = random.choices(string.ascii_lowercase, k=10)
                    for l in liste:
                        newname += l
                newname = (newname + ".png")

                cache_path = os.path.join(cache_folder, newname)

                old_cache = list(lire_cachefile().get("cache"))
                old_cache.append({file_path: cache_path})

                i.save(cache_path, format="PNG")
                modifier_cachefile("cache", old_cache)

                return static_file(newname, root=cache_folder)
            
        except Exception as e:
            return "Erreur {e}", 500

    return static_file(filename, root=path)

@route('/openfileonsystem/<path:path>/<filename>') # Permet d'ouvrir l'explorateur de fichier avec le fichier préséléctionné (si possible)
def openfileonsystem(path, filename):
    if system == "Windows":
        file_path = unquote(os.path.join(path, filename).replace("/", "\\"))
        os.system(f'explorer /select, "{file_path}"')
    elif system == "Darwin":
        file_path = unquote(os.path.join(path, filename).replace("\\", "/"))
        os.system(["open", "-R", file_path])
    elif system == "Linux":
        file_path = unquote(os.path.join(path, filename).replace("\\", "/"))
        try:
            os.system("nautilus --browser " + file_path)
        except:
            os.system(f"xpg-open {file_path}")
    else:
        file_path = unquote(os.path.join(path, filename).replace("\\", "/"))
        os.system(f"xpg-open {file_path}")
    # Renvoie un script js pour fermer la page web
    return ''' 
    <html>
    <body>
        <script>
            window.onload = function() {
                window.close();
            };
        </script>
    </body>
    </html>
    '''
# Lancement du serveur Bottle
run(host="localhost", port="8080", debug=True, reloader=True)