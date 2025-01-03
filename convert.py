from typing import Optional
import fire
import os
import re
from bs4 import BeautifulSoup
import yaml

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# SITELEN_TABLE = os.path.join(CURRENT_DIR_PATH, "table.data")
TEMPLATE = os.path.join(CURRENT_DIR_PATH, "template.html")


def load_table(path: str) -> dict:
    table = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            regex = r"([^\s]+)[\s]+([^\s]+)[\s]+([^\s]+)"
            line = re.findall(regex, line)[0]

            if len(line) != 3:
                print(f"Error: len {len(line)}- {line}")
                continue

            latin, sitelen, _ = line
            table[latin] = sitelen

    # sort table descending by key length
    table = dict(sorted(table.items(), key=lambda x: len(x[0]), reverse=True))
    return table


def convert_text(text: str, table: dict) -> str:
    current_text = text
    output_text = ""

    while current_text:
        # Match either a word, whitespace, or any single character
        # Use (.|\s)* for the rest to properly capture everything including newlines
        match = re.match(r"(\w+|\s+|.)((.|\s)*)", current_text)
        if not match:
            break

        token = match.group(1)
        rest = match.group(2)

        if token in table:
            output_text += table[token]
        else:
            output_text += token

        current_text = rest

    # remove spaces
    output_text = output_text.replace(" ", "")

    return output_text


def convert_html(soup, table: dict):
    # Recursively process all text nodes
    for text in soup.find_all(text=True):
        if text.parent.name not in ["script", "style"]:  # Skip script and style tags
            new_text = convert_text(text.string, table)
            text.replace_with(new_text)

    return soup


def convert(
    table_path: str,
    text_path: str,
    template: str = TEMPLATE,
    preprocessing: Optional[str] = None,
) -> None:

    preprocessing_table = {}
    if preprocessing:
        with open(preprocessing, "r") as f:
            loaded = yaml.safe_load(f)

            for _, data in loaded.items():
                for key, value in data.items():
                    preprocessing_table[key] = value

    with open(text_path, "r") as f:
        html = f.read()

        # html = html.replace("\n", "<br>")
        # html = html.replace("pi", "<pi>")

        for key, value in preprocessing_table.items():
            html = html.replace(key, value)

    table = load_table(table_path)

    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")

    # Convert text while preserving HTML
    converted_soup = convert_html(soup, table)

    with open(template, "r") as f:
        template = f.read()

    # Output the result
    # print(str(converted_soup))

    template = template.replace("{{{content}}}", str(converted_soup))

    print(template)


if __name__ == "__main__":
    fire.Fire(convert)
