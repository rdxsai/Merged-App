"""
Vector Store API module for the Question App.

This module provides an interface for vector store operations,
including creating the vector store and performing semantic search.
It uses ChromaDB as the backend and Ollama for embeddings.
"""

import os
import httpx
import logging
import asyncio # <-- Make sure this is imported
from typing import List, Dict, Any, Optional, Tuple
from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..core import config, get_logger
from ..models import Question  # Using the Pydantic model
from ..services.database import DatabaseManager
from ..services.tutor.interfaces import VectorStoreInterface
from ..utils import (
    clean_question_text, 
    extract_topic_from_text, 
    load_questions, 
    clean_answer_feedback
)

# Import ChromaDB and Ollama embeddings
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    logger.critical(
        "ChromaDB or Ollama not installed. Please run: 'poetry install --with rag'"
    )
    raise

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/vector-store", tags=["vector-store"])

# --- === OLLAMA EMBEDDING FUNCTION === ---
# This is a helper function that your old file had, which is good.
# We will keep it but move it to the top for clarity.
async def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings from Ollama using the nomic-embed-text model.
    """
    embeddings = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, text in enumerate(texts):
            try:
                if not text.strip():
                    logger.warning(f"Empty text at index {i}, skipping.")
                    embeddings.append([0.0] * 768) # Default dimension for nomic
                    continue

                payload = {
                    "model": config.OLLAMA_EMBEDDING_MODEL,
                    "prompt": text.strip(),
                }
                response = await client.post(
                    f"{config.OLLAMA_HOST}/api/embeddings", # Using config.OLLAMA_HOST
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

                result = response.json()
                if "embedding" not in result:
                    logger.error(f"No embedding in response for text {i}: {result}")
                    embeddings.append([0.0] * 768)
                    continue

                embeddings.append(result["embedding"])
                
                if i < len(texts) - 1:
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Error generating embedding for text {i}: {e}")
                embeddings.append([0.0] * 768)

    logger.info(f"Generated {len(embeddings)} embeddings from {len(texts)} texts")
    return embeddings


# --- === THIS IS THE CORRECTED SERVICE CLASS === ---

class ChromaVectorStoreService(VectorStoreInterface):
    """
    Service class for interacting with ChromaDB.
    """

    def __init__(
        self,
        host: str = os.getenv("CHROMA_HOST", config.CHROMA_HOST or "localhost"),
        port: str = os.getenv("CHROMA_PORT", config.CHROMA_PORT or 8000),
        collection_name: str = "quiz_questions",
    ):
        """
        Initialize the ChromaDB client.
        (This is the NEW __init__ that doesn't store self.collection)
        """
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.client.heartbeat() 
            self.collection_name = collection_name
            
            logger.info(f"ChromaDB service initialized for collection '{self.collection_name}'")

        except Exception as e:
            logger.critical(f"Failed to initialize ChromaDB client: {e}", exc_info=True)
            logger.critical(f"Please ensure ChromaDB is running at http://{host}:{port}")
            self.client = None
            self.collection_name = ""
            raise ValueError(
                f"Could not connect to a Chroma server at http://{host}:{port}. Are you sure it is running?"
            ) from e

    async def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a semantic search in the vector store.
        (This is the NEW search that matches the NEW __init__)
        """
        if not self.client:
            logger.error("ChromaDB search failed. Client not initialized.")
            return []
        
        try:
            # --- === THIS IS THE FIX === ---
            # 1. Get the collection *by name* every time.
            try:
                collection = self.client.get_collection(self.collection_name)
            except Exception as get_e:
                logger.error(f"Failed to get collection '{self.collection_name}': {get_e}")
                logger.error("Did you create the vector store yet by clicking the button on the UI?")
                return []
            # --- === END OF FIX === ---

            logger.debug("Generating ollama embeddings for search...")
            query_embeddings_list = await get_ollama_embeddings([query])

            if not query_embeddings_list or not query_embeddings_list[0]:
                logger.error("Failed to generate query embeddings for search")
                return []
            
            query_vector = [query_embeddings_list[0]] # ChromaDB expects a list
            
            # 2. Use the local 'collection' variable
            results = collection.query(
                query_embeddings = query_vector,
                n_results = k,
                include = ["metadatas" , "documents" , "distances"]
            )

            if not results.get("documents") or not results.get('distances'):
                return []
                
            combined_results = []
            docs = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]

            for content, meta, dist in zip(docs , metadatas , distances):
                chunk = meta
                chunk['content'] = content
                chunk['distance'] = dist
                combined_results.append(chunk)
            
            return combined_results

        except Exception as e:
            logger.error(f"ChromaDB search failed : {e}", exc_info=True)
            return []

    async def create_vector_store(self) -> Dict[str, Any]:
        """
        Fetch all questions from the SQLite DB, process them,
        and add them to the ChromaDB vector store.
        (This is the NEW version that matches your old file's logic)
        """
        try:
            logger.info("Starting to create vector store...")
            
            # 1. Fetch data from SQLite
            # We must create a new DB manager for this task
            db_manager = DatabaseManager(config.db_path)
            questions_from_db = db_manager.list_all_questions() # This gets List[Dict]
            
            if not questions_from_db:
                logger.warning("No questions found in the database to add to vector store.")
                return {"message": "No questions found in database.", "count": 0}

            logger.info(f"Fetched {len(questions_from_db)} questions from SQLite.")
            
            # Re-fetch full question data to include answers
            full_questions_data = []
            for q_header in questions_from_db:
                q_detail = db_manager.load_question_details(q_header['id'])
                if q_detail:
                    full_questions_data.append(q_detail)

            # 2. Prepare data for ChromaDB (using your old file's function)
            logger.info("Creating comprehensive chunks from questions...")
            documents, metadatas, ids = create_comprehensive_chunks(full_questions_data)
            logger.info(f"Created {len(documents)} document chunks")

            # 3. Generate embeddings
            logger.info("Generating embeddings using Ollama...")
            embeddings = await get_ollama_embeddings(documents)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # 4. Add to ChromaDB
            logger.info(f"Connecting to ChromaDB to create collection...")
            
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted existing collection: '{self.collection_name}'")
            except Exception:
                logger.info(f"No existing collection '{self.collection_name}' to delete.")

            # Create new collection
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Quiz questions with comprehensive content", "hnsw:space": "cosine"},
            )
            
            logger.info(f"Adding {len(documents)} documents to collection...")
            collection.add(
                documents=documents, 
                embeddings=embeddings, 
                metadatas=metadatas, 
                ids=ids
            )

            logger.info("Successfully created/updated vector store.")
            
            # 5. Get stats
            count = collection.count()
            stats = {
                "total_documents": count,
                "collection_name": collection.name,
                "embedding_model": config.OLLAMA_EMBEDDING_MODEL,
            }
            
            return {
                "message": "Vector store created successfully.",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Failed to create vector store: {e}"
            )

