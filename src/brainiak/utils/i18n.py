from tornado import locale
from brainiak import settings


mapping = {
    "pt": "pt_BR"
}


def translate(word, lang=None):
    lang = lang or settings.DEFAULT_LANG
    language = mapping.get(lang) or lang
    locale.load_gettext_translations(directory="locale", domain="brainiak")
    user_locale = locale.get(language)
    return user_locale.translate(word)


_ = translate
