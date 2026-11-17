"""Download the raw data files into data/raw/.

Run from the repository root:
    python scripts/download_data.py

The files in data/raw/ are not committed (see .gitignore).
Running this script again downloads fresh copies.
"""

from pathlib import Path

import requests

# Folder where the raw files are saved: <repository root>/data/raw
RAW_FOLDER = Path(__file__).resolve().parent.parent / "data" / "raw"

# File name to save -> address to download it from
FILES = {
    # NSIDC Sea Ice Index (G02135), version 4: daily Arctic sea-ice extent
    "nsidc_arctic_daily_extent.csv":
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v4.0.csv",
    # NASA GISTEMP v4: Northern Hemisphere monthly temperature anomalies
    "gistemp_nh_monthly.csv":
        "https://data.giss.nasa.gov/gistemp/tabledata_v4/NH.Ts+dSST.csv",
    # NASA GISTEMP v4: global monthly temperature anomalies
    "gistemp_global_monthly.csv":
        "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
    # NOAA Mauna Loa: monthly mean CO2 (ppm)
    "noaa_co2_monthly.csv":
        "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv",
}


def download(url, save_path):
    """Download one file and save it. Stops with an error if the download fails."""
    response = requests.get(url, timeout=120)
    response.raise_for_status()  # error if the server answers 404, 500, ...
    save_path.write_bytes(response.content)


def main():
    RAW_FOLDER.mkdir(parents=True, exist_ok=True)
    for file_name, url in FILES.items():
        save_path = RAW_FOLDER / file_name
        print(f"Downloading {file_name} ...")
        download(url, save_path)
        size_kb = save_path.stat().st_size / 1024
        print(f"  saved to data/raw/{file_name} ({size_kb:.0f} KB)")
    print("Done.")


if __name__ == "__main__":
    main()
