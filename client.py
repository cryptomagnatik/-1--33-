import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_URL = "http://127.0.0.1:8000/api.php"


def fetch(base_url, params=None):
    """Читаємо дані лише через HTTP, без доступу до books.json."""
    url = base_url + ("?" + urlencode(params) if params else "")
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8"))
            message = body.get("error", error.reason) if isinstance(body, dict) else error.reason
        except (ValueError, UnicodeError):
            message = error.reason
        raise RuntimeError(f"HTTP {error.code}: {message}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError("Не вдалося підключитися до API. Запустіть сервер: composer start") from error
    except (ValueError, UnicodeError) as error:
        raise RuntimeError("Сервер повернув некоректний JSON.") from error

    if not isinstance(payload, dict) or "data" not in payload:
        raise RuntimeError("Неочікуваний формат відповіді API.")
    return payload


def show(payload):
    data = payload["data"]
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise RuntimeError("Неочікуваний формат даних API.")
    if not data:
        print("За цим запитом книг не знайдено.")
        return
    for item in data:
        if isinstance(item, str):
            print(f"• {item}")
        elif isinstance(item, dict) and all(key in item for key in ("id", "title", "author", "year", "genre")):
            print(f"[{item['id']}] {item['title']}")
            print(f"    Автор: {item['author']} | Рік: {item['year']} | Жанр: {item['genre']}")
        else:
            raise RuntimeError("Неочікуваний запис у відповіді API.")
    print(f"Усього: {len(data)}")


def menu(base_url):
    while True:
        print("\nКАТАЛОГ КНИГ\n1. Усі книги\n2. Список жанрів\n3. Книги за жанром\n4. Книга за ID\n0. Вихід")
        choice = input("Ваш вибір: ").strip()
        if choice == "0":
            return
        if choice == "1":
            params = None
        elif choice == "2":
            params = {"action": "genres"}
        elif choice == "3":
            params = {"genre": input("Жанр (наприклад, Роман): ").strip()}
        elif choice == "4":
            params = {"id": input("ID книги: ").strip()}
        else:
            print("Оберіть число від 0 до 4.")
            continue
        try:
            show(fetch(base_url, params))
        except RuntimeError as error:
            print(f"Помилка: {error}")


def main():
    parser = argparse.ArgumentParser(description="Python-клієнт PHP API каталогу книг")
    parser.add_argument("--url", default=DEFAULT_URL, help="Повна адреса api.php без параметрів")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Показати всі книги")
    group.add_argument("--genres", action="store_true", help="Показати жанри")
    group.add_argument("--genre", help="Фільтр за жанром, наприклад Роман")
    group.add_argument("--id", type=int, help="Знайти книгу за ID")
    args = parser.parse_args()

    try:
        if args.all:
            show(fetch(args.url))
        elif args.genres:
            show(fetch(args.url, {"action": "genres"}))
        elif args.genre is not None:
            show(fetch(args.url, {"genre": args.genre}))
        elif args.id is not None:
            show(fetch(args.url, {"id": args.id}))
        else:
            menu(args.url)
    except RuntimeError as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nРоботу завершено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())