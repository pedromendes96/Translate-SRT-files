import logging
import os.path
import shutil
from pathlib import Path
from uuid import uuid4

import pysrt
from deep_translator import GoogleTranslator

SOURCE = "en"
TARGET = "pt"
ENCODING = "utf-8"

TEMP_DIRECTORY = "temp"
INPUT_DIRECTORY = "input"
OUTPUT_DIRECTORY = "output"
SRT_EXTENSION = ".srt"

SEPERATOR = "------"
LENGTH_LIMIT = 4_500

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def get_input_files():
    files = []
    for path in Path(INPUT_DIRECTORY).iterdir():
        if path.is_file() and str(path.suffix) == SRT_EXTENSION:
            files.append(str(path.absolute()))
    return files


def main():
    generate_temp_directory()
    generate_output_directory()

    input_files = get_input_files()
    for input_file in input_files:
        logging.info("Starting to convert the file: {}".format(input_file))
        convert(input_file)

    clean_up()


def convert(input_file):
    translated = GoogleTranslator(source=SOURCE, target=TARGET)
    subs = pysrt.open(input_file, encoding=ENCODING)
    files = generate_temp_files(subs)

    translated_lines = []

    for file in files:
        translated_content = translated.translate_file(file)
        translated_lines += translated_content.split(SEPERATOR)

    for index, translated_line in enumerate(filter(None, translated_lines)):
        subs[index].text = translated_line.strip().rstrip("\n")

    input_file_path = Path(input_file)
    result_file_name = "{}-{}{}".format(input_file_path.name, TARGET, input_file_path.suffix)
    result_file_path = Path(OUTPUT_DIRECTORY, result_file_name)
    subs.save(str(result_file_path), encoding=ENCODING)


def generate_temp_files(subs):
    files = [generate_random_filename()]
    lines = [[]]

    file_index = 0
    current_file_length = 0

    for sub in subs:
        total_length = len(sub.text) + len(SEPERATOR)

        if current_file_length + total_length > LENGTH_LIMIT:
            files.append(generate_random_filename())
            lines.append([])
            file_index += 1
            current_file_length = 0

        lines[file_index].append(sub.text + "\n")
        lines[file_index].append(SEPERATOR + "\n")
        current_file_length += total_length

    for index, file in enumerate(files):
        temp_file = open(file, mode="w", encoding=ENCODING)
        temp_file.writelines(lines[index])
        temp_file.close()

    return files


def generate_output_directory():
    temp_directory = Path(OUTPUT_DIRECTORY)
    temp_directory.mkdir(parents=True, exist_ok=True)


def generate_temp_directory():
    temp_directory = Path(TEMP_DIRECTORY)
    temp_directory.mkdir(parents=True, exist_ok=True)


def clean_up():
    shutil.rmtree(TEMP_DIRECTORY)


def generate_random_filename():
    return os.path.join(TEMP_DIRECTORY, "{}.txt".format(uuid4()))


if __name__ == '__main__':
    main()
