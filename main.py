import os, json, platform, random, string
from bottle import route, run, template, request, static_file
from PIL import Image

# Définition des variables

dossier_config = os.path.join(os.path.expanduser("~"), ".hiveasset")
fichier_config = os.path.join(dossier_config, "config.json")
fichier_scan = os.path.join(dossier_config, "scan.json")
fichier_cache = os.path.join(dossier_config, "cache.json")
cache_folder = os.path.join(dossier_config, "cache")
TYPES_DE_FICHIERS = {
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
DEFAULT_CONFIG = {
        "os": platform.system(),
        "scan_directory": [],
        "3Dviewerhdrname": "",
        "ignoreunknownfiles": True,
        "openwebpageonload": True,
        "filter_texturessizes": ["128 x 128", "256 x 256", "512 x 512", "1024 x 1024", "2048 x 2048"]
}
DONNEES_SCAN = {
    "Textures" : [],
    "Mesh" : [],
    "Unknown" : []
}
ASSETS_TYPES = ["Textures", "Models"]
DONNEES_CACHE = {
    "cache" : [],
    "preview_cache": []
}

# Définition des fonctions

def verif_fichier_config():
    os.makedirs(cache_folder, exist_ok=True)
    os.makedirs(dossier_config, exist_ok=True)
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

def creer_scanfile():
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(DONNEES_SCAN, f, indent=4)

def lire_config():
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
    
def lire_cachefile():
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
    
def modifier_config(cle, valeur):
    config = lire_config()
    if config is None:
        config = {}
    config[cle] = valeur
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def modifier_cachefile(cle, valeur):
    cache = lire_cachefile()
    if cache is None:
        cache = {}
    cache[cle] = valeur
    with open(fichier_cache, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

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

# Autre code

verif_fichier_config()
if not os.path.exists(fichier_cache):
        with open(fichier_cache, "w", encoding="utf-8") as f:
            json.dump(DONNEES_CACHE, f, indent=4)
if lire_config().get("openwebpageonload") == True:
    os.system("start http://localhost:8080")

# Définition des routes

@route('/')
def home():
    return template("home.html", liste_des_fichiers = liste_des_fichiers(), files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)

@route('/model_loader_iframe/<type>/<path:path>/<filename>')
def model_loader_iframe(type, path, filename):
    file_path = os.path.join(path, filename).replace("\\", "/")
    hdr = lire_config().get("3Dviewerhdrname", "")
    if type == "Texture":
        texture = file_path
        model = ""
    else:
        texture = ""
        model = file_path
    typef = type
    print(texture, typef)
    return template("model_loader.html", hdr = hdr, model = model, texture = texture, typef = typef)

@route('/settings', method=["GET", "POST"])
def settings():
    environmentos = lire_config().get("os", None)
    hdrs = [f for f in os.listdir("./static/3dviewer/hdr") if os.path.isfile(os.path.join("./static/3dviewer/hdr", f))]
    hdr = lire_config().get("3Dviewerhdrname", "")
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

    elif action == "select_hdr":
        hdrselect = request.forms.get("hdrselect")
        if hdrselect and hdrselect in hdrs:
            modifier_config("3Dviewerhdrname", hdrselect)
            hdr = lire_config().get("3Dviewerhdrname", None)

    elif action == "remove_hdr":
        modifier_config("3Dviewerhdrname", "")
        hdr = lire_config().get("3Dviewerhdrname", "")

    elif action == "save_global_options":
        returnignoreunknownfiles = request.forms.get("ignoreunknownfiles", False)
        modifier_config("ignoreunknownfiles", bool(returnignoreunknownfiles == 'True'))
        ignoreunknownfiles = lire_config().get("ignoreunknownfiles", True)
        returnopenwebpageonload = request.forms.get("openwebpageonload", False)
        modifier_config("openwebpageonload", bool(returnopenwebpageonload == 'True'))
        openwebpageonload = lire_config().get("openwebpageonload", True)

    if ignoreunknownfiles == False:
        iuf = ""
    if openwebpageonload == False:
        owpol = ""
    
    return template("settings.html", scan_dir = dirconfig, os = environmentos, hdrs = hdrs, hdr = hdr, iuf = iuf, owpol = owpol)

@route('/texturesfiles/<path:path>/<filename>')
def textures_files(path, filename):
    file_path = os.path.join(path, filename)
    print(path, filename, file_path)
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

@route('/openfileonsystem/<path:path>/<filename>')
def openfileonsystem(path, filename):
    file_path = os.path.join(path, filename).replace("\\", "/")
    os.open(file_path)

# Lancement du serveur Bottle
run(host="localhost", port="8080", debug=True, reloader=True)