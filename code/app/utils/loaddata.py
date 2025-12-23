from io import BytesIO
from zipfile import ZipFile
import requests

STCP_DATASET = "https://opendata.porto.digital/dataset/5275c986-592c-43f5-8f87-aabbd4e4f3a4/resource/415bf8d5-4c18-40b3-9516-9d9187185ef9/download/gtfs_stcp.zip"
METRO_DATASET = "https://www.metrodoporto.pt/metrodoporto/uploads/document/file/693/google_transit_08_09_2025.zip"
STCP_PATH = "../../feeds/gtfs_stcp"
METRO_PATH = "../../feeds/gtfs_metro"

def get_dataset_and_extract(url: str, target_path: str = ".") -> None:
    resp = requests.get(url)

    if resp.status_code == 200:
        z = ZipFile(BytesIO(resp.content))
        z.extractall(f"{target_path}")
        return

    raise Exception("Not possible to download.")

try:
    get_dataset_and_extract(STCP_DATASET, STCP_PATH)
    get_dataset_and_extract(METRO_DATASET, METRO_PATH)
except:
    print("Something went wrong!")