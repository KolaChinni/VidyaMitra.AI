from .base_agent import BaseAgent

class PlannerAgent(BaseAgent):

    def create_career_plan(self, resume_analysis, quiz_evaluation):
        system_prompt = """
        You are an expert AI Career Strategist.

        Based on resume analysis and skill evaluation:
        - Refine the target role
        - Identify skill gaps
        - Create a 3-month structured roadmap
        - Suggest weekly milestones
        - Suggest 2-3 practical projects
        - Suggest certifications
        - Suggest portfolio improvements
        - Suggest interview preparation strategy

        Make it structured and professional.
        """

        user_prompt = f"""
        Resume Analysis:
        {resume_analysis}

        Quiz Evaluation:
        {quiz_evaluation}
        """

        return self.think(system_prompt, user_prompt)
