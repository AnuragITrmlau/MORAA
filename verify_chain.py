from app.ai.image_generation_manager import ImageGenerationManager
from app.config import settings

m = ImageGenerationManager()
print("chain:", m.get_provider_chain())
print("openai model:", settings.OPENAI_IMAGE_MODEL)
print("gemini model:", settings.GEMINI_IMAGE_MODEL)
print("pfie enabled:", settings.PFIE_ENABLED)
