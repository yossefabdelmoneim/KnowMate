"""Seed a data analysis user and create a valid token."""
import sys, os, uuid
sys.path.insert(0, '.')
import dotenv
dotenv.load_dotenv()

from app.Back_End.db.data_analysis.session import SessionLocal
from app.Back_End.models.data_analysis.user import User
from app.Back_End.core.security import hash_password, create_access_token

db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == 'datatest@test.com').first()
    if existing:
        user = existing
        print(f'User exists: {user.id}')
    else:
        user = User(
            id=uuid.uuid4(),
            email='datatest@test.com',
            hashed_password=hash_password('TestPass123!'),
            full_name='Data Test User',
            is_active=True,
            is_admin=True,
            role='admin'
        )
        db.add(user)
        db.commit()
        print(f'User created: {user.id}')
    
    token = create_access_token({'sub': str(user.id)})
    print(f'TOKEN:{token}')
finally:
    db.close()
