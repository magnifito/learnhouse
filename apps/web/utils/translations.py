#!/usr/bin/env python3
"""
LearnHouse Translation Management Tool

This script provides tools to:
1. Check translation key usage and consistency
2. Sync translation keys across language files
3. Get untranslated strings for each language
4. Translate untranslated strings
5. Refactor translation calls from scoped namespaces to dot notation
"""

import argparse
import json
import os
import re
import sys
import collections
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
MESSAGES_DIR = PROJECT_ROOT / 'messages'
SOURCE_FILE = 'en.json'
SOURCE_DIRS = [
    PROJECT_ROOT / 'app',
    PROJECT_ROOT / 'components',
    PROJECT_ROOT / 'lib',
    PROJECT_ROOT / 'hooks',
    PROJECT_ROOT / 'services',
]


# ============================================================================
# Shared Utility Functions
# ============================================================================

def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file with UTF-8 encoding."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=collections.OrderedDict)


def save_json(file_path: str, data: Dict[str, Any]) -> None:
    """Save JSON file with UTF-8 encoding and proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def load_json_keys(file_path: str) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """Load JSON file and return flat key dictionary and original structure."""
    data = load_json(file_path)
    
    keys = {}
    def recurse(current: Any, parent_key: str = '') -> None:
        if isinstance(current, dict):
            for k, v in current.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                recurse(v, new_key)
        else:
            keys[parent_key] = current
    
    recurse(data)
    return keys, data


def get_nested_value(data: Dict[str, Any], key_path: str) -> Optional[Any]:
    """Get nested value from dictionary using dot notation key path."""
    keys = key_path.split('.')
    current = data
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return None
        current = current[k]
    return current


def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set nested value in dictionary using dot notation key path."""
    keys = key_path.split('.')
    current = data
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value


def count_keys(d: Dict[str, Any]) -> int:
    """Recursively count all leaf keys in a nested dictionary."""
    count = 0
    for v in d.values():
        if isinstance(v, dict):
            count += count_keys(v)
        else:
            count += 1
    return count


# ============================================================================
# Command: check
# ============================================================================

def find_usages(source_dirs: List[Path]) -> Tuple[Set[str], Dict[str, List[str]]]:
    """Find all translation key usages in source code."""
    used_keys = set()
    usage_locations = {}  # key -> list of file paths

    # Regex to find usage with dot notation: t('namespace.key') or t("namespace.key")
    usage_pattern = re.compile(r"\bt\(\s*['\"]([^'\"]+\.[^'\"]+)['\"]\s*[,)]")

    for source_dir in source_dirs:
        if not source_dir.exists():
            continue
            
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(('.tsx', '.ts', '.jsx', '.js')):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(PROJECT_ROOT)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                            usages = usage_pattern.findall(content)

                            for full_key in usages:
                                if full_key not in usage_locations:
                                    usage_locations[full_key] = []
                                usage_locations[full_key].append(str(rel_path))
                                used_keys.add(full_key)

                    except Exception as e:
                        print(f"Error reading {file_path}: {e}", file=sys.stderr)

    return used_keys, usage_locations


