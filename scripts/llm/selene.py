import os
import json
import shutil

from pathlib import Path
from llama_cpp import Llama

from services.intent_classifier import IntentClassifier
from services.dialogue_engine import DialogueEngine


class Selene:
    def __init__(self):
        root = Path(__file__).parent

        self.model_path = root / "models" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
        self.profile_path = root / "profile" / "Selene.json"
        self.schema_path = root / "schema" / "intent.json"
        self.memory_path = root / "schema" / "memory.json"

        if not self.profile_path.exists():
            shutil.copy(root / "profile" / "Selene.template.json", self.profile_path)

        if not self.memory_path.exists():
            shutil.copy(root / "schema" / "memory.template.json", self.memory_path)
            
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=250,
            n_threads=1,
            use_mlock=False,
            use_mmap=True,
            temperature=0.2,
            top_p=0.85,
            repeat_penalty=1.15,
            verbose=False,
            logits_all=False
        )

        # Gesture mappings (head + arms only)
        self.intent_to_gestures = {
            "greeting": ["wave_hand"],
            "idle_chat": ["idle_hand_movement"],
            "confirmation": ["nod"],
            "question": ["head_tilt"],
            "emotion_share": ["nod"],
            "shutdown": ["lower_head"]
        }

        self.classifier = IntentClassifier()
        self.dialogue = DialogueEngine(llm=self.llm, profile_path=self.profile_path)

        self.memory = self._load_memory()
        self.current_emotion = "neutral"


    # Public Methods
    def handle_input(self, user_text: str) -> dict:
        classification = self.classifier.classify(user_text)

        intent = classification["intent"]
        new_emotion = classification["emotion"]

        if new_emotion != "neutral":
            self.current_emotion = new_emotion

        emotion = self.current_emotion

        speech = self.dialogue.reply(
            user_text=user_text,
            robot_emotion=emotion,
            long_term_memory=self.memory,
        )

        self._extract_long_term_memory(user_text)
        gestures = self._select_gestures(intent)

        ros_return ={
            "intent": intent,
            "gesture": gestures,
            "speech": speech,
        }

        return ros_return

    # Private Methods
    def _load_memory(self) -> dict:
        with open(self.memory_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _save_memory(self):
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

    def _extract_long_term_memory(self, user_text: str):
        text = user_text.lower()

        if "i really like" in text:
            pref = text.split("i really like", 1)[1].strip()
            if pref not in self.memory["preferences"]:
                self.memory["preferences"].append(pref)
                self._save_memory()

    def _select_gestures(self, intent: str) -> list[str]:        
        return self.intent_to_gestures.get(intent, [])
