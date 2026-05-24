from datetime import timedelta

from app.database import SessionLocal, init_db
from app.models.db_models import User
from app.auth import hash_password, create_access_token

init_db()

db = SessionLocal()

email = "mamata@test.com"
password = "123456"
full_name = "D Mamata"

user = db.query(User).filter(User.email == email).first()

if user:
    user.full_name = full_name
    user.password_hash = hash_password(password)
    user.is_active = True
    db.commit()
    db.refresh(user)
    print("Existing user updated")
else:
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("New user created")

token = create_access_token(
    {
        "sub": str(user.id),
        "email": user.email
    },
    timedelta(hours=24)
)

print("User ready")
print("Email:", email)
print("Password:", password)
print("Token:", token[:40] + "...")

db.close()