import uuid

from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None


class CustomerCreate(CustomerBase):
    @classmethod
    def rand_init(cls) -> "CustomerCreate":
        uid = uuid.uuid4().hex[:8]
        return cls(
            full_name=f"User {uid}",
            email=f"user-{uid}@example.com",
            phone=f"+7-9{uid[:2]}-{uid[2:5]}-{uid[5:7]}-{uid[7:]}",
        )


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class CustomerRead(CustomerBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}
