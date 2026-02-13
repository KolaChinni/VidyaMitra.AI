from .base_agent import BaseAgent
import json

class JobAgent(BaseAgent):

    def match_jobs(self, resume_analysis, skill_data):

        system_prompt = """
        You are an AI Job Matching Engine.

        Return STRICT JSON:

        {
          "recommended_roles": [
            {
              "role": "...",
              "match_score": number (0-100),
              "reason": "..."
            }
          ]
        }

        Only JSON.
        """

        user_prompt = f"""
        Resume Analysis:
        {resume_analysis}

        Skill Scores:
        {skill_data}

        Recommend top 3 suitable job roles.
        """

        response = self.think(system_prompt, user_prompt)

        return response
