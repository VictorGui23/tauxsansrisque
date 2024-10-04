import requests
from bs4 import BeautifulSoup
import re
import os
import time 
import sys
from constants import EIOPA_URL

def extract_main_url(full_url):
    pattern = r"(https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+)"
    match = re.match(pattern, full_url)
    if match:
        return match.group(1)
    return None

def extract_date_from_url(url):
    pattern = r"=EIOPA_RFR_(\d{8})\.zip"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def extract_date(string):
    pattern = r"EIOPA_RFR_(\d{8})\.zip"
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    return None

def extract_zip_groups(html_content):
    list_of_paths = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all 'a' tags with 'href' containing '.zip'
    zip_links = soup.find_all('a', href=lambda href: href and '.zip' in href)
    
    for link in zip_links:
        # Find the closest parent div or the link itself if no parent div exists
        href = link.get('href')
        if href:
            print(f"ZIP file link: {href}")
            print("-" * 50)
            list_of_paths.append(href)
    return list_of_paths

def download_file(url, directory, filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    full_path = os.path.join(directory, filename)
    # Check if the request was successful
    if response.status_code == 200:
        # Open the file in binary write mode
        with open(full_path, 'wb') as file:
            # Iterate over the response data in chunks
            for chunk in response.iter_content(chunk_size=8192):
                # Write each chunk to the file
                file.write(chunk)
        print(f"File downloaded successfully: {filename}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def download_files(path_to_folder, url):
    response = requests.get(url)
    main_url = extract_main_url(url)
    files_in_folder = os.listdir(path_to_folder)
    dates_in_folder = [extract_date(x) for x in files_in_folder]
    if response.status_code == 200:
        print("Request successful!")
        list_of_paths = extract_zip_groups(response.text)
        file_urls = [main_url + path for path in list_of_paths]
        for url in file_urls:
            print(url)
            cur_date = extract_date_from_url(url)
            if cur_date is not None and cur_date not in dates_in_folder and int(cur_date) > 20230601:
                download_file(url, path_to_folder, "EIOPA_RFR_" + cur_date + ".zip")
                time.sleep(5)
            if cur_date in dates_in_folder:
                print("Date {} already in folder. Skipping.".format(cur_date))
            if int(cur_date) <= 20230601:
                # avant juin 2023 les courbes ne contiennent pas la valeur 
                # alpha pour certains onglets donc je préfère ne pas m'embêter
                print("Date {} earlier than threshold of June, 2023.")

    else:
        print(f"Request failed with status code: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 collect_zip_files.py output_folder")
        sys.exit(1)

    url = EIOPA_URL
    
    output_folder = sys.argv[1]

    download_files(output_folder, url)

