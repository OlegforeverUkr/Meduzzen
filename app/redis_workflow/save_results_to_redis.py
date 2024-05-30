import json
from typing import Sequence
from fastapi import HTTPException

from app.db.models import QuizResult
from app.redis_workflow.redis_workers import save_data_to_redis_db


async def save_results_to_redis(quiz_results: Sequence[QuizResult]):
    try:
        for result in quiz_results:
            quiz_result_data = {
                "user_id": result.user_id,
                "quiz_id": result.quiz_id,
                "company_id": result.company_id,
                "score": result.score,
                "total_correct_answers": result.total_correct_answers,
                "total_questions_answered": result.total_questions_answered,
            }
            await save_data_to_redis_db(f"{result.user_id}:{result.quiz_id}:{result.company_id}",
                                        json.dumps(quiz_result_data))
    except:
        raise HTTPException(status_code=409, detail="Can`t save data to redis.")