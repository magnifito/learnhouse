#!/usr/bin/env python3
"""
Refactor next-intl translations from scoped namespaces to dot notation.

Before:
  const t = useTranslations('auth')
  const c = useTranslations('common')
  t('login')
  c('save')

After:
  const t = useTranslations()
  t('auth.login')
  t('common.save')
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIRS = [
    PROJECT_ROOT / 'app',
    PROJECT_ROOT / 'components',
    PROJECT_ROOT / 'lib',
    PROJECT_ROOT / 'hooks',
    PROJECT_ROOT / 'services',
]

class TranslationRefactor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            self.original_content = f.read()
        self.content = self.original_content
        self.namespace_map: Dict[str, str] = {}  # var_name -> namespace

    def find_namespaces(self) -> Dict[str, str]:
        """Find all useTranslations declarations and map variable names to namespaces."""
        # Pattern: const varName = useTranslations('namespace')
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
        # This prevents 'tv' from being replaced before 'tvCustom' etc.
        sorted_vars = sorted(self.namespace_map.keys(), key=len, reverse=True)

        for var_name in sorted_vars:
            namespace = self.namespace_map[var_name]

            # Pattern: varName('key') or varName("key")
            # We need to be careful to only match function calls, not declarations
            pattern = r'\b' + re.escape(var_name) + r'\(\s*([\'"])([^\'"]+)\1\s*\)'

            def replace_call(match):
                quote = match.group(1)
                key = match.group(2)
                # Replace with t('namespace.key')
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
        for match in reversed(old_declarations):  # Reverse to maintain indices
            self.content = self.content[:match.start()] + self.content[match.end():]

        # Find where to insert the new declaration
        # Try to find the useTranslations import line
        import_pattern = r"import.*useTranslations.*from.*['\"]next-intl['\"]"
        import_match = re.search(import_pattern, self.content)

        if import_match:
            # Insert after the import
            insert_pos = import_match.end()
            # Find the next newline
            next_newline = self.content.find('\n', insert_pos)
            if next_newline != -1:
                # Find where the component/function starts
                # Look for common patterns
                component_patterns = [
                    r'\nconst\s+\w+\s*=\s*\([^)]*\)\s*(?::\s*\w+\s*)?=>',  # Arrow function
                    r'\nfunction\s+\w+',  # Regular function
                    r'\nconst\s+validate\s*=',  # validate function
                ]

                best_insert_pos = None
                for pattern in component_patterns:
                    match = re.search(pattern, self.content[next_newline:])
                    if match:
                        # Find the opening brace
                        brace_pos = self.content.find('{', next_newline + match.start())
                        if brace_pos != -1:
                            # Find end of line after brace
                            line_end = self.content.find('\n', brace_pos)
                            if line_end != -1:
                                best_insert_pos = line_end
                                break

                if best_insert_pos:
                    # Insert the new declaration
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

        print(f"  Found namespaces: {self.namespace_map}")

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
            print(f"PREVIEW: {self.file_path}")
            print(f"{'='*60}")
            print(self.content[:2000])
            if len(self.content) > 2000:
                print(f"\n... (truncated, total length: {len(self.content)})")
            return

        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"  ✓ Saved {self.file_path}")


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
                        # Check if file has scoped useTranslations
                        if re.search(r"useTranslations\(\s*['\"][^'\"]+['\"]\s*\)", content):
                            files.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return files


def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    preview = '--preview' in sys.argv or '-p' in sys.argv

    print("Translation Refactoring Tool")
    print("="*60)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE RUN'}")
    print()

    files = find_files_to_refactor()
    print(f"Found {len(files)} files to refactor\n")

    success_count = 0
    skip_count = 0
    error_count = 0

    for file_path in files:
        print(f"\n📝 Processing: {file_path.relative_to(PROJECT_ROOT)}")

        try:
            refactor = TranslationRefactor(str(file_path))
            changed, message = refactor.refactor()

            if changed:
                print(f"  ✓ {message}")
                if preview and success_count < 2:  # Show preview of first 2 files
                    refactor.save(dry_run=True)
                if not dry_run:
                    refactor.save(dry_run=False)
                success_count += 1
            else:
                print(f"  ⊘ {message}")
                skip_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
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

    if dry_run:
        print("This was a DRY RUN. No files were modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print("✓ All changes have been applied!")
        print("\nNext steps:")
        print("1. Review the changes with: git diff")
        print("2. Test your application")
        print("3. Run: python utils/check_translations.py")


if __name__ == '__main__':
    main()
