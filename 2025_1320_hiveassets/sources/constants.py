import os, platform
# Définition des variables
system = platform.system()
dossier_config = os.path.join(os.path.expanduser("~"), ".hiveasset")
fichier_config = os.path.join(dossier_config, "config.json")
fichier_scan = os.path.join(dossier_config, "scan.json")
fichier_cache = os.path.join(dossier_config, "cache.json")
cache_folder = os.path.join(dossier_config, "cache")
curdir = os.path.dirname(__file__)
datadir = os.path.join(curdir, "..", "data")
static_dir = os.path.join(curdir, "..", "data", "static")
basedir = os.path.join(curdir, "..")
hdr_dir = os.path.join(static_dir, "3dviewer", "hdr")
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