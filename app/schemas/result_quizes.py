from pydantic import BaseModel
from typing import List



class AnswerSchema(BaseModel):
    question_id: int
    option_id: int


class QuizAttemptSchema(BaseModel):
    quiz_id: int
    answers: List[AnswerSchema]


class QuizResultSchema(BaseModel):
    user_id: int
    quiz_id: int
    company_id: int
    score: float
