from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///inmailer.db')
logger.info(f"🔍 Database engine target: {'SQLite' if DATABASE_URL.startswith('sqlite') else 'PostgreSQL'}")

# Flag to prevent multiple modifications
_url_modified = False

# For development, use SQLite if no DATABASE_URL is provided
if DATABASE_URL.startswith('sqlite'):
    # SQLite configuration for development
    logger.info("🔍 Using SQLite database (development mode)")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # Set to False in production
    )
else:
    # PostgreSQL configuration for production (including Neon)
    logger.info("🔍 Using PostgreSQL database (production mode)")

    # Handle Neon database connection string
    if 'neon.tech' in DATABASE_URL or 'neon' in DATABASE_URL.lower():
        logger.info("🔍 Detected Neon database, applying special configuration")

        # Check if SSL mode is already specified and prevent multiple modifications
        if 'sslmode=' not in DATABASE_URL and not _url_modified:
            # Add SSL mode only if not already present and not already modified
            separator = '&' if '?' in DATABASE_URL else '?'
            DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
            _url_modified = True
            logger.info(f"🔍 Added SSL mode to DATABASE_URL: {DATABASE_URL[:50]}...")
        elif 'sslmode=' in DATABASE_URL:
            logger.info("🔍 SSL mode already specified in DATABASE_URL")
            # Log the current SSL mode to debug
            if 'sslmode=' in DATABASE_URL:
                ssl_part = DATABASE_URL.split('sslmode=')[1].split('&')[0] if '&' in DATABASE_URL.split('sslmode=')[1] else DATABASE_URL.split('sslmode=')[1]
                logger.info(f"🔍 Current SSL mode: {ssl_part}")
        elif _url_modified:
            logger.info("🔍 DATABASE_URL already modified, skipping SSL mode addition")

    logger.info("🔍 PostgreSQL connection URL resolved from environment")

    try:
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10
        ) #

        # Test the connection
        with engine.connect() as conn:
            logger.info("✅ Database connection test successful")

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error("❌ Please check your DATABASE_URL and database credentials")
        logger.error("❌ DATABASE_URL is invalid or unreachable")
        raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        from .models import Base
        from sqlalchemy import text, inspect

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"🔍 Existing tables before init: {existing_tables}")

        # Log user count before any changes
        if 'users' in existing_tables:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                logger.info(f"🔍 Users table exists with {count} rows")

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified successfully")

        # Re-check after create_all
        inspector = inspect(engine)
        existing_tables_after = inspector.get_table_names()
        logger.info(f"🔍 Existing tables after init: {existing_tables_after}")

        if 'users' in existing_tables_after:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                logger.info(f"🔍 Users table now has {count} rows")

        # Add oauth_credentials column if it doesn't already exist (safe migration)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        logger.info(f"🔍 Users table columns: {existing_columns}")
        if 'oauth_credentials' not in existing_columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN oauth_credentials JSON"))
                    conn.commit()
                logger.info("✅ Added oauth_credentials column to users table")
            except Exception as alter_err:
                logger.warning(f"⚠️ Could not add oauth_credentials column (may already exist): {alter_err}")

        # Add campaign_id column to email_logs if it doesn't already exist (safe migration)
        # campaigns table is created by Base.metadata.create_all above for new installs;
        # existing installs only need this ALTER on the email_logs table.
        if 'email_logs' in existing_tables_after:
            existing_email_log_columns = [col['name'] for col in inspector.get_columns('email_logs')]
            logger.info(f"🔍 email_logs table columns: {existing_email_log_columns}")
            if 'campaign_id' not in existing_email_log_columns:
                try:
                    with engine.connect() as conn:
                        conn.execute(text("ALTER TABLE email_logs ADD COLUMN campaign_id INTEGER REFERENCES campaigns(id)"))
                        conn.commit()
                    logger.info("✅ Added campaign_id column to email_logs table")
                except Exception as alter_err:
                    logger.warning(f"⚠️ Could not add campaign_id column to email_logs (may already exist): {alter_err}")

    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise

def get_db_session() -> Session:
    """Get a database session for direct use"""
    try:
        db = SessionLocal()
        # Test the connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return db
    except Exception as e:
        logger.error(f"❌ Failed to get database session: {e}")
        db.close()
        raise
