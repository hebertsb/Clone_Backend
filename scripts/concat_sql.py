from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SQL_DIR = BASE / 'dumps' / 'sql'
OUT_FILE = BASE / 'dumps' / 'all_inserts.sql'

FILES_ORDER = [
    'contenttypes_ContentType.sql',
    'auth_Permission.sql',
    'auth_Group.sql',
    'authz_Rol.sql',
    'authz_Usuario.sql',
    'catalogo_Categoria.sql',
    'catalogo_Destino.sql',
    'catalogo_Itinerario.sql',
    'catalogo_Servicio.sql',
    'catalogo_Paquete.sql',
    'descuentos_Descuento.sql',
    'descuentos_ServicioDescuento.sql',
    'cupones_Cupon.sql',
    'reservas_Reserva.sql',
    'reservas_ReservaServicio.sql',
    'reservas_Acompanante.sql',
    'reservas_ReservaAcompanante.sql',
    'admin_LogEntry.sql',
    'sessions_Session.sql',
]


def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open('w', encoding='utf-8') as out:
        out.write("-- Combined SQL inserts\n")
        out.write("SET session_replication_role = 'replica';\n\n")
        for fname in FILES_ORDER:
            fpath = SQL_DIR / fname
            out.write(f"-- BEGIN FILE: {fname}\n")
            if fpath.exists():
                out.write(fpath.read_text(encoding='utf-8'))
                out.write('\n\n')
            else:
                out.write(f"-- MISSING FILE: {fname}\n\n")
        out.write("SET session_replication_role = 'origin';\n")

    print('Wrote', OUT_FILE)


if __name__ == '__main__':
    main()
