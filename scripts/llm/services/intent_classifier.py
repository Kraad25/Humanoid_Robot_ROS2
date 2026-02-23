class IntentClassifier:
    # Public Methods    
    def classify(self, user_input: str) -> dict:
        text = user_input.lower()
        words = text.split()

        # Simple keyword rules
        if any(w in words for w in ["hello", "hi", "hey"]):
            return {"intent": "greeting", "emotion": "happy"}

        if "?" in text:
            return {"intent": "question", "emotion": "neutral"}

        if any(w in text for w in ["sad", "tired", "under the weather"]):
            return {"intent": "emotion_share", "emotion": "sad"}

        if any(w in words for w in ["happy", "excited"]):
            return {"intent": "emotion_share", "emotion": "happy"}

        if text in ["bye", "shutdown", "sleep"]:
            return {"intent": "shutdown", "emotion": "neutral"}

        return {"intent": "idle_chat", "emotion": "neutral"}