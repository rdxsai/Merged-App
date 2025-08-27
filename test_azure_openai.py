#!/usr/bin/env python3
"""
Azure OpenAI Connection Test Script

This script provides comprehensive testing for Azure OpenAI service connectivity
and functionality. It validates configuration, tests basic connectivity,
performs API calls, and simulates realistic quiz feedback generation scenarios.

The script is designed to help diagnose and troubleshoot Azure OpenAI integration
issues in the Canvas Quiz Manager application.

Features:
- Configuration validation and display
- Basic HTTP connectivity testing
- API endpoint testing with simple requests
- Realistic quiz feedback generation testing
- Detailed error reporting and debugging information

Author: Bryce Kayanuma <BrycePK@vt.edu>
Version: 0.1.0
"""

import os
import json
import asyncio
import httpx
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

def load_config() -> Dict[str, str]:
    """
    Load and validate Azure OpenAI configuration from environment variables.
    
    This function reads the required Azure OpenAI configuration from environment
    variables and provides default values where appropriate.
    
    Returns:
        Dict[str, str]: Configuration dictionary containing:
            - 'endpoint': Azure OpenAI endpoint URL
            - 'deployment_id': Model deployment ID
            - 'api_version': API version string
            - 'subscription_key': Azure subscription key
            
    Note:
        The function uses default values for endpoint and API version if not
        specified in environment variables.
    """
    config = {
        'endpoint': os.getenv(
            "AZURE_OPENAI_ENDPOINT", 
            "https://itls-openai-connect.azure-api.net"
        ),
        'deployment_id': os.getenv("AZURE_OPENAI_DEPLOYMENT_ID"),
        'api_version': os.getenv(
            "AZURE_OPENAI_API_VERSION", 
            "2023-12-01-preview"
        ),
        'subscription_key': os.getenv("AZURE_OPENAI_SUBSCRIPTION_KEY")
    }
    return config

def print_config(config: Dict[str, str]) -> None:
    """
    Print configuration details while masking sensitive data.
    
    This function displays the current Azure OpenAI configuration in a
    user-friendly format, masking the subscription key for security.
    
    Args:
        config (Dict[str, str]): Configuration dictionary from load_config()
        
    Note:
        The subscription key is masked to show only the last 4 characters
        for security purposes.
    """
    print("🔧 Configuration:")
    print(f"   Endpoint: {config['endpoint']}")
    print(f"   Deployment ID: {config['deployment_id']}")
    print(f"   API Version: {config['api_version']}")
    
    # Mask subscription key for security
    if config['subscription_key']:
        masked_key = ('*' * (len(config['subscription_key']) - 4) + 
                     config['subscription_key'][-4:])
        print(f"   Subscription Key: {masked_key}")
    else:
        print("   Subscription Key: NOT SET")
    print()

def validate_config(config: Dict[str, str]) -> bool:
    """
    Validate that all required Azure OpenAI configuration is present.
    
    This function checks that all required environment variables are set
    and provides helpful error messages for missing configuration.
    
    Args:
        config (Dict[str, str]): Configuration dictionary from load_config()
        
    Returns:
        bool: True if all required configuration is present, False otherwise
        
    Note:
        The function provides detailed error messages listing which
        environment variables are missing and what they should contain.
    """
    missing = []
    for key, value in config.items():
        if not value:
            missing.append(key.upper())
    
    if missing:
        print(f"❌ Missing required environment variables: "
              f"{', '.join(missing)}")
        print("\n📝 Required environment variables:")
        print("   AZURE_OPENAI_ENDPOINT")
        print("   AZURE_OPENAI_DEPLOYMENT_ID")
        print("   AZURE_OPENAI_API_VERSION "
              "(optional, defaults to 2023-12-01-preview)")
        print("   AZURE_OPENAI_SUBSCRIPTION_KEY")
        return False
    
    print("✅ All required configuration present")
    return True

