"""Bootstrap intencional del schema de demo. Para producción real, usar Alembic."""
import asyncio
import os
from app.db.session import engine
from app.models.user import Base

async def main():
    if os.getenv('ALLOW_SCHEMA_INIT') != 'yes':
        raise SystemExit('Requiere ALLOW_SCHEMA_INIT=yes (operación explícita, no automática).')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print('Schema inicializado. Preparar migraciones para cambios posteriores.')

if __name__ == '__main__':
    asyncio.run(main())
