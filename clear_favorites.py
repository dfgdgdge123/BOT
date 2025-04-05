import os
import shelve


def clear_favorites_databases():
    # Удаляем все возможные файлы shelve для favorites
    db_names = ['favorites.db', 'favorites.db.dat', 'favorites.db.dir', 'favorites.db.bak']

    for db_name in db_names:
        try:
            if os.path.exists(db_name):
                os.remove(db_name)
                print(f"Deleted: {db_name}")
            else:
                print(f"Not found: {db_name}")
        except Exception as e:
            print(f"Error deleting {db_name}: {e}")

    # Альтернативный вариант - открыть и очистить через shelve
    try:
        with shelve.open('favorites.db') as db:
            db.clear()
            print("Cleared favorites.db contents")
    except Exception as e:
        print(f"Error clearing shelve database: {e}")


if __name__ == "__main__":
    print("Clearing favorites databases...")
    clear_favorites_databases()
    print("Done!")