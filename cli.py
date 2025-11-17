import asyncio
import os

from _pytest.runner import TResult 
from question_app.api import vector_store
from question_app.core import config
from question_app.api.vector_store import ChromaVectorStoreService
from question_app.services.tutor.hybrid_system import HybridCrewAISocraticSystem


def run_cli():

    print("Initializing the Grounded Socratic Tutor CLI...")
    #1. Create an instance of our vector store service

    vector_service = ChromaVectorStoreService()
    azure_config = {
        "api_key" : config.AZURE_OPENAI_SUBSCRIPTION_KEY,
        "endpoint" : config.AZURE_OPENAI_ENDPOINT,
        "deployment_name" : config.AZURE_OPENAI_DEPLOYMENT_ID,
        "api_version" : config.AZURE_OPENAI_API_VERSION
    }

    cli_db_path = os.path.join("data" , "socratic_tutor_db")
    tutor_system = HybridCrewAISocraticSystem(
        azure_config=azure_config,
        vector_store_service=vector_service,
        db_path = cli_db_path
    )
    print("System initialized sucessfully")
    interactive_main_menu(tutor_system)


def interactive_main_menu(tutor : HybridCrewAISocraticSystem):
    while True:
        print("\n" + "=" * 35)
        print("HYBRID CREWAI SOCRATIC MENU")
        print("=" * 35)
        print("1. Create a new student")
        print("2. Conduct session with agent coordination")
        print("3. List students")
        print("0. Exit")

        choice = input("\nSelect option:").strip()
        if choice == "1":
            name = input("Student Name : ").strip()
            topic = input("Learning Topic ").strip()
            if name and topic:
                try:
                    result = tutor.create_student_profile(name , topic)
                    print(f"Student created : {result['name']} (ID: {result['student_id']})")
                except Exception as e:
                    print(f"Error : {e}")
        elif choice == "2":
            students = tutor.list_students()
            if not students:
                print("No existing students found. Please create one first")
                continue
            print("\nAvailable Students:")
            for i,s in enumerate(students , 1):
                print(f"{i}. {s['name']} - {s['topic']}")
            try:
                idx = int(input(f"Select student (1 - {len(students)}): ")) - 1
                if 0 <= idx < len(students):
                    student_id  = students[idx]["id"]
                    print(f"\n--Starting sessio with {students[idx]['name']}. Type quit to exit. ---")

                    while True:
                        response = input("You: ").strip()
                        if response.lower() == "quit":
                            break
                        result = asyncio.run(tutor.conduct_socratic_session(student_id , response))

                        if result.get("status") == "success_debug":
                            print(result["session_metadata"]["retrueved_context"])
                        else:
                            print(result.get("tutor_response" , "An error occured."))
                else:
                    print("Invalid Selection")
            except (ValueError , IndexError):
                print("Invalid Input. Please enter a No from the list")
        elif choice == "3":
            students = tutor.list_students()
            if students:
                print("\n--All Students--")
                for s in students:
                    print(f"- ID : {s['id']}, Name : {s['name']}, Topic : {s['topic']}")
            else:
                print("No students found")
        elif choice == "0":
            print("GoodBye")
            break
        else:
            print("Invalid Option. Please try again")        

if __name__ == "__main__":
    run_cli()