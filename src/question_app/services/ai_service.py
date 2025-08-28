"""
AI Service module for the Question App.

This module contains AI-related services including feedback generation
using Azure OpenAI and other AI integrations.
"""

import json
import re
from typing import Any, Dict

import httpx
from fastapi import HTTPException

from ..core import config, get_logger
from ..utils import clean_answer_feedback

logger = get_logger(__name__)


async def generate_feedback_with_ai(
    question_data: Dict[str, Any], system_prompt: str
) -> Dict[str, Any]:
    """
    Generate educational feedback for quiz questions using Azure OpenAI.

    This function sends a question to Azure OpenAI with a system prompt to
    generate comprehensive educational feedback including general feedback
    and answer-specific feedback for each answer option. It handles API
    communication, response parsing, and error conditions gracefully.

    Args:
        question_data (Dict[str, Any]): Question data including text, type,
                                      points, and answer options. Must contain
                                      'question_text' and 'answers' keys.
        system_prompt (str): The system prompt to guide the AI's response.
                            Should provide context about the educational role.

    Returns:
        Dict[str, Any]: Generated feedback containing:
            - 'general_feedback': Overall feedback for the question
            - 'answer_feedback': Dictionary mapping answer keys to feedback
            - 'token_usage': Token usage statistics from the API call

    Raises:
        HTTPException: If Azure OpenAI configuration is missing, API calls fail,
                      or the response is invalid.

    Note:
        The function validates Azure OpenAI configuration, constructs a detailed
        prompt with question context, and parses the AI response to extract
        structured feedback. It includes comprehensive error handling and logging.

    Example:
        >>> question_data = {
        ...     "id": 1,
        ...     "question_text": "What is the capital of France?",
        ...     "answers": [
        ...         {"id": 1, "text": "London", "weight": 0.0},
        ...         {"id": 2, "text": "Paris", "weight": 100.0}
        ...     ]
        ... }
        >>> system_prompt = "You are an educational assistant helping with quiz feedback."
        >>> feedback = await generate_feedback_with_ai(question_data, system_prompt)
        >>> print(feedback["general_feedback"])
        >>> print(feedback["answer_feedback"])

    See Also:
        :func:`get_ollama_embeddings`: Generate embeddings for vector search
        :func:`search_vector_store`: Search for similar questions
    """
    logger.info(
        f"Starting AI feedback generation for question ID: {question_data.get('id', 'unknown')}"
    )

    if not config.validate_azure_openai_config():
        missing_configs = config.get_missing_azure_openai_configs()
        logger.error(
            f"Missing Azure OpenAI configuration: {', '.join(missing_configs)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI configuration incomplete. Missing: {', '.join(missing_configs)}",
        )

    # Construct the Azure OpenAI URL
    url = (
        f"{config.AZURE_OPENAI_ENDPOINT}/us-east/deployments/"
        f"{config.AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions"
        f"?api-version={config.AZURE_OPENAI_API_VERSION}"
    )
    logger.info(f"Azure OpenAI URL: {url}")

    headers = {
        "Ocp-Apim-Subscription-Key": config.AZURE_OPENAI_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }

    # Prepare question context for AI
    question_context = {
        "question_text": question_data.get("question_text", ""),
        "question_type": question_data.get("question_type", ""),
        "points_possible": question_data.get("points_possible", 0),
        "answers": [],
    }

    # Include answer information
    for answer in question_data.get("answers", []):
        question_context["answers"].append(
            {
                "text": answer.get("text", ""),
                "weight": answer.get("weight", 0),
                "is_correct": answer.get("weight", 0) > 0,
            }
        )

    # Create user message with question context
    user_message = f"""Please generate educational feedback for this web accessibility quiz question:

Question Type: {question_context['question_type']}
Question Text: {question_context['question_text']}
Points Possible: {question_context['points_possible']}

Answer Choices:
"""

    for i, answer in enumerate(question_context["answers"], 1):
        correct_indicator = "✓ CORRECT" if answer["is_correct"] else "✗ INCORRECT"
        user_message += f"{i}. {answer['text']} (Weight: {answer['weight']}%) [{correct_indicator}]\n"

    user_message += """
Format your response as:

Answer 1: [feedback for answer 1]
Answer 2: [feedback for answer 2]
Answer 3: [feedback for answer 3] (if applicable)
Answer 4: [feedback for answer 4] (if applicable)

Please provide specific educational feedback for each answer choice explaining why it is correct or incorrect.
"""

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 1500,
        "temperature": 0.7,
    }

    logger.info(
        f"Sending request to Azure OpenAI with payload keys: {list(payload.keys())}"
    )
    logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            logger.info(f"Azure OpenAI response status: {response.status_code}")

            if response.status_code != 200:
                response_text = response.text
                logger.error(f"Azure OpenAI API error response: {response_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI service error (status {response.status_code}): {response_text}",
                )

            result = response.json()
            logger.info(f"Azure OpenAI response received successfully")
            logger.debug(f"Full response: {json.dumps(result, indent=2)}")

            if "choices" not in result or not result["choices"]:
                logger.error("No choices in Azure OpenAI response")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from AI service - no choices",
                )

            ai_response = result["choices"][0]["message"]["content"]
            logger.info(f"AI response content length: {len(ai_response)} characters")
            logger.debug(f"AI response content: {ai_response}")

            # Extract token usage information
            token_usage = {}
            if "usage" in result:
                token_usage = {
                    "prompt_tokens": result["usage"].get("prompt_tokens", 0),
                    "completion_tokens": result["usage"].get("completion_tokens", 0),
                    "total_tokens": result["usage"].get("total_tokens", 0),
                }
                logger.info(
                    f"Token usage - Prompt: {token_usage['prompt_tokens']}, "
                    f"Completion: {token_usage['completion_tokens']}, "
                    f"Total: {token_usage['total_tokens']}"
                )

            # Parse the AI response to extract general feedback and answer-specific feedback
            feedback = {
                "general_feedback": "",
                "answer_feedback": {},
                "token_usage": token_usage,
            }

            lines = ai_response.split("\n")
            current_section = None
            general_feedback_lines = []
            current_answer_key = None
            current_answer_text = []

            logger.info(f"Parsing AI response with {len(lines)} lines")

            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                logger.debug(f"Processing line {line_num}: {line}")

                # Look for section headers
                if any(
                    phrase in line.lower()
                    for phrase in [
                        "general feedback:",
                        "importance and relevance",
                        "1. general feedback",
                    ]
                ):
                    current_section = "general"
                    logger.info(f"Found general feedback section at line {line_num}")
                    # Extract content after colon if present
                    if ":" in line:
                        content = line.split(":", 1)[1].strip()
                        if content:
                            general_feedback_lines.append(content)
                elif any(
                    phrase in line.lower()
                    for phrase in [
                        "answer feedback:",
                        "2. answer feedback",
                        "answer 1:",
                    ]
                ):
                    current_section = "answers"
                    logger.info(f"Found answer feedback section at line {line_num}")
                    # Check if this line contains answer feedback
                    if "answer" in line.lower() and ":" in line:
                        if current_answer_key and current_answer_text:
                            # Extract answer number from key and get corresponding answer text
                            answer_text = ""
                            try:
                                match = re.search(r"\d+", current_answer_key)
                                if match:
                                    answer_number = (
                                        int(match.group()) - 1
                                    )  # Convert to 0-based index
                                    if (
                                        0
                                        <= answer_number
                                        < len(question_context["answers"])
                                    ):
                                        answer_text = question_context["answers"][
                                            answer_number
                                        ]["text"]
                            except (ValueError, IndexError):
                                pass

                            feedback["answer_feedback"][
                                current_answer_key
                            ] = clean_answer_feedback(
                                "\n".join(current_answer_text), answer_text
                            )

                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = (
                                [parts[1].strip()] if parts[1].strip() else []
                            )
                            logger.debug(f"Found answer key: {current_answer_key}")
                elif current_section == "general":
                    # Continue adding to general feedback
                    general_feedback_lines.append(line)
                elif current_section == "answers":
                    # Check if this is a new answer
                    if "answer" in line.lower() and ":" in line:
                        # Save previous answer if exists
                        if current_answer_key and current_answer_text:
                            # Extract answer number from key and get corresponding answer text
                            answer_text = ""
                            try:
                                match = re.search(r"\d+", current_answer_key)
                                if match:
                                    answer_number = (
                                        int(match.group()) - 1
                                    )  # Convert to 0-based index
                                    if (
                                        0
                                        <= answer_number
                                        < len(question_context["answers"])
                                    ):
                                        answer_text = question_context["answers"][
                                            answer_number
                                        ]["text"]
                            except (ValueError, IndexError):
                                pass

                            feedback["answer_feedback"][
                                current_answer_key
                            ] = clean_answer_feedback(
                                "\n".join(current_answer_text), answer_text
                            )

                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = (
                                [parts[1].strip()] if parts[1].strip() else []
                            )
                            logger.debug(f"Found answer key: {current_answer_key}")
                    elif current_answer_key:
                        # Continue adding to current answer feedback
                        current_answer_text.append(line)
                elif not current_section:
                    # Check if this line looks like an answer before defaulting to general feedback
                    if (
                        "answer" in line.lower()
                        and ":" in line
                        and re.search(r"answer\s*\d+\s*:", line, re.IGNORECASE)
                    ):
                        # This looks like "Answer 1:", "Answer 2:", etc. - switch to answers section
                        current_section = "answers"
                        logger.info(
                            f"Auto-detected answer section at line {line_num}: {line}"
                        )

                        # Process this line as an answer
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = (
                                [parts[1].strip()] if parts[1].strip() else []
                            )
                            logger.debug(f"Found answer key: {current_answer_key}")
                    else:
                        # Before any section is found, assume it's general feedback
                        general_feedback_lines.append(line)

            # Save the last answer if exists
            if current_answer_key and current_answer_text:
                # Extract answer number from key and get corresponding answer text
                answer_text = ""
                try:
                    # Extract number from keys like "answer 1", "answer1", "1", etc.
                    match = re.search(r"\d+", current_answer_key)
                    if match:
                        answer_number = (
                            int(match.group()) - 1
                        )  # Convert to 0-based index
                        if 0 <= answer_number < len(question_context["answers"]):
                            answer_text = question_context["answers"][answer_number][
                                "text"
                            ]
                except (ValueError, IndexError):
                    pass

                feedback["answer_feedback"][current_answer_key] = clean_answer_feedback(
                    "\n".join(current_answer_text), answer_text
                )

            # Combine general feedback lines
            feedback["general_feedback"] = "\n".join(general_feedback_lines)

            # If no structured parsing worked, put everything in general feedback
            if not feedback["general_feedback"] and not feedback["answer_feedback"]:
                logger.warning(
                    "Failed to parse AI response into sections, using full response as general feedback"
                )
                feedback["general_feedback"] = ai_response

            logger.info(
                f"Parsed feedback - General: {len(feedback['general_feedback'])} chars, "
                f"Answer feedback entries: {len(feedback['answer_feedback'])}"
            )

            return feedback

    except httpx.HTTPStatusError as e:
        logger.error(f"Azure OpenAI HTTP error: {e}")
        logger.error(
            f"Response text: {e.response.text if hasattr(e, 'response') else 'No response text'}"
        )
        raise HTTPException(
            status_code=e.response.status_code, detail=f"AI service HTTP error: {e}"
        )
    except httpx.TimeoutException as e:
        logger.error(f"Azure OpenAI timeout error: {e}")
        raise HTTPException(status_code=408, detail="AI service request timed out")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Azure OpenAI response as JSON: {e}")
        raise HTTPException(
            status_code=500, detail="Invalid JSON response from AI service"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating feedback: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate feedback: {str(e)}"
        )
