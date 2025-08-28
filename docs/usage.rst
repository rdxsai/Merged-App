Usage Guide
===========

This guide provides step-by-step instructions for using the Canvas Quiz Manager application.

Getting Started
--------------

1. **Access the Application**

   After starting the server, open your browser and navigate to `http://localhost:8080`

2. **Configure Canvas Integration**

   - Set up your Canvas API token in the environment variables
   - Configure the course ID and quiz ID
   - Use the configuration API to update settings if needed

3. **Fetch Questions from Canvas**

   - Click the "Fetch Questions from Canvas" button
   - This will retrieve all questions from the specified quiz
   - Questions will be displayed in a table format

Question Management
------------------

Creating Questions
~~~~~~~~~~~~~~~~~

1. **Navigate to New Question Page**

   - Click "Create New Question" from the main page
   - Or navigate to `/questions/new`

2. **Fill in Question Details**

   - **Question Text**: Enter the main question content
   - **Topic**: Select from predefined topics (accessibility, navigation, etc.)
   - **Tags**: Add comma-separated tags for categorization
   - **Learning Objective**: Associate with a learning objective
   - **Answer Options**: Add multiple choice answers with weights

3. **Save the Question**

   - Click "Save Question" to create the question
   - The question will be added to your local database

Editing Questions
~~~~~~~~~~~~~~~~

1. **Access Question Editor**

   - Click "Edit" next to any question in the main table
   - Or navigate to `/questions/{question_id}`

2. **Modify Question Content**

   - Update question text, topic, tags, or learning objectives
   - Modify answer options and their weights
   - Add or remove answer choices

3. **Save Changes**

   - Click "Save Question" to update the question
   - Changes are saved to the local database

Deleting Questions
~~~~~~~~~~~~~~~~~

1. **Delete from Main Page**

   - Click "Delete" next to the question you want to remove
   - Confirm the deletion

2. **Bulk Operations**

   - Use the checkboxes to select multiple questions
   - Perform bulk delete operations

AI Feedback Generation
---------------------

Generating Feedback
~~~~~~~~~~~~~~~~~~

1. **Select a Question**

   - Navigate to the question edit page
   - Or use the main page table

2. **Generate AI Feedback**

   - Click "Generate AI Feedback" button
   - The system will send the question to Azure OpenAI
   - Wait for the feedback generation to complete

3. **Review Generated Feedback**

   - General feedback will be added to the question
   - Answer-specific feedback will be added to each answer option
   - Review and edit the feedback as needed

4. **Save the Feedback**

   - The feedback is automatically saved with the question
   - You can edit the feedback manually if needed

System Prompt Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Access System Prompt Editor**

   - Navigate to `/system-prompt`
   - Or use the navigation menu

2. **Customize the Prompt**

   - Edit the system prompt to guide AI feedback generation
   - Include specific instructions for your educational context
   - Reference accessibility guidelines or learning objectives

3. **Test the Prompt**

   - Use the test functionality to verify prompt effectiveness
   - Generate sample feedback to validate the prompt

Vector Store and Semantic Search
-------------------------------

Creating Vector Store
~~~~~~~~~~~~~~~~~~~~

1. **Prepare Questions**

   - Ensure you have questions loaded in the system
   - Questions should have good content for embedding generation

2. **Generate Vector Store**

   - Navigate to the vector store creation endpoint
   - Click "Create Vector Store" or use the API
   - Wait for the embedding generation to complete

3. **Verify Creation**

   - Check the creation statistics
   - Verify that embeddings were generated successfully

Using Semantic Search
~~~~~~~~~~~~~~~~~~~~

1. **Access Chat Interface**

   - Navigate to `/chat`
   - The chat interface will use the vector store for RAG

2. **Ask Questions**

   - Type questions about your quiz content
   - The system will search for relevant questions
   - AI will provide answers based on retrieved context

