from datetime import timedelta
import os
import random

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///db.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Used for JWT tokens and other things later on
    SECRET_KEY = os.getenv("SECRET_KEY") or "".join(
        [chr(random.randint(65, 92)) for _ in range(50)]
    )

    # The days that the jwt token is valid for
    JWT_AGE=timedelta(days=1)
