"""
Model caching system to prevent reloading AI models on every request
"""
import logging
import time
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ModelCache:
    """Singleton class to cache AI models and prevent reloading"""
    _instance = None
    _openai_client = None
    _embedding_model = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_models()
            self._initialized = True
    
    def _initialize_models(self):
        """Initialize models only once"""
        try:
            print("🔄 Initializing models (this should only happen once)...")
            start_time = time.time()
            
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
            
            if api_key and use_openai:
                try:
                    import openai
                    self._openai_client = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI client cached successfully")
                    print("✅ Client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
                    self._openai_client = None
                    print(f"❌ Client failed: {e}")
            else:
                logger.warning("OpenAI not enabled or API key not found")
                self._openai_client = None
                print("⚠️  Service not enabled")
            
            # Initialize embedding model
            try:
                from sentence_transformers import SentenceTransformer
                print("🔄 Loading embedding model (this may take a moment)...")
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("SentenceTransformer model cached successfully")
                print("✅ Embedding model loaded")
            except ImportError:
                logger.warning("Sentence transformers not available")
                self._embedding_model = None
                print("⚠️  Embedding service not available")
            except Exception as e:
                logger.error(f"Failed to initialize SentenceTransformer: {e}")
                self._embedding_model = None
                print(f"❌ Embedding model failed: {e}")
            
            end_time = time.time()
            print(f"🎯 Initialization completed in {end_time - start_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Error initializing model cache: {e}")
            print(f"❌ Cache initialization failed: {e}")
    
    @property
    def openai_client(self):
        """Get cached OpenAI client"""
        return self._openai_client
    
    @property
    def embedding_model(self):
        """Get cached embedding model"""
        return self._embedding_model
    
    def is_ready(self) -> bool:
        """Check if models are ready"""
        return self._openai_client is not None or self._embedding_model is not None

# Global model cache instance
model_cache = ModelCache()
