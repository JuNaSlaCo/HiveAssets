#Projet : HiveAssets
#Auteurs : Judicaël Lenglet, Ewan Jannot, Joan Molle, Maël Pouvreau
"""
ici se trouve toutes les routes ainsi que des fonctions
"""

# les importations necessaire au bon fonctionnement du site
import os, json, random, string, ffmpeg, threading, time, subprocess
from bottle import route, run, template, request, static_file, HTTPResponse
from PIL import Image
from constants import *
from config import *
from base64 import urlsafe_b64decode, urlsafe_b64encode
from queue import Queue

queue = Queue()

# Définition des fonctions

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

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

for loop in range(NUM_WORKERS):
    threading.Thread(target=worker, daemon=True).start()



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
                    verif_fichier_config()
                    out = json.load(f)
                modifoncache = False
                cachecontent = out
                return cachecontent
        else:
            return cachecontent
    else:
        return dict()

# Ces fonctions permettent de modifier le cache ainsi que le fichier de cache
def modifier_cachefile():
    global modifiercache, cachecontent, modifoncache
    with threading.Lock():
        time.sleep(5)
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

# Autre code
verif_fichier_config()
if not os.path.exists(fichier_cache): # Vérifie si le fichier de cache existe
        with open(fichier_cache, "w", encoding="utf-8") as f:
            json.dump(DONNEES_CACHE, f, indent=4)

# Définition des routes

"""
route vers la page d'accueil
recupere ce qui est taper dans le formulaire (barre de recherche)
:return: la page d'accueil du site ou renvoie la liste de touts les fichiers correspondants a la recherche formuler
"""
@route('/', method=["GET", "POST"])
def home():
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
@route('/model_loader_iframe/<type>/<b64path>') 
def model_loader_iframe(type, b64path):
    type = urlsafe_b64decode(type.encode("ascii")).decode("utf-8").replace("\\", "/")
    file_path = urlsafe_b64decode(b64path.encode("ascii")).decode("utf-8").replace("\\", "/")
    hdr = lire_config().get("3Dviewerhdrname", "")
    if os.path.basename(file_path) == 'LOGO':
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
    return template("model_loader.html", hdr = hdr, model = urlsafe_b64encode(model.encode("utf-8")).decode("ascii"), texture = urlsafe_b64encode(texture.encode("utf-8")).decode("ascii"), typef = typef)

"""
route qui permet d'afficher les parametres et de configurer les preferences de l'utilisateurs
:return: renvoie la page avec les parametres voulu selectionner
"""
@route('/settings', method=["GET", "POST"]) 
def settings():
    global cachecontent
    iframereload = False
    reloadexplorer = False
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
    hdr = lire_config().get("3Dviewerhdrname", "")
    if hdr not in hdrs:
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
    ignoreunknownfiles = lire_config().get("ignoreunknownfiles", True)
    dirconfig = list(lire_config().get("scan_directory", []))
    iuf = "checked"

    action = request.forms.get("action")

    if action == "add_repertoire":
        repertoire = str(urlsafe_b64decode(request.forms.get("repertoirepath").encode("ascii")).decode("utf-8").replace("\\", "/"))
        repertoire = repertoire.replace('"', '')
        if repertoire not in dirconfig and repertoire != "":
            dirconfig.append(repertoire)
            modifier_config("scan_directory", dirconfig)
            reloadexplorer = True
    
    elif action == "del_repertoire":
        delete = str(urlsafe_b64decode(request.forms.get("dir_delete").encode("ascii")).decode("utf-8").replace("\\", "/"))
        if delete and delete in dirconfig:
            dirconfig.remove(delete)
            modifier_config("scan_directory", dirconfig)
            reloadexplorer = True

    elif action == "install_hdr":
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
        iframereload = True

    elif action == "uninstall_hdr":
        modifier_config("3Dviewerhdrname", "")
        hdr = ""
        iframereload = True

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
    
    elif action == "delete_cache":
        cachecontent = DONNEES_CACHE
        modifier_cachefile()
        for filename in os.listdir(cache_folder):
            os.remove(os.path.join(cache_folder, filename))

    if ignoreunknownfiles == False:
        iuf = ""

    return template("settings.html", scan_dir = dirconfig, os = environmentos, hdrs = hdrs, hdr = hdr, iuf = iuf, iframereload = iframereload, reloadexplorer = reloadexplorer, NUM_WORKERS = NUM_WORKERS)

