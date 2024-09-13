import os
from pinecone import Pinecone, ServerlessSpec
from app.services.encoder import encode_text
from app.core.config import settings

# Initialize Pinecone using the new method
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Ensure that the index exists, or create one if it doesn't
if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=settings.PINECONE_INDEX_NAME,
        dimension=384,  # Update this to match your vector dimension
        metric='cosine',  # Correct the metric name to 'cosine'
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Function to search documents
async def search_documents(query: str, top_k: int, threshold: float):

    # Get the Pinecone index
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    # Encode the query text into a vector
    query_vector = encode_text(query)

    # Perform the search with keyword arguments (not positional)
    results = index.query(
        vector=query_vector,  # The vector to search
        top_k=top_k,          # The number of top results to retrieve
        include_metadata=True  # Include metadata in the response
    )

    # Filter the results based on the threshold score
    filtered_results = [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        for match in results["matches"]
        if match["score"] >= threshold  # Filter results by threshold
    ]

    return filtered_results
