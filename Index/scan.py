# from Index.create_db import create_vectordb
import chromadb
from Index.scan_default import fast_scan_for_images
from concurrent.futures import ThreadPoolExecutor
import yaml
from tqdm import tqdm
import hashlib

def process_hash(path):
    with open(path, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()    
        # pipe contents of the file through
        md5 = hashlib.md5(data).hexdigest()
    return md5

def getDb(path="db"):
    client = chromadb.PersistentClient(
        path
    )
    paths = client.get_or_create_collection(
        "paths"
    )
    return paths

def save_to_db(image_paths, save_hash=False, db="db"):
    paths_collection = getDb(db)
    ### Delete existing paths before inserting new ones.
    ids=paths_collection.get()["ids"]
    if len(ids)>0:
        paths_collection.delete(ids)

    image_paths = [path.replace("\\", "/") for path in image_paths]
    image_paths = list(set(image_paths))

    upsert_metadatas = []
     
    if save_hash:
        with ThreadPoolExecutor() as executor:
            hash = list(
                tqdm(
                    executor.map(process_hash, image_paths), desc="Hashing", total=len(image_paths)
                )
            )
    else:
        hash = [
            0 for i in image_paths
        ]
        
    for i, path in enumerate(image_paths):
        upsert_metadatas.append({ "hash": hash[i] })
        # Perform batch upsert for image collection
    upsert_embeddings = [[0] for i in image_paths]
    paths_collection.upsert(
        ids=image_paths,
        embeddings=upsert_embeddings,
        metadatas=upsert_metadatas,
    )


def read_from_db(db="db"):
    """
    Reads image paths and, optionally, their hashes from the db.

    Returns:
        tuple: Depending on read_average, returns a tuple containing one or two lists: one of the image paths and, if read_average is True, one of their average pixel values.
    """
    paths_collection = getDb(db)
    paths = paths_collection.get()["ids"]
    hashes = [paths_collection.get(
        ids=[path])["metadatas"][0]["hash"] for path in paths]

    return (paths, hashes)


def scan_and_save():
    """
    Scans for images based on the configuration specified in 'config.yaml' and saves the paths.

    The function supports two scanning methods: 'default' and 'Everything'. The 'default' method uses specified
    include and exclude directories to find images, while the 'Everything' method utilizes the Everything SDK for scanning.

    Returns:
        bool: True if the scan and save operation was successful, False otherwise.
    """
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        if config["scan_method"] == "default":
            include_dirs = config["include_directories"]
            exclude_dirs = config["exclude_directories"]
            if len(include_dirs) == 0:
                include_dirs = None
                print("No directories to include")
                return False
            paths, _ = fast_scan_for_images(include_dirs, exclude_dirs)
        elif config["scan_method"] == "Everything":
            from Index.scan_EverythingSDK import search_EverythingSDK

            paths = search_EverythingSDK()
        else:
            print("Error in config.yaml: scan_method must be 'default' or 'Everything'")
            return False

        save_to_db(paths, config["deep_scan"])
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
