from configparser import ConfigParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.ini"

if not CONFIG_FILE.is_file():
    raise FileNotFoundError(
        f"Configuration file not found: {CONFIG_FILE}. "
        "Copy config.ini.example to config.ini and set the database connection."
    )

parser = ConfigParser(interpolation=None)
parser.read(CONFIG_FILE, encoding="utf-8")
if "database" not in parser:
    raise ValueError(f"Missing [database] section in {CONFIG_FILE}")

database_settings = parser["database"]
DB_CONFIG = {
    "dbname": database_settings["dbname"],
    "user": database_settings["user"],
    "password": database_settings["password"],
    "host": database_settings["host"],
    "port": database_settings.getint("port"),
}

RESOURCES_DIR = PROJECT_ROOT / "resources"
IMAGES_DIR = RESOURCES_DIR / "images"
PRODUCT_IMAGES_DIR = RESOURCES_DIR / "products"
IMPORT_DATA_DIR = RESOURCES_DIR / "import-data"
SCHEMA_FILE = PROJECT_ROOT / "database" / "shoe_store.sql"
ICON_FILE = IMAGES_DIR / "Icon.ico"
LOGO_FILE = IMAGES_DIR / "Icon.png"
DEFAULT_PRODUCT_IMAGE = IMAGES_DIR / "picture.png"

COLOR_MAIN_BG = "#FFFFFF"
COLOR_ADDITIONAL_BG = "#7FFF00"
COLOR_ACCENT = "#00FA9A"
COLOR_DISCOUNT_BG = "#2E8B57"

FONT_PRIMARY = ("Times New Roman", 12)
FONT_PRIMARY_BOLD = ("Times New Roman", 12, "bold")
FONT_TITLE = ("Times New Roman", 16, "bold")
FONT_CARD_TITLE = ("Times New Roman", 14, "bold")
FONT_CARD_BODY = ("Times New Roman", 11)
FONT_CARD_ACCENT = ("Times New Roman", 12, "bold")


def resolve_product_image(photo_path: str | None) -> Path:
    if not photo_path:
        return DEFAULT_PRODUCT_IMAGE

    path = Path(photo_path)
    if path.is_absolute():
        return path

    if path.parts[:2] == ("import", "products"):
        return PRODUCT_IMAGES_DIR / path.name

    return PROJECT_ROOT / path
