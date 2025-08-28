"""
Question API module for the Question App.

This module contains all question-related CRUD operations and endpoints.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..core import config, get_logger
from ..models import QuestionUpdate
from ..utils import (
    load_questions,
    save_questions,
    load_objectives,
    load_system_prompt,
    get_all_existing_tags,
    extract_topic_from_text,
)
from ..services.ai_service import generate_feedback_with_ai

logger = get_logger(__name__)

# Create router for question endpoints
router = APIRouter(prefix="/questions", tags=["questions"])

# Templates setup
templates = Jinja2Templates(directory="templates")


@router.delete("/{question_id}")
async def delete_question(question_id: int):
    """Delete a question from the dataset"""
    try:
        questions = load_questions()
        questions = [q for q in questions if q.get("id") != question_id]

        if save_questions(questions):
            logger.info(f"Deleted question {question_id}")
            return {
                "success": True, 
                "message": "Question deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save changes"
            )
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/new", response_class=HTMLResponse)
async def new_question_page(request: Request):
    """Show new question creation page"""
    questions = load_questions()

    # Create a template new question
    new_question = {
        "id": "new",
        "question_text": "Enter your question text here...",
        "question_type": "multiple_choice_question",
        "points_possible": 1.0,
        "quiz_id": config.QUIZ_ID,
        "topic": "general",
        "tags": "",
        "learning_objective": "",
        "neutral_comments": "",
        "answers": [
            {"id": 1, "text": "Answer option 1", "weight": 100, "html": ""},
            {"id": 2, "text": "Answer option 2", "weight": 0, "html": ""},
            {"id": 3, "text": "Answer option 3", "weight": 0, "html": ""},
            {"id": 4, "text": "Answer option 4", "weight": 0, "html": ""},
        ],
    }

    # Available topic options
    available_topics = [
        ("accessibility", "Accessibility"),
        ("navigation", "Navigation"),
        ("forms", "Forms"),
        ("media", "Media"),
        ("color", "Color & Contrast"),
        ("keyboard", "Keyboard"),
        ("content", "Content & Structure"),
        ("general", "General"),
    ]

    # Get all existing tags for suggestions
    existing_tags = get_all_existing_tags(questions)

    # Get learning objectives for dropdown
    learning_objectives = load_objectives()

    return templates.TemplateResponse(
        "edit_question.html",
        {
            "request": request,
            "question": new_question,
            "available_topics": available_topics,
            "existing_tags": existing_tags,
            "learning_objectives": learning_objectives,
            "prev_question_id": None,
            "next_question_id": None,
            "current_position": 0,
            "total_questions": len(questions),
            "is_new_question": True,
        },
    )


@router.post("/new")
async def create_new_question(question_data: QuestionUpdate):
    """Create a new question"""
    try:
        questions = load_questions()

        # Generate new ID (find the highest existing ID and add 1)
        max_id = max([q.get("id", 0) for q in questions] + [0])
        new_id = max_id + 1

        # Create new question object
        new_question = {
            "id": new_id,
            "question_text": question_data.question_text,
            "question_type": "multiple_choice_question",  # Default type
            "points_possible": 1.0,  # Default points
            "quiz_id": config.QUIZ_ID,
            "topic": question_data.topic,
            "tags": question_data.tags,
            "learning_objective": question_data.learning_objective,
            "correct_comments": question_data.correct_comments,
            "incorrect_comments": question_data.incorrect_comments,
            "neutral_comments": question_data.neutral_comments,
            "correct_comments_html": question_data.correct_comments_html,
            "incorrect_comments_html": question_data.incorrect_comments_html,
            "neutral_comments_html": question_data.neutral_comments_html,
            "answers": [answer.model_dump() for answer in question_data.answers],
        }

        # Add to questions list
        questions.append(new_question)

        if save_questions(questions):
            logger.info(f"Created new question with ID {new_id}")
            return {
                "success": True,
                "message": "Question created successfully",
                "question_id": new_id,
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save new question"
            )
    except Exception as e:
        logger.error(f"Error creating new question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{question_id}", response_class=HTMLResponse)
async def edit_question(request: Request, question_id: int):
    """Show question edit page"""
    questions = load_questions()
    question = next((q for q in questions if q.get("id") == question_id), None)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Find previous and next question IDs for navigation
    question_ids = [q.get("id") for q in questions]
    current_index = question_ids.index(question_id)

    prev_question_id = question_ids[current_index - 1] if current_index > 0 else None
    next_question_id = (
        question_ids[current_index + 1]
        if current_index < len(question_ids) - 1
        else None
    )

    # Ensure question has a topic field (backward compatibility)
    if "topic" not in question:
        question["topic"] = extract_topic_from_text(
            question.get("question_text", ""), question.get("neutral_comments", "")
        )

    # Ensure question has a tags field (backward compatibility)
    if "tags" not in question:
        question["tags"] = ""

    # Ensure question has a learning_objective field (backward compatibility)
    if "learning_objective" not in question:
        question["learning_objective"] = ""

    # Available topic options
    available_topics = [
        ("accessibility", "Accessibility"),
        ("navigation", "Navigation"),
        ("forms", "Forms"),
        ("media", "Media"),
        ("color", "Color & Contrast"),
        ("keyboard", "Keyboard"),
        ("content", "Content & Structure"),
        ("general", "General"),
    ]

    # Get all existing tags for suggestions
    existing_tags = get_all_existing_tags(questions)

    # Get learning objectives for dropdown
    learning_objectives = load_objectives()

    return templates.TemplateResponse(
        "edit_question.html",
        {
            "request": request,
            "question": question,
            "available_topics": available_topics,
            "existing_tags": existing_tags,
            "learning_objectives": learning_objectives,
            "prev_question_id": prev_question_id,
            "next_question_id": next_question_id,
            "current_position": current_index + 1,
            "total_questions": len(questions),
        },
    )


@router.put("/{question_id}")
async def update_question(question_id: int, question_data: QuestionUpdate):
    """Update a question"""
    try:
        questions = load_questions()
        question_index = next(
            (i for i, q in enumerate(questions) if q.get("id") == question_id), None
        )

        if question_index is None:
            raise HTTPException(status_code=404, detail="Question not found")

        # Update the question
        questions[question_index].update(
            {
                "question_text": question_data.question_text,
                "topic": question_data.topic,
                "tags": question_data.tags,
                "learning_objective": question_data.learning_objective,
                "correct_comments": question_data.correct_comments,
                "incorrect_comments": question_data.incorrect_comments,
                "neutral_comments": question_data.neutral_comments,
                "correct_comments_html": question_data.correct_comments_html,
                "incorrect_comments_html": question_data.incorrect_comments_html,
                "neutral_comments_html": question_data.neutral_comments_html,
                "answers": [answer.model_dump() for answer in question_data.answers],
            }
        )

        if save_questions(questions):
            logger.info(f"Updated question {question_id}")
            return {"success": True, "message": "Question updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save changes")
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without wrapping them
        raise
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{question_id}/generate-feedback")
async def generate_question_feedback(question_id: int):
    """Generate AI feedback for a question"""
    logger.info(f"=== Generate Feedback Request Started for Question {question_id} ===")

    try:
        # Load system prompt
        logger.info("Loading system prompt...")
        system_prompt = load_system_prompt()
        if not system_prompt:
            logger.error("No system prompt found")
            raise HTTPException(
                status_code=400,
                detail="No system prompt configured. Please set a system prompt first.",
            )

        logger.info(
            f"System prompt loaded successfully (length: {len(system_prompt)} characters)"
        )

        # Find the question
        logger.info(f"Loading questions to find question {question_id}...")
        questions = load_questions()
        logger.info(f"Loaded {len(questions)} questions from file")

        question = next((q for q in questions if q.get("id") == question_id), None)

        if not question:
            logger.error(f"Question {question_id} not found in dataset")
            raise HTTPException(status_code=404, detail="Question not found")

        logger.info(
            f"Found question: type={question.get('question_type')}, text_length={len(question.get('question_text', ''))}"
        )
        logger.info(f"Question has {len(question.get('answers', []))} answers")

        # Generate feedback using AI
        logger.info("Starting AI feedback generation...")
        feedback = await generate_feedback_with_ai(question, system_prompt)
        logger.info("AI feedback generation completed successfully")

        # Update the question with generated feedback
        logger.info("Updating question with generated feedback...")
        question_index = next(
            (i for i, q in enumerate(questions) if q.get("id") == question_id), None
        )
        if question_index is not None:
            logger.info(f"Found question at index {question_index}")

            # Update the general feedback
            questions[question_index]["neutral_comments"] = feedback["general_feedback"]

            # Update answer-specific feedback
            for i, answer in enumerate(questions[question_index].get("answers", [])):
                # Try different keys to match the answer
                answer_keys_to_try = [
                    f"answer {i+1}",
                    f"answer{i+1}",
                    f"{i+1}",
                    str(i + 1),
                ]

                for key in answer_keys_to_try:
                    if key in feedback["answer_feedback"]:
                        answer["comments"] = feedback["answer_feedback"][key]
                        logger.info(f"Updated answer {i+1} feedback")
                        break

            logger.info("Saving updated questions to file...")
            if save_questions(questions):
                logger.info(
                    f"Successfully generated and saved AI feedback for question {question_id}"
                )
                return {
                    "success": True,
                    "message": "Feedback generated successfully",
                    "feedback": feedback,
                }
            else:
                logger.error("Failed to save questions to file")
                raise HTTPException(
                    status_code=500, detail="Failed to save generated feedback"
                )
        else:
            logger.error(f"Could not find question {question_id} for update")
            raise HTTPException(status_code=404, detail="Question not found for update")

    except HTTPException as e:
        # Re-raise HTTP exceptions (they're already properly formatted)
        logger.error(f"HTTP Exception in generate_question_feedback: {e.detail}")
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error generating feedback for question {question_id}: {e}"
        )
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
