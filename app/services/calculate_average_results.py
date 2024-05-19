from typing import Sequence
from app.db.models import QuizResult


async def calculate_average_score_db(quiz_results):
    total_questions_answered = 0
    total_correct_answers = 0

    for result in quiz_results:
        total_questions_answered += result.total_questions_answered
        total_correct_answers += result.total_correct_answers

    if not total_questions_answered:
        return None

    average_score = round((total_correct_answers / total_questions_answered) * 100, 2)
    return average_score



async def calculate_average_score_redis(quiz_results):
    total_questions_answered = quiz_results["total_questions_answered"]
    total_correct_answers = quiz_results["total_correct_answers"]

    if not total_questions_answered:
        return None

    average_score = round((total_correct_answers / total_questions_answered) * 100, 2)
    return average_score