import ctypes
import re
import sqlite3
import time
from io import BytesIO

import rapidfuzz.utils
from PIL import ImageGrab, ImageDraw, Image, ImageEnhance
from rapidfuzz import process
from win32gui import EnumWindows, SetForegroundWindow, GetClientRect, GetWindowRect, GetWindowText

from PPOCR_api import GetOcrApi
import tbpu
from PPOCR_visualize import visualize

print("================================")
print("Princess Connect! Re:Dive - 2022 Anniversary Quiz Solver")
print("================================")

window_title = "PrincessConnectReDive"
first_question_region = (30, 110, 700, 280)
second_question_region = (30, 280, 700, 380)

player_position_1 = (70, 690)
position_x_difference = 190
active_player_color = (255, 139, 55)

print("Window Title:", window_title)
print("Question Area:", first_question_region)

debug_window = False
debug_ocr = False


class Window:
    def __init__(self, hwindow):
        self.ybase = None
        self.xbase = None
        self.height = None
        self.width = None
        if not hwindow:
            return
        self.hwnd = hwindow
        _frame = self.screenshot()
        print("Resolution:", _frame.size)
        print("Base Coordinates:", (self.xbase, self.ybase))
        draw = ImageDraw.Draw(_frame)
        draw.rectangle(first_question_region, outline=(255, 0, 0))
        draw.text((first_question_region[0], first_question_region[1]), "question", "red")
        draw.rectangle(second_question_region, outline=(255, 0, 0))
        draw.text((second_question_region[0], second_question_region[1]), "question 2", "red")
        _frame.save(window_title + ".png", "PNG")

    def screenshot(self):
        SetForegroundWindow(pcrd_window)
        x1, y1, x2, y2 = GetClientRect(self.hwnd)
        self.width = x2 - x1
        self.height = y2 - y1

        wx1, wy1, wx2, wy2 = GetWindowRect(self.hwnd)
        bx = wx1
        by = wy1
        # normalize to origin
        wx1, wx2 = wx1 - wx1, wx2 - wx1
        wy1, wy2 = wy1 - wy1, wy2 - wy1
        # compute border width and title height
        bw = int((wx2 - x2) / 2.)
        th = wy2 - y2 - bw
        # calc offset x and y taking into account border and titlebar, screen coordiates of client rect
        sx = bw
        sy = th

        self.xbase = bx + sx
        self.ybase = by + sy

        left, top = self.xbase, self.ybase
        right, bottom = left + self.width, top + self.height

        _frame = ImageGrab.grab(bbox=(left, top, right, bottom))

        if debug_window:
            image = Image.open("frame.png")
            return image

        return _frame


class OCR:
    def __init__(self, argument=None):
        if argument is None:
            argument = {'config_path': "models/config_japan.txt"}
        self.ocr = GetOcrApi(r".\PaddleOCR-json\PaddleOCR-json.exe", argument)

    def get_single_line_from_ocr_result(self, frame_data):
        buffered = BytesIO()
        original_width, original_height = frame_data.size
        new_width = int(original_width * 3)
        new_height = int(original_height * 3)
        resized_image = frame_data.resize((new_width, new_height)).convert('L')
        enhancer = ImageEnhance.Contrast(resized_image)
        final_image = enhancer.enhance(2)

        final_image.save(buffered, format="PNG")

        if debug_window:
            final_image.save("123.png", format="PNG")

        result = self.ocr.runBytes(buffered.getvalue())

        if debug_ocr:
            with open('123.png', 'rb') as image_file:
                # Read the contents of the image file as bytes
                image_bytes = image_file.read()
            result = self.ocr.runBytes(image_bytes)

        if result['code'] == 100:
            # Exclude list of word that fill in the upper answer box
            exclude_words = ["かな", "がな", "カナ", "ガナ", "ガす", "漢字", "数字", "漢宮"]
            # filtered_data = [item for item in result["data"] if not any(word in item["text"] for word in exclude_words)]
            # filtered_data = [item for item in result["data"] if not any(exclude_word in item["text"] for exclude_word in exclude_words)]
            filtered_data = [item for item in result["data"] if item["text"] not in exclude_words]
            txts = tbpu.run_merge_line_h_m_paragraph(filtered_data)
            if debug_window:
                img1 = visualize(result["data"], "123.png").get(isOrder=True)
                img2 = visualize(txts, "123.png").get(isOrder=True)
                visualize.createContrast(img1, img2).show()
            if len(txts) == 1:
                text = txts[0]['text'] if txts and 'text' in txts[0] else ''
            else:
                text = ''.join(item['text'] for item in txts)
            return text
        else:
            return ""


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def set_dpi_awareness():
    awareness = ctypes.c_int()
    error_code = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
    error_code = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    success = ctypes.windll.user32.SetProcessDPIAware()


def get_windows_by_title(title_text):
    def _window_callback(_hwnd, all_windows):
        all_windows.append((_hwnd, GetWindowText(_hwnd)))

    windows = []
    EnumWindows(_window_callback, windows)
    return [(hwnd, title) for hwnd, title in windows if title_text in title]


