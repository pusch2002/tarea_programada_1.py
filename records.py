# records.py
from __future__ import annotations

import os
import random
import struct
from dataclasses import dataclass
from datetime import date, timedelta
from typing import BinaryIO, Optional

# =========================
# Constantes de "tamaño fijo"
# =========================
NAME_LEN = 40
PROV_LEN = 20
CANT_LEN = 20
DIST_LEN = 20

COUNT_STRUCT = struct.Struct(">I")  # 4 bytes: cantidad de registros (big-endian)

# Nuevo campo: numero_empleado (entero positivo)
# Layout del registro (tamaño fijo):
# numero_empleado: 4 bytes unsigned int
# nombre: 40 bytes
# edad: 1 byte unsigned
# fecha_ordinal: 4 bytes unsigned int
# provincia: 20 bytes
# canton: 20 bytes
# distrito: 20 bytes
RECORD_STRUCT = struct.Struct(f">I {NAME_LEN}s B I {PROV_LEN}s {CANT_LEN}s {DIST_LEN}s")
RECORD_SIZE = RECORD_STRUCT.size
HEADER_SIZE = COUNT_STRUCT.size


# =========================
# Datos (ampliados)
# =========================
NOMBRES = [
    "Ana", "Luis", "María", "José", "Valeria", "Sebastián", "Camila", "Diego", "Sofía", "Daniel",
    "Paula", "Andrés", "Lucía", "Mateo", "Laura", "Gabriel", "Isabela", "Marco", "Elena", "Javier",
    "Natalia", "David", "Carla", "Tomás", "Fernanda", "Pablo", "Noelia", "Bruno", "Ariana", "Emilio",
    "Mónica", "Ricardo", "Andrea", "Kevin", "Alonso", "Cristina", "Fabián", "Juliana", "Vicky", "Esteban",
]

PROVINCIAS = [
    "San Jose", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limon",
    # inventadas (2-3)
    "Monteverde", "Pacifica", "Atlantida",
]

CANTONES = [
    "Central", "Escazu", "Desamparados", "Santa Ana", "Goicoechea", "Alajuelita", "Tibas",
    "Grecia", "San Ramon", "Atenas", "Oreamuno", "Paraiso", "Santo Domingo", "Barva",
    "Nicoya", "Liberia", "Santa Cruz", "Esparza", "Quepos", "Golfito", "Pococi", "Siquirres",
]

DISTRITOS = [
    "Carmen", "Merced", "Hospital", "Catedral", "Zapote", "San Francisco", "San Rafael",
    "San Miguel", "San Juan", "San Pedro", "San Isidro", "San Pablo", "San Antonio",
    "Pavas", "Hatillo", "Guadalupe", "Curridabat", "Tres Rios", "Guacima", "Coyol",
    "Rio Claro", "Palmares", "Naranjo", "Turrialba", "Guapiles",
]


# =========================
# Modelo
# =========================
@dataclass(frozen=True)
class Record:
    numero_empleado: int
    nombre: str
    edad: int
    nacimiento: date
    provincia: str
    canton: str
    distrito: str


# =========================
# Utilidades de bytes fijos
# =========================
def _to_fixed_bytes(text: str, length: int) -> bytes:
    b = text.encode("utf-8", errors="replace")
    if len(b) > length:
        b = b[:length]
    return b + b"\0" * (length - len(b))


def _from_fixed_bytes(b: bytes) -> str:
    return b.decode("utf-8", errors="replace").rstrip("\0").strip()


# =========================
# Pack / Unpack
# =========================
def pack_record(r: Record) -> bytes:
    if r.numero_empleado <= 0:
        raise ValueError("numero_empleado debe ser positivo (> 0).")
    if not (0 <= r.edad <= 255):
        raise ValueError("edad debe caber en 1 byte (0..255).")

    return RECORD_STRUCT.pack(
        r.numero_empleado,
        _to_fixed_bytes(r.nombre, NAME_LEN),
        r.edad,
        r.nacimiento.toordinal(),
        _to_fixed_bytes(r.provincia, PROV_LEN),
        _to_fixed_bytes(r.canton, CANT_LEN),
        _to_fixed_bytes(r.distrito, DIST_LEN),
    )


