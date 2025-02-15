import pinecone

# Pinecone credentials
api_key = "pcsk_73bNrj_7YwqkwP76jvEyMy3aU7Z5eASbRA3Gd9CbLfzW96sewVYAUhZgWjq5K6U4prdk2n"
environment = "us-east-1"

print(f"Environment: {environment}")
print(f"API Key: {api_key[:10]}...")  # Only print first 10 chars for security

try:
    # Initialize Pinecone
    pc = pinecone.Pinecone(api_key=api_key)
    
    # List indexes
    print("\nListing indexes:")
    indexes = pc.list_indexes()
    print(f"Available indexes: {indexes.names() if indexes else 'No indexes found'}")
    
except Exception as e:
    print(f"\nError: {str(e)}") 