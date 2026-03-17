import os
import sys
from sqlmodel import Session, select
from database import engine
from models.user_models import User
from security.hashing import hash_password

def seed_users():
    """Seed initial users into the database"""
    
    # Define users to seed
    users_to_seed = [
        {
            "name": "pharmacy",
            "username": "phar",
            "password": "phar",
            "role": "pharmacy"
        },
    ]
    
    with Session(engine) as session:
        for user_data in users_to_seed:
            username = user_data["username"]
            name = user_data["name"]
            password = user_data["password"]
            role=user_data["role"]
            
            # Check if user already exists
            existing_user = session.exec(select(User).where(User.username == username)).first()
            
            if not existing_user:
                # Create new user
                user = User(
                    name=name,
                    username=username,
                    password_hash=hash_password(password),
                    role=role
                )
                session.add(user)
                print(f"✅ Seeded user: {username}")
            else:
                print(f"⚠️ User already exists: {username}")
        
        # Commit all changes at once
        session.commit()
        print("\n🎉 Seeding completed!")

if __name__ == "__main__":
    seed_users()


# name = os.getenv("SEED_NAME", "SDC")
# username = os.getenv("SEED_USER", "SDC")
# password = os.getenv("SEED_PASSWORD", "Alraz@22026")