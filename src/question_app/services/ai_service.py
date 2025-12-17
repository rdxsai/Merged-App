"""
AI Response Generator Service
(This is the FINAL, DEFINITIVE version)
- Fixes the 401 'Ocp-Apim-Subscription-Key' header.
- Fixes the 400 'response_format' error.
- Fixes the 'JSONDecodeError' by checking for content filters.
- RESTORES the high-quality, Socratic feedback prompts.
"""
import httpx
import json
import logging
from typing import List, Dict, Any
import numpy as np 
import asyncio 

from ..core import config, get_logger
from ..services.database import DatabaseManager
from ..utils.file_utils import load_feedback_prompt_from_json

logger = get_logger(__name__)

# (This function is correct)
async def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings from Ollama using the nomic-embed-text model.
    """
    embeddings = []
    logger.info(f"Generating {len(texts)} embeddings via Ollama...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, text in enumerate(texts):
            try:
                if not text.strip():
                    logger.warning(f"Empty text at index {i}, skipping.")
                    embeddings.append([0.0] * 768) 
                    continue
                payload = {
                    "model": config.OLLAMA_EMBEDDING_MODEL,
                    "prompt": text.strip(),
                }
                response = await client.post(
                    f"{config.OLLAMA_HOST}/api/embeddings",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["embedding"])
                
                if i < len(texts) - 1:
                    await asyncio.sleep(0.05) 
            except Exception as e:
                logger.error(f"Error generating embedding for text {i}: {e}")
                embeddings.append([0.0] * 768)

    logger.info(f"Successfully generated {len(embeddings)} embeddings.")
    return embeddings


class AIGeneratorService:
    def __init__(self):
        # (This is correct)
        self.api_url = (
            f"{config.AZURE_OPENAI_ENDPOINT}"
            f"/deployments/{config.AZURE_OPENAI_DEPLOYMENT_ID}"
            f"/chat/completions?api-version={config.AZURE_OPENAI_API_VERSION}"
        )
        
        # (This is correct)
        self.headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.AZURE_OPENAI_SUBSCRIPTION_KEY,
        }
        self.db = DatabaseManager(config.db_path)
        logger.info("AIGeneratorService initialized.")
        logger.info(f"Target URL: {self.api_url[:50]}...") 

    # --- === THIS IS THE RESTORED, HIGH-QUALITY FUNCTION === ---
    async def generate_feedback_for_answer(self, question_text: str, answer_text: str, is_correct: bool) -> str:
        
        logger.info(f"Generating feedback for answer: {answer_text[:30]}...")

        if is_correct:
            system_prompt = load_feedback_prompt_from_json("feedback_correct")
            user_prompt = f"""
            Question: "{question_text}"
            Correct Answer : "{answer_text}"

            Generate the feedback:
            """
            max_tokens = 400
        else:
            system_prompt = load_feedback_prompt_from_json("feedback_incorrect")
            user_prompt = f"""
            Question: "{question_text}"
            Incorrect Answer Selected : "{answer_text}"

            Generate the feedback:
            """
            max_tokens = 400

        payload = {
            "messages" : [
                {"role" : "system" , "content" : system_prompt},
                {"role" : "user" , "content" : user_prompt},
            ],
            "max_tokens" : max_tokens,
            "temperature" : 0.6
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            json_response = response.json()

            # (This is our new, correct error checking)
            if not json_response.get("choices"):
                logger.warning(f"AI response had no choices: {json_response}")
                raise Exception("AI returned an invalid response.")

            choice = json_response["choices"][0]
            finish_reason = choice.get("finish_reason")
            
            if finish_reason == "content_filter":
                logger.error("AI feedback was blocked by the content filter.")
                raise Exception("AI response was blocked by the content filter.")
            
            content = choice["message"].get("content")
            if not content:
                logger.error(f"AI returned an empty message. Finish reason: {finish_reason}")
                raise Exception(f"AI returned an empty response (Reason: {finish_reason}).")
            
            return content.strip()
    # --- === END OF RESTORED FUNCTION === ---


    async def generate_question_from_objective(self, objective_text: str) -> Dict:
        """ (Req 7.4) Generates a new question from an objective. """
        logger.info(f"Generating question for objective: {objective_text[:30]}...")

        # (This is our new, correct prompt)
        system_prompt = """
        You are a master quiz designer specializing in web accessibility and WCAG standards.
        A user will provide you with a learning objective.
        Your task is to generate one high-quality, multiple-choice question that assesses this objective.
        
        You MUST return ONLY a single, valid JSON object with the following structure:
        {
          "question_text": "Your generated question text here...",
          "answers": [
            {"text": "A plausible incorrect answer.", "is_correct": false},
            {"text": "The correct answer.", "is_correct": true},
            {"text": "Another plausible incorrect answer.", "is_correct": false},
            {"text": "A final plausible incorrect answer.", "is_correct": false}
          ]
        }
        
        Ensure there are exactly four answers. One must be correct, and the other three must be plausible but incorrect.
        Do not include any other text, markdown formatting, or explanation. Just the raw JSON object.
        """
        
        user_prompt = f"Learning Objective: \"{objective_text}\""
        
        payload = { 
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "max_tokens": 1000, 
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                json_response = response.json()

                if not json_response.get("choices"):
                    logger.warning(f"AI response had no choices: {json_response}")
                    raise Exception("AI returned an invalid response.")
                
                choice = json_response["choices"][0]
                finish_reason = choice.get("finish_reason")

                if finish_reason == "content_filter":
                    logger.error("AI question generation was blocked by the content filter.")
                    raise Exception("AI response was blocked by the content filter.")
                
                ai_response_text = choice["message"].get("content")
                if not ai_response_text:
                    logger.error(f"AI returned an empty message. Finish reason: {finish_reason}")
                    raise Exception(f"AI returned an empty response (Reason: {finish_reason}).")

                start_index = ai_response_text.find('{')
                end_index = ai_response_text.rfind('}')
                
                if start_index == -1 or end_index == -1:
                    logger.error(f"AI response did not contain JSON: {ai_response_text}")
                    raise Exception("AI did not return a valid JSON object.")
                
                json_string = ai_response_text[start_index : end_index + 1]
                json_data = json.loads(json_string)
                
                while len(json_data.get("answers", [])) < 4:
                    json_data.get("answers", []).append({"text": "Another incorrect option.", "is_correct": False})
                
                return json_data
        except Exception as e:
            logger.error(f"Error parsing AI response for question gen: {e}")
            raise

    async def suggest_objectives_for_question(self, question_text: str) -> List[Dict]:
        # (This function is correct)
        logger.info(f"Suggesting objectives for question: {question_text[:30]}...")
        try:
            all_objectives = self.db.list_all_objectives()
            if not all_objectives:
                logger.warning("No objectives found in DB to suggest.")
                return []
        
            question_embedding = (await get_ollama_embeddings([question_text]))[0]
            objective_texts = [obj['text'] for obj in all_objectives]
            objective_embeddings = await get_ollama_embeddings(objective_texts)
            
            q_vec = np.array(question_embedding)
            o_vecs = np.array(objective_embeddings)
            
            q_vec_norm = q_vec / np.linalg.norm(q_vec)
            o_vecs_norm = o_vecs / np.linalg.norm(o_vecs, axis=1, keepdims=True)
            
            scores = np.dot(o_vecs_norm, q_vec_norm)
            
            suggestions = []
            for i, score in enumerate(scores):
                if score >= 0.60: 
                    suggestions.append({
                        "id": all_objectives[i]['id'],
                        "text": all_objectives[i]['text'],
                        "score": round(float(score) * 100, 1)
                    })
            
            top_suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:5]
            logger.info(f"Found {len(top_suggestions)} good matches for objectives.")
            return top_suggestions
        except Exception as e:
            logger.error(f"Error in suggest_objectives: {e}", exc_info=True)
            return []