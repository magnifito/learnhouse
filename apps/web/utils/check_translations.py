import os
import json
import re
import sys

# Configuration
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
MESSAGES_FILE = os.path.join(PROJECT_ROOT, 'messages', 'en.json')
SOURCE_DIRS = [
    os.path.join(PROJECT_ROOT, 'app'),
    os.path.join(PROJECT_ROOT, 'components'),
    os.path.join(PROJECT_ROOT, 'lib'),
    os.path.join(PROJECT_ROOT, 'hooks'),
    os.path.join(PROJECT_ROOT, 'services') # Sometimes text is in services
]

def load_json_keys(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keys = {}
    def recurse(current, parent_key=''):
        if isinstance(current, dict):
            for k, v in current.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                recurse(v, new_key)
        else:
            keys[parent_key] = current
    
    recurse(data)
    return keys, data

def find_usages(source_dirs):
    used_keys = set()
    usage_locations = {} # key -> list of file paths

    # Regex to find usage with dot notation: t('namespace.key') or t("namespace.key")
    # This pattern matches t('...') where ... contains at least one dot
    usage_pattern = re.compile(r"\bt\(\s*['\"]([^'\"]+\.[^'\"]+)['\"]\s*[,)]")

    for source_dir in source_dirs:
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(('.tsx', '.ts', '.jsx', '.js')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                            usages = usage_pattern.findall(content)

                            for full_key in usages:
                                if full_key not in usage_locations:
                                    usage_locations[full_key] = []
                                usage_locations[full_key].append(rel_path)
                                used_keys.add(full_key)

                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

    return used_keys, usage_locations

def compare_languages(messages_dir, source_map, source_filename='en.json'):
    print("\n" + "="*50)
    print("LANGUAGE COMPARISON REPORT")
    print("="*50)

    try:
        files = os.listdir(messages_dir)
        json_files = [f for f in files if f.endswith('.json') and f != source_filename]
        
        if not json_files:
            print("No other language files found to compare.")
            return

        source_keys_set = set(source_map.keys())

        for lang_file in json_files:
            file_path = os.path.join(messages_dir, lang_file)
            print(f"\nComparing {lang_file} with {source_filename}...")
            
            try:
                lang_map, _ = load_json_keys(file_path)
                lang_keys_set = set(lang_map.keys())
                
                # Missing keys (in EN but not in Lang)
                missing_in_lang = source_keys_set - lang_keys_set
                
                # Extra keys (in Lang but not in EN)
                extra_in_lang = lang_keys_set - source_keys_set

                # Untranslated keys (Value is identical to source)
                untranslated = []
                for k in source_keys_set:
                    if k in lang_map and source_map[k] == lang_map[k]:
                        # Optional: filter out short/common words? No, strict is better for now.
                        untranslated.append(k)
                
                if not missing_in_lang and not extra_in_lang and not untranslated:
                    print(f"  [OK] {lang_file} matches {source_filename} structure and has unique values.")
                else:
                    if missing_in_lang:
                        print(f"  [!] Missing Keys ({len(missing_in_lang)}):")
                        for k in sorted(missing_in_lang):
                            print(f"      - {k}")
                    
                    if extra_in_lang:
                        print(f"  [?] Extra Keys ({len(extra_in_lang)}):")
                        for k in sorted(extra_in_lang):
                            print(f"      + {k}")
                            
                    if untranslated:
                        print(f"  [*] Untranslated Strings (Same as English) ({len(untranslated)}):")
                        # Only show a few if too many
                        limit = 10
                        for k in sorted(untranslated)[:limit]:
                             print(f"      ~ {k}: \"{lang_map[k][:50]}...\"")
                        if len(untranslated) > limit:
                            print(f"      ... and {len(untranslated) - limit} more.")

            except Exception as e:
                print(f"  [Error] Could not process {lang_file}: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"Error reading messages directory: {e}")

def main():
    if not os.path.exists(MESSAGES_FILE):
        print(f"Error: Messages file not found at {MESSAGES_FILE}")
        sys.exit(1)

    print(f"Loading keys from {MESSAGES_FILE}...")
    defined_map, json_data = load_json_keys(MESSAGES_FILE)
    defined_keys = set(defined_map.keys())
    print(f"Found {len(defined_keys)} defined keys.")

    print("Scanning codebase for usages...")
    used_keys_found, usage_locations = find_usages(SOURCE_DIRS)
    
    # Analyze Code Usage vs EN JSON
    valid_used_keys = used_keys_found.intersection(defined_keys)
    unused_keys = defined_keys - valid_used_keys
    
    print("\n" + "="*50)
    print("CODE USAGE REPORT")
    print("="*50)
    
    print(f"\nUnused Keys in en.json ({len(unused_keys)}):")
    for k in sorted(unused_keys):
        print(f"  [?] {k}")

    potentially_missing = used_keys_found - defined_keys
    filtered_missing = {k for k in potentially_missing if "." in k}
    
    print(f"\nPotentially Missing Keys in en.json ({len(filtered_missing)}):")
    for k in sorted(filtered_missing):
        print(f"  [!] {k}")

    # Compare Languages
    messages_dir = os.path.dirname(MESSAGES_FILE)
    compare_languages(messages_dir, defined_map)

if __name__ == "__main__":
    main()
