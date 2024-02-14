# Configuration Options

## Standard Options

### APP_NAME
The name of the app.

### APP_DESCRIPTION
Description of the app.
It is optional but recommended.

### FOOTER_TEXT
Text that will be shown in the footer of the page.
It can contain HTML elements.
Be careful to not include anything potentially harmful here as it can result in XSS.

## Monitoring Options

### TARGETS
The list of targets that the app will monitor.
You have to run the command "sync_targets" to synchronize
this list with the system's database after any modification.
Run this command in the root directory of the project:
flask --app status_dwarf commands sync_targets
List format: ("user-friendly name", "URL or IP address", "strategy")
The "strategy" option determines the strategy to check whether a target is operational
and can have the following values: "HTTP" and "PING"

### INTERVAL_SECONDS
How often should the app check whether the targets are up in seconds.
It isn't recommended to set this to anything lower than 15.

### STATUS_BLOCK_COVERAGE
How many hours should a status block encompass.
Note that changing this afterward will only affect future status blocks.
It isn't recommended to set this to anything lower than 1.

### STATUS_BLOCK_COUNT
How many status blocks should be displayed per target.

### PAGE_SIZE
How many targets should a page have.
Higher sizes may negatively affect the performance.

## Advanced Options

### CUSTOM_USER_AGENT
The user-agent text the app sends when making HTTP requests.

### SQLALCHEMY_DATABASE_URI
The location of your database.

### TRANSLATIONS_ENABLED
Turn on/off translations. If it is False, only English will be shown.
If you want to internationalize the app,
you have to translate the text used in the app from the i18n/i18n.json file.
You can find all words used in the app in the i18n/i18n_base.json file.
However, you should still add translations for custom text you set here in the config
from the i18n files if you want them to get translated too.

### ATOM_ENABLED
Turn on/off the ATOM feed.
