from .resume_agent import ResumeAgent
from .quiz_agent import QuizAgent
from .career_agent import CareerAgent
from .job_match_agent import JobMatchAgent  # Change this from JobAgent to JobMatchAgent

class Orchestrator:

    def __init__(self):
        self.resume_agent = ResumeAgent()
        self.quiz_agent = QuizAgent()
        self.career_agent = CareerAgent()
        self.job_match_agent = JobMatchAgent()  # Change this

    # ================= Resume =================
    def handle_resume_analysis(self, resume_text):
        return self.resume_agent.analyze(resume_text)

    # ================= Quiz =================
    def handle_quiz_generation(self, resume_text, focus_skill=None, difficulty="medium"):
        return self.quiz_agent.generate_questions(resume_text, focus_skill, difficulty)

    def handle_quiz_evaluation(self, questions, answers):
        return self.quiz_agent.evaluate_answers(questions, answers)

    # ================= Career =================
    def handle_career_planning(self, resume_analysis, quiz_evaluation, memory_context=""):
        return self.career_agent.generate_plan(
            resume_analysis,
            quiz_evaluation,
            memory_context
        )

    # ================= Job Match =================
    def handle_job_matching(self, user_skills):  # Change parameter from (resume_analysis, skill_context) to just user_skills
        return self.job_match_agent.match_role(user_skills)  # Change this