def compare_languages(messages_dir: Path, source_map: Dict[str, str], 
                      source_filename: str = 'en.json', verbose: bool = False) -> None:
    """Compare language files with source file and report differences."""
    if verbose:
        print("\n" + "="*50)
        print("LANGUAGE COMPARISON REPORT")
        print("="*50)

    try:
        files = [f for f in os.listdir(messages_dir) 
                 if f.endswith('.json') and f != source_filename]
        
        if not files:
            if verbose:
                print("No other language files found to compare.")
            return

        source_keys_set = set(source_map.keys())

        for lang_file in sorted(files):
            file_path = messages_dir / lang_file
            if verbose:
                print(f"\nComparing {lang_file} with {source_filename}...")
            
            try:
                lang_map, _ = load_json_keys(str(file_path))
                lang_keys_set = set(lang_map.keys())
                
                # Missing keys (in EN but not in Lang)
                missing_in_lang = source_keys_set - lang_keys_set
                
                # Extra keys (in Lang but not in EN)
                extra_in_lang = lang_keys_set - source_keys_set

                # Untranslated keys (Value is identical to source)
                untranslated = []
                for k in source_keys_set:
                    if k in lang_map and source_map[k] == lang_map[k]:
                        untranslated.append(k)
                
                if not missing_in_lang and not extra_in_lang and not untranslated:
                    if verbose:
                        print(f"  [OK] {lang_file} matches {source_filename} structure and has unique values.")
                else:
                    if missing_in_lang:
                        print(f"  [!] Missing Keys ({len(missing_in_lang)}):")
                        for k in sorted(missing_in_lang)[:10]:
                            print(f"      - {k}")
                        if len(missing_in_lang) > 10 and not verbose:
                            print(f"      ... and {len(missing_in_lang) - 10} more")
                    
                    if extra_in_lang:
                        print(f"  [?] Extra Keys ({len(extra_in_lang)}):")
                        for k in sorted(extra_in_lang)[:10]:
                            print(f"      + {k}")
                        if len(extra_in_lang) > 10 and not verbose:
                            print(f"      ... and {len(extra_in_lang) - 10} more")
                            
                    if untranslated:
                        print(f"  [*] Untranslated Strings (Same as English) ({len(untranslated)}):")
                        limit = 10 if not verbose else 50
                        for k in sorted(untranslated)[:limit]:
                            print(f"      ~ {k}: \"{lang_map[k][:50]}...\"")
                        if len(untranslated) > limit:
                            print(f"      ... and {len(untranslated) - limit} more.")

            except Exception as e:
                print(f"  [Error] Could not process {lang_file}: {e}", file=sys.stderr)
                if verbose:
                    import traceback
                    traceback.print_exc()
                
    except Exception as e:
        print(f"Error reading messages directory: {e}", file=sys.stderr)


def cmd_check(args):
    """Check translation key usage and consistency."""
    messages_file = MESSAGES_DIR / SOURCE_FILE
    
    if not messages_file.exists():
        print(f"Error: Messages file not found at {messages_file}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Loading keys from {messages_file}...")
    
    defined_map, json_data = load_json_keys(str(messages_file))
    defined_keys = set(defined_map.keys())
    
    if args.verbose:
        print(f"Found {len(defined_keys)} defined keys.")

    if args.verbose:
        print("Scanning codebase for usages...")
    
    used_keys_found, usage_locations = find_usages(SOURCE_DIRS)
    
    # Analyze Code Usage vs EN JSON
    valid_used_keys = used_keys_found.intersection(defined_keys)
    unused_keys = defined_keys - valid_used_keys
    
    print("\n" + "="*50)
    print("CODE USAGE REPORT")
    print("="*50)
    
    if unused_keys:
        print(f"\nUnused Keys in en.json ({len(unused_keys)}):")
        for k in sorted(unused_keys):
            print(f"  [?] {k}")
            if args.verbose and k in usage_locations:
                for loc in usage_locations[k][:3]:
                    print(f"      → {loc}")
                if len(usage_locations[k]) > 3:
                    print(f"      ... and {len(usage_locations[k]) - 3} more locations")
    else:
        print("\n✓ No unused keys found")

    potentially_missing = used_keys_found - defined_keys
    filtered_missing = {k for k in potentially_missing if "." in k}
    
    if filtered_missing:
        print(f"\nPotentially Missing Keys in en.json ({len(filtered_missing)}):")
        for k in sorted(filtered_missing):
            print(f"  [!] {k}")
            if args.verbose and k in usage_locations:
                for loc in usage_locations[k][:3]:
                    print(f"      → {loc}")
    else:
        print("\n✓ No missing keys found")

    # Compare Languages
    compare_languages(MESSAGES_DIR, defined_map, SOURCE_FILE, verbose=args.verbose)


# ============================================================================
# Command: sync
# ============================================================================