3. **Review Retrieved Content**

   - The system shows which questions were retrieved
   - You can see the similarity scores
   - Context is automatically injected into the AI response

Chat Assistant Configuration
---------------------------

Customizing Chat System Prompt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Access Chat Prompt Editor**

   - Navigate to `/chat/system-prompt`
   - Edit the prompt that guides the chat assistant

2. **Configure Context Usage**

   - Modify how the system uses retrieved context
   - Add specific instructions for your use case
   - Include guidelines for response format

3. **Set Welcome Message**

   - Customize the welcome message shown to users
   - Explain the assistant's capabilities
   - Provide usage instructions

Learning Objectives Management
-----------------------------

Creating Learning Objectives
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Access Objectives Page**

   - Navigate to `/objectives`
   - View and manage learning objectives

2. **Add New Objectives**

   - Enter objective text
   - Select Bloom's taxonomy level
   - Set priority (low, medium, high)

3. **Organize Objectives**

   - Group related objectives
   - Set appropriate priority levels
   - Link objectives to questions

Associating with Questions
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Edit Question**

   - Open the question editor
   - Select a learning objective from the dropdown
   - Save the association

2. **Filter by Objectives**

   - Use objectives to organize and filter questions
   - Track coverage of learning objectives
   - Ensure comprehensive assessment

Advanced Features
----------------

Topic Classification
~~~~~~~~~~~~~~~~~~~

The system automatically classifies questions into topics:

- **Accessibility**: Screen readers, alt text, WCAG guidelines
- **Navigation**: Menus, links, breadcrumbs, sitemaps
- **Forms**: Input fields, labels, validation, submission
- **Media**: Images, video, audio, captions, transcripts
- **Color**: Contrast, visual design, appearance
- **Keyboard**: Focus, tab navigation, shortcuts
- **Content**: Text, headings, structure, semantics

Tag Management
~~~~~~~~~~~~~

1. **Add Tags to Questions**

   - Use comma-separated tags in question editor
   - Tags help with organization and filtering

2. **View All Tags**

   - The system shows existing tags as suggestions
   - Use consistent tagging conventions

3. **Filter by Tags**

   - Use tags to find related questions
   - Group questions by specific topics or concepts

Debugging and Troubleshooting
----------------------------

Debug Endpoints
~~~~~~~~~~~~~~

1. **Configuration Status**

   - Visit `/debug/config` to check configuration
   - Verify all required environment variables

2. **Ollama Connection**

   - Visit `/debug/ollama-test` to test Ollama
   - Ensure the embedding model is available

3. **Question Debug**

   - Visit `/debug/question/{id}` for specific question info
   - Check question structure and content

Common Issues
~~~~~~~~~~~~

1. **Canvas API Errors**

   - Verify API token and permissions
   - Check course and quiz IDs
   - Ensure network connectivity

2. **AI Generation Failures**

   - Check Azure OpenAI configuration
   - Verify system prompt is set
   - Review API quotas and limits

3. **Vector Store Issues**

   - Ensure Ollama is running
   - Check embedding model availability
   - Verify ChromaDB permissions

Best Practices
-------------

Question Design
~~~~~~~~~~~~~~

1. **Write Clear Questions**

   - Use clear, unambiguous language
   - Ensure questions test specific concepts
   - Include relevant context

2. **Provide Good Feedback**

   - Use AI-generated feedback as a starting point
   - Customize feedback for your specific context
   - Include educational explanations

3. **Organize Content**

   - Use consistent tagging
   - Associate with learning objectives
   - Group related questions

System Configuration
~~~~~~~~~~~~~~~~~~~

1. **Optimize Prompts**

   - Test system prompts with sample questions
   - Refine prompts based on output quality
   - Include specific educational guidelines

2. **Monitor Performance**

   - Check logs for errors and warnings
   - Monitor API usage and costs
   - Track vector store performance

3. **Regular Maintenance**

   - Update questions and feedback regularly
   - Refresh vector store when content changes
   - Backup important data
