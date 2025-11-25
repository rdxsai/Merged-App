import httpx
import json
import logging
from typing import Dict, Any

from fastapi import HTTPException
from ..core import config


logger = logging.getLogger(__name__)

class AIGeneratorService:
    """
    Handles all AI-powered content generation.
    This new class-based approach is cleaner and allows for
    different types of AI generation as the app grows.
    """

    def __init__(self):
        """
        Initializes the service, loading all necessary config.
        This runs ONCE when your FastAPI app starts up.
        """

        if not config.validate_azure_openai_config():
            missing = config.get_missing_azure_openai_configs()
            logger.error(f"Missing Azure OpenAI config: {', '.join(missing)}")

        self.api_url = (
            f"{config.AZURE_OPENAI_ENDPOINT}/deployments/"
            f"{config.AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions"
            f"?api-version={config.AZURE_OPENAI_API_VERSION}"
        )

        self.headers = {
            "Ocp-Apim-Subscription-Key": str(config.AZURE_OPENAI_SUBSCRIPTION_KEY or ""),
            "Content-Type": "application/json"
        }

        logger.info(f"AIGeneratorService initialized. Target URL : {self.api_url}")
        if "gpt-4" in self.api_url:
            logger.warning("Target URL contains 'gpt-4'. If gotten 404, check model name in config.")
    

    async def generate_feedback_for_answer(self, question_text:str, answer:Dict[str, Any]) -> str:
        logger.info(f"Generating feedback for answer_id: {answer.get('id')}")

        is_correct = answer.get('is_correct' , False)
        answer_Text = answer.get('text' , '')

        if is_correct:
            system_prompt = """
            You are an expert instructional designer. A student has selected the
            CORRECT answer to a multiple-choice question.
            
            Your task is to:
            1.  Affirm that their answer is correct.
            2.  Provide a detailed explanation (at least 4-5 sentences) of *why* this answer is correct.
            3.  You should tie the concept back to the core learning objective.
            
            Respond *only* with the feedback text. Do not add any extra titles or "Feedback:" prefix.
            """

            user_prompt = f"""
            Question: "{question_text}"
            Correct Answer : "{answer_Text}"

            Generate the feedback:
            """
        else:
            system_prompt = """
            You are an expert instructional designer. A student has selected the
            INCORRECT answer to a multiple-choice question.
            
            Your task is to:
            1.  Affirm that their answer is incorrect.
            2.  Generate one (1) probing socratic questions (2-3 sentences) that gently guides them to reconsider their choice.
            3.  Your question should make them think about the *concept* that makes their answers incorrect.
            
            Respond *only* with the feedback text. Do not add any extra titles or "Feedback:" prefix.
            """

            user_prompt = f"""
            Question: "{question_text}"
            Incorrect Answer Selected : "{answer_Text}"

            Generate the feedback:
            """
        payload = {
            "messages" : [
                {"role" : "system" , "content" : system_prompt},
                {"role" : "user" , "content" : user_prompt},
            ],
            "max_tokens" : 400,
            "temperature" : 0.6
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers = self.headers , json = payload)

                if response.status_code != 200:
                    response_text = response.text
                    logger.error(f"Azure OpenAI API error (Status {response.status_code}): {response_text}")
                    raise HTTPException(
                       status_code=response.status_code,
                       detail = f"AI service error : {response_text}" 
                    )
                result = response.json()

                if not result.get("choices") or not result["choices"][0].get("message"):
                    logger.error("Invalid response from AI servie - no choices.")
                    return "ERROR: Invalid response from AI service"

                feedback_text = result["choices"][0]["message"]["content"]
                return feedback_text.strip()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Azure OpenAI HTTP error : {e}")
            raise HTTPException(
                status_code=e.response.status_code , detail = f"AI service HTTP error : {e}"
            )
        except httpx.TimeoutException as e:
            logger.error(f"Azure OpenAI timeout error : {e}")
            raise HTTPException(status_code=408, detail = "AI service request timed out")
        except Exception as e:
            logger.error(f"Unexpected error in feedback generation : {e}")
            raise HTTPException(
                status_code=500, detail = f"Internal Server Error : {str(e)}"
            )


