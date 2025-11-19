### Requirement 2

**User Story:** As an educator, I want to create, edit, view, and delete questions and learning objectives separately, so that I can maintain and customize my educational content with flexible associations.

**Acceptance Criteria**

1. THE Socratic_Tutor_System SHALL provide separate CRUD_Interface components for managing questions and Learning_Objectives (e.g., question_list.html, question_edit.html, objective_list.html).

2. THE Socratic_Tutor_System SHALL display questions and Learning_Objectives in paginated lists.

3. THE Socratic_Tutor_System SHALL display total record count, total page count, and current page number for list views.

4. THE Socratic_Tutor_System SHALL allow associating multiple Learning_Objectives with a single question and associating a single Learning_Objective with multiple questions.

5. THE Socratic_Tutor_System SHALL store Learning_Objective associations as metadata within the Vector_Database for enhanced similarity search.

6. WHEN deleting questions or objectives, THE Socratic_Tutor_System SHALL require confirmation.

7. THE Socratic_Tutor_System SHALL require educators to navigate to a separate edit view to edit questions.

8. WHEN viewing/editing a question, THE Socratic_Tutor_System SHALL visually indicate which answer option is marked as correct.

9. WHEN editing a question, THE Socratic_Tutor_System SHALL allow the educator to change which answer option is marked as correct (e.g., using radio buttons).

10. THE Socratic_Tutor_System SHALL visually highlight questions that are not associated with any Learning_Objectives in the question list view with a "⚠️" warning icon.

11. THE Socratic_Tutor_System SHALL visually highlight Learning_Objectives that are not associated with any questions in the objectives list view with a "⚠️" warning icon.

12. THE Socratic_Tutor_System SHALL allow educators to delete Learning_Objectives and Questions individually.


### Requirement 4

**User Story:** As an educator, I want to generate AI-powered feedback for questions and answers, so that I can enhance the educational value of my content with personalized explanations.

**Acceptance Criteria**
1. THE Socratic_Tutor_System SHALL provide an interface for generating feedback for individual questions using the AI_Response_Generator, located within the existing question_edit.html page.

2. WHEN generating feedback for incorrect answers, THE AI_Response_Generator SHALL create socratic questions that guide thinking without revealing the correct answer.

3. WHEN generating feedback for correct answers, THE AI_Response_Generator SHALL explain why the answer is correct and why each incorrect option is wrong.

4. THE Rich_Text_Editor SHALL allow editing of feedback for each individual answer.

5. THE Socratic_Tutor_System SHALL allow educators to mark feedback for each individual answer as approved (e.g., via a simple checkbox).

6. WHEN an educator requests feedback generation for a question, THE Socratic_Tutor_System SHALL regenerate feedback only for answers that are not marked as approved.

7. THE Socratic_Tutor_System SHALL provide a "Generate All Unapproved" button on the question edit page that generates feedback for all unapproved answers for that specific question.


### Requirement 5

**User Story:** As a student, I want to interact with the tutor through a conversational chatbot interface, so that I can have an engaging and natural learning experience.

#### Acceptance Criteria

1. THE Socratic_Tutor_System SHALL provide a conversational chat interface that responds to natural language input

2. WHEN a student starts a session, THE Socratic_Tutor_System SHALL greet the student and explain the learning process

3. THE Socratic_Tutor_System SHALL use similarity search to find relevant content for contextual responses

4. THE Socratic_Tutor_System SHALL engage students through socratic questioning techniques to promote critical thinking

5. THE Socratic_Tutor_System SHALL maintain conversation context throughout the learning session

6. WHEN a student struggles after multiple attempts or explicitly requests the answer, THE Socratic_Tutor_System SHALL provide the correct answer with explanation

7. THE Socratic_Tutor_System SHALL display messages in conversation bubbles with tutor messages aligned left and student messages aligned right

8. THE Socratic_Tutor_System SHALL display timestamps and avatars for each message

9. THE Socratic_Tutor_System SHALL provide a multi-line text input field that expands up to 5 lines

10. THE Socratic_Tutor_System SHALL display a typing indicator when the tutor is generating a response

11. THE Socratic_Tutor_System SHALL auto-scroll the message area to the bottom when new messages are added

12. THE Socratic_Tutor_System SHALL provide a "New Conversation" button to start a fresh conversation

13. THE Socratic_Tutor_System SHALL display a progress panel alongside the chat showing the student's learning objective mastery

14. THE Socratic_Tutor_System SHALL make the progress panel collapsible on mobile devices


### Requirement 7

**User Story:** As an educator, I want to manually create learning objectives and use AI to help me build questions for them, so that I can establish the core educational goals for my curriculum.

### Acceptance Criteria

1. THE Socratic_Tutor_System SHALL allow educators to manually create Learning_Objectives by entering the objective text via a simple form on the objective_list.html page.

2. WHEN an educator creates a Learning_Objective, THE Socratic_Tutor_System SHALL check for semantic similarity with existing objectives to help prevent duplicates.

3. WHEN an objective is created, THE Socratic_Tutor_System SHALL store it in the learning_objectives table in the Unified_DB.

4. THE Socratic_Tutor_System SHALL allow educators to automatically generate questions for Learning_Objectives that are not associated with any questions (e.g., via a "Generate Question" button on the objective_list.html page).


### Requirement 8

**User Story:** As an educator, I want AI-powered assistance to find or create learning objectives for questions, so that I can efficiently associate questions with appropriate educational goals.

**Acceptance Criteria**

1. WHEN a question has no associated Learning_Objectives, THE Socratic_Tutor_System SHALL display a warning banner in the question edit view.

2. THE Socratic_Tutor_System SHALL provide a "Suggest Objective" button that uses the AI_Response_Generator to find matching existing objectives.

3. WHEN suggesting objectives, THE Socratic_Tutor_System SHALL analyze the question and rank existing objectives by match score.

4. THE Socratic_Tutor_System SHALL display the top 3-5 matching objectives with match score badges when matches are found.

5. THE Socratic_Tutor_System SHALL allow educators to select one or more suggested objectives to associate with the question.

6. WHEN match scores are below 60% confidence, THE Socratic_Tutor_System SHALL indicate that no good matches were found.

7. THE Socratic_Tutor_System SHALL provide a "Generate New Objective" button that uses the AI_Response_Generator to create a new objective based on the question.

8. WHEN generating a new objective, THE Socratic_Tutor_System SHALL allow educators to review and edit the generated objective text before creating it.

9. WHEN a new objective is created and associated, THE Socratic_Tutor_System SHALL make it available for association with other questions.

10. THE Socratic_Tutor_System SHALL automatically save the question with new objective associations after the educator confirms the selection.

11. THE Socratic_Tutor_System SHALL ensure only one modal dialog is open at a time, automatically closing previous modals when opening a new one.






