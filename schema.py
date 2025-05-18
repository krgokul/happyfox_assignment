from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel


class ActionTypeEnum(str, Enum):
    MARK_AS_READ = "mark_as_read"
    MARK_AS_UNREAD = "mark_as_unread"
    MOVE_MESSAGE = "move_message"


class MatchTypeEnum(str, Enum):
    ALL = "all"
    ANY = "any"


class ConditionBase(BaseModel):
    field: str


class PredicateEnum(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    DOES_NOT_CONTAINS = "does_not_contains"


class StringCondition(ConditionBase):
    predicate: PredicateEnum
    value: str


class DatePredicateEnum(str, Enum):
    GREATER_THAN = "greater_than"
    LESSER_THAN = "lesser_than"


class DateUnitEnum(str, Enum):
    DAYS = "days"
    MONTHS = "months"


class DateCondition(ConditionBase):
    predicate: DatePredicateEnum
    value: int
    unit: DateUnitEnum


class Action(BaseModel):
    type: ActionTypeEnum
    target: Optional[str] = None


class RuleConfig(BaseModel):
    name: str
    conditions: List[Union[StringCondition, DateCondition]]
    match: MatchTypeEnum
    actions: List[Action]


class Rule(BaseModel):
    rules: List[RuleConfig]
