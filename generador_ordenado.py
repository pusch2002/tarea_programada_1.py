# generador_ordenado.py
from __future__ import annotations

from records import generate_sorted_records, write_file

def main() -> None:
    print("=== Generador de registros (.bin) ordenados por número de empleado ===")

    try:
        n_str = input("¿Cuántos registros desea generar? ").strip()
        n = int(n_str)
        if n <= 0:
            print("Debe ingresar un entero mayor que 0.")
            return
    except ValueError:
        print("Entrada inválida. Debe ser un número entero.")
        return

    out_path = input("Nombre del archivo de salida (ej: empleados.bin): ").strip()
    if not out_path:
        out_path = "empleados.bin"

    try:
        records = generate_sorted_records(n)
        write_file(out_path, records)
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Listo ✅ Se generó '{out_path}' con {n} registros ordenados por número de empleado.")

if __name__ == "__main__":
    main()
