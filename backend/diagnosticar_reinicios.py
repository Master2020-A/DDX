"""
Script para diagnosticar qué está causando los reinicios del servidor
"""

import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.changes = []

    def on_modified(self, event):
        if not event.is_directory:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] MODIFICADO: {event.src_path}")
            self.changes.append(("modified", event.src_path, timestamp))

    def on_created(self, event):
        if not event.is_directory:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] CREADO: {event.src_path}")
            self.changes.append(("created", event.src_path, timestamp))

    def on_deleted(self, event):
        if not event.is_directory:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] ELIMINADO: {event.src_path}")
            self.changes.append(("deleted", event.src_path, timestamp))


def main():
    print("=" * 80)
    print("DIAGNÓSTICO DE REINICIOS DEL SERVIDOR")
    print("=" * 80)
    print("\nMonitoreando cambios en archivos Python...")
    print("Presiona Ctrl+C para detener\n")

    # Directorio a monitorear
    path = Path(__file__).parent / "app"

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n" + "=" * 80)
        print("RESUMEN DE CAMBIOS")
        print("=" * 80)

        # Agrupar por archivo
        file_changes = {}
        for change_type, filepath, timestamp in event_handler.changes:
            if filepath not in file_changes:
                file_changes[filepath] = []
            file_changes[filepath].append((change_type, timestamp))

        # Mostrar archivos que cambiaron más frecuentemente
        print("\nArchivos modificados frecuentemente:")
        sorted_files = sorted(
            file_changes.items(), key=lambda x: len(x[1]), reverse=True
        )

        for filepath, changes in sorted_files[:10]:
            print(f"\n{filepath}")
            print(f"  Total de cambios: {len(changes)}")
            print(f"  Tipos: {', '.join(set(c[0] for c in changes))}")

    observer.join()


if __name__ == "__main__":
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        main()
    except ImportError:
        print("ERROR: watchdog no está instalado")
        print("\nInstala con: pip install watchdog")
        print("\nAlternativamente, revisa manualmente:")
        print("1. ¿Hay algún proceso escribiendo logs constantemente?")
        print("2. ¿Hay archivos .pyc siendo regenerados?")
        print("3. ¿Hay archivos temporales siendo creados?")
        print("\nPara desactivar el auto-reload temporalmente:")
        print("   Cambia 'reload=True' a 'reload=False' en app/main.py")
