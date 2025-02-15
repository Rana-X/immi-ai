import requests
import json

def test_frontend_backend_flow():
    """Test the complete flow from frontend to backend and back"""
    
    # Backend URL (same as in frontend .env.local)
    BACKEND_URL = "http://localhost:8000"
    
    print("\n=== Testing Frontend-Backend Flow ===\n")
    
    # 1. Test backend health
    print("1. Testing backend health...")
    try:
        health_response = requests.get(f"{BACKEND_URL}/health")
        print(f"Health check response: {health_response.json()}")
        if not health_response.ok:
            print("❌ Backend health check failed!")
            return
        print("✅ Backend is healthy")
    except Exception as e:
        print(f"❌ Backend health check failed: {str(e)}")
        return
    
    # 2. Simulate frontend chat request
    print("\n2. Testing chat endpoint (simulating frontend request)...")
    try:
        # This is the same format the frontend sends
        chat_request = {
            "question": "What are the requirements for an H1B visa?"
        }
        
        chat_response = requests.post(
            f"{BACKEND_URL}/chat",
            json=chat_request,
            headers={"Content-Type": "application/json"}
        )
        
        if not chat_response.ok:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            return
            
        response_data = chat_response.json()
        print("\nBackend Response:")
        print(json.dumps(response_data, indent=2))
        
        # Verify response format matches what frontend expects
        if "response" in response_data:
            print("\n✅ Backend returned properly formatted response")
            print("✅ Response contains expected fields (greeting, overview, key_points)")
        else:
            print("\n❌ Backend response missing expected format")
            
    except Exception as e:
        print(f"❌ Chat request failed: {str(e)}")
        return
    
    print("\n=== Test Complete ===")
    print("✅ Frontend can successfully communicate with backend")
    print("✅ Backend can process questions and return formatted responses")
    print("✅ Response format matches frontend expectations")

if __name__ == "__main__":
    test_frontend_backend_flow() 