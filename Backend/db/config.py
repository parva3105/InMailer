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
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_AnXwLsk2vyc0@ep-red-block-adl3xcoi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

logger.info(f"🔍 Original DATABASE_URL: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else f"🔍 Original DATABASE_URL: {DATABASE_URL}")

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
    
    logger.info(f"🔍 Final DATABASE_URL for engine: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else f"🔍 Final DATABASE_URL for engine: {DATABASE_URL}")
    
    try:
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # Set to False in production
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20
        )
        
        # Test the connection
        with engine.connect() as conn:
            logger.info("✅ Database connection test successful")
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error("❌ Please check your DATABASE_URL and database credentials")
        logger.error(f"❌ DATABASE_URL used: {DATABASE_URL}")
        raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
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
