"""This script downloads protein structures predicted by AlphaFold2"""

import argparse
import logging
from pathlib import Path

import requests
from multiprocessing import Pool

import pandas as pd  # type: ignore

from tqdm.auto import tqdm

logging.basicConfig()
logger = logging.getLogger("Downloading AlphaFold2 structures")
logger.setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """
    This function parses arguments
    :return: current argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--structures-output-path", type=str, default="../data/af_structs"
    )
    parser.add_argument("--path-to-file-with-ids", type=str, 
                        default="../data/uniprot_ids_of_interest.txt", help="Path to a file containing UniProt IDs,"
                                                                            "for which the script will download AF2 structures")
    parser.add_argument("--n-jobs", type=int, default=1)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    cl_args = parse_args()
    root_af = Path(cl_args.structures_output_path)
    if not root_af.exists():
        root_af.mkdir()

    with open(cl_args.path_to_file_with_ids, 'r') as file:
        all_ids_of_interest = [line.strip() for line in file.readlines()]


    def download_af_struct(uniprot_id):
        try:
            URL = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
            if not requests.get(URL).ok:
                for ver in ['v3','v2','v1']:
                    if requests.get(f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_{ver}.pdb").ok:
                        URL = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_{ver}.pdb"

            response = requests.get(URL)
            with open(root_af / f"{uniprot_id}.pdb", "wb") as file:
                file.write(response.content)
        except:
            logger.warning(f"Error downloading AlphaFold2 structure for {uniprot_id}")

    with Pool(processes=cl_args.n_jobs) as pool:
        pool.map(download_af_struct, all_ids_of_interest)