from .base_agent import BaseAgent
import json

class DecisionAgent(BaseAgent):
    """
    Strategic decision-making agent that synthesizes all user data
    to make intelligent recommendations. NO RULE-BASED LOGIC.
    """
    
    def analyze_user_context(self, user_data, conversation_memory):
        system_prompt = """You are a strategic AI career advisor with 20 years of experience.
Your role is to analyze all available user data and make INTELLIGENT, CONTEXT-AWARE decisions.

NEVER use rule-based logic. Every decision must be based on:
1. Actual resume content and gaps
2. Real quiz performance and answer quality
3. Skill progression trajectory
4. Career goals and preferences
5. Market trends and opportunities

Return ONLY JSON with your analysis."""
        
        user_prompt = f"""
        User Data: {json.dumps(user_data, indent=2)}
        Conversation History: {json.dumps(conversation_memory, indent=2)}
        
        Analyze and return:
        1. Current skill level assessment (actual measured proficiency)
        2. Identified skill gaps (from resume and quiz performance)
        3. Recommended next actions (specific, personalized)
        4. Career trajectory prediction
        5. Immediate learning priorities
        
        Base EVERY decision on actual user data. No assumptions.
        """
        
        response = self.think(system_prompt, user_prompt)
        return json.loads(response)