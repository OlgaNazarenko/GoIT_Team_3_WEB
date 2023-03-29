import pickle
from typing import Optional

import redis as redis_db
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connect import get_db
from app.repository import users as repository_users
from app.database.models import User
from config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key_jwt
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis_db.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        The verify_password function takes a plain-text password and hashed password as arguments.
        It then uses the verify method of the pwd_context object to check if they match.
        The result is returned as a boolean value.

        :param self: Represent the instance of the class
        :param plain_password: Compare the password that is entered by the user to see if it matches
        :param hashed_password: Check if the password is hashed
        :return: True if the plain_password matches the hashed_password
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        The get_password_hash function takes a password as input and returns the hashed version of that password.
        The hashing algorithm used is PBKDF2, which is considered secure for most applications.

        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is being hashed
        :return: A hashed password
        """
        return self.pwd_context.hash(password)

    def __decode_jwt(self, token: str) -> dict:
        """
        The __decode_jwt function takes a token as an argument and returns the decoded payload.
        The decode function from the jwt library is used to decode the token, using our SECRET_KEY and ALGORITHM.

        :param self: Represent the instance of the class
        :param token: str: Pass the token to the function
        :return: A dictionary with the following keys:
        """
        return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

    def __encode_jwt(self, data: dict, iat: datetime, exp: datetime, scope: str) -> str:
        """
        The __encode_jwt function takes in a dictionary of data, an issued at time (iat),
        an expiration time (exp), and a scope. It then creates a copy of the data dictionary
        and adds the iat, exp, and scope to it. Finally it returns the encoded JWT.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the jwt
        :param iat: datetime: Set the issued at time for the token
        :param exp: datetime: Set the expiration time of the token
        :param scope: str: Specify the scope of the token
        :return: A string containing the encoded jwt
        """
        to_encode = data.copy()
        to_encode.update({"iat": iat, "exp": exp, "scope": scope})

        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary of key-value pairs to be stored in the JWT payload.
                expires_delta (Optional[float]): An optional expiration time for the token, in seconds. Defaults to 15 minutes if not provided.

        :param self: Access the class attributes and methods
        :param data: dict: Pass the data to be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A string that is the access token
        """
        expire = datetime.utcnow() + timedelta(seconds=expires_delta or 15 * 60)
        return self.__encode_jwt(data, datetime.utcnow(), expire, "access_token")

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_refresh_token function creates a refresh token for the user.

        :param self: Reference the current object
        :param data: dict: Pass the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the time to live for the refresh token
        :return: A jwt token
        """
        expire = datetime.utcnow() + (
            timedelta(seconds=expires_delta) if expires_delta else timedelta(days=7)
        )
        return self.__encode_jwt(data, datetime.utcnow(), expire, "refresh_token")

    # define a function to generate a new confirmed email token
    async def create_email_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_email_token function creates a JWT token that is used to verify the user's email address.
        The function takes in two parameters: data and expires_delta. The data parameter is a dictionary containing the
        user's id, username, and email address. The expires_delta parameter specifies how long the token will be valid for;
        if it isn't specified then it defaults to one day.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A jwt token
        """
        expire = datetime.utcnow() + (
            timedelta(seconds=expires_delta) if expires_delta else timedelta(days=1)
        )
        return self.__encode_jwt(data, datetime.utcnow(), expire, "email_token")

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes in a refresh_token as an argument and returns the email of the user who owns that token.
        If there is no scope for that token, it will raise an HTTPException with status code 401 (Unauthorized).
        If there was a JWTError, it will also raise an HTTPException with status code 401 (Unauthorized).

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to decode_refresh_token
        :return: The email of the user, if the token is valid
        """
        try:
            payload = self.__decode_jwt(refresh_token)

            if payload.get('scope') == 'refresh_token':
                email = payload.get('sub')
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        """
        The get_current_user function is a dependency that will be used in the
            UserRouter class. It takes an access token as input and returns the user
            associated with that token. If no user is found, it raises an exception.

        :param self: Access the class attributes and methods
        :param token: str: Get the token from the request header
        :param db: AsyncSession: Get the database session
        :return: The user object that matches the email in the jwt
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = self.__decode_jwt(token)

            if payload.get('scope') == 'access_token':
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.redis.get(f"user:{email}")
        if user is None:

            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception

            self.redis.set(f"user:{email}", pickle.dumps(user))
            self.redis.expire(f"user:{email}", 900)

        else:
            user = pickle.loads(user)

        return user

    async def get_email_from_token(self, token: str) -> str:
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
        It does this by decoding the JWT, checking if it has a scope of 'email_token', and then returning the subject (sub)
        of that JWT. If there is no sub or scope in the payload, or if there is no such token in our database, we raise an
        HTTPException.

        :param self: Represent the instance of the class
        :param token: str: Pass the token to the function
        :return: The email address of the user who requested a password reset
        """
        try:
            payload = self.__decode_jwt(token)

            if payload.get('scope') == 'email_token':
                email = payload.get('sub')
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
