from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel
from src.db.roles import RoleRead

from src.db.organization_config import OrganizationConfig


class OrganizationBase(SQLModel):
    name: str
    description: Optional[str]
    about: Optional[str]
    socials: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    links: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    scripts: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    logo_image: Optional[str]
    thumbnail_image: Optional[str]
    previews: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    explore: Optional[bool] = Field(default=False)
    label: Optional[str]
    slug: str
    email: str
    default_locale: Optional[str] = Field(default="en", max_length=5)
    supported_locales: Optional[List[Any]] = Field(default=["en"], sa_column=Column(JSON))


class Organization(OrganizationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_uuid: str = ""
    creation_date: str = ""
    update_date: str = ""

class OrganizationWithConfig(BaseModel):
    org: Organization
    config: OrganizationConfig


class OrganizationUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    about: Optional[str] = None
    socials: Optional[Dict[str, Any]] = None
    links: Optional[Dict[str, Any]] = None
    scripts: Optional[Dict[str, Any]] = None
    logo_image: Optional[str] = None
    thumbnail_image: Optional[str] = None
    previews: Optional[Dict[str, Any]] = None
    label: Optional[str] = None
    slug: Optional[str] = None
    email: Optional[str] = None
    explore: Optional[bool] = None
    default_locale: Optional[str] = None
    supported_locales: Optional[List[Any]] = None

class OrganizationCreate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: int
    org_uuid: str
    config: Optional[Union[OrganizationConfig, Dict[str, Any]]] = None
    creation_date: str
    update_date: str


class OrganizationUser(BaseModel):
    user: "UserRead"
    role: RoleRead


# Rebuild models to resolve forward references
from src.db.users import UserRead
OrganizationUser.model_rebuild()
