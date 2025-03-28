#Projet : HiveAssets
#Auteurs : Judicaël Lenglet, Ewan Jannot, Joan Molle, Maël Pouvreau
import os, platform
"""
Définition de toutes les variables
"""
system = platform.system()
serverport = 0
dossier_config = os.path.join(os.path.expanduser("~"), ".hiveasset")
fichier_config = os.path.join(dossier_config, "config.json")
fichier_scan = os.path.join(dossier_config, "scan.json")
fichier_cache = os.path.join(dossier_config, "cache.json")
cache_folder = os.path.join(dossier_config, "cache")
curdir = os.path.dirname(__file__)
static_dir = os.path.join(curdir, "static")
hdr_dir = os.path.join(static_dir, "3dviewer", "hdr")
# Ici est défini tout les fichiers qui sont pris en charge par le logiciel
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
 # Ici est défini la configuration par défaut du logiciel
DEFAULT_CONFIG = {
        "os": system,
        "scan_directory": [],
        "3Dviewerhdrname": "BaseHDR.hdr",
        "ignoreunknownfiles": True,
        "openwebpageonload": True,
        "filter_texturessizes": ["128 x 128", "256 x 256", "512 x 512", "1024 x 1024", "2048 x 2048"]
}
# Ici est défini la configuration du fichier de scan, il n'est pas utile pour le moment
DONNEES_SCAN = { 
    "Textures" : [],
    "Mesh" : [],
    "Unknown" : []
}
# Ici est défini le type d'assets qui peut s'afficher dqns les filtres, n'est pas utile pour le moment
ASSETS_TYPES = ["Textures", "Models"]
 # Ici est défini le fichier servant de cache au logiciel, il garde en mémoire les textures non compatibles
 # avec les navigateurs qui ont étés converties par le programme afin de les afficher correctement. 
DONNEES_CACHE = {
    "cache" : [],
    "preview_cache": []
}