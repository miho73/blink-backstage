from pydantic import field_validator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RegisterPasskeyRequest(BaseModel):
  attestation: dict
  recaptcha: str

  model_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
  )

  @field_validator("recaptcha", mode="before")
  @classmethod
  def validate_recaptcha(cls, value):
    if value is None:
      raise ValueError("reCAPTCHA token was not passed")
    return value


class SignInPasskeyRequest(BaseModel):
  attestation: dict[str, object]
  recaptcha: str

  @field_validator("recaptcha", mode="before")
  @classmethod
  def validate_recaptcha(cls, value):
    if value is None:
      raise ValueError("reCAPTCHA token was not passed")
    return value