def unpack_record(raw: bytes) -> Record:
    (emp, nombre_b, edad, ordinal, prov_b, cant_b, dist_b) = RECORD_STRUCT.unpack(raw)
    return Record(
        numero_empleado=int(emp),
        nombre=_from_fixed_bytes(nombre_b),
        edad=int(edad),
        nacimiento=date.fromordinal(int(ordinal)),
        provincia=_from_fixed_bytes(prov_b),
        canton=_from_fixed_bytes(cant_b),
        distrito=_from_fixed_bytes(dist_b),
    )


# =========================
# Archivo binario (servicios)
# =========================
def write_file(path: str, records_in_order: list[Record]) -> None:
    if not path.lower().endswith(".bin"):
        raise ValueError("El archivo DEBE tener extensión .bin")

    with open(path, "wb") as f:
        f.write(COUNT_STRUCT.pack(len(records_in_order)))
        for r in records_in_order:
            f.write(pack_record(r))


def read_count(f: BinaryIO) -> int:
    f.seek(0)
    header = f.read(HEADER_SIZE)
    if len(header) != HEADER_SIZE:
        raise ValueError("Archivo inválido: no contiene encabezado.")
    (n,) = COUNT_STRUCT.unpack(header)
    return int(n)


def read_record_at(f: BinaryIO, index: int) -> Record:
    # index es 0-based
    offset = HEADER_SIZE + index * RECORD_SIZE
    f.seek(offset)
    raw = f.read(RECORD_SIZE)
    if len(raw) != RECORD_SIZE:
        raise IndexError("No se pudo leer el registro: índice fuera de rango o archivo corrupto.")
    return unpack_record(raw)


def binary_search_by_employee(f: BinaryIO, employee_number: int) -> Optional[tuple[int, Record]]:
    """
    Devuelve (index, record) si existe, si no None.
    Búsqueda binaria SOBRE EL ARCHIVO (sin cargar todo en memoria).
    """
    if employee_number <= 0:
        return None

    n = read_count(f)
    low, high = 0, n - 1

    while low <= high:
        mid = (low + high) // 2
        r = read_record_at(f, mid)
        if r.numero_empleado == employee_number:
            return mid, r
        if r.numero_empleado < employee_number:
            low = mid + 1
        else:
            high = mid - 1

    return None


# =========================
# Generación aleatoria ordenada
# =========================
def _random_birthdate(rng: random.Random) -> date:
    # Rango razonable: 18 a 65 años
    today = date.today()
    min_days = 18 * 365
    max_days = 65 * 365
    days_ago = rng.randint(min_days, max_days)
    return today - timedelta(days=days_ago)


def generate_sorted_records(count: int, seed: Optional[int] = None) -> list[Record]:
    if count <= 0:
        raise ValueError("La cantidad de registros debe ser > 0.")

    rng = random.Random(seed)

    # Para que NO sea consecutivo: usamos sample en un rango amplio y luego ordenamos.
    # Esto produce números aleatorios únicos y no la secuencia 1..N.
    max_emp = max(1000, count * 50)  # rango amplio para evitar repetición
    if max_emp <= count:
        max_emp = count + 1000

    employee_numbers = rng.sample(range(1, max_emp + 1), k=count)
    employee_numbers.sort()  # orden ascendente obligatorio

    records: list[Record] = []
    for emp in employee_numbers:
        nombre = rng.choice(NOMBRES)
        edad = rng.randint(18, 65)
        nac = _random_birthdate(rng)

        prov = rng.choice(PROVINCIAS)
        cant = rng.choice(CANTONES)
        dist = rng.choice(DISTRITOS)

        records.append(
            Record(
                numero_empleado=emp,
                nombre=nombre,
                edad=edad,
                nacimiento=nac,
                provincia=prov,
                canton=cant,
                distrito=dist,
            )
        )

    return records


def ensure_file_exists(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")