# --- (The rest of your file is unchanged, but I've included it for completeness) ---

def create_comprehensive_chunks(
    questions: List[Dict[str, Any]]
) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
    """
    Create comprehensive chunks from quiz questions for vector store processing.
    (This function is from your old file)
    """
    documents = []
    metadatas = []
    ids = []

    for question in questions:
        question_id = str(question.get("id", "unknown"))
        question_text = clean_question_text(question.get("question_text", ""))
        
        # --- (This logic is different from my last version, but let's use yours) ---
        general_feedback = clean_question_text(
            question.get("neutral_comments", "") # Your old file used this key
        )
        topic = question.get("topic", "Web Accessibility") # Set default
        tags = ", ".join(question.get("tags", [])) # Handle tags as a list
        learning_objective = question.get("learning_objective", "")
        question_type = question.get("question_type", "multiple_choice_question")

        # Create main question chunk
        if question_text:
            main_content = f"Question: {question_text}"
            if general_feedback:
                main_content += f"\n\nGeneral Feedback: {general_feedback}"
            if learning_objective:
                main_content += f"\n\nLearning Objective: {learning_objective}"

            documents.append(main_content)
            metadatas.append(
                {
                    "question_id": question_id,
                    "chunk_type": "question",
                    "topic": topic,
                    "tags": tags,
                    "question_type": question_type,
                    "learning_objective": learning_objective,
                }
            )
            ids.append(f"q_{question_id}_main")

        # Create answer-specific chunks
        answers = question.get("answers", [])
        for i, answer in enumerate(answers):
            answer_text = clean_question_text(answer.get("text", ""))
            # Use 'feedback_text' from our new DB model
            answer_feedback = clean_answer_feedback(answer.get("feedback_text", "")) 
            answer_feedback = clean_question_text(answer_feedback)

            if answer_text:
                answer_content = (
                    f"Question: {question_text}\n\nAnswer {i+1}: {answer_text}"
                )
                if answer_feedback:
                    answer_content += f"\n\nAnswer Feedback: {answer_feedback}"

                documents.append(answer_content)
                metadatas.append(
                    {
                        "question_id": question_id,
                        "chunk_type": "answer",
                        "answer_index": i,
                        "is_correct": answer.get("is_correct", False), # Use new key
                        "topic": topic,
                        "tags": tags,
                        "question_type": question_type,
                        "learning_objective": learning_objective,
                    }
                )
                ids.append(f"q_{question_id}_answer_{i}")

    logger.info(
        f"Created {len(documents)} comprehensive chunks from {len(questions)} questions"
    )
    return documents, metadatas, ids


# --- === API Endpoints for the /vector-store router === ---

@router.post("/create")
async def create_vector_store_endpoint(background_tasks: BackgroundTasks):
    """
    API endpoint to create/update the vector store.
    """
    logger.info("Received request to create vector store.")
    try:
        # We must re-create the service here to use it
        vector_service = ChromaVectorStoreService()
        result = await vector_service.create_vector_store()
        return result
    except Exception as e:
        logger.error(f"Endpoint /create failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_vector_store_endpoint(query: str):
    """
    API endpoint to test semantic search.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        vector_service = ChromaVectorStoreService()
        results = await vector_service.search(query, k=3)
        return {"results": results}
    except Exception as e:
        logger.error(f"Endpoint /search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_vector_store_status():
    """Get the current status of the vector store"""
    try:
        client = chromadb.HttpClient(host = config.CHROMA_HOST , port = config.CHROMA_PORT)
        try:
            collection = client.get_collection("quiz_questions")
            count = collection.count()
            return {
                "success": True, "status": "active",
                "collection_name": "quiz_questions",
                "document_count": count,
            }
        except Exception:
            return {
                "success": True, "status": "not_initialized",
                "collection_name": "quiz_questions",
                "document_count": 0,
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
        client = chromadb.HttpClient(host = config.CHROMA_HOST , port = config.CHROMA_PORT)
        try:
            client.delete_collection("quiz_questions")
            logger.info("Vector store collection deleted successfully")
            return {"success": True, "message": "Vector store deleted successfully"}
        except Exception as e:
            logger.warning(f"Error deleting collection (may not exist): {e}")
            return {
                "success": True,
                "message": "Vector store was already deleted or does not exist",
            }
    except Exception as e:
        logger.error(f"Error deleting vector store: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete vector store: {str(e)}"
        )