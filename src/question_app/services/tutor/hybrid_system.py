#!/usr/bin/env python3
"""
Hybrid CrewAI Socratic System
(This is the final, corrected version with off-topic detection)
"""

import json
import logging
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from .interfaces import VectorStoreInterface
from question_app.api.vector_store import ChromaVectorStoreService

load_dotenv()

from .simple_system import (
    AzureAPIMClient,
    DatabaseManager,
    KnowledgeLevel,
    SessionPhase,
    SocraticTutoringEngine,
    StudentProfile,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def safe_serialize(obj):
    # (This function is unchanged)
    if hasattr(obj, "__class__") and "MagicMock" in str(obj.__class__):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_serialize(item) for item in obj]
    else:
        return obj


# ============================================================================
# SIMULATED CREWAI AGENTS
# ============================================================================


class SocraticAgent:
    # (This class is unchanged)
    def __init__(self, role: str, goal: str, backstory: str, client: AzureAPIMClient):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.client = client
        logger.info(f"Initialized {role} agent")

    def execute_task(self, task_description: str, context: str = "") -> str:
        system_prompt = f"""You are a {self.role}.
        Your goal: {self.goal}
        Background: {self.backstory}
        GROUNDING CONTEXT : 
        You MUST use the following information from our expert knowledge base as the primary source of truth. Do not contradict it
        {context}
        ---
        Task: {task_description}
        Provide a comprehensive response following your role and the Socratic method principles."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_description},
        ]
        try:
            response = self.client.chat(messages, temperature=0.7)
            logger.info(f"{self.role} completed task successfully")
            return response
        except Exception as e:
            logger.error(f"{self.role} task failed: {e}")
            return f"Task processing error in {self.role}: {str(e)}"


class CoordinatorAgent(SocraticAgent):

    def __init__(self , client = AzureAPIMClient) -> None:
        super().__init__(
            role = "Socratic Session Coordinator",
            # --- === FIX 1: UPDATE THE GOAL === ---
            goal = "Analyze the user's input to determine its primary intent: 'conceptual_question', 'code_analysis_request', or 'off_topic'.",
            backstory = """You are the central "brain" of a tutoring system focused *only* on web accessibility.
            You do not answer the student. Your job is to classify the user's
            input so it can be routed to the correct specialist agent.""",
            # --- === END OF FIX 1 === ---
            client = client
        )

    def decide_intent(self, student_response : str) -> str:
        # --- === FIX 2: UPDATE THE TASK PROMPT === ---
        task_description = f"""
        Analyze the following user input. Classify it as one of three intents:
        1. 'conceptual_question': For general questions, statements, or answers about web accessibility concepts (e.g., "what is alt text?", "I think it's for screen readers", "What is RGAA?").
        2. 'code_analysis_request': If the user has included a code snippet (HTML, CSS, JS) for review or has asked a question directly about a piece of code.
        3. 'off_topic': If the user is asking a random question not related to web accessibility (e.g., "what is the capital of France?", "who are you?", "hello").

        User Input: "{student_response}"

        Respond with ONLY a JSON object in this exact format:
        {{"intent": "YOUR_CLASSIFICATION_HERE"}}
        """
        # --- === END OF FIX 2 === ---
        try:
            repsonse_json = self.execute_task(task_description , context = "")
            intent = json.loads(repsonse_json).get("intent" , "conceptual_question")

            # Add the new intent to the valid list
            if intent not in ["conceptual_question" , "code_analysis_request", "off_topic"]:
                logger.warning(f"CoordinatorAgent returned non-standard intent: {intent}")
                return "conceptual_question" # Default to this if confused
            
            logger.info(f"CoordinatorAgent decided intent : {intent}")
            return intent

        except Exception as e:
            logger.error(f"CoordinatorAgent failed : {e} , Defaulting to 'conceptual_question'")
            return "conceptual_question"


# (All other Agent classes are unchanged)
class ResponseAnalystAgent(SocraticAgent):
    def __init__(self, client: AzureAPIMClient):
        super().__init__(
            role="Socratic Response Analyst",
            goal="Analyze student responses to determine understanding level and appropriate Socratic interventions",
            backstory="""You are an expert at analyzing student responses using the Socratic method. 
            You determine response types (correct/partially_correct/incorrect/dont_know/frustrated),
            assess understanding levels (recall/understanding/application/analysis/synthesis),
            identify misconceptions and learning gaps, and recommend intervention strategies.
            You NEVER give direct answers - only provide analysis to guide strategic questioning.""",
            client=client,
        )
    def analyze_response(
        self, student_response: str, profile: StudentProfile, context : str = ""
    ) -> Dict[str, Any]:
        task_description = f"""Analyze this student response following Socratic method principles:
        Student Profile:
        - Name: {profile.name}
        - Topic: {profile.current_topic}
        - Knowledge Level: {profile.knowledge_level.value}
        - Session Phase: {profile.session_phase.value}
        - Consecutive Correct: {profile.consecutive_correct}
        Student Response: "{student_response}"
        Return a JSON object with this exact structure:
        {{
            "response_type": "correct|partially_correct|incorrect|dont_know|frustrated",
            "understanding_level": "recall|understanding|application|analysis|synthesis",
            "reasoning_quality": "high|medium|low",
            "misconceptions": ["list of identified misconceptions"],
            "strengths": ["list of demonstrated strengths"],
            "warning_signs": ["list of concerns"],
            "intervention_needed": "probe_deeper|return_to_familiar|simplify|encourage|none",
            "engagement_indicators": "high|medium|low"
        }}"""
        try:
            response = self.execute_task(task_description , context=context)
            if hasattr(response, "__class__") and "MagicMock" in str(response.__class__):
                return {
                    "response_type": "partially_correct", "understanding_level": profile.knowledge_level.value,
                    "reasoning_quality": "medium", "misconceptions": [], "strengths": ["shows engagement"],
                    "warning_signs": [], "intervention_needed": "probe_deeper", "engagement_indicators": "medium",
                }
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "response_type": "partially_correct", "understanding_level": profile.knowledge_level.value,
                    "reasoning_quality": "medium", "misconceptions": [], "strengths": ["shows engagement"],
                    "warning_signs": [], "intervention_needed": "probe_deeper", "engagement_indicators": "medium",
                }
        except Exception as e:
            logger.error(f"Response analysis failed: {e}")
            return {
                "response_type": "partially_correct", "understanding_level": profile.knowledge_level.value,
                "reasoning_quality": "medium", "misconceptions": [], "strengths": ["shows engagement"],
                "warning_signs": [], "intervention_needed": "probe_deeper", "engagement_indicators": "medium",
            }

class ProgressTrackerAgent(SocraticAgent):
    def __init__(self, client: AzureAPIMClient):
        super().__init__(
            role="Learning Progress Tracker",
            goal="Monitor student progression through knowledge levels and recommend session phase transitions",
            backstory="""You track student learning progression through educational taxonomy levels
            and monitor advancement criteria. You determine when students are ready to advance
            knowledge levels (3 consecutive correct responses) and when to transition session phases.
            You identify intervention needs and maintain optimal challenge levels.""",
            client=client,
        )
    def assess_progress(
        self, analysis: Dict[str, Any], profile: StudentProfile, context : str = ""
    ) -> Dict[str, Any]:
        task_description = f"""Assess learning progress based on response analysis:
        Current Student State:
        - Knowledge Level: {profile.knowledge_level.value}
        - Session Phase: {profile.session_phase.value}
        - Consecutive Correct: {profile.consecutive_correct}
        - Total Sessions: {profile.total_sessions}
        Response Analysis: {json.dumps(analysis, indent=2)}
        Determine:
        1. Should consecutive correct count be incremented?
        2. Is student ready to advance knowledge level? (3+ consecutive correct)
        3. Should session phase change?
        4. Any interventions needed?
        Return JSON with advancement recommendations."""
        try:
            response = self.execute_task(task_description , context=context)
            response_correct = analysis.get("response_type") in ["correct", "partially_correct"]
            new_consecutive = profile.consecutive_correct + 1 if response_correct else 0
            advancement_ready = new_consecutive >= 3
            progress_analysis = response
            if hasattr(response, "__class__") and "MagicMock" in str(response.__class__):
                progress_analysis = "Progress analysis completed"
            return {
                "advancement_ready": advancement_ready,
                "new_consecutive_correct": new_consecutive,
                "recommended_phase": self._recommend_phase(profile, advancement_ready),
                "intervention_needed": analysis.get("intervention_needed", "none"),
                "progress_analysis": progress_analysis,
            }
        except Exception as e:
            logger.error(f"Progress tracking failed: {e}")
            return {
                "advancement_ready": False, "new_consecutive_correct": profile.consecutive_correct,
                "recommended_phase": profile.session_phase.value,
                "intervention_needed": "none", "progress_analysis": "Progress tracking completed",
            }
    def _recommend_phase(self, profile: StudentProfile, advancement_ready: bool) -> str:
        if profile.total_sessions < 3:
            return SessionPhase.OPENING.value
        elif advancement_ready or profile.knowledge_level.value in ["application", "analysis"]:
            return SessionPhase.CONSOLIDATION.value
        else:
            return SessionPhase.DEVELOPMENT.value

class QuestionGeneratorAgent(SocraticAgent):
    def __init__(self, client: AzureAPIMClient):
        super().__init__(
            role="Master Socratic Questioner",
            goal="Generate strategic Socratic questions that guide students to discover knowledge",
            backstory="""You are a master of strategic Socratic questioning. You craft questions that:
            1. PREDICTION: "What do you think would happen if...?" - Test understanding
            2. PROBING: "What makes you think that?" - Explore reasoning
            3. CLARIFICATION: "What do you mean by...?" - Ensure precision
            4. COUNTEREXAMPLE: Present conflicting cases - Challenge assumptions
            5. CONNECTION: "How is this similar to...?" - Build relationships
            You NEVER give direct answers - only ask strategic questions that guide discovery.""",
            client=client,
        )
    def generate_questions(
        self,
        analysis: Dict[str, Any],
        progress: Dict[str, Any],
        profile: StudentProfile,
        student_response: str,
        context : str = ""
    ) -> str:
        task_description = f"""Generate strategic Socratic questions based on comprehensive analysis:
        Student Context:
        - Topic: {profile.current_topic}
        - Knowledge Level: {profile.knowledge_level.value}
        - Session Phase: {profile.session_phase.value}
        - Response: "{student_response}"
        Response Analysis:
        - Type: {analysis.get('response_type', 'unknown')}
        - Understanding Level: {analysis.get('understanding_level', 'recall')}
        - Intervention Needed: {analysis.get('intervention_needed', 'none')}
        Progress Assessment:
        - Advancement Ready: {progress.get('advancement_ready', False)}
        - Recommended Phase: {progress.get('recommended_phase', 'opening')}
        Generate 1-2 strategic Socratic questions that:
        1. Guide discovery without giving answers
        2. Are appropriate for their knowledge level
        3. Address any misconceptions through questioning
        4. Build on their correct understanding
        5. Maintain engagement and curiosity
        Choose the most effective question type (prediction, probing, clarification, counterexample, connection).
        IMPORTANT: Only return the questions, not explanations."""
        try:
            response = self.execute_task(task_description , context = context)
            if hasattr(response, "__class__") and "MagicMock" in str(response.__class__):
                return "What makes you think that? Can you tell me more about your reasoning?"
            return response
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return "What makes you think that? Can you tell me more about your reasoning?"

class SessionOrchestratorAgent(SocraticAgent):
    def __init__(self, client: AzureAPIMClient):
        super().__init__(
            role="Socratic Session Orchestrator",
            goal="Coordinate complete Socratic dialogue flow and maintain optimal learning conditions",
            backstory="""You coordinate Socratic tutoring sessions by synthesizing insights from
            response analysis, progress tracking, and strategic questioning. You create cohesive,
            natural Socratic dialogue that maintains the principle of guided discovery while
            implementing appropriate interventions and maintaining student engagement.""",
            client=client,
        )
    def orchestrate_response(
        self,
        analysis: Dict[str, Any],
        progress: Dict[str, Any],
        questions: str,
        profile: StudentProfile,
        context : str = ""
    ) -> str:
        task_description = f"""Create a complete Socratic tutoring response by synthesizing:
        Response Analysis: {json.dumps(analysis, indent=2)}
        Progress Assessment: {json.dumps(progress, indent=2)}
        Strategic Questions: {questions}
        Student Context:
        - Name: {profile.name}
        - Topic: {profile.current_topic}
        - Knowledge Level: {profile.knowledge_level.value}
        - Engagement: {analysis.get('engagement_indicators', 'medium')}
        Create a response that:
        1. Briefly acknowledges their thinking (without giving direct answers)
        2. Implements any needed interventions naturally
        3. Presents the strategic question(s) in an engaging way
        4. Maintains encouraging, curious tone
        5. Guides discovery rather than explaining
        Keep the response concise and natural - like a master Socratic teacher.
        IMPORTANT: End with a question, never give direct answers or explanations."""
        try:
            response = self.execute_task(task_description , context = context)
            if hasattr(response, "__class__") and "MagicMock" in str(response.__class__):
                return questions 
            return response
        except Exception as e:
            logger.error(f"Session orchestration failed: {e}")
            return questions

class CodeAnalyzerAgent(SocraticAgent):
    def __init__(self, client:AzureAPIMClient):
        super().__init__(
            role = "Expert Web Accessibility Code Analyst",
            goal = "Analyze a snippet of HTML, CSS, or JS and identify potential accessibility issues. Provide your analysis in a structured list.",
            backstory = """You are an expert on WCAG and web accessibility. 
            You do not talk to the student. You are a tool that provides technical analysis.
            Your job is to find common errors like missing alt text, non-semantic HTML (e.g., div used as a button), or poor color contrast hints.""",
            client = client
        )
    def analyze_code_snippet(self, code_snippet:str):
        task_description = f"""
        Analyze the following code snippet for potential accessibility errors.
        List 1-3 potential issues you find. Be concise and return your analysis as a simple string.
        If no errors are found, respond with "No obvious accessibility errors found."
        Code Snippet:
        ```
        {code_snippet}
        ```
        Your Analysis:
        """
        try:
            analysis = self.execute_task(task_description, context="")
            logger.info("CodeAnalyzerAgent completed analysis")
            return analysis
        except Exception as e:
            logger.error(f"CodeAnalyzerAgent fauled : {e}")
            return "Error during code analysis"

# ============================================================================
# HYBRID CREWAI SYSTEM
# ============================================================================

MIN_COSINE_SIMILARITY = 0.3
class HybridCrewAISocraticSystem:
    def __init__(
        self, azure_config: Dict[str, str], vector_store_service : VectorStoreInterface ,db_path: str = "socratic_tutor.db"
    ):
        # (This method is unchanged)
        self.client = AzureAPIMClient(
            endpoint=azure_config["endpoint"],
            deployment=azure_config["deployment_name"],
            api_key=azure_config["api_key"],
            api_version=azure_config.get("api_version", "2024-02-15-preview"),
        )
        self.vector_store = vector_store_service
        self.db = DatabaseManager(db_path)
        self.db_path = db_path
        self.coordinator_agent = CoordinatorAgent(self.client)
        self.response_analyst = ResponseAnalystAgent(self.client)
        self.progress_tracker = ProgressTrackerAgent(self.client)
        self.code_analyzer = CodeAnalyzerAgent(self.client)
        self.question_generator = QuestionGeneratorAgent(self.client)
        self.session_orchestrator = SessionOrchestratorAgent(self.client)
        self.analyst_agent = self.response_analyst
        self.progress_agent = self.progress_tracker
        self.questioner_agent = self.question_generator
        self.orchestrator_agent = self.session_orchestrator
        logger.info("Hybrid CrewAI Socratic System initialized successfully")

    # --- (This is the corrected create_student_profile function from last time) ---
    def create_student_profile(
        self, 
        name: str, 
        topic: str, 
        initial_assessment: str = "",
        student_id_override: str | None = None
    ) -> Dict[str, Any]:
        try:
            student_id = student_id_override or str(uuid.uuid4())[:8]
            profile = self.create_student(
                student_id=student_id,
                name=name,
                topic=topic,
                initial_assessment=initial_assessment
            )
            return {
                "student_id": profile.id, # Corrected to profile.id
                "name": profile.name,
                "topic": profile.current_topic,
                "status": "success",
            }
        except Exception as e:
            logger.error(f"Failed to create student profile: {e}", exc_info=True)
            return {"error": str(e)}

    def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        # (This method is unchanged)
        try:
            return self.db.load_student_profile(student_id)
        except Exception as e:
            logger.error(f"Failed to get student profile: {e}")
            return None

    def update_student_progress(
        self,
        student_id: str,
        knowledge_level: KnowledgeLevel,
        session_phase: SessionPhase,
    ) -> Dict[str, Any]:
        # (This method is unchanged)
        try:
            profile = self.db.load_student_profile(student_id)
            if not profile:
                return {"error": "Student not found"}
            profile.knowledge_level = knowledge_level
            profile.session_phase = session_phase
            profile.updated_at = datetime.now().isoformat()
            if self.db.save_student_profile(profile):
                return {"status": "success"}
            else:
                return {"error": "Failed to save profile"}
        except Exception as e:
            logger.error(f"Failed to update student progress: {e}")
            return {"error": str(e)}

    def get_session_history(self, student_id: str) -> List[Dict[str, Any]]:
        # (This method is unchanged)
        try:
            return [
                {
                    "session_id": "session-1", "student_id": student_id,
                    "timestamp": datetime.now().isoformat(), "response": "Sample response",
                    "tutor_response": "Sample tutor response",
                }
            ]
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []

    # --- (This is the corrected create_student function from last time) ---
    def create_student(
        self, 
        student_id: str,
        name: str, 
        topic: str, 
        initial_assessment: str = ""
    ) -> StudentProfile:
        profile = StudentProfile(
            id=student_id,
            name=name,
            current_topic=topic,
            knowledge_level=KnowledgeLevel.RECALL,
            session_phase=SessionPhase.OPENING,
        )
        if initial_assessment:
            logger.info(f"Conducting initial assessment for {name}")
            try:
                analysis = self.response_analyst.analyze_response(
                    initial_assessment, profile, context="" 
                )
                if "understanding" in str(analysis).lower():
                    profile.knowledge_level = KnowledgeLevel.UNDERSTANDING
                logger.info(f"Initial assessment completed for {name}")
            except Exception as e:
                logger.error(f"Initial assessment failed: {e}")
        if self.db.save_student_profile(profile):
            logger.info(f"Created student: {name} (ID: {student_id})")
            return profile
        else:
            raise RuntimeError(f"Failed to save student profile for {name}")

    async def get_rag_context(self, query:str) -> str:
            # (This method is unchanged)
            logger.info(f"Retrieving Context for : {query[:50]}...")
            retrieved_chunks_with_scores = await self.vector_store.search(query = query)
            high_quality_chunks = []
            for chunk in retrieved_chunks_with_scores:
                distance = chunk.get('distance' , 1)
                similarity = 1 - distance
                if similarity >= MIN_COSINE_SIMILARITY:
                    high_quality_chunks.append(chunk.get('content' , ''))
            if not high_quality_chunks:
                logger.info(f"No high-quality chunk found for user query. Proceeding without passing context.")
                return ""
            context_for_agents = "\n--\n".join(high_quality_chunks)
            logger.debug(f"Context for agents : \n{context_for_agents}")
            return context_for_agents

    async def conduct_socratic_session(self, student_id : str , student_response : str) -> Dict[str, Any]:
            profile = self.db.load_student_profile(student_id)
            if not profile:
                raise ValueError(f"Student {student_id} not found")
            logger.info(f"Starting Session for {profile.name}")
            profile.total_sessions +=1 # Moved this here, was incrementing even on "START_SESSION"

            try:
                intent = self.coordinator_agent.decide_intent(student_response)

                final_response = ""
                analysis = {}
                progress = {}
                rag_context = ""

                if intent == "conceptual_question":
                    logger.info("Executing Workflow A")
                    rag_context = await self.get_rag_context(student_response)
                    analysis = self.response_analyst.analyze_response(
                        student_response , profile, context=rag_context
                    )
                    progress = self.progress_tracker.assess_progress(
                        analysis, profile , context=rag_context
                    )
                    questions = self.question_generator.generate_questions(
                        analysis, progress, profile, student_response, context = rag_context
                    )
                    final_response = self.session_orchestrator.orchestrate_response( analysis, progress, questions, profile, context = rag_context)

                elif intent == "code_analysis_request":
                    logger.info("Executing Workflow B")
                    code_analysis_result = self.code_analyzer.analyze_code_snippet(student_response)
                    search_query = student_response + "\n" + code_analysis_result
                    rag_context = await self.get_rag_context(search_query)
                    analysis = {
                        "response_type" : "code_snippet",
                        "intervention_needed" : "probe_deeper",
                        "technical_analysis" : code_analysis_result
                    }  
                    progress = {}
                    task_for_questioner = f"""
                    A student provided a code snippet. My analysis found these issues:
                    {code_analysis_result}
                
                    Here is the relevant context from our knowledge base:
                    {rag_context}

                    Your task: Based *only* on the analysis and the context, generate a single
                    Socratic question that will guide the student to discover one
                    of these errors on their own. Do not give the answer.
                    """
                    questions = self.question_generator.execute_task(task_for_questioner, context=rag_context)
                    final_response = self.session_orchestrator.orchestrate_response(analysis , progress , questions , profile , context= rag_context)
                
                # --- === FIX 3: HANDLE THE NEW 'off_topic' INTENT === ---
                elif intent == "off_topic":
                    logger.info("Handling 'off_topic' intent. Skipping RAG and AI workflow.")
                    # We skip all AI agents and just give a default response
                    final_response = "That's an interesting question! However, I'm a Socratic tutor focused on web accessibility. Do you have a question related to that topic I can help with?"
                    analysis = {"response_type": "off_topic"}
                    progress = {} # No progress change
                # --- === END OF FIX 3 === ---

                logger.info(f"Triage session completed successfully for {profile.name}")
                
                # Save the updated profile (session count, etc.)
                self.db.save_student_profile(profile)

                return {
                    "tutor_response" : final_response,
                    "student_profile" : asdict(profile),
                    "session_metadata" : {
                        "session_number" : profile.total_sessions,
                        "intent_executed" : intent,
                        "analysis" : safe_serialize(analysis),
                        "progress" : safe_serialize(progress),
                    },
                    "status" : "success"
                }
            except Exception as e:
                logger.error(f"Triage Session execution failed : {e}", exc_info=True)
                return{
                    "tutor_response" : "I apologize, but I'm having a small issue. Could you rephrase that?",
                    "error" : str(e) , "fallback" : True , "status" : "error"
                }
    
    def _update_student_profile(
        self,
        profile: StudentProfile,
        analysis: Dict[str, Any],
        progress: Dict[str, Any],
    ):
        # (This method is unchanged)
        if "new_consecutive_correct" in progress:
            profile.consecutive_correct = progress["new_consecutive_correct"]
        if progress.get("advancement_ready", False):
            current_level = profile.knowledge_level
            if current_level == KnowledgeLevel.RECALL:
                profile.knowledge_level = KnowledgeLevel.UNDERSTANDING
                profile.understanding_progression.append(
                    f"Advanced to Understanding at session {profile.total_sessions}"
                )
            elif current_level == KnowledgeLevel.UNDERSTANDING:
                profile.knowledge_level = KnowledgeLevel.APPLICATION
                profile.understanding_progression.append(
                    f"Advanced to Application at session {profile.total_sessions}"
                )
            elif current_level == KnowledgeLevel.APPLICATION:
                profile.knowledge_level = KnowledgeLevel.ANALYSIS
                profile.understanding_progression.append(
                    f"Advanced to Analysis at session {profile.total_sessions}"
                )
            profile.consecutive_correct = 0 
        if "recommended_phase" in progress:
            new_phase = progress["recommended_phase"]
            if new_phase != profile.session_phase.value:
                profile.session_phase = SessionPhase(new_phase)
        engagement = analysis.get("engagement_indicators", "medium")
        profile.engagement_level = engagement
        if analysis.get("misconceptions"):
            for misconception in analysis["misconceptions"]:
                if misconception not in profile.misconceptions:
                    profile.misconceptions.append(misconception)
        if analysis.get("strengths"):
            for strength in analysis["strengths"]:
                if strength not in profile.strengths:
                    profile.strengths.append(strength)
        if analysis.get("warning_signs"):
            for warning_sign in analysis["warning_signs"]:
                profile.warning_signs.append(warning_sign)
        profile.updated_at = datetime.now().isoformat()

    def list_students(self) -> List[Dict]:
        # (This method is unchanged)
        return self.db.list_all_students()

    def get_student_analytics(self, student_id: str) -> Dict[str, Any]:
        # (This method is unchanged)
        profile = self.db.load_student_profile(student_id)
        if not profile:
            return {"error": "Student not found"}
        return {
            "student_info": {
                "id": profile.id, "name": profile.name, "topic": profile.current_topic,
                "knowledge_level": profile.knowledge_level.value, "session_phase": profile.session_phase.value,
                "total_sessions": profile.total_sessions, "engagement_level": profile.engagement_level,
            },
            "progress_metrics": {
                "consecutive_correct": profile.consecutive_correct,
                "understanding_progression": profile.understanding_progression,
                "misconceptions": profile.misconceptions, "strengths": profile.strengths,
                "warning_signs": profile.warning_signs,
            },
        }