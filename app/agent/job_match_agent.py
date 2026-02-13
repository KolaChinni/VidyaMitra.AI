import json
import re
from .base_agent import BaseAgent
from .role_profiles import ROLE_PROFILES

class JobMatchAgent(BaseAgent):

    def match_role(self, user_skills):
        """
        Use AI to intelligently match skills to jobs, considering:
        - Skill transferability
        - Industry demand
        - Career progression
        - Company preferences
        """
        
        # Convert skills dict to readable format
        skills_text = "\n".join([f"- {skill}: {score}/100" for skill, score in user_skills.items()])
        
        system_prompt = """You are an AI career advisor at LinkedIn with access to real-time job market data.
Your task is to match candidates with the best job opportunities based on their skills.

Consider:
1. Skill transferability (e.g., React dev can learn Vue quickly)
2. Current market demand
3. Career growth potential
4. Salary benchmarks
5. Company culture fit
6. Remote work opportunities

Be realistic but optimistic in matches."""

        user_prompt = f"""
Candidate Skills Profile:
{skills_text if skills_text else "Early career candidate with foundational skills"}

Based on these skills, generate 5-8 job matches in this EXACT JSON format:
[
    {{
        "title": "Specific job title",
        "company": "Real company name that fits their profile",
        "location": "Specific city or Remote",
        "salary": "Realistic salary range in ₹",
        "match_score": 0-100,
        "required_skills": ["skill1", "skill2"],
        "matched_skills": ["skill1", "skill2"],
        "missing_skills": ["skill3", "skill4"],
        "description": "Detailed job description with responsibilities",
        "type": "Full-time/Contract/Remote",
        "benefits": ["benefit1", "benefit2"],
        "experience_level": "Years of experience needed",
        "growth_potential": "Career progression at this company",
        "interview_difficulty": "Easy/Medium/Hard",
        "remote_policy": "Fully remote/Hybrid/On-site",
        "industry": "Tech/Finance/Healthcare/etc"
    }}
]

Make matches realistic and personalized. Don't give everyone Google/Microsoft.
Consider Indian job market and companies.
"""

        response = self.think(system_prompt, user_prompt)
        
        try:
            # Clean and parse JSON
            cleaned = response.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
            if json_match:
                cleaned = json_match.group(1)
            
            matches = json.loads(cleaned)
            
            # Ensure it's a list
            if isinstance(matches, list):
                # Sort by match score
                matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
                return matches[:8]  # Return top 8
            elif isinstance(matches, dict) and "jobs" in matches:
                return matches["jobs"][:8]
            else:
                return matches[:8] if isinstance(matches, list) else []
                
        except Exception as e:
            print(f"AI job matching failed, using intelligent fallback: {e}")
            
            # If AI fails, use ROLE_PROFILES but with AI-generated descriptions
            results = []
            for role, requirements in list(ROLE_PROFILES.items())[:5]:
                # Calculate match score
                total = 0
                matched = []
                missing = []
                
                for skill, req_score in requirements.items():
                    user_score = user_skills.get(skill, 0)
                    if user_score >= req_score:
                        total += 100
                        matched.append(skill)
                    else:
                        # Partial credit for related skills
                        similarity = self._calculate_skill_similarity(skill, user_skills.keys())
                        total += (user_score / req_score) * 70 + similarity * 30
                        missing.append(skill)
                
                match_score = min(98, int(total / len(requirements))) if requirements else 70
                
                # Use AI to generate job description
                try:
                    desc_prompt = f"Write a 2-sentence job description for {role} position, focusing on {matched[0] if matched else 'growth'}."
                    description = self.think("Brief job description writer.", desc_prompt)
                except:
                    description = f"Join our team as a {role}. You'll work on challenging problems and grow your career."
                
                results.append({
                    "title": role,
                    "company": self._get_company_for_role(role, user_skills),
                    "location": self._get_location_for_role(role),
                    "salary": self._get_salary_for_role(role, match_score),
                    "match_score": match_score,
                    "score": match_score,
                    "required_skills": list(requirements.keys()),
                    "matched_skills": matched[:5],
                    "missing_skills": missing[:5],
                    "description": description,
                    "type": "Full-time",
                    "benefits": ["Health Insurance", "Flexible Hours", "Learning Budget"],
                    "experience_level": f"{max(1, int(match_score/20))}-{max(2, int(match_score/15))} years",
                    "growth_potential": "Fast track to senior role with strong performance",
                    "interview_difficulty": "Medium" if match_score > 70 else "Hard",
                    "remote_policy": "Hybrid",
                    "industry": "Technology"
                })
            
            results.sort(key=lambda x: x["match_score"], reverse=True)
            return results

    def _calculate_skill_similarity(self, required_skill, user_skills_list):
        """Calculate similarity between skills (simplified)"""
        # This could be enhanced with embeddings, but keeping it simple
        related_skills = {
            "python": ["django", "flask", "data science", "ml", "ai", "backend"],
            "javascript": ["react", "vue", "angular", "node", "frontend", "typescript"],
            "java": ["spring", "android", "backend", "enterprise"],
            "react": ["javascript", "frontend", "vue", "angular", "ui"],
            "aws": ["cloud", "azure", "devops", "docker", "kubernetes"],
        }
        
        for user_skill in user_skills_list:
            if user_skill.lower() == required_skill.lower():
                return 1.0
            if required_skill.lower() in related_skills:
                if user_skill.lower() in related_skills[required_skill.lower()]:
                    return 0.7
        return 0.3

    def _get_company_for_role(self, role, skills):
        """Dynamically select company based on role and skills"""
        companies = {
            "Software Engineer": ["Google", "Microsoft", "Amazon", "Flipkart", "Uber"],
            "Frontend Developer": ["Adobe", "Zomato", "Swiggy", "Booking.com"],
            "Data Scientist": ["Netflix", "Spotify", "LinkedIn", "Twitter"],
            "DevOps Engineer": ["Netflix", "Adobe", "Oracle", "Cisco"],
            "Product Manager": ["Meta", "Google", "Amazon", "Microsoft"],
        }
        
        import random
        choices = companies.get(role, ["Startup", "Product Company", "Tech Firm"])
        return random.choice(choices)

    def _get_location_for_role(self, role):
        """Get realistic location based on role"""
        locations = {
            "tech": ["Bangalore", "Hyderabad", "Pune", "Chennai", "NCR", "Remote"],
            "data": ["Bangalore", "Hyderabad", "Remote"],
            "frontend": ["Remote", "Bangalore", "Mumbai"],
        }
        
        import random
        return random.choice(locations.get("tech", ["Bangalore/Remote"]))

    def _get_salary_for_role(self, role, score):
        """Dynamic salary based on role and match score"""
        base_ranges = {
            "Software Engineer": (1800000, 3500000),
            "Frontend Developer": (1500000, 2800000),
            "Data Scientist": (2200000, 4200000),
            "DevOps Engineer": (2000000, 3800000),
            "Product Manager": (2500000, 5000000),
        }
        
        base_min, base_max = base_ranges.get(role, (1200000, 2500000))
        multiplier = 0.7 + (score / 100) * 0.6
        min_salary = int(base_min * multiplier)
        max_salary = int(base_max * multiplier)
        
        return f"₹{min_salary//100000}.{min_salary%100000//10000}L - ₹{max_salary//100000}.{max_salary%100000//10000}L"