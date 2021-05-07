#!/usr/bin/python3
"""Module used to download data files"""
from pathlib import Path
import tqdm
import requests as rq

FILES = {
    "data/resnet101_wordmap.json":
        ("15Nl3f5DHW-Esk05tbX_-goD-OyMxkB2k", 155872),
    "data/resnet101_attention.pth.tar":
        ("1Xj8iykySqnPC6IbYW-Oy-5cKOgqPlSu3", 416470881)
}

def download_data():
    """Download all of the data right now"""
    for file, (url, size) in FILES.items():
        attempt_download(url, file, known_size=size)

def attempt_download(gdrive_id, outfile, known_size=1):
    """Download the file URL and put it in outfile"""
    # In order to download large files we'll need a cookie
    out = Path(outfile)
    # If they exist, abort
    if out.exists():
        return
    print(f"Downloading {outfile}...")
    # Open a session
    session = rq.Session()
    param = {"id": gdrive_id}
    url_base = "https://drive.google.com/uc?export=download"
    response = session.get(url_base, params=param, stream=True)
    # Find the confirmation token if any
    confirmation_token = None
    for key, value in response.cookies.items():
        if "download_warning" in key:
            confirmation_token = value
    if confirmation_token is not None:
        # Re-download because it's a large file
        param["confirm"] = confirmation_token
        response = session.get(url_base, params=param, stream=True)

    # Download
    with open(str(out), "wb") as fptr:
        chunk_size = 4096 * 8
        iterator = response.iter_content(chunk_size)
        for chunk in tqdm.tqdm(iterator,
                total=known_size/chunk_size,
                unit='bytes',
                unit_scale = chunk_size,
                leave=False):
            if chunk:
                fptr.write(chunk)

if __name__ == "__main__":
    download_data()
