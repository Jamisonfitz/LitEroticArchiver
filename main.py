#┏━  ┓ • ┏┓     • ┏┓   ┓ •        ━┓#
#┃   ┃ ┓╋┣ ┏┓┏┓╋┓┏┣┫┏┓┏┣┓┓┓┏┏┓┏┓   ┃#
#┗━  ┗┛┗┗┗┛┛ ┗┛┗┗┗┛┗┛ ┗┛┗┗┗┛┗ ┛   ━┛#

import requests
import logging
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import re
from bs4 import BeautifulSoup
import sys

# Global variable to store the selected directory
selected_directory = None

# Custom handler for logging
class TextHandler(logging.Handler):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        self.text.configure(state='normal')
        self.text.insert(tk.END, msg + '\n')
        self.text.configure(state='disabled')
        self.text.yview(tk.END)

class OutputRedirector(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, string)
        self.text_widget.configure(state='disabled')
        self.text_widget.yview(tk.END)

    def flush(self):
        pass

def setup_logging():
    text_handler = TextHandler(logging_textbox)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.addHandler(text_handler)

# Default user-agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def clean_url(url):
    url = url.replace('https://i.literotica.com/stories/showstory.php?id=', 'https://www.literotica.com/s/')
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(query=""))

def proper_case(title):
    return ' '.join(word.capitalize() for word in title.replace('-', ' ').split())

def fetch_story_data(story_id, page_num):
    api_url = f"https://literotica.com/api/3/stories/{story_id}?params=%7B%22contentPage%22%3A{page_num}%7D"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch data for story ID {story_id} on page {page_num}. Status code: {response.status_code}")
        return None

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '', filename)

def download_audio_file(audio_url, file_path):
    logging.info(f"Attempting to download audio file from URL: {audio_url}")
    response = requests.get(audio_url, headers=headers)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Successfully downloaded audio file: {file_path}")
    else:
        logging.error(f"Failed to download audio file. URL: {audio_url}, HTTP Status: {response.status_code}")

def extract_audio_url(page_content):
    logging.info("Extracting audio URL from page content...")
    soup = BeautifulSoup(page_content, 'html.parser')
    audio_tag = soup.find('audio')
    if audio_tag and audio_tag.get('src'):
        audio_url = audio_tag['src']
        logging.info(f"Found audio URL: {audio_url}")
        return audio_url
    else:
        logging.warning("No audio URL found in the page content.")
        return None

def save_to_file(author, category, title, markdown_content, audio_extraction_content, page_num, base_path, header="", pages_count=1):
    if not selected_directory:
        logging.error("No output directory selected.")
        return

    base_path = Path(selected_directory)
    sanitized_title = sanitize_filename(proper_case(title))
    author_path = base_path / category / author
    author_path.mkdir(parents=True, exist_ok=True)
    file_path = author_path / f"{sanitized_title}.md"
    audio_file_path = author_path / f"{sanitized_title}.m4a"

    mode = 'w' if page_num == 1 else 'a'
    with open(file_path, mode, encoding='utf-8') as file:
        if page_num == 1:
            file.write(header)
        file.write(markdown_content)  # Write the text content to the markdown file

        if category == 'audio-sex-stories' and page_num == pages_count:
            audio_file_link = f"file:///{audio_file_path}".replace(' ', '%20').replace('\\', '/')
            file.write(f"\n\n[Audio File]({audio_file_link})")
            logging.info(f"Added audio file link to markdown file: {audio_file_link}")

    logging.info(f"Saved page {page_num} of '{sanitized_title}' in '{category}/{author}'.")

    if category == 'audio-sex-stories' and page_num == 1 and audio_extraction_content:
        logging.info(f"Processing audio category for '{sanitized_title}'. Trying to extract audio URL...")
        audio_url = extract_audio_url(audio_extraction_content)  # Extract audio URL from HTML content
        if audio_url:
            download_audio_file(audio_url, audio_file_path)
        else:
            logging.error(f"Unable to find audio URL for '{sanitized_title}'.")

