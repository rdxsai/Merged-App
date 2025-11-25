from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from ..core import config, get_logger
from ..models import QuestionUpdate
from ..services.database import DatabaseManager
from ..services.ai_service import AIGeneratorService

import markdown2

logger = get_logger(__name__)

router = APIRouter(prefix = "/questions", tags = ["questions"])
templates = Jinja2Templates(directory="templates")

logger.info("Initializing DatabaseManager")
db = DatabaseManager(config.db_path)

logger.info("Initializing AIGeneratorSerive")
ai_generator = AIGeneratorService()

@router.get("/{question_id}" , response_class=HTMLResponse)
async def get_question_page(request:Request , question_id :str):

    logger.info(f"Loading edit page for question_id : {question_id}")
    if question_id == "new":
        raise HTTPException(status_code=400 , detail= "Creating new questions is not implemented in this version. Please use the main list")
    
    try:
        question = db.load_question_details(question_id)
        if not question:
            logger.error(f"Question {question_id} not found in database")
            raise HTTPException(status_code=404 , detail = "Question not found")
        
        question['question_text_html'] = markdown2.markdown(
            question.get('question_text' , ''),
            extras = ["fenced-code-blocks"]
        )

        for answer in question.get('answers' , []):
            answer['text_html'] = markdown2.markdown(
                answer.get('text' , ''),
                extras = ["fenced-code-blocks"]
            )
        
        all_objectives = db.list_all_objectives()
        return templates.TemplateResponse(
            "edit_question.html" , 
            {
                "request" : request,
                "question" : question,
                "all_objectives" : all_objectives,
                "prev_question_id" : None,
                "next_question_id" : None,
                "current_position" : 1,
                "total_questions" : 1,
            },
        )
    except Exception as e:
        logger.error(f"Error loading question page {question_id} : {e}",  exc_info=True)
        raise HTTPException(status_code=500, detail = str(e))

@router.put("/{question_id}")
async def update_question_data(question_id : str, data : QuestionUpdate):

    try:
        success = db.update_question_and_answers(question_id, data)
        if not success:
            raise HTTPException(status_code=500, detail = "Failed to save changes to DB")
        return {"success" : True, "message" : "Question updated succesfully"}
    except Exception as e:
        logger.error(f"Error updating question {question_id} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail = str(e))



@router.delete("/{question_id}")
async def delete_question(question_id:str):
    try:
        success = db.delete_question(question_id)
        if not success:
            logger.error(f"Failed to delete question {question_id}. It may not exist in the DB")
            raise HTTPException(status_code=404 ,  detail = "Question not found or failed to delete")
        logger.info(f"Deleted question {question_id}")
        return {"success" : True , "message" : "Question deleted succesfully"}

    except Exception as e:
        logger.error(f"Error deleting question {question_id} : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/{question_id}/generate-feedback", response_class=JSONResponse)
async def generate_feedback_for_all_unapproved(question_id : str):
    logger.info(f"Generating feedbacl request started for question {question_id}")
    try:
        question = db.load_question_details(question_id)
        if not question:
            raise HTTPException(status_code=404 , detail = "Question not found")
        updated_answers = []

        for answer in question.get('answers' , []):
            if not answer.get('feedback_approved', False):
                logger.info(f"Generating feedback for unapproaved answer_id : {answer['id']}")

                feedback_text = await ai_generator.generate_feedback_for_answer(
                    question_text = question['question_text'],
                    answer= answer
                )

                db.update_answer_feedback(answer['id'] , feedback_text)
                updated_answers.append({
                    "answer_id" : answer['id'],
                    "feedback_text" : feedback_text
                })

        logger.info(f"Feedback geeration complete for question {question_id}")
        return {
            "success" : True,
            "message" : "Feedback generated for all unapproved answers",
            "updated_answers" : updated_answers
        }
    except Exception as e:
        logger.error(f"Error in generate_feedback_for_all_unapproved : {e}" ,exc_info=True)
        raise HTTPException(status_code=500, detail = f"Internal server error : {str(e)}")