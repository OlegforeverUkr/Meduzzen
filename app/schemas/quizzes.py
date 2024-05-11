from typing import List, Optional
from pydantic import BaseModel


class OptionBaseSchema(BaseModel):
    text: str
    is_correct: bool


class OptionCreateSchema(OptionBaseSchema):
    pass


class OptionSchema(OptionBaseSchema):
    id: int
    question_id: int

    class Config:
        from_attributes = True


class OptionUpdateSchema(BaseModel):
    id: int = None
    text: str
    is_correct: bool


class QuestionBaseSchema(BaseModel):
    text: str
    options: List[OptionBaseSchema]


class QuestionCreateSchema(QuestionBaseSchema):
    pass


class QuestionUpdateSchema(BaseModel):
    id: int = None
    text: str
    options: List[OptionUpdateSchema] = None


class QuestionSchema(QuestionBaseSchema):
    id: int
    quiz_id: int

    class Config:
        from_attributes = True


class QuizBaseSchema(BaseModel):
    title: str
    description: Optional[str]
    frequency_days: int
    questions: List[QuestionBaseSchema]


class QuizCreateSchema(QuizBaseSchema):
    pass


class QuizUpdateSchema(BaseModel):
    title: str
    description: Optional[str]
    frequency_days: int


class QuizReadSchema(QuizBaseSchema):
    id: int
    company_id: int

    class Config:
        from_attributes = True