import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Tuple
from datetime import datetime

class IncidentEmbedder:
    """
    Creates text embeddings for incident summaries using Sentence Transformers
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize embedder with pre-trained model
        
        Args:
            model_name: Sentence Transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def generate_summary(self, incident_dict) -> str:
        """
        Generate text summary from incident data
        
        Args:
            incident_dict: Dictionary with incident details
        
        Returns:
            Text summary suitable for embedding
        """
        event_type = incident_dict.get('event_type', 'unknown')
        event_cause = incident_dict.get('event_cause', 'unknown')
        corridor = incident_dict.get('corridor', 'unknown')
        priority = incident_dict.get('priority', 'low')
        vehicle_type = incident_dict.get('veh_type', 'unknown')
        clearance_time = incident_dict.get('clearance_time', 'unknown')
        zone = incident_dict.get('zone', 'unknown')
        
        summary = (
            f"{event_cause.replace('_', ' ')} incident on {corridor} in {zone} zone. "
            f"Event type: {event_type}, Priority: {priority}, "
            f"Vehicle type: {vehicle_type}. "
        )
        
        if clearance_time and clearance_time != 'unknown':
            summary += f"Resolved in {clearance_time} minutes."
        
        return summary
    
    def embed(self, text: str) -> np.ndarray:
        """
        Embed text using Sentence Transformer
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype('float32')
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple texts efficiently
        
        Args:
            texts: List of texts to embed
        
        Returns:
            Matrix of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype('float32')


class FAISSIndex:
    """
    FAISS-based vector database for storing and retrieving incident embeddings
    """
    
    def __init__(self, embedding_dim=384):
        """
        Initialize FAISS index
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.incident_ids = []  # Map index position to incident ID
        self.incident_summaries = []  # Store summaries
    
    def add(self, embedding: np.ndarray, incident_id: int, summary: str):
        """
        Add embedding to index
        
        Args:
            embedding: Embedding vector
            incident_id: ID of incident
            summary: Text summary of incident
        """
        # Ensure embedding is float32
        embedding = np.array([embedding], dtype='float32')
        
        self.index.add(embedding)
        self.incident_ids.append(incident_id)
        self.incident_summaries.append(summary)
    
    def add_batch(self, embeddings: np.ndarray, incident_ids: List[int], summaries: List[str]):
        """
        Add multiple embeddings at once
        
        Args:
            embeddings: Matrix of embeddings
            incident_ids: List of incident IDs
            summaries: List of summaries
        """
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        self.index.add(embeddings)
        self.incident_ids.extend(incident_ids)
        self.incident_summaries.extend(summaries)
    
    def search(self, embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float, str]]:
        """
        Search for similar incidents
        
        Args:
            embedding: Query embedding
            k: Number of results to return
        
        Returns:
            List of tuples (incident_id, distance, summary)
        """
        embedding = np.array([embedding], dtype='float32')
        
        distances, indices = self.index.search(embedding, min(k, len(self.incident_ids)))
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0 and idx < len(self.incident_ids):
                incident_id = self.incident_ids[idx]
                summary = self.incident_summaries[idx]
                similarity_score = 1 / (1 + distance)  # Convert distance to similarity
                results.append((incident_id, similarity_score, summary))
        
        return results
    
    def save(self, path='models/faiss_index.pkl'):
        """
        Save index to disk
        
        Args:
            path: Path to save index
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {
            'index': self.index,
            'incident_ids': self.incident_ids,
            'incident_summaries': self.incident_summaries,
            'embedding_dim': self.embedding_dim
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, path='models/faiss_index.pkl'):
        """
        Load index from disk
        
        Args:
            path: Path to load index from
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.index = data['index']
        self.incident_ids = data['incident_ids']
        self.incident_summaries = data['incident_summaries']
        self.embedding_dim = data['embedding_dim']
    
    def get_size(self) -> int:
        """Get number of incidents in index"""
        return len(self.incident_ids)


class RAGSystem:
    """
    Complete RAG system combining embedder and FAISS index
    """
    
    def __init__(self, embedding_dim=384):
        self.embedder = IncidentEmbedder()
        self.faiss_index = FAISSIndex(embedding_dim)
    
    def index_incident(self, incident_dict: Dict, incident_id: int):
        """
        Index a single incident
        
        Args:
            incident_dict: Dictionary with incident data
            incident_id: Incident ID
        """
        summary = self.embedder.generate_summary(incident_dict)
        embedding = self.embedder.embed(summary)
        self.faiss_index.add(embedding, incident_id, summary)
    
    def index_batch(self, incidents_list: List[Dict], incident_ids: List[int]):
        """
        Index multiple incidents
        
        Args:
            incidents_list: List of incident dictionaries
            incident_ids: List of incident IDs
        """
        summaries = [self.embedder.generate_summary(inc) for inc in incidents_list]
        embeddings = self.embedder.embed_batch(summaries)
        self.faiss_index.add_batch(embeddings, incident_ids, summaries)
    
    def retrieve_similar(self, incident_dict: Dict, k: int = 5) -> List[Dict]:
        """
        Retrieve similar incidents
        
        Args:
            incident_dict: Query incident dictionary
            k: Number of results
        
        Returns:
            List of similar incident information
        """
        summary = self.embedder.generate_summary(incident_dict)
        embedding = self.embedder.embed(summary)
        
        results = self.faiss_index.search(embedding, k)
        
        return [
            {
                'incident_id': incident_id,
                'similarity_score': similarity_score,
                'summary': summary
            }
            for incident_id, similarity_score, summary in results
        ]
    
    def save(self, embedder_path='models/embedder.pkl', index_path='models/faiss_index.pkl'):
        """Save RAG system"""
        self.faiss_index.save(index_path)
    
    def load(self, index_path='models/faiss_index.pkl'):
        """Load RAG system"""
        self.faiss_index.load(index_path)
    
    def get_index_size(self) -> int:
        """Get size of index"""
        return self.faiss_index.get_size()
