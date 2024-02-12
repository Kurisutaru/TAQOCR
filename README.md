# Princess Connect ! Re:Dive Anniversary Quiz Solver

## Table of Contents

- [Introduction](#introduction)
- [Usage](#usage)
- [Setup](#setup)
- [Dependencies](#dependencies)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Introduction

This script is designed for solving quizzes in the `Princess Connect! Re:Dive` game. Inspired from [ASMOCR](https://github.com/paulzzh/ASMOCR), it has been adapted to work with the 2022 Anniversary Minigame, Landsol Quiz Minigame (TAQ). The script leverages RapidFuzz to improve accuracy and processing speed when identifying quiz questions.

**Kuri Note:**
I have made several enhancements to this script. First, I adapted it from ASM (Academy Quiz Minigame) to TAQ (2022 Anniversary Minigame, Landsol Quiz Minigame). Additionally, I incorporated a fuzzy matcher from RapidFuzz, replacing the existing SequenceMatcher, thereby enhancing the script's capabilities. Furthermore, I've improved the script's overall readability and reduced the likelihood of crashes.

I've also introduced two regions for question checking: one designed for typical questions that are large on the screen, and another for specific questions like Dungeon EX names and their variants. However, please note that the recognition of these specific questions may not be perfect with PaddleOCR. To ensure accurate results, standard image processing steps have been included before the image is passed to PaddleOCR.

Translation to English.


## Usage

Before running the script, make sure to start the DMM client and enter the mini-game. The script will automatically provide answers to the quiz questions.

If you encounter issues with misaligned boxes, refer to this text and search for 'question_region' in the 'run.py' file to make necessary modifications.

## Setup

1. Install the required libraries by running the following command:
   `pip install Pillow rapidfuzz pywin32`
2. Download the `redive_jp.db` database file from [estertion](https://redive.estertion.win/db/redive_jp.db.br).
3. Unpack the Brotli compression archive to obtain the `redive_jp.db` file. You can use tools like [PeaZip](https://github.com/peazip/PeaZip) to perform this extraction.
4. Place the `redive_jp.db` file in the same directory as your script.
5. Download the PaddleOCR-json Release files from the [PaddleOCR-json repository](https://github.com/hiroi-sora/PaddleOCR-json) and place them in the appropriate directories:
	- Place the model files and configurations in the `PaddleOCR-json` directory.
6. Configure the script by modifying the `window_title` and `question_region` variables in the code according to your game setup.
7. Run the script using Python 3.10.

These steps will ensure that you have the necessary database file and dependencies to run the script. If you have any more questions or need further assistance, feel free to ask!

## Dependencies

- [PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json): Optical Character Recognition (OCR) library for text extraction. This library is used to perform OCR on images and generate JSON output.
- [Pillow](https://python-pillow.org/): Python Imaging Library.
- [pywin32](https://pypi.org/project/pywin32/): Python extensions for Windows.
- [RapidFuzz](https://pypi.org/project/rapidfuzz/): A fast string matching library.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Forked from [ASMOCR](https://github.com/paulzzh/ASMOCR)
- Thanks to the developers of Pillow, RapidFuzz, pywin32, and PaddleOCR for their contributions to the Python community.
