"""
Быстрая проверка доступности сервера и порта Firebird.
Запускайте перед настройкой для диагностики проблем.
"""

import socket
import sys
from pathlib import Path

# Добавить корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_server_ping(host: str, port: int = 3055) -> bool:
    """
    Проверка доступности сервера (TCP соединение).
    
    Args:
        host: IP адрес сервера
        port: Порт для проверки
        
    Returns:
        bool: True если сервер доступен
    """
    print(f"Проверка доступности сервера {host}...")
    
    try:
        # Используем socket для проверки (кросс-платформенно)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Пытаемся подключиться к порту Firebird
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Сервер {host} доступен (порт {port} открыт)")
            return True
        else:
            print(f"⚠️  Сервер {host} доступен, но порт {port} закрыт")
            print(f"   Код ошибки: {result}")
            return False
            
    except socket.timeout:
        print(f"❌ Таймаут подключения к серверу {host}")
        print("   Возможные причины:")
        print("   - Сервер выключен")
        print("   - Проблемы с сетью")
        print("   - Firewall блокирует соединение")
        return False
    except socket.error as e:
        print(f"❌ Ошибка соединения с сервером {host}: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def check_port_open(host: str, port: int, timeout: int = 5) -> bool:
    """
    Проверка доступности конкретного порта.
    
    Args:
        host: IP адрес сервера
        port: Номер порта
        timeout: Таймаут в секундах
        
    Returns:
        bool: True если порт открыт
    """
    print(f"\nПроверка порта {port} на {host}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Порт {port} открыт и доступен")
            return True
        else:
            print(f"❌ Порт {port} закрыт или недоступен")
            print(f"   Код ошибки: {result}")
            return False
            
    except socket.timeout:
        print(f"❌ Таймаут при проверке порта {port}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке порта {port}: {e}")
        return False


def check_dns_resolution(host: str) -> bool:
    """
    Проверка разрешения DNS (если используется доменное имя).
    
    Args:
        host: Имя хоста или IP
        
    Returns:
        bool: True если разрешение успешно
    """
    print(f"\nПроверка разрешения DNS для {host}...")
    
    try:
        ip_address = socket.gethostbyname(host)
        print(f"✅ DNS разрешен: {host} -> {ip_address}")
        return True
    except socket.gaierror:
        print(f"⚠️  DNS не разрешен (используется как IP адрес)")
        return True  # Это нормально для IP адресов
    except Exception as e:
        print(f"❌ Ошибка разрешения DNS: {e}")
        return False


def main():
    """Главная функция диагностики."""
    
    print("=" * 80)
    print("  ДИАГНОСТИКА ДОСТУПНОСТИ УДАЛЕННОГО СЕРВЕРА FIREBIRD")
    print("=" * 80)
    
    # Параметры подключения
    HOST = "85.114.224.45"
    PORT = 3055
    
    print(f"\nПараметры:")
    print(f"  Сервер: {HOST}")
    print(f"  Порт Firebird: {PORT}")
    print(f"  Путь к БД: G:\\Гранит\\GRANITDB\\GEORGIA.GDB")
    
    # Список проверок
    checks = []
    
    # 1. Проверка DNS (если используется доменное имя)
    dns_ok = check_dns_resolution(HOST)
    checks.append(("DNS разрешение", dns_ok))
    
    # 2. Проверка доступности сервера
    server_ok = check_server_ping(HOST, PORT)
    checks.append(("Доступность сервера", server_ok))
    
    # 3. Проверка порта 3055
    if server_ok:
        port_ok = check_port_open(HOST, PORT)
        checks.append((f"Порт {PORT}", port_ok))
    else:
        print(f"\n⏭️  Пропуск проверки порта (сервер недоступен)")
        checks.append((f"Порт {PORT}", False))
    
    # Итоговые результаты
    print("\n" + "=" * 80)
    print("  РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
    print("=" * 80 + "\n")
    
    all_ok = True
    for check_name, result in checks:
        status = "✅ OK" if result else "❌ FAIL"
        print(f"{status:10} | {check_name}")
        if not result:
            all_ok = False
    
    print("\n" + "=" * 80)
    
    if all_ok:
        print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\nСервер доступен и готов к настройке Firebird.")
        print("\nСледующие шаги:")
        print("  1. Выполните команды из: docs/SERVER_SETUP_QUICK_COMMANDS.txt")
        print("  2. Запустите тесты: python scripts/test_remote_connection.py")
        return 0
    else:
        print("\n❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("\nЧто делать:")
        
        if not checks[1][1]:  # Сервер недоступен
            print("\n1. Проверьте подключение к сети:")
            print("   - Убедитесь, что вы подключены к интернету")
            print("   - Попробуйте: ping 85.114.224.45")
            print("\n2. Проверьте доступность сервера:")
            print("   - Сервер может быть выключен")
            print("   - Firewall может блокировать соединение")
            print("   - VPN может требоваться для доступа")
        
        elif not checks[2][1]:  # Порт закрыт
            print("\n1. На сервере нужно:")
            print("   - Запустить службу Firebird")
            print("   - Открыть порт 3050 в Windows Firewall")
            print("   - Настроить проброс портов на роутере (если нужно)")
            print("\n2. Следуйте инструкциям:")
            print("   - docs/SERVER_SETUP_INSTRUCTIONS.md")
            print("   - docs/SERVER_SETUP_QUICK_COMMANDS.txt")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

