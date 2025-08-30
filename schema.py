from pydantic import BaseModel, ValidationError, field_validator
from errors import HttpError


class BaseAdvRequest(BaseModel):
    name: str
    description: str
    owner: str


class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def secure_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("password is too short")
        return v


class AuthRequest(BaseModel):
    email: str
    password: str


class CreateAdvRequest(BaseAdvRequest):
    pass


class UpdateAdvRequest(BaseAdvRequest):
    name: str | None = None
    description: str | None = None
    owner: str | None = None


def validate(
    schema: type[CreateAdvRequest | UpdateAdvRequest], json_data: dict
) -> dict:
    try:
        schema_instance = schema(**json_data)
        return schema_instance.model_dump(exclude_unset=True)
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)
