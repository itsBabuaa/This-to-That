import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

# Disable SSL verification for corporate proxies
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
old_request = requests.Session.request
def _patched_request(self, *args, **kwargs):
    kwargs["verify"] = False
    return old_request(self, *args, **kwargs)
requests.Session.request = _patched_request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian", "Portuguese",
    "Chinese (Simplified)", "Chinese (Traditional)", "Japanese", "Korean",
    "Arabic", "Hindi", "Russian", "Turkish", "Dutch", "Polish", "Swedish",
    "Thai", "Vietnamese", "Indonesian",
]

LANG_CODES = {
    "English": "en", "Spanish": "es", "French": "fr", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW", "Japanese": "ja", "Korean": "ko",
    "Arabic": "ar", "Hindi": "hi", "Russian": "ru", "Turkish": "tr",
    "Dutch": "nl", "Polish": "pl", "Swedish": "sv", "Thai": "th",
    "Vietnamese": "vi", "Indonesian": "id",
}

LANG_NAMES = {
    "en": "English", "ja": "Japanese", "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)", "ko": "Korean", "es": "Spanish",
    "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese",
    "ar": "Arabic", "hi": "Hindi", "ru": "Russian", "tr": "Turkish",
    "nl": "Dutch", "pl": "Polish", "sv": "Swedish", "th": "Thai",
    "vi": "Vietnamese", "id": "Indonesian",
}

MAX_CHARS = 50_000
SUPPORTED_EXTS = {".txt", ".json", ".csv", ".md", ".xml", ".html", ".yml", ".yaml", ".log", ".ini", ".cfg", ".tsv"}
