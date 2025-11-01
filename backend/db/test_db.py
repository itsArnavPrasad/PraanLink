"""
Simple test script to verify database connection and table creation
"""
from db.database import engine, init_db, SessionLocal
from db.models import CheckIn, Prescription, Report, Hospital, Insurance

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_tables():
    """Test table creation"""
    try:
        init_db()
        print("✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False

def test_models():
    """Test model imports"""
    try:
        print("✓ All models imported successfully:")
        print(f"  - CheckIn")
        print(f"  - Prescription")
        print(f"  - Report")
        print(f"  - Hospital")
        print(f"  - Insurance")
        return True
    except Exception as e:
        print(f"✗ Model import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing database setup...")
    print("-" * 40)
    
    test_models()
    if test_connection():
        test_tables()
    
    print("-" * 40)
    print("Test complete!")

