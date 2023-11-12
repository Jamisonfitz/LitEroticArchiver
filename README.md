```
┏━  ┓ • ┏┓     • ┏┓   ┓ •        ━┓
┃   ┃ ┓╋┣ ┏┓┏┓╋┓┏┣┫┏┓┏┣┓┓┓┏┏┓┏┓   ┃
┗━  ┗┛┗┗┗┛┛ ┗┛┗┗┗┛┗┛ ┗┛┗┗┗┛┗ ┛   ━┛
```
Python script to aid in archiving stories from Lite Erotica to markdown including series and audio. 

## Features
- Downloads stories with metadata including tags to markdown.
- Determines if a story is part of a series, if so it downloads all other installments as well, notates reading order in header.
- Supports audio stories, M4A filename will match that of the MD also linked within the MD. (This is hardcoded and will need to be updated if moved.)
- Accepts mobile or desktop links.
- Overwrites previous archives making sync straightforward.

## Prerequisites:
- Python 3.x

## Usage:

1. **Setup**:
    - Clone this repository to your local machine.
    - Navigate to the directory.
    - Install the required Python packages by running:  
      ```bash
      pip install -r requirements.txt
      ```

2. **Run the Tool**:
    - Execute the script using Python:
      ```bash
      python main.py
      ```

3. **Output**:
    - Paste story URLs one per line, select the output directory, and start.

## Dependencies:

- **BeautifulSoup4**: For HTML parsing.
- **requests**: To make HTTP requests.

## Contribution:
If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.

## Issues:
If you encounter any issues or have feature requests, please file an issue on the GitHub project. 

## Disclaimer:
Please use this tool responsibly. Making rapid or aggressive requests may lead to IP bans or other restrictions. Always respect the terms of service of any platform you interact with.

## License:
This project is licensed under the MIT License. 
