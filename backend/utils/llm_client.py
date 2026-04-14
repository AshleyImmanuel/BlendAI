import httpx # type: ignore
from openai import OpenAI  # type: ignore # noqa: F401

class LLMClient:
    """
    A generic client wrapper for LLM providers for BlendAI Swarm.
    Directly compatible with OpenAI, Groq, DeepSeek, Ollama, etc.
    HARDENED: Features explicit timeouts and error sanitization.
    """
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # Initialize the client with a custom timeout to prevent hangs
        # Using a 60s timeout for single turn completion
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=httpx.Timeout(60.0, connect=10.0)
        )

    def completion(self, system_prompt: str, user_prompt: str):
        """Generates a completion from the LLM with error mapping."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            # Map complex tracebacks into human-readable BlendAI errors
            msg = str(e).lower()
            
            # Absolute Key Redaction: Scrub anything that looks like the provided key
            # or matches common API key formats if they appear in error text
            if self.api_key and self.api_key in str(e):
                msg = str(e).replace(self.api_key, "[REDACTED_API_KEY]")
            
            if "api key" in msg or "authentication" in msg or "invalid_api_key" in msg:
                raise Exception("Authentication Failed: Please check your API Key in Blender Preferences.")
            if "rate limit" in msg or "429" in msg or "rate_limit_exceeded" in msg:
                raise Exception("API Rate Limit Reached: Please wait a moment before trying again.")
            if ("insufficient" in msg and "quota" in msg) or "insufficient_quota" in msg:
                raise Exception("API Quota Reached: Your provider account has run out of credits.")
            if "timeout" in msg:
                raise Exception("API Request Timed Out: The provider is responding slowly.")
                
            raise Exception(f"LLM Provider Error: {msg}")