async def test_basic_connection(config: Dict[str, str]) -> bool:
    """
    Test basic HTTP connectivity to the Azure OpenAI endpoint.
    
    This function performs a simple HTTP GET request to the base endpoint
    to verify that the service is reachable and responding.
    
    Args:
        config (Dict[str, str]): Configuration dictionary from load_config()
        
    Returns:
        bool: True if the endpoint is reachable, False otherwise
        
    Note:
        A 404 status code is considered successful as it indicates the
        endpoint is reachable but the base URL doesn't serve content.
    """
    print("🌐 Testing basic connection...")
    
    # Just test the base endpoint
    base_url = config['endpoint']
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 404:
                print("   ✅ Endpoint is reachable "
                      "(404 is expected for base URL)")
                return True
            elif response.status_code < 500:
                print("   ✅ Endpoint is reachable")
                return True
            else:
                print(f"   ❌ Server error: {response.status_code}")
                return False
                
    except httpx.ConnectError as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    except httpx.TimeoutException as e:
        print(f"   ❌ Connection timeout: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

async def test_api_endpoint(config: Dict[str, str]) -> bool:
    """
    Test the Azure OpenAI API endpoint with a simple chat completion request.
    
    This function sends a basic chat completion request to verify that the
    API is working correctly and can generate responses.
    
    Args:
        config (Dict[str, str]): Configuration dictionary from load_config()
        
    Returns:
        bool: True if the API call is successful, False otherwise
        
    Note:
        The function uses a simple test message to verify API functionality
        and displays the AI response for verification.
    """
    print("🤖 Testing Azure OpenAI API endpoint...")
    
    # Construct the full API URL
    url = (f"{config['endpoint']}/us-east/deployments/"
           f"{config['deployment_id']}/chat/completions"
           f"?api-version={config['api_version']}")
    print(f"   API URL: {url}")
    
    headers = {
        "Ocp-Apim-Subscription-Key": config['subscription_key'],
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", 
             "content": "Say 'Hello, this is a test!' and nothing else."}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    print(f"   Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ API call successful!")
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                # Extract the actual response content
                if 'choices' in result and result['choices']:
                    ai_response = result['choices'][0]['message']['content']
                    print(f"   🤖 AI Response: '{ai_response}'")
                
                return True
            else:
                print(f"   ❌ API call failed with status "
                      f"{response.status_code}")
                try:
                    error_content = response.json()
                    print(f"   Error details: "
                          f"{json.dumps(error_content, indent=2)}")
                except Exception:
                    print(f"   Error text: {response.text}")
                return False
                
    except httpx.HTTPStatusError as e:
        print(f"   ❌ HTTP error: {e}")
        print(f"   Response text: {e.response.text}")
        return False
    except httpx.TimeoutException as e:
        print(f"   ❌ Request timeout: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

async def test_quiz_feedback_scenario(config: Dict[str, str]) -> bool:
    """Test with a realistic quiz feedback scenario"""
    print("📝 Testing quiz feedback generation scenario...")
    
    url = f"{config['endpoint']}/us-east/deployments/{config['deployment_id']}/chat/completions?api-version={config['api_version']}"
    
    headers = {
        "Ocp-Apim-Subscription-Key": config['subscription_key'],
        "Content-Type": "application/json"
    }
    
    # Realistic quiz scenario payload
    system_prompt = "You are an expert educator creating helpful feedback for quiz questions. Generate constructive, educational feedback that helps students learn from their answers."
    
    user_message = """Please generate appropriate feedback for this quiz question:

Question Type: multiple_choice_question
Question Text: What is the capital of France?
Points Possible: 1.0

Answers:
1. London (Weight: 0) [✗ Incorrect]
2. Paris (Weight: 100.0) [✓ CORRECT]
3. Berlin (Weight: 0) [✗ Incorrect]
4. Madrid (Weight: 0) [✗ Incorrect]

Please provide feedback in the following format:
- Correct feedback: [feedback for when student gets the question right]
- Incorrect feedback: [feedback for when student gets the question wrong]
- General feedback: [general educational feedback about the topic]
"""
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Quiz feedback generation successful!")
                
                if 'choices' in result and result['choices']:
                    ai_response = result['choices'][0]['message']['content']
                    print(f"   🤖 Generated feedback:")
                    print(f"   {ai_response}")
                    
                    # Test parsing like the main app does
                    feedback = {"correct_comments": "", "incorrect_comments": "", "neutral_comments": ""}
                    lines = ai_response.split('\n')
                    current_section = None
                    
                    for line in lines:
                        line = line.strip()
                        if 'correct feedback:' in line.lower():
                            current_section = 'correct'
                            feedback['correct_comments'] = line.split(':', 1)[1].strip() if ':' in line else ""
                        elif 'incorrect feedback:' in line.lower():
                            current_section = 'incorrect'  
                            feedback['incorrect_comments'] = line.split(':', 1)[1].strip() if ':' in line else ""
                        elif 'general feedback:' in line.lower():
                            current_section = 'general'
                            feedback['neutral_comments'] = line.split(':', 1)[1].strip() if ':' in line else ""
                        elif line and current_section:
                            if current_section == 'correct':
                                feedback['correct_comments'] += " " + line
                            elif current_section == 'incorrect':
                                feedback['incorrect_comments'] += " " + line
                            elif current_section == 'general':
                                feedback['neutral_comments'] += " " + line
                    
                    print(f"   📊 Parsed feedback:")
                    print(f"      Correct: '{feedback['correct_comments']}'")
                    print(f"      Incorrect: '{feedback['incorrect_comments']}'")
                    print(f"      General: '{feedback['neutral_comments']}'")
                
                return True
            else:
                print(f"   ❌ Quiz feedback generation failed with status {response.status_code}")
                try:
                    error_content = response.json()
                    print(f"   Error details: {json.dumps(error_content, indent=2)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error in quiz feedback test: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Azure OpenAI Connection Test")
    print("=" * 50)
    print()
    
    # Load configuration
    config = load_config()
    print_config(config)
    
    # Validate configuration
    if not validate_config(config):
        print("\n❌ Configuration validation failed. Please check your .env file.")
        return
    
    print()
    
    # Test 1: Basic connection
    connection_ok = await test_basic_connection(config)
    print()
    
    # Test 2: API endpoint
    if connection_ok:
        api_ok = await test_api_endpoint(config)
        print()
        
        # Test 3: Quiz feedback scenario
        if api_ok:
            quiz_ok = await test_quiz_feedback_scenario(config)
            print()
            
            if quiz_ok:
                print("🎉 All tests passed! Azure OpenAI is working correctly.")
            else:
                print("⚠️  Basic API works but quiz feedback test failed.")
        else:
            print("❌ API endpoint test failed.")
    else:
        print("❌ Basic connection test failed.")
    
    print("\n" + "=" * 50)
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main())