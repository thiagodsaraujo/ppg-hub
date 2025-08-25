# test_db.py
from sqlalchemy import create_engine, text
from app.core.config import settings

def main() -> None:
    print("🔌 Testando conexão com o banco...")
    engine = create_engine(settings.DATABASE_URL, echo=True)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
        print("✅ Conexão OK! SELECT 1 ->", result)

        # Verifica tabelas existentes
        tables = conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )).fetchall()
        print("📋 Tabelas disponíveis:", [t[0] for t in tables])

if __name__ == "__main__":
    main()