def sync_dict(source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sync keys from source to target."""
    synced = collections.OrderedDict()
    
    for key, value in source.items():
        if key in target:
            if isinstance(value, dict) and isinstance(target[key], dict):
                # Recurse
                synced[key] = sync_dict(value, target[key])
            else:
                # Keep existing translation
                synced[key] = target[key]
                # Warn if type mismatch
                if type(value) != type(target[key]):
                    print(f"    [!] Type mismatch for key '{key}'. Overwriting with source structure.")
                    synced[key] = value
        else:
            # Missing key: copy from source
            synced[key] = value
    
    return synced


def cmd_sync(args):
    """Sync translation keys across language files."""
    source_path = MESSAGES_DIR / SOURCE_FILE
    
    if not source_path.exists():
        print(f"Error: Source file {SOURCE_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Loading source: {SOURCE_FILE}")
    
    source_data = load_json(str(source_path))
    source_key_count = count_keys(source_data)
    
    if args.verbose:
        print(f"Source keys: {source_key_count}")

    files = [f for f in os.listdir(MESSAGES_DIR) 
             if f.endswith('.json') and f != SOURCE_FILE]
    
    if not files:
        print("No other language files found.")
        return

    for filename in sorted(files):
        file_path = MESSAGES_DIR / filename
        
        if args.verbose:
            print(f"\nSyncing {filename}...")
        
        try:
            target_data = load_json(str(file_path))
            original_count = count_keys(target_data)
            
            synced_data = sync_dict(source_data, target_data)
            new_count = count_keys(synced_data)
            
            if args.dry_run:
                print(f"  [DRY RUN] Would sync {filename}")
                print(f"    Keys: {original_count} -> {new_count}")
            else:
                save_json(str(file_path), synced_data)
                print(f"  ✓ Synced {filename}. Keys: {original_count} -> {new_count}")
            
        except Exception as e:
            print(f"  Error processing {filename}: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()


# ============================================================================
# Command: get-untranslated
# ============================================================================

def cmd_get_untranslated(args):
    """Get all untranslated strings for each language."""
    source_path = MESSAGES_DIR / SOURCE_FILE
    
    if not source_path.exists():
        print(f"Error: Source file {SOURCE_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    
    source_map = load_json_keys(str(source_path))[0]

    files = [f for f in os.listdir(MESSAGES_DIR) 
             if f.endswith('.json') and f != SOURCE_FILE]
    
    if args.lang:
        files = [f for f in files if f.replace('.json', '') in args.lang]

    for lang_file in sorted(files):
        file_path = MESSAGES_DIR / lang_file
        lang_map = load_json_keys(str(file_path))[0]

        # Find untranslated (identical to English)
        untranslated = []
        for key in source_map:
            if key in lang_map and source_map[key] == lang_map[key]:
                untranslated.append((key, source_map[key]))

        if untranslated:
            print(f"\n{'='*60}")
            print(f"{lang_file.replace('.json', '').upper()} - {len(untranslated)} untranslated strings")
            print(f"{'='*60}")
            
            limit = args.limit if args.limit > 0 else len(untranslated)
            for key, value in sorted(untranslated)[:limit]:
                print(f"{key}: {value}")
            
            if len(untranslated) > limit:
                print(f"\n... and {len(untranslated) - limit} more untranslated strings")
        else:
            if args.verbose:
                print(f"\n✓ {lang_file.replace('.json', '').upper()}: All strings translated")


# ============================================================================
# Command: translate
# ============================================================================

# Translation mappings for specific languages
TRANSLATIONS_MAP = {
    'de': {
        'activityNavigation.next': 'Weiter',
        'activityNavigation.previous': 'Zurück',
        'activityNavigation.of': 'von',
        'activityNavigation.noNextActivity': 'Keine weitere Aktivität',
        'activityNavigation.noPreviousActivity': 'Keine vorherige Aktivität',
        'activityModals.assignment.create': 'Aufgabe erstellen',
        'activityModals.assignment.desc': 'Beschreibung',
        'activityModals.assignment.descPlaceholder': 'Bitte geben Sie eine Beschreibung ein',
        'activityModals.assignment.datePlaceholder': 'Bitte wählen Sie ein Fälligkeitsdatum',
        'activityModals.assignment.gradingPlaceholder': 'Bitte wählen Sie einen Bewertungstyp',
        'activityModals.assignment.options.alphabet': 'Alphabetisch (A, B, C, D, F)',
        'activityModals.assignment.options.numeric': 'Numerisch (0-100)',
        'activityModals.assignment.options.percentage': 'Prozentsatz (0%-100%)',
        'certificatePage.types.achievement': 'Leistung',
        'certificatePage.types.assessment': 'Bewertung',
        'certificatePage.types.completion': 'Abschluss',
        'certificatePage.types.continuing': 'Fortbildung',
        'certificatePage.types.mastery': 'Meisterschaft',
        'certificatePage.types.participation': 'Teilnahme',
        'certificatePage.types.professional': 'Beruflich',
        'certificatePage.types.specialization': 'Spezialisierung',
        'usergroups.title': 'Benutzergruppen & Benutzer verwalten',
    },
    'fr': {
        'activityNavigation.next': 'Suivant',
        'activityNavigation.previous': 'Précédent',
        'activityNavigation.of': 'de',
        'activityNavigation.noNextActivity': 'Aucune activité suivante',
        'activityNavigation.noPreviousActivity': 'Aucune activité précédente',
        'activityModals.assignment.create': 'Créer un Devoir',
        'activityModals.assignment.desc': 'Description',
        'activityModals.assignment.descPlaceholder': 'Veuillez entrer une description',
        'activityModals.assignment.description': 'Description',
        'activityModals.assignment.datePlaceholder': 'Veuillez sélectionner une date d\'échéance',
        'activityModals.assignment.gradingPlaceholder': 'Veuillez sélectionner un type de notation',
        'activityModals.assignment.options.alphabet': 'Alphabétique (A, B, C, D, F)',
        'activityModals.assignment.options.numeric': 'Numérique (0-100)',
        'activityModals.assignment.options.percentage': 'Pourcentage (0%-100%)',
        'activityModals.video.minutes': 'Minutes',
        'certificatePage.types.achievement': 'Réalisation',
        'certificatePage.types.assessment': 'Évaluation',
        'certificatePage.types.completion': 'Achèvement',
        'certificatePage.types.continuing': 'Formation continue',
        'certificatePage.types.mastery': 'Maîtrise',
        'certificatePage.types.participation': 'Participation',
        'certificatePage.types.professional': 'Professionnel',
        'certificatePage.types.specialization': 'Spécialisation',
        'certificatePage.types.workshop': 'Atelier',
        'usergroups.title': 'Gérer les Groupes d\'Utilisateurs et les Utilisateurs',
    },
    'bg': {
        'images.youtube': 'YouTube',
        'images.loom': 'Loom',
        'usergroups.buttons.create': 'Създай Потребителска Група',
        'usergroups.buttons.manageUsers': 'Управлявай Потребители',
        'usergroups.createModal.title': 'Създай Потребителска Група',
        'usergroups.createModal.description': 'Създай нова потребителска група за управление на потребители',
        'usergroups.deleteError': 'Грешка при изтриване на потребителска група',
        'usergroups.deleteModal.title': 'Изтрий Потребителска Група?',
        'usergroups.deleteModal.confirmButton': 'Изтрий Потребителска Група',
        'usergroups.deleteModal.message': 'Достъпът до всички ресурси ще бъде премахнат за всички потребители в тази група.',
        'usergroups.deletedSuccess': 'Потребителската група е изтрита',
        'usergroups.deleting': 'Изтриване...',
        'usergroups.description': 'Потребителските групи са начин за групиране на потребители заедно за управление на достъпа.',
        'usergroups.manageUsersModal.title': 'Управлявай Потребители в Група',
        'usergroups.manageUsersModal.description': 'Управлявай потребителите в тази потребителска група',
        'usergroups.table.actions': 'Действия',
        'usergroups.table.description': 'Описание',
        'usergroups.table.manageUsers': 'Управлявай Потребители',
        'usergroups.table.userGroup': 'Потребителска Група',
        'usergroups.title': 'Управлявай Потребителски Групи и Потребители',
    },
    'es': {
        'activityNavigation.next': 'Siguiente',
        'activityNavigation.previous': 'Anterior',
        'activityNavigation.of': 'de',
        'activityNavigation.noNextActivity': 'No hay siguiente actividad',
        'activityNavigation.noPreviousActivity': 'No hay actividad anterior',
        'activityModals.assignment.create': 'Crear Tarea',
        'activityModals.assignment.desc': 'Descripción',
        'activityModals.assignment.descPlaceholder': 'Por favor ingresa una descripción',
        'activityModals.assignment.datePlaceholder': 'Por favor selecciona una fecha de vencimiento',
        'activityModals.assignment.gradingPlaceholder': 'Por favor selecciona un tipo de calificación',
        'activityModals.assignment.options.alphabet': 'Alfabético (A, B, C, D, F)',
        'activityModals.assignment.options.numeric': 'Numérico (0-100)',
        'activityModals.assignment.options.percentage': 'Porcentaje (0%-100%)',
        'certificatePage.types.achievement': 'Logro',
        'certificatePage.types.assessment': 'Evaluación',
        'certificatePage.types.completion': 'Finalización',
        'certificatePage.types.continuing': 'Educación continua',
        'certificatePage.types.mastery': 'Dominio',
        'certificatePage.types.participation': 'Participación',
        'certificatePage.types.professional': 'Profesional',
        'certificatePage.types.specialization': 'Especialización',
        'certificatePage.types.workshop': 'Taller',
        'usergroups.title': 'Administrar Grupos de Usuarios y Usuarios',
    }
}


def translate_file(lang_code: str, messages_dir: Path, verbose: bool = False, 
                   dry_run: bool = False) -> int:
    """Translate untranslated strings in a language file."""
    en_file = messages_dir / SOURCE_FILE
    lang_file = messages_dir / f'{lang_code}.json'
    
    if not lang_file.exists():
        print(f"File {lang_file} not found", file=sys.stderr)
        return 0
    
    en_data = load_json(str(en_file))
    lang_data = load_json(str(lang_file))
    
    # Flatten English keys
    en_keys = {}
    def recurse_en(current: Any, parent_key: str = '') -> None:
        if isinstance(current, dict):
            for k, v in current.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                recurse_en(v, new_key)
        else:
            en_keys[parent_key] = current
    recurse_en(en_data)
    
    # Find untranslated keys
    updates = {}
    translations = TRANSLATIONS_MAP.get(lang_code, {})
    
    for key_path, en_value in en_keys.items():
        lang_value = get_nested_value(lang_data, key_path)
        if lang_value == en_value:  # Untranslated
            if key_path in translations:
                updates[key_path] = translations[key_path]
    
    if not updates:
        if verbose:
            print(f"⊘ {lang_code.upper()}: No updates needed")
        return 0
    
    # Apply updates
    for key_path, new_value in updates.items():
        set_nested_value(lang_data, key_path, new_value)
        if verbose:
            print(f"  Updated {key_path}: {new_value}")
    
    if dry_run:
        print(f"  [DRY RUN] Would update {lang_code.upper()}: {len(updates)} keys")
    else:
        save_json(str(lang_file), lang_data)
        print(f"✓ {lang_code.upper()}: Updated {len(updates)} keys")
    
    return len(updates)


def cmd_translate(args):
    """Translate untranslated strings in language files."""
    languages = args.lang if args.lang else ['de', 'fr', 'bg', 'es']
    
    if args.verbose:
        print(f"Translating files for: {', '.join(languages)}")
    
    total_updates = 0
    for lang in languages:
        if args.verbose:
            print(f"\nProcessing {lang.upper()}...")
        updates = translate_file(lang, MESSAGES_DIR, verbose=args.verbose, dry_run=args.dry_run)
        total_updates += updates
    
    if args.dry_run:
        print(f"\n[DRY RUN] Would update {total_updates} keys total")
    else:
        print(f"\n✓ Updated {total_updates} keys across {len(languages)} language(s)")


# ============================================================================
# Command: refactor
# ============================================================================

class TranslationRefactor:
    """Refactor translation calls from scoped namespaces to dot notation."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.original_content = f.read()
        self.content = self.original_content
        self.namespace_map: Dict[str, str] = {}  # var_name -> namespace

    def find_namespaces(self) -> Dict[str, str]:
        """Find all useTranslations declarations and map variable names to namespaces."""
        pattern = r"const\s+(\w+)\s*=\s*useTranslations\(\s*['\"]([^'\"]+)['\"]\s*\)"

        for match in re.finditer(pattern, self.content):
            var_name = match.group(1)
            namespace = match.group(2)
            self.namespace_map[var_name] = namespace

        return self.namespace_map

    def refactor_translation_calls(self) -> str:
        """Replace all translation calls with dot notation."""
        if not self.namespace_map:
            return self.content

        # Sort by length (descending) to handle longer variable names first
        sorted_vars = sorted(self.namespace_map.keys(), key=len, reverse=True)

        for var_name in sorted_vars:
            namespace = self.namespace_map[var_name]
            pattern = r'\b' + re.escape(var_name) + r'\(\s*([\'"])([^\'"]+)\1\s*\)'

            def replace_call(match):
                quote = match.group(1)
                key = match.group(2)
                return f"t({quote}{namespace}.{key}{quote})"

            self.content = re.sub(pattern, replace_call, self.content)

        return self.content

    def refactor_declarations(self) -> str:
        """Replace all useTranslations declarations with a single one."""
        if not self.namespace_map:
            return self.content

        # Find all the old declarations
        pattern = r"const\s+\w+\s*=\s*useTranslations\(\s*['\"][^'\"]+['\"]\s*\)\s*\n?"
        old_declarations = list(re.finditer(pattern, self.content))

        if not old_declarations:
            return self.content

        # Remove all old declarations
        for match in reversed(old_declarations):
            self.content = self.content[:match.start()] + self.content[match.end():]

        # Find where to insert the new declaration
        import_pattern = r"import.*useTranslations.*from.*['\"]next-intl['\"]"
        import_match = re.search(import_pattern, self.content)

        if import_match:
            insert_pos = import_match.end()
            next_newline = self.content.find('\n', insert_pos)
            if next_newline != -1:
                component_patterns = [
                    r'\nconst\s+\w+\s*=\s*\([^)]*\)\s*(?::\s*\w+\s*)?=>',
                    r'\nfunction\s+\w+',
                    r'\nconst\s+validate\s*=',
                ]

                best_insert_pos = None
                for pattern in component_patterns:
                    match = re.search(pattern, self.content[next_newline:])
                    if match:
                        brace_pos = self.content.find('{', next_newline + match.start())
                        if brace_pos != -1:
                            line_end = self.content.find('\n', brace_pos)
                            if line_end != -1:
                                best_insert_pos = line_end
                                break

                if best_insert_pos:
                    new_declaration = "\n  const t = useTranslations()"
                    self.content = (
                        self.content[:best_insert_pos] +
                        new_declaration +
                        self.content[best_insert_pos:]
                    )

        return self.content

    def refactor(self) -> Tuple[bool, str]:
        """Perform the full refactoring."""
        self.find_namespaces()

        if not self.namespace_map:
            return False, "No scoped useTranslations found"

        # Step 1: Replace translation calls
        self.refactor_translation_calls()

        # Step 2: Replace declarations
        self.refactor_declarations()

        # Check if anything changed
        if self.content == self.original_content:
            return False, "No changes needed"

        return True, "Refactored successfully"

    def save(self, dry_run: bool = True):
        """Save the refactored content."""
        if dry_run:
            print(f"\n{'='*60}")
            print(f"PREVIEW: {self.file_path.relative_to(PROJECT_ROOT)}")
            print(f"{'='*60}")
            print(self.content[:2000])
            if len(self.content) > 2000:
                print(f"\n... (truncated, total length: {len(self.content)})")
            return

        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"  ✓ Saved {self.file_path.relative_to(PROJECT_ROOT)}")


