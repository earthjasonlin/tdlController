import subprocess
import time
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import re
import logging


logging.basicConfig(filename='script.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')


def log_message(message):
    print(message)
    logging.info(message)


def get_chat_id_from_url(url):
    return url.strip().split("/")[-1]


def read_chat_links(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]
    
    
def get_meta_title(url, proxy):
    proxies = {
        "http": proxy,
        "https": proxy
    }
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tag = soup.find('meta', property='og:title')
    if meta_tag:
        return meta_tag['content']
    return get_chat_id_from_url(url)  # Fallback to chat ID if meta tag is not found


def execute_commands(tdl_exe, chat_link, last_timestamp, current_timestamp, proxy, output_dir):
    file_name = "我的收藏"
    if chat_link == "fav":
        export_command = f"{tdl_exe} chat export -i {last_timestamp},{current_timestamp} --proxy {proxy} -o {output_dir}/{file_name}.json >> tdl.log"
        download_command = f"{tdl_exe} dl -f {output_dir}/{file_name}.json --proxy {proxy} --reconnect-timeout 0 --continue --skip-same -d {output_dir}/{file_name} >> tdl.log"
    else:
        file_name = re.sub(r'[<>:"/\\|?* ]', '_', get_meta_title(chat_link, proxy))
        export_command = f"{tdl_exe} chat export -c {chat_link} -i {last_timestamp},{current_timestamp} --proxy {proxy} -o {output_dir}/{file_name}.json >> tdl.log"
        download_command = f"{tdl_exe} dl -f {output_dir}/{file_name}.json --proxy {proxy} --reconnect-timeout 0 --continue --skip-same -d {output_dir}/{file_name} >> tdl.log"
    
#     log_message(f"开始导出：{file_name}")
    subprocess.run(export_command, shell=True)
#     log_message(f"开始下载：{file_name}")
    subprocess.run(download_command, shell=True)
#     log_message(f"下载完成：{file_name}")


def main(tdl_exe, file_path, proxy, output_dir, sleep_time):
    last_timestamp = int(time.time()) - 86400  # Initialize with the timestamp of 1 days ago

    while True:
        current_timestamp = int(time.time())
        chat_links = read_chat_links(file_path)
        
        for chat_link in chat_links:
            execute_commands(tdl_exe, chat_link, last_timestamp, current_timestamp, proxy, output_dir)
        
        last_timestamp = current_timestamp
        log_message(f"本轮完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_message(f"暂停时间：{sleep_time}秒")
        log_message(f"===========================================================")
        time.sleep(sleep_time)
        

if __name__ == "__main__":
    tdl_exe = "tdl.exe"  # Path to tdl.exe
    file_path = "./chat_links.txt"  # Path to your file containing chat links
    proxy = "socks5://127.0.0.1:10808"  # Proxy address
    output_dir = "./res"  # Output directory for downloaded content
    sleep_time = 3600  # Sleep time in second
    
    main(tdl_exe, file_path, proxy, output_dir, sleep_time)
