# ============ Standard Options ============

APP_NAME = "Status Dwarf"

# APP_DESCRIPTION is optional but recommended.
APP_DESCRIPTION = "A simple uptime status page."

# FOOTER_TEXT can contain HTML elements.
# Be careful to not include anything potentially harmful here as it can result in XSS.
FOOTER_TEXT = (
    "Made with <a href='https://github.com/cosmicproc/status_dwarf'>Status Dwarf</a>"
)

# ============ Monitoring Options ============

# The list of targets that the app will monitor.
# You have to run the command "sync_targets" to synchronize
# this list with the system's database after any modification.
# Run this command in the root directory of the project:
# flask --app status_dwarf commands sync_targets
# List format: ("user-friendly name", "URL address")
TARGETS = [
    ("GitHub", "https://github.com"),
    ("Python.org", "https://python.org"),
]

# How often should the app check whether the targets are up in seconds.
# It isn't recommended to set this to anything lower than 15.
INTERVAL_SECONDS = 60

# How many hours should a status block encompass.
# Note that changing this afterward will only affect future status blocks.
# It isn't recommended to set this to anything lower than 1.
STATUS_BLOCK_COVERAGE = 24

# How many status blocks should be displayed per target.
STATUS_BLOCK_COUNT = 30

# How many targets should a page have.
# Higher sizes may negatively affect the performance.
PAGE_SIZE = 8

# ============ Advanced Options ============

# The user-agent text the app sends when making HTTP requests.
CUSTOM_USER_AGENT = APP_NAME

# The location of your database.
SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"

# Turn on/off translations. If it is False, only English will be shown.
# If you want to internationalize the app,
# you have to translate the text used in the app from the i18n/i18n.json file.
# You can find all words used in the app in the i18n/i18n_base.json file.
# However, you should still add translations for custom text you set here in the config
# from the i18n files if you want them to get translated too.
TRANSLATIONS_ENABLED = True

# Turn on/off the ATOM feed.
ATOM_ENABLED = True
