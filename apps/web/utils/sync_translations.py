import os
import json
import collections

# Configuration
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
MESSAGES_DIR = os.path.join(PROJECT_ROOT, 'messages')
SOURCE_FILE = 'en.json'

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=collections.OrderedDict)

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n') # Add trailing newline

def sync_dict(source, target):
    """
    Recursively syncs keys from source to target.
    - Adds missing keys (value = source value).
    - Removes extra keys (optional, currently enabled).
    - Sorts keys to match source order.
    """
    synced = collections.OrderedDict()
    
    for key, value in source.items():
        if key in target:
            if isinstance(value, dict) and isinstance(target[key], dict):
                # Recurse
                synced[key] = sync_dict(value, target[key])
            else:
                # Keep existing translation
                synced[key] = target[key]
                # Warn if type mismatch? (e.g. string vs dict) - for now assume structure match
                if type(value) != type(target[key]):
                     print(f"    [!] Type mismatch for key '{key}'. Overwriting with source structure.")
                     synced[key] = value # Force overwrite if structure changed
        else:
            # Missing key: copy from source
            synced[key] = value
            # print(f"    [+] Added missing key: {key}") 
    
    # Check for extra keys in target (that are not in source)
    extras = set(target.keys()) - set(source.keys())
    if extras:
        # print(f"    [-] Removing extra keys: {extras}")
        pass # They are naturally removed because we are building a new dict from source structure

    return synced

def count_keys(d):
    count = 0
    for v in d.values():
        if isinstance(v, dict):
            count += count_keys(v)
        else:
            count += 1
    return count

def main():
    source_path = os.path.join(MESSAGES_DIR, SOURCE_FILE)
    if not os.path.exists(source_path):
        print(f"Error: Source file {SOURCE_FILE} not found.")
        return

    print(f"Loading source: {SOURCE_FILE}")
    source_data = load_json(source_path)
    source_key_count = count_keys(source_data)
    print(f"Source keys: {source_key_count}")

    files = [f for f in os.listdir(MESSAGES_DIR) if f.endswith('.json') and f != SOURCE_FILE]
    
    if not files:
        print("No other language files found.")
        return

    for filename in files:
        file_path = os.path.join(MESSAGES_DIR, filename)
        print(f"\nSyncing {filename}...")
        
        try:
            target_data = load_json(file_path)
            original_count = count_keys(target_data)
            
            synced_data = sync_dict(source_data, target_data)
            new_count = count_keys(synced_data)
            
            save_json(file_path, synced_data)
            print(f"  Done. Keys: {original_count} -> {new_count} (matched source)")
            
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
