import asyncio
import argparse
import os
import time
import json
from requests.models import HTTPError

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from trafilatura import extract
from boltons.setutils import IndexedSet
import requests

from gradio_assistant.url_result import UrlResult

options = Options()
options.add_argument("--headless=new")  # For Chrome 109+
driver = webdriver.Chrome(options=options)

def download_url(url):
    driver.get(url)
    time.sleep(1)  # Wait for content to load
    content = driver.page_source

    current_url = driver.current_url
    response = requests.head(current_url)
    if response.status_code >= 400:
        raise HTTPError(current_url, response.status_code,
                      f"HTTP Error {response.status_code}", None, None)

    result = extract(content, include_formatting=True, include_links=True)
    if not result:
        print(f"No content found for url: '{url}'")
        return None
    return UrlResult(result, url=url)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="Path to the input file.")
    parser.add_argument("output_file", type=str, help="Path to the output file.")
    args = parser.parse_args()
    urls = []
    with open(args.input_file, "r") as f:
        for line in f:
            urls.append(line.strip())

    urls = IndexedSet(urls)
    failed_urls = []
    url_results = []
    for url in urls:
        try:
            url_result = download_url(url)
        except HTTPError as e:
            print(f"Url failed: {e} : '{url}'")
            failed_urls.append(url)
            continue
        if url_result:
            url_results.append(url_result)
        else:
            print(f"Url failed to retrieve content: '{url}'")
            failed_urls.append(url)

    json_seq = []
    for url_result in url_results:
        json_seq.append(url_result.to_dict())

    if os.path.exists(args.output_file):
        with open(args.output_file, "r") as f:
            existing_json_seq = json.loads(f.read())
            json_seq = existing_json_seq + json_seq
    with open(args.output_file, "w") as f:
        f.write(json.dumps(json_seq))
    if failed_urls:
        with open("failed_urls.txt", "w") as f:
            f.write("\n".join(failed_urls))


if __name__ == "__main__":
    asyncio.run(main())
