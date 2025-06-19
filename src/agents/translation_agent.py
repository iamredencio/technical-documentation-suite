"""
Translation Agent - Translates documentation to multiple languages
Built for the Google Cloud ADK Hackathon
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, Message
from ..services.ai_service import ai_service

class TranslationAgent(BaseAgent):
    """Agent responsible for translating documentation to multiple languages"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "TranslationAgent")
        self.supported_languages = {
            "spanish": {
                "code": "es",
                "name": "Spanish",
                "native_name": "Español"
            },
            "french": {
                "code": "fr", 
                "name": "French",
                "native_name": "Français"
            },
            "german": {
                "code": "de",
                "name": "German", 
                "native_name": "Deutsch"
            },
            "japanese": {
                "code": "ja",
                "name": "Japanese",
                "native_name": "日本語"
            },
            "portuguese": {
                "code": "pt",
                "name": "Portuguese",
                "native_name": "Português"
            }
        }
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        if message.type == "translate_documentation":
            return await self._translate_documentation(message)
        elif message.type == "get_supported_languages":
            return await self._get_supported_languages(message)
        else:
            self.logger.warning(f"Unknown message type: {message.type}")
            return None
    
    async def _get_supported_languages(self, message: Message) -> Message:
        """Return list of supported languages"""
        return Message(
            type="supported_languages",
            data={
                "languages": self.supported_languages,
                "total_count": len(self.supported_languages)
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    async def _translate_documentation(self, message: Message) -> Message:
        """Translate documentation to specified languages"""
        original_content = message.data.get("content", "")
        selected_languages = message.data.get("languages", [])
        project_context = message.data.get("project_context", {})
        
        self.logger.info(f"Translating documentation to {len(selected_languages)} languages")
        
        if not original_content:
            return Message(
                type="translation_error",
                data={"error": "No content provided for translation"},
                sender=self.agent_id,
                recipient=message.sender
            )
        
        if not selected_languages:
            return Message(
                type="translation_error", 
                data={"error": "No languages specified for translation"},
                sender=self.agent_id,
                recipient=message.sender
            )
        
        translations = {}
        translation_stats = {
            "original_length": len(original_content),
            "languages_processed": 0,
            "successful_translations": 0,
            "failed_translations": 0
        }
        
        for lang_code in selected_languages:
            if lang_code not in self.supported_languages:
                self.logger.warning(f"Unsupported language: {lang_code}")
                continue
                
            try:
                language_info = self.supported_languages[lang_code]
                self.logger.info(f"Translating to {language_info['name']} ({lang_code})")
                
                translated_content = await self._perform_translation(
                    original_content, 
                    language_info,
                    project_context
                )
                
                translations[lang_code] = {
                    "content": translated_content,
                    "language": language_info,
                    "word_count": len(translated_content.split()),
                    "character_count": len(translated_content),
                    "status": "success"
                }
                
                translation_stats["successful_translations"] += 1
                
            except Exception as e:
                self.logger.error(f"Translation to {lang_code} failed: {e}")
                translations[lang_code] = {
                    "content": "",
                    "language": self.supported_languages[lang_code],
                    "word_count": 0,
                    "character_count": 0,
                    "status": "failed",
                    "error": str(e)
                }
                translation_stats["failed_translations"] += 1
            
            translation_stats["languages_processed"] += 1
        
        return Message(
            type="translation_complete",
            data={
                "translations": translations,
                "original_content": original_content,
                "statistics": translation_stats,
                "ai_powered": ai_service.is_available()
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    async def _perform_translation(self, content: str, language_info: Dict[str, Any], project_context: Dict[str, Any]) -> str:
        """Perform the actual translation using AI service"""
        if not ai_service.is_available():
            return self._fallback_translation(content, language_info)
        
        try:
            # Use the proper AI service translate_content method
            translated_content = await ai_service.translate_content(
                content=content,
                target_language=language_info,
                context=project_context
            )
            return translated_content
            
        except Exception as e:
            self.logger.error(f"AI translation failed: {e}")
            return self._fallback_translation(content, language_info)
    
    def _fallback_translation(self, content: str, language_info: Dict[str, Any]) -> str:
        """Fallback translation when AI is not available"""
        language_name = language_info["name"]
        native_name = language_info["native_name"]
        
        fallback_content = f"""
# {language_name} Translation / {native_name}

**Note: This is a placeholder translation. AI translation service is not available.**

---

{content}

---

**Translation Status:** Placeholder content in English
**Target Language:** {language_name} ({native_name})
**AI Service:** Not available - showing original content

To enable proper translation, please configure the GEMINI_API_KEY environment variable.
"""
        return fallback_content
    
    def get_language_selection_options(self) -> List[Dict[str, Any]]:
        """Get language options formatted for UI selection"""
        return [
            {
                "value": lang_code,
                "label": f"{info['name']} ({info['native_name']})",
                "code": info['code'],
                "name": info['name'],
                "native_name": info['native_name']
            }
            for lang_code, info in self.supported_languages.items()
        ] 