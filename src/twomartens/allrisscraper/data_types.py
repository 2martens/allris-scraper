from dataclasses import dataclass
from typing import List


@dataclass
class Consultation:
    authoritative: bool
    agenda_item: str
    meeting: str
    organization: List[str]
    role: str
    result: str


@dataclass
class Motion:
    consultations: List[Consultation]
    context: str
    file: str
    name: str
    reference: str
    petition: str
    type: str
    under_direction_of: str


@dataclass
class AgendaItem:
    number: str
    order: int
    name: str
    public: bool
    link: str
    motion_link: str
    motion_reference: str
    resolution_text: str


@dataclass
class Agenda:
    agenda_items: List[AgendaItem]


@dataclass
class Membership:
    person: str
    organization: str
    role: str
    on_behalf_of: str


@dataclass
class Organization:
    classification: str
    membership: List[Membership]
    name: str
    organization_type: str


@dataclass
class Person:
    name: str
    form_of_address: str
    phone: List[str]
    email: List[str]
