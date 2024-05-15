from typing import List
from app.db.models import Quiz
from app.schemas.result_quizes import AnswerSchema


def calculate_quiz_score(quiz: Quiz, answers: List[AnswerSchema]) -> float:
    questions_dict = {question.id: question for question in quiz.questions}
    total_questions = len(questions_dict)
    correct_answers = 0

    for answer in answers:
        question = questions_dict.get(answer.question_id)
        if question:
            option = next((o for o in question.options if o.id == answer.option_id and o.is_correct), None)
            if option:
                correct_answers += 1

    return (correct_answers / total_questions) * 100
