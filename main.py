import json
import os
import sys
import tempfile
import urllib.request
from urllib.parse import urlparse
from PIL import Image

# Config
IMAGE_FOLDER = "Monument_dataset_new"
pause = "--pause" in sys.argv

def download_url_to_temp(url):
    # Download a URL to a temp file and return the filepath
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1] or ".jpg"
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tf.close()
    try:
        urllib.request.urlretrieve(url, tf.name)
        return tf.name
    except Exception:
        try:
            # fallback: stream write
            with urllib.request.urlopen(url) as resp, open(tf.name, "wb") as out:
                out.write(resp.read())
            return tf.name
        except Exception:
            os.unlink(tf.name)
            raise

def resolve_image_path(site):
    # Decide between local path and URL; return (path, is_temp_file)
    image_path = site.get("image_path") or site.get("image_url")
    if not image_path:
        return None, False

    # URL?
    if image_path.startswith("http://") or image_path.startswith("https://"):
        path = download_url_to_temp(image_path)
        return path, True

    # If absolute path, use it directly
    if os.path.isabs(image_path):
        return image_path, False

    # Try inside IMAGE_FOLDER first, then as given
    candidate = os.path.join(IMAGE_FOLDER, image_path)
    if os.path.exists(candidate):
        return candidate, False
    if os.path.exists(image_path):
        return image_path, False

    # Try normalizing slashes
    candidate2 = os.path.normpath(candidate)
    if os.path.exists(candidate2):
        return candidate2, False

    # Not found — still return the candidate path (will error later)
    return candidate, False

# Load JSON
try:
    with open("heritage_sites.json", "r", encoding="utf-8") as f:
        heritage_sites = json.load(f)
except FileNotFoundError:
    print("❌ Error: 'heritage_sites.json' file not found.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Error: Failed to decode JSON: {e}")
    sys.exit(1)

# Resolve image paths (and possibly download URLs to temp files)
for site in heritage_sites:
    resolved, is_temp = resolve_image_path(site)
    site["resolved_image_path"] = resolved
    site["_image_is_temp"] = is_temp

# Display loop
for site in heritage_sites:
    print(f"🏛️ {site.get('name', 'Unknown')} — {site.get('location', 'Unknown')}")
    print(f"  Built Year: {site.get('built_year', 'N/A')}")
    print(f"  Facts: {site.get('facts', '')}")
    precautions = site.get("precautions") or []
    print(f"  Precautions: {', '.join(precautions)}")
    print("-" * 60)

    image_path = site.get("resolved_image_path")
    if image_path:
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(image_path)
            img = Image.open(image_path)
            img.show()
        except FileNotFoundError:
            print(f"⚠️ Image not found: {image_path}")
        except Exception as e:
            print(f"❌ Error showing image for {site.get('name', 'Unknown')}: {e}")
        finally:
            # remove temp file if we downloaded it
            if site.get("_image_is_temp"):
                try:
                    os.unlink(image_path)
                except Exception:
                    pass
    else:
        print("⚠️ No image path provided for this site.")

    if pause:
        input("Press Enter to continue to the next monument...\n")
