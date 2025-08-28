"""
Chat API module for the Question App.

This module contains all RAG-based chat functionality including:
- Chat interface endpoints
- Vector store operations
- Embedding generation
- Semantic search
- Chat system prompt management
- Welcome message management
"""

import asyncio
import logging
import os
from typing import Any, Dict, List

import chromadb
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..utils import (
    load_chat_system_prompt,
    save_chat_system_prompt,
    load_welcome_message,
    save_welcome_message,
    get_default_chat_system_prompt,
    get_default_welcome_message,
    clean_html_for_vector_store,
    load_questions,
    extract_topic_from_text,
)

logger = logging.getLogger(__name__)

# Create router for chat endpoints
router = APIRouter(prefix="/chat", tags=["chat"])

# Templates setup
templates = Jinja2Templates(directory="templates")

# Configuration from environment
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", "https://itls-openai-connect.azure-api.net"
)
AZURE_OPENAI_DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_OPENAI_SUBSCRIPTION_KEY = os.getenv("AZURE_OPENAI_SUBSCRIPTION_KEY")

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


async def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings from Ollama using the nomic-embed-text model.

    This function generates vector embeddings for a list of text inputs using
    the local Ollama service with the nomic-embed-text model. It handles
    connection management, error handling, and request throttling
    automatically.

    Args:
        texts (List[str]): List of text strings to generate embeddings for.
                          Empty strings are allowed but will result in zero vectors.

    Returns:
        List[List[float]]: List of embedding vectors, where each vector is a
        list of floats representing the text in high-dimensional space.
        Returns empty list if all requests fail.

    Raises:
        HTTPException: If there are connection issues, timeouts, or API errors
                      with the Ollama service.

    Note:
        The function includes a small delay between requests to avoid overwhelming
        the Ollama service. It also handles various error conditions including
        connection failures, timeouts, and invalid responses.

    Example:
        >>> texts = [
        ...     "What is the capital of France?",
        ...     "Explain the concept of accessibility in web design"
        ... ]
        >>> embeddings = await get_ollama_embeddings(texts)
        >>> print(f"Generated {len(embeddings)} embeddings")
        >>> print(f"Each embedding has {len(embeddings[0])} dimensions")
        Generated 2 embeddings
        Each embedding has 768 dimensions

    See Also:
        :func:`search_vector_store`: Use embeddings for semantic search
        :func:`create_comprehensive_chunks`: Prepare text for embedding
    """
    embeddings = []

    # Ensure OLLAMA_HOST has proper protocol
    ollama_host = OLLAMA_HOST
    if not ollama_host.startswith(("http://", "https://")):
        ollama_host = f"http://{ollama_host}"

    logger.info(f"Using Ollama host: {ollama_host}")
    logger.info(f"Using embedding model: {OLLAMA_EMBEDDING_MODEL}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            for i, text in enumerate(texts):
                payload = {"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}

                logger.info(
                    f"Generating embedding {i+1}/{len(texts)} (text length: {len(text)} chars)"
                )

                url = f"{ollama_host}/api/embeddings"
                logger.debug(f"Making request to: {url}")

                response = await client.post(
                    url, json=payload, headers={"Content-Type": "application/json"}
                )

                if response.status_code != 200:
                    error_text = response.text
                    logger.error(
                        f"Ollama API error (status {response.status_code}): {error_text}"
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Ollama API error: {error_text}",
                    )

                result = response.json()

                if "embedding" not in result:
                    logger.error(f"No embedding in Ollama response: {result}")
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid response from Ollama - no embedding found",
                    )

                embeddings.append(result["embedding"])

                # Add small delay to avoid overwhelming Ollama
                await asyncio.sleep(0.1)

        logger.info(
            f"Generated {len(embeddings)} embeddings using Ollama {OLLAMA_EMBEDDING_MODEL} model"
        )
        return embeddings

    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to Ollama at {ollama_host}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama at {ollama_host}. Please ensure Ollama is running and the {OLLAMA_EMBEDDING_MODEL} model is installed.",
        )
    except httpx.TimeoutException as e:
        logger.error(f"Ollama request timeout: {e}")
        raise HTTPException(status_code=408, detail="Ollama request timed out")
    except Exception as e:
        logger.error(f"Error generating embeddings with Ollama: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate embeddings: {str(e)}"
        )


def create_comprehensive_chunks(
    questions: List[Dict[str, Any]]
) -> tuple[List[str], List[Dict[str, Any]], List[str]]:
    """
    Create comprehensive chunks from quiz questions for vector store processing.

    This function transforms quiz questions into comprehensive text chunks that
    include question text, answer options, feedback, and metadata. The chunks
    are designed to provide rich context for semantic search and RAG operations.

    Args:
        questions (List[Dict[str, Any]]): List of question dictionaries to process.

    Returns:
        tuple[List[str], List[Dict[str, Any]], List[str]]: A tuple containing:
            - List of document texts (the chunks)
            - List of metadata dictionaries for each chunk
            - List of unique IDs for each chunk

    Note:
        The function creates comprehensive chunks that include:
        - Question text and type
        - All answer options with correctness indicators
        - General feedback and answer-specific feedback
        - Rich metadata for filtering and analysis
    """
    documents = []
    metadatas = []
    ids = []

    for question in questions:
        # Extract and clean question text
        question_text = clean_html_for_vector_store(question.get("question_text", ""))
        question_type = question.get("question_type", "")
        general_feedback = clean_html_for_vector_store(
            question.get("neutral_comments", "")
        )

        # Build comprehensive document text
        doc_parts = []

        # Add question
        if question_text:
            doc_parts.append(f"Question: {question_text}")

        # Add question type context
        if question_type:
            doc_parts.append(
                f"Question Type: {question_type.replace('_', ' ').title()}"
            )

        # Process answers
        correct_answers = []
        all_answers = []
        answer_feedback_parts = []

        for answer in question.get("answers", []):
            answer_text = clean_html_for_vector_store(answer.get("text", ""))
            weight = answer.get("weight", 0)
            is_correct = weight > 0
            answer_feedback = clean_html_for_vector_store(answer.get("comments", ""))

            if answer_text:
                status = "CORRECT" if is_correct else "INCORRECT"
                all_answers.append(f"- {answer_text} ({status})")

                if is_correct:
                    correct_answers.append(answer_text)

                # Add specific answer feedback if available
                if answer_feedback:
                    answer_feedback_parts.append(
                        f"Feedback for '{answer_text}': {answer_feedback}"
                    )

        # Combine all answers
        if all_answers:
            doc_parts.append("Answer Options:\n" + "\n".join(all_answers))

        # Add general feedback
        if general_feedback:
            doc_parts.append(f"General Explanation: {general_feedback}")

        # Add answer-specific feedback
        if answer_feedback_parts:
            doc_parts.append("Answer Feedback:\n" + "\n".join(answer_feedback_parts))

        # Create final document
        document_text = "\n\n".join(doc_parts)

        # Create metadata (ChromaDB only accepts str, int, float, bool, or None)
        metadata = {
            "question_id": question.get("id"),
            "question_type": question_type,
            "points_possible": float(question.get("points_possible", 0)),
            "correct_answers": " | ".join(correct_answers)
            if correct_answers
            else "",  # Convert list to string
            "answer_count": len(question.get("answers", [])),
            "has_feedback": bool(general_feedback),
                            "topic": question.get(
                    "topic", extract_topic_from_text(question_text)
                ),
            "tags": question.get("tags", ""),
            "learning_objective": question.get("learning_objective", ""),
        }

        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(f"question_{question.get('id')}")

    return documents, metadatas, ids


async def search_vector_store(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the ChromaDB vector store for relevant chunks using semantic similarity.

    This function generates an embedding for the query text and searches the
    vector store for the most similar question chunks, returning them with
    their metadata and similarity scores.

    Args:
        query (str): The search query text.
        n_results (int, optional): Number of results to return. Defaults to 5.

    Returns:
        List[Dict[str, Any]]: List of chunk dictionaries, each containing:
            - 'content': The chunk text content
            - 'metadata': Associated metadata (question_id, topic, etc.)
            - 'distance': Similarity distance score (lower is more similar)

    Note:
        The function uses Ollama embeddings for the query and searches the
        ChromaDB collection named "quiz_questions". It handles errors gracefully
        and returns an empty list if the search fails.
    """
    try:
        client = chromadb.PersistentClient(path="./vector_store")
        collection = client.get_collection("quiz_questions")

        # Generate embedding for the query using Ollama
        query_embeddings = await get_ollama_embeddings([query])

        if not query_embeddings:
            logger.error("Failed to generate query embedding")
            return []

        # Search the vector store
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        chunks = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                chunk = {
                    "content": doc,
                    "metadata": results["metadatas"][0][i]
                    if results["metadatas"] and results["metadatas"][0]
                    else {},
                    "distance": results["distances"][0][i]
                    if results["distances"] and results["distances"][0]
                    else 0.0,
                }
                chunks.append(chunk)

        logger.info(f"Found {len(chunks)} relevant chunks for query: {query[:50]}...")
        return chunks

    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        return []


