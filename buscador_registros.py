# buscador_registros.py
from __future__ import annotations

from records import (
    ensure_file_exists,
    read_count,
    read_record_at,
    binary_search_by_employee,
)

def _print_record(index: int, r) -> None:
    print("\n=== Registro encontrado ===")
    print(f"Posición (0-based): {index}")
    print(f"Número empleado: {r.numero_empleado}")
    print(f"Nombre: {r.nombre}")
    print(f"Edad: {r.edad}")
    print(f"Nacimiento: {r.nacimiento.isoformat()}")
    print(f"Provincia: {r.provincia}")
    print(f"Cantón: {r.canton}")
    print(f"Distrito: {r.distrito}")
    print("==========================\n")

def main() -> None:
    print("=== Lector/Buscador de registros en archivo .bin ===")

    path = input("Ruta del archivo .bin (ej: empleados.bin): ").strip()
    if not path:
        path = "empleados.bin"

    try:
        ensure_file_exists(path)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\n¿Qué desea hacer?")
    print("1) Recuperar por posición (índice)")
    print("2) Recuperar por número de empleado (búsqueda binaria)")
    choice = input("Opción (1/2): ").strip()

    try:
        with open(path, "rb") as f:
            total = read_count(f)
            if total == 0:
                print("El archivo no tiene registros.")
                return

            if choice == "1":
                pos_str = input(f"Ingrese la posición (0 a {total-1}): ").strip()
                pos = int(pos_str)
                if pos < 0 or pos >= total:
                    print("Posición fuera de rango.")
                    return

                r = read_record_at(f, pos)
                _print_record(pos, r)

            elif choice == "2":
                emp_str = input("Ingrese el número de empleado (entero positivo): ").strip()
                emp = int(emp_str)
                res = binary_search_by_employee(f, emp)
                if res is None:
                    print("No existe un registro con ese número de empleado.")
                    return
                idx, r = res
                _print_record(idx, r)

            else:
                print("Opción inválida. Debe ser 1 o 2.")

    except ValueError:
        print("Entrada inválida. Debe ser un entero.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
