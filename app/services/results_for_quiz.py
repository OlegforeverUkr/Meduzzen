from typing import List
from app.db.models import Quiz
from app.schemas.result_quizes import AnswerSchema


def calculate_quiz_score(quiz: Quiz, answers: List[AnswerSchema]) -> float:
    total_questions = len(quiz.questions)
    correct_answers = 0

    for answer in answers:
        question = next((q for q in quiz.questions if q.id == answer.question_id), None)
        if question:
            option = next((o for o in question.options if o.id == answer.option_id), None)
            if option and option.is_correct:
                correct_answers += 1

    return (correct_answers / total_questions) * 100
