#Projet : HiveAssets
#Auteurs : Judicaël Lenglet, Ewan Jannot, Joan Molle, Maël Pouvreau
"""
ici se trouve toutes les routes ainsi que des fonctions
"""

# les importations necessaire au bon fonctionnement du site
import os, json, random, string, ffmpeg
from bottle import route, run, template, request, static_file, HTTPResponse
from PIL import Image
from urllib.parse import unquote, quote
from constants import *
from config import *

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Définition des fonctions

# Cette fonction crée le fichier de scan si il n'existe pas
def creer_scanfile(): 
    with open(fichier_config, "w", encoding="utf-8") as f:
        json.dump(DONNEES_SCAN, f, indent=4)
    
# Cette fonction permet de lire le fichier de cache
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
        return dict()

# Cette fonction permet de modifier le fichier de cache
def modifier_cachefile(cle, valeur): 
    cache = lire_cachefile()
    if cache is None:
        cache = {}
    cache[cle] = valeur
    with open(fichier_cache, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

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

# Autre code

verif_fichier_config()
if not os.path.exists(fichier_cache): # Vérifie si le fichier de cache existe
        with open(fichier_cache, "w", encoding="utf-8") as f:
            json.dump(DONNEES_CACHE, f, indent=4)

# Définition des routes

"""
route vers la page d'accueil
:return: la page d'accueil du site
"""
@route('/')
def home():
    return template("home.html", liste_des_fichiers = liste_des_fichiers(), files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)

"""
route de la barre de recherche
recupere ce qui est taper dans le formulaire (barre de recherche)
:return:renvoie la liste de touts les fichiers correspondants a la recherche formuler
"""
@route('/recherche', method=['POST'])
def recherche():
    file_list = liste_des_fichiers()
    search_query = request.forms.get('search_query') 
    if not search_query:
        return template("home.html", liste_des_fichiers = file_list, files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)
    else:
        fich_trouv=[]
        for f in file_list:
            if search_query.lower() in f[0].lower():
                fich_trouv.append(f)
        if fich_trouv == []:
            fich_trouv = file_list
        return template("home.html", liste_des_fichiers = fich_trouv, files_types = TYPES_DE_FICHIERS, filtertexturessizes = lire_config().get("filter_texturessizes", None), ASSETS_TYPES = ASSETS_TYPES)

"""
route qui permet d'afficher le viewer 3D pour visualiser les assets visuels
:return:sort soit le model soit la texture demander
"""
@route('/model_loader_iframe/<type>/<path:path>/<filename>') 
def model_loader_iframe(type, path, filename):
    path = unquote(path)
    filename = unquote(filename)
    file_path = os.path.join(path, filename).replace("\\", "/")
    hdr = lire_config().get("3Dviewerhdrname", "")
    if path == '"LOGO"' and filename == '"LOGO"':
        file_path = os.path.join(static_dir, "icons", "HiveAssets.png").replace("\\", "/")
    if not os.path.exists(os.path.join(hdr_dir, hdr)):
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

"""
route qui permet d'afficher les parametres et de configurer les preferences de l'utilisateurs
:return: renvoie la page avec les parametres voulu selectionner
"""
@route('/settings', method=["GET", "POST"]) 
def settings():
    iframereload = False
    hdrs = []
    environmentos = lire_config().get("os", None)
    try:
        if os.listdir(hdr_dir) != "":
            for f in os.listdir(hdr_dir):
                file_extension = f.lower().split(".")[-1]
                if file_extension == "hdr" or file_extension == "hdri":
                    if os.path.isfile(os.path.join(hdr_dir, f)):
                        hdrs.append(f)
    except FileNotFoundError as e:
        hdrs = []
        print("Erreur :", e)
    hdr = lire_config().get("3Dviewerhdrname", "")
    if hdr not in hdrs:
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
    ignoreunknownfiles = lire_config().get("ignoreunknownfiles", True)
    dirconfig = list(lire_config().get("scan_directory", []))
    iuf = "checked"

    action = request.forms.get("action")

    if action == "add_repertoire":
        repertoire = str(unquote(request.forms.get("repertoire")))
        repertoire = repertoire.replace('"', '')
        if repertoire not in dirconfig and repertoire != "":
            dirconfig.append(repertoire)
            modifier_config("scan_directory", dirconfig)
    
    elif action == "del_repertoire":
        delete = unquote(request.forms.get("dir_delete"))
        if delete and delete in dirconfig:
            dirconfig.remove(delete)
            modifier_config("scan_directory", dirconfig)

    elif action == "remove_hdr":
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
        iframereload = True

    elif action == "save_options":
        returnignoreunknownfiles = request.forms.get("ignoreunknownfiles", False)
        modifier_config("ignoreunknownfiles", bool(returnignoreunknownfiles == 'True'))
        ignoreunknownfiles = lire_config().get("ignoreunknownfiles", True)

        hdrselect = request.forms.get("select_hdr")
        if hdrselect and hdrselect in hdrs:
            modifier_config("3Dviewerhdrname", hdrselect)
            hdr = lire_config().get("3Dviewerhdrname", None)
            iframereload = True

    if ignoreunknownfiles == False:
        iuf = ""

    return template("settings.html", scan_dir = dirconfig, os = environmentos, hdrs = hdrs, hdr = hdr, iuf = iuf, iframereload = iframereload)

""""
route qui permet de renvoyer l'image originale demandée ou l'image convertie
:return: renvoi l'image original ou convertie pqr le programme
"""
@route('/texturesfiles/<path:path>/<filename>') 
def textures_files(path, filename):
    path = os.sep.join([*unquote(path).split("/")])
    filename = unquote(filename)
    file_path = os.path.join("\\", path, filename)
    if not os.path.exists(file_path):
        raise HTTPResponse("non trouvé", status=404)
    for l in lire_cachefile().get("preview_cache", list()):
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
                cachelist = lire_cachefile().get("preview_cache", [])

                while newname == "" or newname in cachelist:
                    liste = random.choices(string.ascii_lowercase, k=10)
                    for l in liste:
                        newname += l
                newname = (newname + ".png")

                cache_path = os.path.join(cache_folder, newname)

                old_cache = list(lire_cachefile().get("preview_cache", []))
                old_cache.append({file_path: cache_path})

                i.save(cache_path, format="PNG")
                modifier_cachefile("preview_cache", old_cache)

                return static_file(newname, root=cache_folder)
            
        except Exception as e:
            return "Erreur {e}", 500
    return static_file(filename, root=os.path.dirname(file_path))

"""
route qui permet d'obtenir un fichier grâce a son lien
:return: renvoie un fichier contenu dans le dossier static du programme
"""
@route('/static/<path:path>/<filename>') 
def server_static(path, filename):
    return static_file(filename, root=os.path.join(static_dir, path))

"""
Route pour les previews des textures sur la page web
Permet d'obtenir une image a prévisualiser, si le format est inconnu le fichier est converti avec une taille de 128px par 128px
:return: renvoie soit une image convertie soit l'original en 128px*128px
"""
@route('/texturespreview/<path:path>/<filename>') 
def textures_preview(path, filename):
    file_path = os.path.join(path, filename).replace("\\", "/")

    if not os.path.exists(file_path):
        raise HTTPResponse("Texture non trouvé", status=404)
    for l in lire_cachefile().get("cache", list()):
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
                cachelist = lire_cachefile().get("cache", [])

                while newname == "" or newname in cachelist:
                    liste = random.choices(string.ascii_lowercase, k=10)
                    for l in liste:
                        newname += l
                newname = (newname + ".png")

                cache_path = os.path.join(cache_folder, newname)

                old_cache = list(lire_cachefile().get("cache", []))
                old_cache.append({file_path: cache_path})

                i.save(cache_path, format="PNG")
                modifier_cachefile("cache", old_cache)

                return static_file(newname, root=cache_folder)
            
        except Exception as e:
            return "Erreur {e}", 500

    return static_file(filename, root=path)
 
"""
Permet d'ouvrir l'explorateur de fichier avec le fichier préséléctionné (si possible)
:return: nous ouvre l'explorer avec le fichier présélectionner si  disponible
"""
@route('/openfileonsystem/<path:path>/<filename>') 
def openfileonsystem(path, filename):
    if system == "Windows":
        file_path = unquote(os.path.join(path, filename).replace("/", "\\"))
        os.system(f'explorer /select, "{file_path}"')
    elif system == "Darwin":
        file_path = unquote(os.path.join(path, filename).replace("\\", "/"))
        os.system(f'open -R "{file_path}"')
    elif system == "Linux":
        file_path = unquote(os.path.join(path, filename).replace("\\", "/"))
        environnement = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        print(environnement)
        if "gnome" in environnement :
            os.system(f'nautilus --browser "{file_path}"')
        elif "xcfe" in environnement :
            os.system(f'thunar "{file_path}')
        elif "lxde" in environnement :
            os.system(f'pacmanfm "{file_path}"')
        elif "cinnamon" in environnement :
            os.system(f'nemo "{file_path}"')
        if "unity" in environnement :
            os.system(f'nautilus --browser "{file_path}"')
        else:
            os.system(f'xdg-open "{file_path}"')
    else:
        file_path = unquote(os.path.join(path, filename).replace("\\", "/"))
        os.system(f'xdg-open "{file_path}"')
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

@route('/getaudiofile/<path:path>/<filename>') 
def getaudiofile(path, filename):
    path = os.sep.join([*unquote(path).split("/")])
    filename = unquote(filename)
    file_path = os.path.join("\\", path, filename)
    if not os.path.exists(file_path):
        raise HTTPResponse("Sound Wave non trouvé", status=404)
    for l in lire_cachefile().get("audio_cache", list()):
        if file_path in l:
            for k, v in l.items():
                if not os.path.exists(v):
                    break
                else:
                    return static_file(v, root=cache_folder)
    extension = filename.lower().split('.')[-1]
    types = ["wav", "ogg", "flac", "aac"]

    if extension in types:
        try:
            newname = ""
            cachelist = lire_cachefile().get("audio_cache", [])

            while newname == "" or newname in cachelist:
                liste = random.choices(string.ascii_lowercase, k=10)
                for l in liste:
                    newname += l
            newname = (newname + ".mp3")

            cache_path = os.path.join(cache_folder, newname)
            old_cache = list(lire_cachefile().get("audio_cache", []))
            old_cache.append({file_path: cache_path})

            ffmpeg.input(file_path).output(cache_path, audio_bitrate='192k').run(overwrite_output=True)
            return static_file(newname, root=cache_folder)
        except ffmpeg.Error as e:
            print(f"Erreur FFmpeg : {e}")
            raise HTTPResponse((f"Erreur FFmpeg : {e}"), status=404)
    return static_file(filename, root=os.path.dirname(file_path))

@route("/ping")
def ping():
    return "pong"

# Execution du serveur Bottle
run(host="localhost", port=5069)