""""
route qui permet de renvoyer l'image originale demandée ou l'image convertie
:return: renvoi l'image original ou convertie pqr le programme
"""
@route('/texturesfiles/<b64path>')
def textures_files(b64path):
    file_path = urlsafe_b64decode(b64path.encode("ascii")).decode("utf-8").replace("\\", "/")

    if not os.path.exists(file_path):
        raise HTTPResponse("non trouvé", status=404)
    for l in lire_cachefile().get("cache", list()):
        if file_path in l:
            for k, v in l.items():
                if not os.path.exists(os.path.join(cache_folder, v)):
                    break
                else:
                    return static_file(v, root=cache_folder)
    extension = file_path.lower().split('.')[-1]
    types = ["tif", "tiff", "tga", "dds", "exr"]

    if extension in types:
        threading.Thread(target=convertimage, args=(file_path, -1, "cache"), daemon=True).start()

        while True:
            for l in lire_cachefile().get("cache", list()):
                if file_path in l:
                    for p, v in l.items():
                        cached_path = os.path.join(cache_folder, v)
                        if os.path.exists(cached_path):
                            return static_file(v, root=cache_folder)
            time.sleep(0.5)

    return static_file(os.path.basename(file_path), root=os.path.dirname(file_path))

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
@route('/texturespreview/<b64path>')
def textures_preview(b64path):
    file_path = urlsafe_b64decode(b64path.encode("ascii")).decode("utf-8").replace("\\", "/")

    if not os.path.exists(file_path):
        raise HTTPResponse("Texture non trouvé", status=404)
    for l in lire_cachefile().get("preview_cache", list()):
        if file_path in l:
            for k, v in l.items():
                if not os.path.exists(os.path.join(cache_folder, v)):
                    break
                else:
                    return static_file(v, root=cache_folder)
        
    extension = file_path.lower().split('.')[-1]
    types = ["tif", "tiff", "tga", "dds", "exr"]

    if extension in types:
        file_deja_queue = any(file_path in task for task in list(queue.queue))
        if not file_deja_queue:
            queue.put((file_path, 128, "preview_cache"))
        raise HTTPResponse("Conversion en cours", status=202)

    return static_file(os.path.basename(file_path), root=os.path.dirname(file_path))
 
"""
Permet d'ouvrir l'explorateur de fichier avec le fichier préséléctionné (si possible)
:return: nous ouvre l'explorer avec le fichier présélectionner si  disponible
"""
@route('/openfileonsystem/<b64path>') 
def openfileonsystem(b64path):
    file_path = str(urlsafe_b64decode(b64path.encode("ascii")).decode("utf-8").replace("\\", "/"))
    file_path = os.path.abspath(file_path)
    print(file_path)
    if system == "Windows":
        file_path = file_path.replace("/", "\\")
        reveal_in_explorer(file_path)
    elif system == "Darwin":
        subprocess.Popen(f'open -R "{file_path}"')
    elif system == "Linux":
        environnement = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        print(environnement)
        if "gnome" in environnement :
            subprocess.Popen(f'nautilus --browser "{file_path}"')
        elif "xcfe" in environnement :
            subprocess.Popen(f'thunar "{file_path}')
        elif "lxde" in environnement :
            subprocess.Popen(f'pacmanfm "{file_path}"')
        elif "cinnamon" in environnement :
            subprocess.Popen(f'nemo "{file_path}"')
        if "unity" in environnement :
            subprocess.Popen(f'nautilus --browser "{file_path}"')
        else:
            subprocess.Popen(f'xdg-open "{file_path}"')
    else:
        subprocess.Popen(f'xdg-open "{file_path}"')
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

@route('/getaudiofile/<b64path>') 
def getaudiofile(b64path):
    file_path = urlsafe_b64decode(b64path.encode("ascii")).decode("utf-8").replace("\\", "/")
    if not os.path.exists(file_path):
        raise HTTPResponse("Sound Wave non trouvé", status=404)
    for l in lire_cachefile().get("audio_cache", list()):
        if file_path in l:
            for k, v in l.items():
                if not os.path.exists(os.path.join(cache_folder, v)):
                    break
                else:
                    return static_file(v, root=cache_folder)
    extension = file_path.lower().split('.')[-1]
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

            ffmpeg.input(file_path).output(cache_path, audio_bitrate='192k').run(overwrite_output=True, cmd=ffmpeg_path)
            modifier_cache(file_path, newname, "audio_cache")
            return static_file(newname, root=cache_folder)
        except ffmpeg.Error as e:
            raise HTTPResponse((f"Erreur FFmpeg : {e}"), status=500)
    return static_file(os.path.basename(file_path), root=os.path.dirname(file_path))

@route("/ping")
def ping():
    return "pong"

# Execution du serveur Bottle
run(host="localhost", port=5069, server='paste')