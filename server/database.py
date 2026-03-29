import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', 'database.sqlite')

async def init_db():
    # Ensure storage folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                filename TEXT NOT NULL,
                target_lang TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error TEXT,
                vtt_content TEXT,
                srt_content TEXT,
                segments_json TEXT
            )
        ''')
        await db.commit()

        # Migrate: add segments_json column if missing (for existing DBs)
        try:
            await db.execute("ALTER TABLE jobs ADD COLUMN segments_json TEXT")
            await db.commit()
        except Exception:
            pass  # Column already exists

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
