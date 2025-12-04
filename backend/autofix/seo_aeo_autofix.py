import os
import json

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_PATH = os.path.join(BASE_DIR, "templates", "seo_aeo_templates.json")

SEO_DIR = "frontend/src/pages/seo"
AEO_DIR = "frontend/src/pages/aeo"


def write_if_missing(path, content):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def autofix_seo_aeo():
    changed = False

    # load templates
    with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
        templates = json.load(f)

    # SEO files
    for filename, body in templates["seo"].items():
        output = os.path.join(SEO_DIR, filename)
        if write_if_missing(output, body):
            changed = True

    # AEO files
    for filename, body in templates["aeo"].items():
        output = os.path.join(AEO_DIR, filename)
        if write_if_missing(output, body):
            changed = True

    return changed
