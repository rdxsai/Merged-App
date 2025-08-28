"""
Vector Store API module for the Question App.

This module contains all vector store operations including:
- Vector store creation and management
- Semantic search functionality
- Embedding generation
- Document chunking and processing
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Tuple

import chromadb
import httpx
from fastapi import APIRouter, HTTPException

from ..utils import (
    clean_html_for_vector_store,
    load_questions,
    extract_topic_from_text,
)

logger = logging.getLogger(__name__)

# Create router for vector store endpoints
router = APIRouter(prefix="/vector-store", tags=["vector-store"])

# Configuration from environment
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
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, text in enumerate(texts):
            try:
                # Skip empty texts but add a zero vector
                if not text.strip():
                    logger.warning(f"Empty text at index {i}, skipping embedding generation")
                    embeddings.append([0.0] * 768)  # Default dimension for nomic-embed-text
                    continue

                # Prepare request payload
                payload = {
                    "model": OLLAMA_EMBEDDING_MODEL,
                    "prompt": text.strip()
                }

                # Make request to Ollama
                response = await client.post(
                    f"{OLLAMA_HOST}/api/embeddings",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()

                # Parse response
                result = response.json()
                if "embedding" not in result:
                    logger.error(f"No embedding in response for text {i}: {result}")
                    embeddings.append([0.0] * 768)
                    continue

                embedding = result["embedding"]
                if not isinstance(embedding, list) or not embedding:
                    logger.error(f"Invalid embedding format for text {i}: {embedding}")
                    embeddings.append([0.0] * 768)
                    continue

                embeddings.append(embedding)
                logger.debug(f"Generated embedding {i+1}/{len(texts)} with {len(embedding)} dimensions")

                # Small delay to avoid overwhelming the service
                if i < len(texts) - 1:
                    await asyncio.sleep(0.1)

            except httpx.TimeoutException:
                logger.error(f"Timeout generating embedding for text {i}")
                embeddings.append([0.0] * 768)
            except httpx.RequestError as e:
                logger.error(f"Request error generating embedding for text {i}: {e}")
                embeddings.append([0.0] * 768)
            except Exception as e:
                logger.error(f"Unexpected error generating embedding for text {i}: {e}")
                embeddings.append([0.0] * 768)

    logger.info(f"Generated {len(embeddings)} embeddings from {len(texts)} texts")
    return embeddings


def create_comprehensive_chunks(questions: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
    """
    Create comprehensive chunks from quiz questions for vector store processing.

    This function processes each question and creates detailed text chunks that include
    the question text, feedback, and answer information. Each chunk is designed to
    provide comprehensive context for semantic search and retrieval.

    Args:
        questions (List[Dict[str, Any]]): List of question dictionaries from the JSON file.

    Returns:
        Tuple[List[str], List[Dict[str, Any]], List[str]]: A tuple containing:
            - List of document chunks (text content)
            - List of metadata dictionaries for each chunk
            - List of unique IDs for each chunk

    Note:
        The function creates multiple chunks per question to capture different aspects:
        1. Question text with general feedback
        2. Individual answer information with specific feedback
        3. Topic and tag information for categorization

    Example:
        >>> questions = load_questions()
        >>> documents, metadatas, ids = create_comprehensive_chunks(questions)
        >>> print(f"Created {len(documents)} chunks from {len(questions)} questions")
        Created 150 chunks from 50 questions
    """
    documents = []
    metadatas = []
    ids = []

    for question in questions:
        question_id = question.get("id", "unknown")
        
        # Clean and prepare question text
        question_text = clean_html_for_vector_store(question.get("question_text", ""))
        
        # Clean general feedback
        general_feedback = clean_html_for_vector_store(
            question.get("neutral_comments", "")
        )
        
        # Get topic (with fallback to extraction)
        topic = question.get("topic", "")
        if not topic:
            topic = extract_topic_from_text(question_text)
        
        # Get tags
        tags = question.get("tags", "")
        
        # Get learning objective
        learning_objective = question.get("learning_objective", "")
        
        # Create main question chunk
        if question_text:
            main_content = f"Question: {question_text}"
            if general_feedback:
                main_content += f"\n\nGeneral Feedback: {general_feedback}"
            if learning_objective:
                main_content += f"\n\nLearning Objective: {learning_objective}"
            
            documents.append(main_content)
            metadatas.append({
                "question_id": question_id,
                "chunk_type": "question",
                "topic": topic,
                "tags": tags,
                "question_type": question.get("question_type", "multiple_choice_question"),
                "learning_objective": learning_objective,
            })
            ids.append(f"q_{question_id}_main")

        # Create answer-specific chunks
        answers = question.get("answers", [])
        for i, answer in enumerate(answers):
            answer_text = clean_html_for_vector_store(answer.get("text", ""))
            answer_feedback = clean_html_for_vector_store(answer.get("comments", ""))
            
            if answer_text:
                answer_content = f"Question: {question_text}\n\nAnswer {i+1}: {answer_text}"
                if answer_feedback:
                    answer_content += f"\n\nAnswer Feedback: {answer_feedback}"
                
                documents.append(answer_content)
                metadatas.append({
                    "question_id": question_id,
                    "chunk_type": "answer",
                    "answer_index": i,
                    "answer_weight": answer.get("weight", 0),
                    "topic": topic,
                    "tags": tags,
                    "question_type": question.get("question_type", "multiple_choice_question"),
                    "learning_objective": learning_objective,
                })
                ids.append(f"q_{question_id}_answer_{i}")

    logger.info(f"Created {len(documents)} comprehensive chunks from {len(questions)} questions")
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


@router.post("/create")
async def create_vector_store():
    """Create ChromaDB vector store from quiz questions using Ollama embeddings"""
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
            "message": f"Successfully created vector store with {len(questions)} questions",
            "stats": {
                "total_questions": len(questions),
                "total_chunks": len(documents),
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


@router.get("/search")
async def search_vector_store_endpoint(query: str, n_results: int = 5):
    """Search the vector store for relevant content"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if n_results < 1 or n_results > 20:
            n_results = 5

        logger.info(f"Searching vector store for: {query}")
        results = await search_vector_store(query, n_results=n_results)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in vector store search endpoint: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to search vector store: {str(e)}"
        )


@router.get("/status")
async def get_vector_store_status():
    """Get the current status of the vector store"""
    try:
        client = chromadb.PersistentClient(path="./vector_store")
        
        try:
            collection = client.get_collection("quiz_questions")
            count = collection.count()
            
            return {
                "success": True,
                "status": "active",
                "collection_name": "quiz_questions",
                "document_count": count,
                "vector_store_path": "./vector_store"
            }
        except Exception:
            return {
                "success": True,
                "status": "not_initialized",
                "collection_name": "quiz_questions",
                "document_count": 0,
                "vector_store_path": "./vector_store"
            }

    except Exception as e:
        logger.error(f"Error checking vector store status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to check vector store status: {str(e)}"
        )


@router.delete("/")
async def delete_vector_store():
    """Delete the entire vector store"""
    try:
        client = chromadb.PersistentClient(path="./vector_store")
        
        try:
            client.delete_collection("quiz_questions")
            logger.info("Vector store collection deleted successfully")
            
            return {
                "success": True,
                "message": "Vector store deleted successfully"
            }
        except Exception as e:
            logger.warning(f"Error deleting collection (may not exist): {e}")
            return {
                "success": True,
                "message": "Vector store was already deleted or does not exist"
            }

    except Exception as e:
        logger.error(f"Error deleting vector store: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete vector store: {str(e)}"
        )
