import json
import re
from .base_agent import BaseAgent

class CareerAgent(BaseAgent):

    def generate_plan(self, resume_analysis, quiz_evaluation, memory_context=""):
        system_prompt = """You are a strategic career planner with expertise in:
- Tech industry trends (2024-2026)
- Salary negotiations
- Career progression paths
- Skill development strategies
- Personal branding

Your plans must be:
1. Realistic - achievable in given timeframe
2. Specific - exact technologies, courses, projects
3. Strategic - considering market demand
4. Personalized - based on their unique profile
5. Adaptive - with alternative paths

Think like a VP of Engineering mentoring their best engineer."""

        # Convert inputs to readable format
        resume_str = json.dumps(resume_analysis, indent=2) if isinstance(resume_analysis, dict) else str(resume_analysis)
        quiz_str = json.dumps(quiz_evaluation, indent=2) if isinstance(quiz_evaluation, dict) else str(quiz_evaluation)
        
        user_prompt = f"""
Create a comprehensive 6-month career acceleration plan.

Candidate Profile:
{resume_str[:1500]}

Recent Performance:
{quiz_str[:1000]}

{memory_context[:500]}

Return a detailed plan in this EXACT JSON format:
{{
    "career_path": "Specific title → Next title → Future title",
    "summary": "2-3 sentence personalized summary",
    "steps": [
        {{
            "title": "Week 1-2: Specific focus area",
            "description": "Detailed description of what to learn and why",
            "skills": ["specific skill 1", "skill 2"],
            "timeline": "2 weeks",
            "resources": ["exact resource 1", "resource 2"],
            "success_metric": "How to measure completion",
            "difficulty": "Easy/Medium/Hard"
        }}
    ],
    "recommendations": [
        "specific recommendation 1",
        "specific recommendation 2"
    ],
    "resources": [
        {{
            "title": "exact course/book name",
            "type": "Course/Book/Article",
            "duration": "time to complete",
            "provider": "provider name",
            "cost": "Free/Paid",
            "priority": "High/Medium/Low",
            "reason": "why this specific resource"
        }}
    ],
    "milestones": [
        {{"month": 1, "goal": "specific goal", "verification": "how to prove completion"}}
    ],
    "estimated_salary_growth": {{
        "current": "range",
        "6months": "range",
        "1year": "range",
        "2years": "range"
    }},
    "alternative_paths": [
        "alternative career direction 1",
        "alternative career direction 2"
    ],
    "networking_strategy": "Specific people/events to connect with",
    "personal_branding": "How to build online presence",
    "interview_timeline": "When to start applying",
    "negotiation_tips": "Specific salary negotiation advice"
}}

Make it extremely specific and actionable. Include exact technologies, platforms, and timelines.
"""
        
        response = self.think(system_prompt, user_prompt)
        
        try:
            # Clean and parse
            cleaned = response.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
            if json_match:
                cleaned = json_match.group(1)
            
            plan = json.loads(cleaned)
            
            # Validate structure
            if "steps" not in plan or len(plan["steps"]) < 3:
                plan["steps"] = self._generate_default_steps()
            
            return plan
            
        except Exception as e:
            print(f"Career planning failed, generating AI plan: {e}")
            
            # Dynamically generate career plan using AI
            try:
                # Extract key info
                resume_text = resume_analysis.get("feedback", "") if isinstance(resume_analysis, dict) else str(resume_analysis)
                quiz_score = 0
                if isinstance(quiz_evaluation, dict):
                    quiz_score = quiz_evaluation.get("overall_score", 75)
                
                # Generate personalized steps
                steps = []
                for i, focus in enumerate(["Foundations", "Advanced Skills", "Projects", "Interview Prep", "Job Search"]):
                    step_title = self.think(f"Create a 2-week career step title for {focus} based on: {resume_text[:200]}", "")
                    step_desc = self.think(f"Write detailed description for {step_title}", "")
                    step_skills = self.think(f"List 3 skills for {step_title} as JSON array", "")
                    
                    try:
                        skills = json.loads(step_skills) if step_skills.startswith('[') else [focus, "Technical Skills", "Best Practices"]
                    except:
                        skills = [focus, "Practical Application", "Industry Standards"]
                    
                    steps.append({
                        "title": step_title[:50] if len(step_title) > 50 else step_title,
                        "description": step_desc[:200] if len(step_desc) > 200 else step_desc,
                        "skills": skills[:3],
                        "timeline": f"Week {i*2+1}-{i*2+2}",
                        "resources": [self.think(f"Suggest one resource for {step_title}", "")],
                        "success_metric": f"Complete {focus.lower()} project",
                        "difficulty": "Medium"
                    })
                
                return {
                    "career_path": self.think(f"Suggest career progression path for: {resume_text[:200]}", ""),
                    "summary": self.think(f"Write 2-sentence career summary", ""),
                    "steps": steps[:5],
                    "recommendations": [
                        self.think("Generate career recommendation 1", ""),
                        self.think("Generate career recommendation 2", ""),
                        self.think("Generate career recommendation 3", "")
                    ],
                    "resources": [
                        {
                            "title": self.think("Recommend a specific course", ""),
                            "type": "Course",
                            "duration": "4 weeks",
                            "provider": "Coursera/Udemy",
                            "cost": "Free/Paid",
                            "priority": "High",
                            "reason": self.think("Why this course?", "")
                        }
                    ],
                    "milestones": [
                        {"month": 1, "goal": self.think("1 month career goal", ""), "verification": "Project completion"},
                        {"month": 3, "goal": self.think("3 month career goal", ""), "verification": "Certification"},
                        {"month": 6, "goal": self.think("6 month career goal", ""), "verification": "Job offer"}
                    ],
                    "estimated_salary_growth": {
                        "current": "₹12-18L",
                        "6months": "₹15-22L",
                        "1year": "₹20-28L",
                        "2years": "₹25-35L"
                    }
                }
            except Exception as e2:
                print(f"AI fallback also failed: {e2}")
                return self._generate_default_steps()
    
    def _generate_default_steps(self):
        """Last resort AI-generated steps"""
        return {
            "career_path": "Software Engineer → Senior Engineer → Tech Lead",
            "summary": self.think("Write a generic but encouraging career summary", ""),
            "steps": [
                {
                    "title": self.think("Week 1-2: First career step", ""),
                    "description": self.think("Describe first step", ""),
                    "skills": [self.think("Skill 1", ""), self.think("Skill 2", ""), self.think("Skill 3", "")],
                    "timeline": "2 weeks"
                },
                {
                    "title": self.think("Week 3-4: Second career step", ""),
                    "description": self.think("Describe second step", ""),
                    "skills": [self.think("Skill 1", ""), self.think("Skill 2", ""), self.think("Skill 3", "")],
                    "timeline": "2 weeks"
                },
                {
                    "title": self.think("Week 5-6: Third career step", ""),
                    "description": self.think("Describe third step", ""),
                    "skills": [self.think("Skill 1", ""), self.think("Skill 2", ""), self.think("Skill 3", "")],
                    "timeline": "2 weeks"
                }
            ],
            "recommendations": [
                self.think("Recommendation 1", ""),
                self.think("Recommendation 2", ""),
                self.think("Recommendation 3", "")
            ]
        }