def find_files_to_refactor() -> List[Path]:
    """Find all TypeScript/JavaScript files with scoped useTranslations."""
    files = []

    for source_dir in SOURCE_DIRS:
        if not source_dir.exists():
            continue

        for file_path in source_dir.rglob('*'):
            if file_path.suffix in ['.tsx', '.ts', '.jsx', '.js']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if re.search(r"useTranslations\(\s*['\"][^'\"]+['\"]\s*\)", content):
                            files.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}", file=sys.stderr)

    return files


def cmd_refactor(args):
    """Refactor translation calls from scoped namespaces to dot notation."""
    if args.verbose:
        print("Translation Refactoring Tool")
        print("="*60)
        print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE RUN'}")
        print()

    files = find_files_to_refactor()
    
    if args.verbose:
        print(f"Found {len(files)} files to refactor\n")

    success_count = 0
    skip_count = 0
    error_count = 0

    for file_path in files:
        if args.verbose:
            print(f"\n📝 Processing: {file_path.relative_to(PROJECT_ROOT)}")

        try:
            refactor = TranslationRefactor(str(file_path))
            changed, message = refactor.refactor()

            if changed:
                if args.verbose:
                    print(f"  ✓ {message}")
                if args.preview and success_count < 2:
                    refactor.save(dry_run=True)
                if not args.dry_run:
                    refactor.save(dry_run=False)
                success_count += 1
            else:
                if args.verbose:
                    print(f"  ⊘ {message}")
                skip_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            error_count += 1

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Successfully refactored: {success_count}")
    print(f"Skipped: {skip_count}")
    print(f"Errors: {error_count}")
    print()

    if args.dry_run:
        print("This was a DRY RUN. No files were modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print("✓ All changes have been applied!")
        if args.verbose:
            print("\nNext steps:")
            print("1. Review the changes with: git diff")
            print("2. Test your application")
            print("3. Run: python utils/translations.py check")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='LearnHouse Translation Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  check           Check translation key usage and consistency
  sync            Sync translation keys across language files
  get-untranslated Get all untranslated strings for each language
  translate       Translate untranslated strings using predefined mappings
  refactor        Refactor translation calls from scoped namespaces to dot notation

Examples:
  %(prog)s check --verbose
  %(prog)s sync --dry-run
  %(prog)s get-untranslated --lang de fr
  %(prog)s translate --lang de fr
  %(prog)s refactor --dry-run --preview
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands', metavar='COMMAND')
    subparsers.required = True
    
    # Check command
    parser_check = subparsers.add_parser('check', help='Check translation key usage and consistency')
    parser_check.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser_check.set_defaults(func=cmd_check)
    
    # Sync command
    parser_sync = subparsers.add_parser('sync', help='Sync translation keys across language files')
    parser_sync.add_argument('--dry-run', '-n', action='store_true', help='Show what would be changed without making changes')
    parser_sync.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser_sync.set_defaults(func=cmd_sync)
    
    # Get-untranslated command
    parser_get_untranslated = subparsers.add_parser('get-untranslated', help='Get all untranslated strings for each language')
    parser_get_untranslated.add_argument('--lang', nargs='+', help='Language codes to check (default: all)')
    parser_get_untranslated.add_argument('--limit', type=int, default=0, help='Limit number of results per language (0 = all)')
    parser_get_untranslated.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser_get_untranslated.set_defaults(func=cmd_get_untranslated)
    
    # Translate command
    parser_translate = subparsers.add_parser('translate', help='Translate untranslated strings using predefined mappings')
    parser_translate.add_argument('--lang', nargs='+', help='Language codes to translate (default: all)')
    parser_translate.add_argument('--dry-run', '-n', action='store_true', help='Show what would be changed without making changes')
    parser_translate.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser_translate.set_defaults(func=cmd_translate)
    
    # Refactor command
    parser_refactor = subparsers.add_parser('refactor', help='Refactor translation calls from scoped namespaces to dot notation')
    parser_refactor.add_argument('--dry-run', '-n', action='store_true', help='Show what would be changed without making changes')
    parser_refactor.add_argument('--preview', '-p', action='store_true', help='Show preview of first 2 files')
    parser_refactor.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser_refactor.set_defaults(func=cmd_refactor)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

