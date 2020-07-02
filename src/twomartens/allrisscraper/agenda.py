# -*- coding: utf-8 -*-

#   Copyright 2020 Jim Martens
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from dataclasses import dataclass
from typing import List


@dataclass
class Consultation:
    authoritative: bool
    role: str


@dataclass
class Motion:
    name: str
    reference: str
    type: str
    underDirectionOf: str
    context: str
    petition: str


@dataclass
class AgendaItem:
    number: str
    order: int
    name: str
    public: bool
    link: str
    motion_link: str
    motion_reference: str
    

@dataclass
class Agenda:
    agendaItems: List[AgendaItem]