# Chat endpoints
@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat assistant page"""
    return templates.TemplateResponse("chat.html", {"request": request})


@router.post("/message")
async def chat_message(request: Request):
    """Process chat message with RAG using vector store"""
    try:
        # Parse request body
        body = await request.json()
        user_message = body.get("message", "").strip()
        max_chunks = body.get("max_chunks", 3)

        # Validate max_chunks
        if not isinstance(max_chunks, int) or max_chunks < 1 or max_chunks > 10:
            max_chunks = 3

        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"=== Chat Message Processing Started ===")
        logger.info(f"User message: {user_message}")
        logger.info(f"Max chunks requested: {max_chunks}")

        # Search vector store for relevant chunks
        logger.info("Searching vector store for relevant context...")
        retrieved_chunks = await search_vector_store(user_message, n_results=max_chunks)
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks")

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(f"Context {i+1}:\n{chunk['content']}")

        context = (
            "\n\n".join(context_parts)
            if context_parts
            else "No relevant context found."
        )

        # Load custom chat system prompt and inject context
        chat_system_prompt_template = load_chat_system_prompt()
        system_prompt = chat_system_prompt_template.format(context=context)

        # Prepare messages for Azure OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Call Azure OpenAI for chat completion
        logger.info("Calling Azure OpenAI for chat completion...")

        url = f"{AZURE_OPENAI_ENDPOINT}/us-east/deployments/{AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_OPENAI_SUBSCRIPTION_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Azure OpenAI API error: {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI service error: {error_text}",
                )

            result = response.json()

            if "choices" not in result or not result["choices"]:
                raise HTTPException(
                    status_code=500, detail="Invalid response from AI service"
                )

            ai_response = result["choices"][0]["message"]["content"]

            # Log token usage if available
            if "usage" in result:
                usage = result["usage"]
                logger.info(
                    f"Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                    f"Completion: {usage.get('completion_tokens', 0)}, "
                    f"Total: {usage.get('total_tokens', 0)}"
                )

        logger.info("Chat message processed successfully")

        return {
            "response": ai_response,
            "retrieved_chunks": retrieved_chunks,
            "context_used": len(context_parts) > 0,
        }

    except HTTPException as e:
        logger.error(f"HTTP Exception in chat_message: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in chat_message: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process chat message: {str(e)}"
        )


# Vector store endpoints
@router.post("/create-vector-store")
async def create_vector_store():
    """Create ChromaDB vector store from quiz questions using Azure embeddings"""
    logger.info("=== Vector Store Creation Started ===")

    try:
        # Load questions
        logger.info("Loading questions from JSON file...")
        questions = load_questions()
        if not questions:
            raise HTTPException(
                status_code=400, detail="No questions found to create vector store"
            )

        logger.info(f"Loaded {len(questions)} questions for vector store creation")

        # Create comprehensive chunks
        logger.info("Creating comprehensive chunks from questions...")
        documents, metadatas, ids = create_comprehensive_chunks(questions)
        logger.info(f"Created {len(documents)} document chunks")

        # Generate embeddings using Ollama nomic-embed-text
        logger.info("Generating embeddings using Ollama nomic-embed-text model...")
        embeddings = await get_ollama_embeddings(documents)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Initialize ChromaDB
        logger.info("Initializing ChromaDB client...")
        client = chromadb.PersistentClient(path="./vector_store")

        # Delete existing collection if it exists
        try:
            client.delete_collection("quiz_questions")
            logger.info("Deleted existing vector store collection")
        except Exception:
            logger.info("No existing collection to delete")

        # Create new collection
        collection = client.create_collection(
            name="quiz_questions",
            metadata={"description": "Quiz questions with comprehensive content"},
        )

        # Add documents to collection
        logger.info("Adding documents to ChromaDB collection...")
        collection.add(
            documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
        )

        # Create summary statistics
        topic_counts = {}
        question_type_counts = {}
        tag_counts = {}

        for metadata in metadatas:
            topic = metadata.get("topic", "unknown")
            question_type = metadata.get("question_type", "unknown")
            tags = metadata.get("tags", "")

            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            question_type_counts[question_type] = (
                question_type_counts.get(question_type, 0) + 1
            )

            # Count individual tags
            if tags:
                individual_tags = [
                    tag.strip() for tag in tags.split(",") if tag.strip()
                ]
                for tag in individual_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        logger.info("Vector store creation completed successfully")

        return {
            "success": True,
            "message": f"Successfully created vector store with {len(documents)} questions",
            "stats": {
                "total_questions": len(documents),
                "total_embeddings": len(embeddings),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "topics": topic_counts,
                "question_types": question_type_counts,
                "tags": tag_counts,
                "vector_store_path": "./vector_store",
            },
        }

    except HTTPException as e:
        logger.error(f"HTTP Exception in create_vector_store: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating vector store: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create vector store: {str(e)}"
        )


# Chat system prompt management endpoints
@router.get("/system-prompt", response_class=HTMLResponse)
async def chat_system_prompt_page(request: Request):
    """Chat system prompt edit page"""
    current_prompt = load_chat_system_prompt()
    default_prompt = get_default_chat_system_prompt()

    return templates.TemplateResponse(
        "chat_system_prompt_edit.html",
        {
            "request": request,
            "current_prompt": current_prompt,
            "default_prompt": default_prompt,
        },
    )


@router.post("/system-prompt")
async def save_chat_system_prompt_endpoint(request: Request):
    """Save chat system prompt"""
    try:
        form = await request.form()
        prompt = form.get("prompt", "").strip()

        if not prompt:
            raise HTTPException(status_code=400, detail="System prompt cannot be empty")

        if save_chat_system_prompt(prompt):
            logger.info("Chat system prompt saved successfully")
            return {"success": True, "message": "Chat system prompt saved successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save chat system prompt"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving chat system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-prompt/default")
async def get_default_chat_system_prompt_endpoint():
    """Get default chat system prompt"""
    return {"default_prompt": get_default_chat_system_prompt()}


# Welcome message management endpoints
@router.get("/welcome-message")
async def get_chat_welcome_message():
    """Get the current chat welcome message"""
    try:
        welcome_message = load_welcome_message()
        return {"welcome_message": welcome_message}
    except Exception as e:
        logger.error(f"Error loading welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/welcome-message")
async def save_chat_welcome_message(request: Request):
    """Save chat welcome message"""
    try:
        # Check if it's JSON or form data
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            body = await request.json()
            message = body.get("welcome_message", "").strip()
        else:
            form = await request.form()
            message = form.get("welcome_message", "").strip()

        if not message:
            raise HTTPException(
                status_code=400, detail="Welcome message cannot be empty"
            )

        if save_welcome_message(message):
            logger.info("Welcome message saved successfully")
            return {"success": True, "message": "Welcome message saved successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save welcome message"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/welcome-message/default")
async def get_default_chat_welcome_message():
    """Get default chat welcome message"""
    try:
        default_message = get_default_welcome_message()
        return {"default_welcome_message": default_message}
    except Exception as e:
        logger.error(f"Error loading default welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