def format_header(url, author, userid, description, date_approve, tags, series_info=""):
    author_url = f"https://www.literotica.com/stories/memberpage.php?uid={userid}&page=submissions"
    formatted_tags = ' '.join([f"#{tag['tag'].replace(' ', '-')}" for tag in tags])
    header = f"{date_approve} | [Permalink]({url}) | [{author}]({author_url})\n\n{description}\n\n{series_info}\n\nTags: {formatted_tags}\n\n---\n\n"
    return header

def fetch_html_content(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        logging.error(f"Failed to fetch HTML content. Status code: {response.status_code}")
        return None

def process_story(url, processed_ids, urls_to_process, base_path):
    story_id = urlparse(url).path.split('/')[-1]
    if story_id in processed_ids:
        return

    processed_ids.add(story_id)
    json_data = fetch_story_data(story_id, 1)
    html_content = None

    if json_data and 'submission' in json_data:
        submission = json_data['submission']
        pages_count = json_data['meta']['pages_count']
        author = submission['author']['username']
        userid = submission['author']['userid']
        title = submission.get('title', 'Untitled')
        description = submission.get('description', 'No description available')
        date_approve = submission.get('date_approve', 'Unknown Date')
        tags = submission.get('tags', [])
        series_info = ""
        category_url = submission.get('category_info', {}).get('pageUrl', '')
        category = urlparse(category_url).path.split('/')[-1] if category_url else 'Uncategorized'

        if 'series' in submission and isinstance(submission['series'], dict):
            series_meta = submission['series'].get('meta', {})
            if 'order' in series_meta:
                series_stories = series_meta['order']
                for series_story_id in series_stories:
                    if series_story_id != submission['id'] and series_story_id not in processed_ids:
                        series_story_url = f"https://www.literotica.com/s/{series_story_id}"
                        urls_to_process.append(series_story_url)
                series_name = series_meta.get('title', 'Unnamed Series')
                installment_number = series_stories.index(submission['id']) + 1
                series_info = f"Installment {installment_number} of {series_name} Series"

        header = format_header(url, author, userid, description, date_approve, tags, series_info)

        if category == 'audio-sex-stories':
            html_content = fetch_html_content(url)
            if not html_content:
                logging.error(f"Failed to fetch HTML content for audio story: {url}")
                return

        for page_num in range(1, pages_count + 1):
            json_data = fetch_story_data(story_id, page_num)
            if json_data and 'pageText' in json_data:
                text = json_data['pageText']
                save_to_file(author, category, title, text, html_content, page_num, base_path, header if page_num == 1 else "", pages_count)
            
def process_stories():
    base_path = Path(selected_directory)
    input_urls = text_input.get('1.0', tk.END).strip().split('\n')
    urls_to_process = [clean_url(url.strip()) for url in input_urls if url.strip()]
    processed_ids = set()

    while urls_to_process:
        url = urls_to_process.pop(0)
        process_story(url, processed_ids, urls_to_process, base_path)

def paste_text():
    text_input.delete('1.0', tk.END)  # Clear the existing content
    try:
        text = root.clipboard_get()
        text_input.insert(tk.INSERT, text)
    except tk.TclError:
        messagebox.showerror("Paste Error", "Nothing to paste from clipboard")

def choose_directory():
    global selected_directory
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        logging.info(f"Selected directory: {selected_directory}")
    else:
        logging.info("No directory selected.")

# GUI
root = tk.Tk()
root.title("LitEroticArchiver")

text_input = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10)
text_input.pack(padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Paste button
paste_button = tk.Button(button_frame, text="Paste", command=paste_text)
paste_button.pack(side=tk.LEFT, padx=5)

# Directory button
directory_button = tk.Button(button_frame, text="Output Dir", command=choose_directory)
directory_button.pack(side=tk.LEFT, padx=5)

# Process (Start) button
process_button = tk.Button(button_frame, text="Start", command=process_stories)
process_button.pack(side=tk.LEFT, padx=5)

logging_textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, state='disabled')
logging_textbox.pack(padx=10, pady=10)

sys.stdout = OutputRedirector(logging_textbox)
sys.stderr = OutputRedirector(logging_textbox)

setup_logging()

root.mainloop()

