import time
from string import Template
import re
import json

import httpx
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip


controller = Controller()

OLLAMA_ENDPOINT = "http://127.0.0.1:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "llama3:instruct",
    "keep_alive": "5m",
    "stream": False,
}

template_dic = dict()
template_dic['fix']  = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:
Return only the corrected text, don't include a preamble or any note.
text: $text
"""
)
template_dic['explain']  = Template(
    """Write a short description to explain the following concept. don't include any preamble or any note on how to generate it. please only return the explaination. 
text: $text
""")

template_dic['rephrase']  = Template(
    """Please rephrase the following text. Don't include any preamble or any note on how to generate it. please only return the explaination. 
text: $text
""")
template_dic['longer']  = Template(
    """Please elaborate and enrich the following text. Don't include any preamble or any note on how to generate it. please only return the explaination. 
text: $text
"""
)


template_dic['shorter']  = Template(
    """Please make a shorter summary of the following text. Don't include any preamble or any note on how to generate it. please only return the explaination. 
text: $text
"""
)

template_dic['empty']  = Template(
    """$text"""
)


def process_text(text, command_str):
    template_str = template_dic.get(command_str, template_dic['empty'])
    prompt = template_str.substitute(text=text)
    print(prompt)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=100,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    print('response ----')
    print(response.json()["response"].strip())
    print("----")
    return response.json()["response"].strip()

# parse the text where text is a command followed by comment text. a command is a word start with #, and it should be one of the keys in template_dic.
def parse_text(text):
    #regular expression to parse the command
    text = text.strip()
    if text.startswith("#"):
       x = text.split(" ", 1)
       command = x[0][1:]
       com_text = "" if len(x) == 1 else x[1]
       return command, com_text
       
    return "", text

def process_selection():
    # 1. Copy selection to clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")

    # 2. Get the clipboard string
    time.sleep(0.1)
    text = pyperclip.paste()
    command_str, command_text = parse_text(text)
    print("command is : ", command_str)
    # 3. Fix string
    if not text:
        return
    
    fixed_text = process_text(command_text, command_str)
    if not fixed_text:
        return

    # 4. Paste the fixed string to the clipboard
    pyperclip.copy(fixed_text)
    time.sleep(0.1)

    # 5. Paste the clipboard and replace the selected text
    with controller.pressed(Key.cmd):
        controller.tap("v")


def on_f9():
    #fix_current_line()
    process_selection()



with keyboard.GlobalHotKeys({"<101>": on_f9}) as h:
    h.join()