try:
    set_dpi_awareness()
    wins = get_windows_by_title(window_title)
    print("Window Handle:", wins)
    print("Defaulting to the first one; modify the configuration file if it's not correct")
    pcrd_window = wins[0][0]
    SetForegroundWindow(pcrd_window)
    time.sleep(1)
    window = Window(pcrd_window)
    ocr_class = OCR()
except Exception as e:
    print(f"Caught an exception: {e}")
    print("Initializing failed, exiting program")
    exit(1)


def query_jp_db(query, args=(), one=False):
    conn = sqlite3.connect('redive_jp.db')
    cur = conn.cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return (r[0] if r else None) if one else r


taq_data = query_jp_db("""
SELECT 
  taq_no, 
  word, 
  REPLACE (
    REPLACE (
      REPLACE (
        REPLACE (
          CASE WHEN detail_2 = '' THEN assist_detail ELSE detail_2 END, 
            '\n', ''
          ),
        '\\n', ''
      ), 
      ' ',  ''
    ), 
    '　', ''
  ) AS clue 
FROM 
  taq_data
""")

taq_data_clue = {elt['clue']: elt['clue'] for elt in taq_data}

single_sentence = query_jp_db("""
SELECT 
  GROUP_CONCAT(
    REPLACE (
      REPLACE (
        REPLACE (
          REPLACE (
            CASE WHEN detail_2 = '' THEN assist_detail ELSE detail_2 END, 
              '\n', ''
            ),
          '\\n', ''
        ), 
        ' ',  ''
      ), 
      '　', ''
    )
  ) AS clue 
FROM 
  taq_data
""")
# make an answer only character string to filter out junk text from OCR result
unique_text = ''.join(dict.fromkeys(single_sentence[0]['clue']))


def get_current_active_player_by_pixel(frame_data):
    for i in range(5):
        # Calculate the current position
        x, y = player_position_1[0] + i * position_x_difference, player_position_1[1]

        # Get the pixel color at the current position
        pixel_color = frame_data.getpixel((x, y))

        # Compare the pixel color with the active player color
        if pixel_color == active_player_color:
            return i


def format_answer_text_from_position(text, position):
    formatted_text = " ".join(
        [f"{Color.GREEN}{Color.BOLD}[{char}]{Color.END}" if i == position else f"{Color.RED}{char}{Color.END}" for
         i, char in enumerate(text)])
    return formatted_text


def colorize_acc_text_value(accuracy):
    if accuracy >= 70:
        color = Color.GREEN  # Green for accuracy >= 70%
    elif accuracy >= 50:
        color = Color.YELLOW  # Yellow for accuracy between 50% and 69.99%
    else:
        color = Color.RED  # Red for accuracy < 50%

    formatted_accuracy = "{:.2f}%".format(accuracy)
    return f"{color}{formatted_accuracy}{Color.END}"


word = None
minimum_acceptable_score = 35
while True:
    try:
        frame = window.screenshot()
        current_active_player_position = get_current_active_player_by_pixel(frame)
        question_regions = [first_question_region, second_question_region]
        final_question = None

        for region in question_regions:
            question_image = frame.crop(region)
            question_ocr = ocr_class.get_single_line_from_ocr_result(question_image)
            question_fixed = ''.join(char for char in question_ocr if char in unique_text)

            data_fuzzy_select = process.extractOne(query=question_fixed,
                                                   choices=taq_data_clue,
                                                   scorer=rapidfuzz.fuzz.QRatio,
                                                   processor=rapidfuzz.utils.default_process)

            fuzzy_score = data_fuzzy_select[1] if data_fuzzy_select else 0

            if fuzzy_score >= minimum_acceptable_score:
                final_question = question_fixed
                break

        if final_question:
            data_fuzzy_select = process.extractOne(query=final_question,
                                                   choices=taq_data_clue,
                                                   scorer=rapidfuzz.fuzz.QRatio,
                                                   processor=rapidfuzz.utils.default_process)
            data_fuzzy = [item for item in taq_data if item["clue"] == data_fuzzy_select[0]][0]
            fuzzy_score = data_fuzzy_select[1] if data_fuzzy_select else 0

            if word != data_fuzzy['word'] and fuzzy_score >= minimum_acceptable_score:
                # OCR = OCR ?
                # QUE = Query
                # ACC = Accuracy
                # ANS = Answer. Character in [] that your answer
                print("================================")
                print("OCR:", final_question)
                print("QUE:", data_fuzzy['clue'])
                print("ACC:", colorize_acc_text_value(fuzzy_score))
                print("ANS:", format_answer_text_from_position(text=data_fuzzy['word'],
                                                               position=current_active_player_position))
                print("================================")
                word = data_fuzzy['word']

        time.sleep(2)

    except Exception as e:
        print("================================")
        print(f"Caught an exception: {e}")
        print(f"Timeout 5s before retrying")
        time.sleep(5)
        print("================================")
