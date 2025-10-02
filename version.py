#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Version Management

Управление версиями проекта.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def get_current_version():
    """Получение текущей версии."""
    version_file = Path("VERSION")
    
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return "0.0.0"

def set_version(version):
    """Установка версии."""
    version_file = Path("VERSION")
    
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version)
    
    print(f"✅ Версия установлена: {version}")

def get_git_info():
    """Получение информации из Git."""
    try:
        # Получаем хеш коммита
        commit_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip()[:8]
        
        # Получаем количество коммитов
        commit_count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip()
        
        # Получаем дату последнего коммита
        commit_date = subprocess.run(
            ["git", "log", "-1", "--format=%ci"],
            capture_output=True, text=True
        ).stdout.strip()
        
        return {
            'hash': commit_hash,
            'count': commit_count,
            'date': commit_date
        }
        
    except Exception as e:
        print(f"⚠️ Ошибка получения Git информации: {e}")
        return None

def create_version_info():
    """Создание информации о версии."""
    print("📋 Создание информации о версии...")
    
    version = get_current_version()
    git_info = get_git_info()
    
    version_info = {
        'version': version,
        'build_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'git': git_info
    }
    
    # Создаем файл с информацией о версии
    version_file = Path("src/version_info.py")
    
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(f'''"""
Coffee Sales Analysis Tool - Version Information

Автоматически сгенерированный файл с информацией о версии.
Не редактируйте этот файл вручную.
"""

VERSION = "{version}"
BUILD_DATE = "{version_info['build_date']}"
GIT_HASH = "{git_info['hash'] if git_info else 'unknown'}"
GIT_COMMITS = "{git_info['count'] if git_info else 'unknown'}"
GIT_DATE = "{git_info['date'] if git_info else 'unknown'}"

def get_version():
    """Получение версии приложения."""
    return VERSION

def get_build_info():
    """Получение информации о сборке."""
    return {{
        'version': VERSION,
        'build_date': BUILD_DATE,
        'git_hash': GIT_HASH,
        'git_commits': GIT_COMMITS,
        'git_date': GIT_DATE
    }}

def get_version_string():
    """Получение строки версии."""
    return f"{{VERSION}} ({{GIT_HASH}})"
''')
    
    print("✅ Создан файл version_info.py")

def update_version_file(version):
    """Обновление файла версии."""
    print(f"🔄 Обновление версии до {version}...")
    
    # Обновляем VERSION файл
    set_version(version)
    
    # Обновляем version_info.py
    create_version_info()
    
    # Обновляем config.env
    config_file = Path("config.env")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Обновляем версию в config.env
        if "APP_VERSION=" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("APP_VERSION="):
                    lines[i] = f"APP_VERSION={version}"
                    break
            content = '\n'.join(lines)
        else:
            content += f"\nAPP_VERSION={version}\n"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Обновлен config.env")

def create_changelog_entry(version, changes):
    """Создание записи в changelog."""
    print(f"📝 Создание записи в changelog для версии {version}...")
    
    changelog_file = Path("docs/CHANGELOG.md")
    
    if not changelog_file.exists():
        print("⚠️ Файл changelog не найден")
        return
    
    # Читаем существующий changelog
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Создаем новую запись
    date = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""## [{version}] - {date}

### Added
{changes.get('added', '- Нет изменений')}

### Changed
{changes.get('changed', '- Нет изменений')}

### Fixed
{changes.get('fixed', '- Нет изменений')}

### Removed
{changes.get('removed', '- Нет изменений')}

"""
    
    # Вставляем новую запись после заголовка
    lines = content.split('\n')
    insert_index = 0
    
    for i, line in enumerate(lines):
        if line.startswith('## [') and not line.startswith('## [Unreleased'):
            insert_index = i
            break
    
    lines.insert(insert_index, new_entry)
    
    # Записываем обновленный changelog
    with open(changelog_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ Обновлен changelog")

def create_release_tag(version):
    """Создание тега релиза."""
    print(f"🏷️ Создание тега релиза {version}...")
    
    try:
        # Создаем тег
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"Release {version}"], check=True)
        print(f"✅ Создан тег v{version}")
        
        # Отправляем тег
        subprocess.run(["git", "push", "origin", f"v{version}"], check=True)
        print(f"✅ Тег v{version} отправлен")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания тега: {e}")
        return False

def main():
    """Главная функция управления версиями."""
    print("📋 Управление версиями Coffee Sales Analysis Tool...")
    
    if len(sys.argv) < 2:
        print("Использование: python version.py <команда> [аргументы]")
        print("Команды:")
        print("  get - получить текущую версию")
        print("  set <версия> - установить версию")
        print("  bump <тип> - увеличить версию (major, minor, patch)")
        print("  release <версия> - создать релиз")
        return 1
    
    command = sys.argv[1]
    
    if command == "get":
        version = get_current_version()
        print(f"Текущая версия: {version}")
        
        git_info = get_git_info()
        if git_info:
            print(f"Git хеш: {git_info['hash']}")
            print(f"Коммитов: {git_info['count']}")
            print(f"Дата: {git_info['date']}")
        
        return 0
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("❌ Укажите версию")
            return 1
        
        version = sys.argv[2]
        update_version_file(version)
        return 0
    
    elif command == "bump":
        if len(sys.argv) < 3:
            print("❌ Укажите тип увеличения (major, minor, patch)")
            return 1
        
        bump_type = sys.argv[2]
        current_version = get_current_version()
        
        # Парсим версию
        parts = current_version.split('.')
        if len(parts) != 3:
            print("❌ Неверный формат версии")
            return 1
        
        major, minor, patch = map(int, parts)
        
        # Увеличиваем версию
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            print("❌ Неверный тип увеличения")
            return 1
        
        new_version = f"{major}.{minor}.{patch}"
        update_version_file(new_version)
        return 0
    
    elif command == "release":
        if len(sys.argv) < 3:
            print("❌ Укажите версию")
            return 1
        
        version = sys.argv[2]
        
        # Обновляем версию
        update_version_file(version)
        
        # Создаем тег
        if create_release_tag(version):
            print(f"🎉 Релиз {version} создан успешно!")
        else:
            print(f"⚠️ Релиз {version} создан, но тег не создан")
        
        return 0
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

