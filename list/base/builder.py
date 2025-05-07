import os
import shutil
import subprocess
import json
import urllib.request
from pathlib import Path

MINECRAFT_DIR = Path(os.getenv('APPDATA')) / '.minecraft'
PROFILES_JSON = MINECRAFT_DIR / 'launcher_profiles.json'
INSTALLER_DIR = Path.cwd()
MODS_DIR = MINECRAFT_DIR / 'mods'
FABRIC_INSTALLER_URL = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.11.2/fabric-installer-0.11.2.jar"

RUNE_PROFILE_ID = "RuneLoader"
RUNE_VERSION_ID = "1.21.5-fabric-rune"

def download_fabric_installer():
    jar_path = INSTALLER_DIR / 'fabric-installer.jar'
    if not jar_path.exists():
        print("Downloading Fabric installer...")
        urllib.request.urlretrieve(FABRIC_INSTALLER_URL, jar_path)
    return jar_path

def run_fabric_installer(jar_path):
    print("Running Fabric installer...")
    subprocess.run([
        'java', '-jar', str(jar_path),
        'client',
        '--dir', str(MINECRAFT_DIR),
        '--minecraft-version', '1.21.5',
        '--loader', '0.15.6',
        '--noprofile'
    ], check=True)

def inject_launcher_profile():
    if not PROFILES_JSON.exists():
        print("Cannot find launcher_profiles.json")
        return

    with open(PROFILES_JSON, 'r') as f:
        profiles = json.load(f)

    rune_profile = {
        "name": "RuneLoader",
        "type": "custom",
        "lastVersionId": RUNE_VERSION_ID,
        "icon": "Furnace",
        "javaArgs": "-Xmx4G",
        "gameDir": str(MODS_DIR)
    }

    profiles.setdefault("profiles", {})[RUNE_PROFILE_ID] = rune_profile

    with open(PROFILES_JSON, 'w') as f:
        json.dump(profiles, f, indent=4)

    print("Injected RuneLoader profile.")

def patch_version_files():
    version_dir = MINECRAFT_DIR / "versions"
    src = version_dir / "1.21.5"
    dst = version_dir / RUNE_VERSION_ID

    dst.mkdir(parents=True, exist_ok=True)

    shutil.copy(src / "1.21.5.jar", dst / f"{RUNE_VERSION_ID}.jar")
    with open(src / "1.21.5.json", "r") as f:
        data = json.load(f)

    data["id"] = RUNE_VERSION_ID
    with open(dst / f"{RUNE_VERSION_ID}.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Patched version files.")

def generate_uninstaller():
    code = f"""
import os
import json
from pathlib import Path

minecraft_dir = Path(os.getenv('APPDATA')) / '.minecraft'
profiles_path = minecraft_dir / 'launcher_profiles.json'

if profiles_path.exists():
    with open(profiles_path, 'r') as f:
        profiles = json.load(f)

    profiles['profiles'].pop('{RUNE_PROFILE_ID}', None)

    with open(profiles_path, 'w') as f:
        json.dump(profiles, f, indent=4)

print('RuneLoader uninstalled.')
"""
    with open("rune_uninstaller.py", "w") as f:
        f.write(code)

    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "rune_uninstaller.py"])
    os.remove("rune_uninstaller.py")
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("__pycache__", ignore_errors=True)
    print("Uninstaller generated.")

def build_injector():
    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "builder.py"])
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("__pycache__", ignore_errors=True)
    print("Installer EXE built.")

def main():
    fabric_installer = download_fabric_installer()
    run_fabric_installer(fabric_installer)
    inject_launcher_profile()
    patch_version_files()
    generate_uninstaller()
    build_injector()

if __name__ == '__main__':
    main()
