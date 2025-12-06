#!/usr/bin/env python3
"""
Translate untranslated strings in language files.
Finds keys that have the same value as English and translates them.
"""
import json
import os

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_nested_value(data, key_path):
    keys = key_path.split('.')
    current = data
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return None
        current = current[k]
    return current

def set_nested_value(data, key_path, value):
    keys = key_path.split('.')
    current = data
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value

# Translation mappings - these are specific translations that need to be done
# For many technical terms, we'll keep them as-is or provide minimal translations
translations_map = {
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
        # Note: "Video", "Dashboard", "Analyst", "Moderator" are commonly used loanwords in German
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

def translate_file(lang_code, messages_dir):
    en_file = os.path.join(messages_dir, 'en.json')
    lang_file = os.path.join(messages_dir, f'{lang_code}.json')
    
    if not os.path.exists(lang_file):
        print(f"File {lang_file} not found")
        return
    
    en_data = load_json(en_file)
    lang_data = load_json(lang_file)
    
    # Flatten English keys
    en_keys = {}
    def recurse_en(current, parent_key=''):
        if isinstance(current, dict):
            for k, v in current.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                recurse_en(v, new_key)
        else:
            en_keys[parent_key] = current
    recurse_en(en_data)
    
    # Find untranslated keys
    updates = {}
    translations = translations_map.get(lang_code, {})
    
    for key_path, en_value in en_keys.items():
        lang_value = get_nested_value(lang_data, key_path)
        if lang_value == en_value:  # Untranslated
            if key_path in translations:
                updates[key_path] = translations[key_path]
            # For keys like "Video", "Document", "Admin" - these are loanwords, 
            # but we can still translate context-dependent ones
    
    # Apply updates
    for key_path, new_value in updates.items():
        set_nested_value(lang_data, key_path, new_value)
        print(f"  Updated {key_path}: {new_value}")
    
    if updates:
        save_json(lang_file, lang_data)
        print(f"✓ {lang_code.upper()}: Updated {len(updates)} keys")
    else:
        print(f"⊘ {lang_code.upper()}: No updates needed")

if __name__ == '__main__':
    messages_dir = os.path.join(os.path.dirname(__file__), '..', 'messages')
    for lang in ['de', 'fr', 'bg', 'es']:
        print(f"\nProcessing {lang.upper()}...")
        translate_file(lang, messages_dir)

