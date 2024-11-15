from typing import Optional
from fastapi import HTTPException, Request , Header
from backend.db import open_connection, close_connection
from datetime import datetime, timedelta
import jwt
from asyncpg import Connection


# Function to log login attempts
async def log_login_attempt(conn, username: str, success: bool, token ,error_message: Optional[str] = None):
    """Log the login attempt to the 'login_logs' table."""
    try:
        await conn.execute("DROP TABLE login_logs;")
        # Ensure that the login_logs table exists
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS login_logs (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                token TEXT
            );
            """
        )
        
        # Insert the login attempt into the login_logs table
        await conn.execute(
            """
            INSERT INTO login_logs (email, success, error_message, token)
            VALUES ($1, $2, $3, $4);
            """,
            username, success, error_message, token
        )
        print(f"Login attempt for user '{username}' logged successfully.")
    except Exception as e:
        print(f"Failed to log login attempt for '{username}': {e}")


# Helper function to verify JWT token and extract user info
async def verify_jwt_token(authorization: str = Header(...)) -> int:
    # Ensure the Authorization header exists and starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )
    
    # Extract the token
    token = authorization[len("Bearer "):]
    
    # Connect to the database and check the token
    conn: Connection = await open_connection()
    try:
        query = "SELECT id FROM login_logs WHERE token = $1"
        result = await conn.fetchrow(query, token)
        
        if result:
            return result["id"]
        else:
            raise HTTPException(
                status_code=401, detail="Invalid or expired token"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error verifying token: {str(e)}"
        )
    finally:
        await close_connection(conn)

# Helper function to generate JWT token
def create_jwt_token(username: str, SECRET_KEY, ALGORITHM):
    expiration_time = datetime.utcnow() + timedelta(minutes=10)  # 1 hour validity
    payload = {
        "sub": username,
        "exp": expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expiration_time

