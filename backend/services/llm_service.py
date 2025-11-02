from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import logging
from config import settings
from services.logging_config import logger


class LLMService:
    def __init__(self):
        self.model_name = settings.model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.generator = None
        self._load_model()
    
    def _load_model(self):
        """Загрузить модель"""
        try:
            logger.info(f"Loading model {self.model_name} on {self.device}...")
            
            # Используем pipeline для упрощения
            self.generator = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if self.device == "cuda" else -1,
                model_kwargs={"torch_dtype": torch.float16 if self.device == "cuda" else torch.float32}
            )
            
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback на более легкую модель
            try:
                logger.info("Trying fallback model...")
                self.model_name = "gpt2"
                self.generator = pipeline(
                    "text-generation",
                    model=self.model_name,
                    device=-1
                )
            except Exception as e2:
                logger.error(f"Failed to load fallback model: {e2}")
                raise
    
    def generate_response(
        self,
        question: str,
        context_chunks: List[Dict],
        max_length: int = 512,
        temperature: float = 0.7
    ) -> str:
        """Генерировать ответ на основе вопроса и контекста"""
        
        # Формируем промпт с контекстом
        context_text = "\n".join([
            f"- {chunk['text']}" for chunk in context_chunks[:5]
        ])
        
        prompt = f"""На основе предоставленной информации ответь на вопрос пользователя.
Если информации недостаточно, скажи об этом честно.

Информация:
{context_text}

Вопрос: {question}

Ответ:"""
        
        try:
            # Генерируем ответ
            outputs = self.generator(
                prompt,
                max_length=max_length,
                temperature=temperature,
                num_return_sequences=1,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            
            generated_text = outputs[0]["generated_text"]
            
            # Извлекаем только ответ (после "Ответ:")
            if "Ответ:" in generated_text:
                answer = generated_text.split("Ответ:")[-1].strip()
            else:
                answer = generated_text[len(prompt):].strip()
            
            return answer
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Извините, произошла ошибка при генерации ответа. Попробуйте переформулировать вопрос."
