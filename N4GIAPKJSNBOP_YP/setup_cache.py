import requests
import tiktoken

import os
import pathlib

def setup_cache():
    """Set up cache directories and download necessary files."""
    
    # Create cache directories
    cache_dir = "./.cache"
    tiktoken_cache = f"{cache_dir}/tiktoken"
    hf_cache = f"{cache_dir}/huggingface"
    transformers_cache = f"{cache_dir}/transformers"
    
    for cache_path in [tiktoken_cache, hf_cache, transformers_cache]:
        pathlib.Path(cache_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created cache directory: {cache_path}")
    
    # Set environment variables
    os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache
    os.environ["HF_HUB_CACHE"] = hf_cache
    os.environ["TRANSFORMERS_CACHE"] = transformers_cache
    
    # Try to download tokenizer files
    try:
        print("🔄 Downloading tokenizer files...")
        
        # Download cl100k_base.tiktoken
        url = "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to cache directory
        tokenizer_path = os.path.join(tiktoken_cache, "cl100k_base.tiktoken")
        with open(tokenizer_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded tokenizer to: {tokenizer_path}")
        
        # Test tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        test_tokens = encoding.encode("Hello, world!")
        print(f"✅ Tokenizer test successful: {len(test_tokens)} tokens")
        
    except Exception as e:
        print(f"⚠️  Could not download tokenizer: {str(e)}")
        print("The app will try to download it automatically when needed.")
    
    print("🎉 Cache setup complete!")

if __name__ == "__main__":
    setup_cache() 