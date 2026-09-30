from pydantic import BaseModel



from pydantic import BaseModel, Field, model_validator


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int
    gender: str
    role: str = "patient"
    specialization: str | None = None

    @model_validator(mode="after")
    def validate_specialization(self):
        if self.role == "doctor":
            if not self.specialization or not self.specialization.strip():
                raise ValueError(
                    "Specialization is required for doctors"
                )
            self.specialization = self.specialization.strip()
        return self





class LoginRequest(BaseModel):
    email: str
    password: str