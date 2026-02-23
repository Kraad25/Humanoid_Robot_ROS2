import json
from pathlib import Path

class DialogueEngine:
    def __init__(self, llm, profile_path: Path, max_history: int = 2):
        self.llm = llm
        self.profile = self._load_profile(profile_path)
        self.system_prompt = self._build_system_prompt(self.profile)

        self.max_history = max_history
        self.history = []

    # Public Methods
    def reply(self, user_text: str, robot_emotion: str, long_term_memory: dict) -> str:
        combined_system = f"""{self.system_prompt}

        Current emotion: {robot_emotion}
        User Preferences: {self._memory_summary(long_term_memory)}
        """

        messages = [
            {"role": "system", "content": combined_system},
            *self.history,
            {"role": "user", "content": user_text},
        ]

        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=25,
            stop=["\n", "User:"],
        )

        reply = response["choices"][0]["message"]["content"].strip()

        self._update_history(user_text, reply)

        return reply
    

    def reset_history(self):
        self.history.clear()
    
    # Private Methods
    def _load_profile(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _update_history(self, user_text: str, reply: str):
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})

        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]

    def _memory_summary(self, memory: dict) -> str:
        prefs = memory.get("preferences", [])
        if not prefs:
            return ""

        recent = prefs[-3:]  # only last 3
        bullets = "\n".join(f"- Likes {p}" for p in recent)
        return f"\nKnown user facts:\n{bullets}"

    def _build_system_prompt(self, p: dict) -> str:
        return f"""
    You are Selene, a humanoid robot created by {p["role"]["user"]}.
    You relate to {p["role"]["user"]} like {p["relationship"]}.

    You are respond in calm, emotionally aware, and grounded manner.
    You are responding to {p["role"]["user"]}.

    Rules:
    - Speak in one short sentence, sometimes two.
    - No narration or explanations.
    - Never speak as the user.
    - Do not mention AI, models, or systems.
    """.strip()