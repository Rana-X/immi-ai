import requests
import json

def test_rag_system():
    """Test the RAG system's chat endpoint"""
    
    # Test server status
    print("\nTesting server status...")
    try:
        response = requests.get("http://localhost:8000/test")
        print(f"Server status: {response.json()}")
    except Exception as e:
        print(f"Error connecting to server: {str(e)}")
        return
    
    # Test questions
    test_questions = [
        "What are the requirements for an H1B visa?",
        "Tell me about F1 student visa",
        "hi"
    ]
    
    for question in test_questions:
        print(f"\nTesting question: {question}")
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status code: {response.status_code}")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_rag_system() 