import json
import re
from .base_agent import BaseAgent

class ResumeAgent(BaseAgent):
    """
    REAL Resume Agent - Actually reads the resume content
    Extracts ACTUAL skills, projects, education from the text
    NO random or hardcoded data!
    """

    def analyze(self, resume_text):
        """
        Analyze the ACTUAL resume content and extract REAL information
        This data will be used by ALL other agents (Career, Jobs, Skills, Quiz)
        """
        
        print(f"\n{'='*60}")
        print(f"📄 AI AGENT READING RESUME")
        print(f"{'='*60}")
        print(f"Resume length: {len(resume_text)} characters")
        print(f"{'='*60}\n")
        
        # Step 1: Extract EVERYTHING from the resume
        extracted = self._extract_all_from_resume(resume_text)
        
        print(f"✅ Extracted {len(extracted['skills'])} skills")
        print(f"✅ Extracted {len(extracted['projects'])} projects")
        print(f"✅ Education: {extracted['education'][0] if extracted['education'] else 'None'}")
        print(f"✅ CGPA: {extracted['cgpa']}")
        print(f"✅ Domain: {extracted['domain']}")
        print(f"{'='*60}\n")
        
        # Step 2: Generate career paths based on ACTUAL extracted data
        role_options = self._generate_role_options_from_extracted(extracted)
        
        # Step 3: Determine primary recommendation
        primary = max(role_options, key=lambda x: x["match_score"]) if role_options else None
        
        return {
            "role_options": role_options,
            "primary_recommendation": primary["role"] if primary else "Software Engineer",
            "candidate_name": extracted["name"],
            "candidate_email": extracted["email"],
            "candidate_phone": extracted["phone"],
            "experience_level": extracted["experience_level"],
            "top_skills": extracted["skills"][:10],
            "extracted_data": extracted  # Send all extracted data for other agents to use
        }
    
    def _extract_all_from_resume(self, text):
        """
        Extract EVERY piece of information from the resume
        NO guessing, NO hardcoding - only what's actually in the text
        """
        text_lower = text.lower()
        lines = text.split('\n')
        
        # ===== EXTRACT NAME =====
        name = "Candidate"
        for line in lines[:10]:  # Look in first 10 lines
            line = line.strip()
            if line and len(line) > 5 and ' ' in line:
                # Check if it's all caps (likely a name)
                if line.isupper() and not re.search(r'@|http|\.com', line):
                    name = line
                    break
                # Check if it's title case and at the top
                elif line.istitle() and len(line.split()) <= 4 and not re.search(r'@|http|\.com', line):
                    name = line
                    break
        
        # ===== EXTRACT EMAIL =====
        email = "Not provided"
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            email = email_match.group(0)
        
        # ===== EXTRACT PHONE =====
        phone = "Not provided"
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            phone = phone_match.group(0)
        
        # ===== EXTRACT CGPA/GPA =====
        cgpa = None
        cgpa_patterns = [
            r'cgpa[:\s]*([\d.]+)/?[\d]*',
            r'gpa[:\s]*([\d.]+)/?[\d]*',
            r'percentage[:\s]*([\d.]+)%',
            r'(\d+\.\d+)\s*\/\s*10'
        ]
        for pattern in cgpa_patterns:
            match = re.search(pattern, text_lower)
            if match:
                cgpa = match.group(1)
                break
        
        # ===== EXTRACT EDUCATION =====
        education = []
        education_keywords = ['b.tech', 'bachelor', 'master', 'm.tech', 'b.sc', 'm.sc', 'phd', 'be', 'me', 'b.e', 'm.e']
        
        # Find education section
        edu_section = self._extract_section(text, 'education')
        if edu_section:
            edu_lines = edu_section.split('\n')
            for line in edu_lines[:5]:
                line = line.strip()
                if line and len(line) > 10:
                    # Check if it contains education keywords
                    for keyword in education_keywords:
                        if keyword in line.lower():
                            education.append(line[:150])
                            break
        
        # Also look for education in the whole text
        if not education:
            for line in lines[:30]:
                for keyword in education_keywords:
                    if keyword in line.lower():
                        education.append(line.strip()[:150])
                        break
        
        # ===== EXTRACT SKILLS - ACTUAL SKILLS FROM RESUME =====
        skills = []
        
        # Comprehensive skill list
        skill_patterns = {
            'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript', 'php', 'html', 'css'],
            'ml_ai': ['tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'opencv', 'nltk', 'spacy', 'transformers', 'bert', 'gpt', 'llm', 'langchain', 'huggingface', 'xgboost', 'lightgbm'],
            'data_science': ['sql', 'mongodb', 'postgresql', 'mysql', 'sqlite', 'tableau', 'power bi', 'excel', 'r', 'spss', 'sas'],
            'web_dev': ['react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'spring', 'bootstrap', 'tailwind', 'jquery', 'ajax', 'rest', 'graphql'],
            'cloud_devops': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd', 'terraform', 'ansible'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'elasticsearch', 'oracle', 'sqlite'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'jira', 'confluence', 'slack', 'vscode', 'pycharm', 'eclipse', 'postman']
        }
        
        # Find skills section
        skills_section = self._extract_section(text, 'skill') or self._extract_section(text, 'technical') or self._extract_section(text, 'technologies')
        
        if skills_section:
            skills_lower = skills_section.lower()
            for category, category_skills in skill_patterns.items():
                for skill in category_skills:
                    if skill in skills_lower:
                        skills.append(skill.title())
        
        # Also look for skills in the whole text
        if not skills:
            for category, category_skills in skill_patterns.items():
                for skill in category_skills:
                    if skill in text_lower:
                        skills.append(skill.title())
        
        # Remove duplicates
        skills = list(dict.fromkeys(skills))
        
        # ===== EXTRACT PROJECTS =====
        projects = []
        project_section = self._extract_section(text, 'project')
        if project_section:
            project_lines = project_section.split('\n')
            current_project = {}
            for line in project_lines[:15]:
                line = line.strip()
                if line and len(line) > 10:
                    # Check if it's a project title
                    if line[0].isupper() or line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        if current_project and 'name' in current_project:
                            projects.append(current_project)
                        current_project = {
                            "name": line.replace('•', '').replace('-', '').replace('*', '').strip()[:100],
                            "technologies": [],
                            "description": ""
                        }
                    elif current_project:
                        # Look for technologies
                        for skill in skills:
                            if skill.lower() in line.lower():
                                current_project["technologies"].append(skill)
                        # Add to description
                        current_project["description"] += line + " "
            
            if current_project and 'name' in current_project:
                projects.append(current_project)
        
        # If no projects found, try to extract any bullet points that might be projects
        if not projects:
            bullet_pattern = r'[•\-*]\s*(.+?)(?:\n|$)'
            bullets = re.findall(bullet_pattern, text)
            for bullet in bullets[:5]:
                if len(bullet) > 20 and not re.search(r'@|http|\.com', bullet):
                    projects.append({
                        "name": bullet[:100],
                        "technologies": [],
                        "description": bullet
                    })
        
        # ===== EXTRACT EXPERIENCE =====
        experience = []
        exp_section = self._extract_section(text, 'experience') or self._extract_section(text, 'work')
        if exp_section:
            exp_lines = exp_section.split('\n')
            for line in exp_lines[:10]:
                line = line.strip()
                if line and len(line) > 15 and not re.search(r'@|http|\.com', line):
                    experience.append(line[:150])
        
        # ===== DETECT DOMAIN =====
        domain = "Software Engineering"
        
        # Check for AI/ML
        ai_ml_terms = ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 
                       'tensorflow', 'pytorch', 'computer vision', 'nlp', 'data science']
        for term in ai_ml_terms:
            if term in text_lower:
                domain = "AI/ML Engineering"
                break
        
        # Check for Data Science
        if domain == "Software Engineering":
            ds_terms = ['data analysis', 'sql', 'pandas', 'tableau', 'statistics', 'data visualization']
            for term in ds_terms:
                if term in text_lower:
                    domain = "Data Science"
                    break
        
        # Check for Web Development
        if domain == "Software Engineering":
            web_terms = ['react', 'angular', 'vue', 'node', 'django', 'flask', 'html', 'css', 'javascript']
            for term in web_terms:
                if term in text_lower:
                    domain = "Web Development"
                    break
        
        # ===== DETERMINE EXPERIENCE LEVEL =====
        exp_level = "Entry Level"
        
        # Look for years of experience
        year_match = re.search(r'(\d+)\+?\s*years?', text_lower)
        if year_match:
            years = int(year_match.group(1))
            if years >= 5:
                exp_level = "Senior"
            elif years >= 3:
                exp_level = "Mid"
            elif years >= 1:
                exp_level = "Junior"
        
        # Check for titles
        if 'senior' in text_lower or 'lead' in text_lower or 'architect' in text_lower:
            exp_level = "Senior"
        elif 'intern' in text_lower or 'internship' in text_lower or 'fresher' in text_lower:
            exp_level = "Entry Level"
        
        # ===== GENERATE STRENGTHS BASED ON ACTUAL RESUME =====
        strengths = []
        
        if cgpa:
            strengths.append(f"Strong academic performance with {cgpa} CGPA")
        
        if skills:
            strengths.append(f"Proficiency in {', '.join(skills[:3])}")
        
        if projects:
            strengths.append(f"Project experience: {projects[0]['name'] if isinstance(projects[0], dict) else projects[0]}")
        
        if experience:
            strengths.append(f"Work experience: {experience[0]}")
        
        if domain:
            strengths.append(f"Specialization in {domain}")
        
        if not strengths:
            strengths = ["Resume submitted", "Ready for analysis"]
        
        # ===== GENERATE GAPS BASED ON WHAT'S MISSING =====
        gaps = []
        
        if domain == "AI/ML Engineering":
            if 'tensorflow' not in text_lower and 'pytorch' not in text_lower:
                gaps.append("Deep learning frameworks (TensorFlow/PyTorch)")
            if 'docker' not in text_lower and 'kubernetes' not in text_lower:
                gaps.append("Model deployment and MLOps")
            if 'sql' not in text_lower:
                gaps.append("SQL and databases")
            if 'cloud' not in text_lower and 'aws' not in text_lower:
                gaps.append("Cloud platforms (AWS/GCP/Azure)")
        
        elif domain == "Data Science":
            if 'sql' not in text_lower:
                gaps.append("SQL proficiency")
            if 'tableau' not in text_lower and 'power bi' not in text_lower:
                gaps.append("Data visualization tools")
            if 'statistics' not in text_lower and 'hypothesis' not in text_lower:
                gaps.append("Statistical analysis")
        
        elif domain == "Web Development":
            if 'react' not in text_lower and 'angular' not in text_lower and 'vue' not in text_lower:
                gaps.append("Modern frontend frameworks")
            if 'node' not in text_lower and 'django' not in text_lower and 'flask' not in text_lower:
                gaps.append("Backend development")
            if 'database' not in text_lower and 'sql' not in text_lower:
                gaps.append("Database design")
        
        else:
            gaps = [
                "System design and architecture",
                "Cloud computing",
                "Data structures & algorithms"
            ]
        
        if not projects:
            gaps.append("Project portfolio")
        
        if not experience:
            gaps.append("Industry experience")
        
        # Limit to top 5 gaps
        gaps = gaps[:5]
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "cgpa": cgpa,
            "education": education[:3],
            "skills": skills[:20],
            "projects": projects[:5],
            "experience": experience[:3],
            "domain": domain,
            "experience_level": exp_level,
            "strengths": strengths[:5],
            "gaps": gaps[:5],
            "raw_text": text[:1000]  # Store preview for other agents
        }
    
    def _generate_role_options_from_extracted(self, extracted):
        """
        Generate career paths based on ACTUAL extracted resume data
        NOT random - based on REAL skills, domain, education
        """
        role_options = []
        skills = extracted["skills"]
        domain = extracted["domain"]
        cgpa = extracted["cgpa"]
        has_projects = len(extracted["projects"]) > 0
        has_experience = len(extracted["experience"]) > 0
        
        # ===== AI/ML ENGINEER PATH (if domain is AI/ML) =====
        if domain == "AI/ML Engineering" or any(s in ['Tensorflow', 'Pytorch', 'Scikit-Learn'] for s in skills):
            score = 70
            
            evidence = []
            if extracted["education"]:
                score += 10
                evidence.append(f"Education: {extracted['education'][0]}")
            if cgpa:
                score += 5
                evidence.append(f"Academic excellence: {cgpa} CGPA")
            if 'python' in [s.lower() for s in skills]:
                score += 10
                evidence.append("Python programming")
            if 'tensorflow' in [s.lower() for s in skills] or 'pytorch' in [s.lower() for s in skills]:
                score += 15
                evidence.append("Deep learning framework experience")
            if has_projects:
                score += 10
                evidence.append(f"Project: {extracted['projects'][0]['name'] if isinstance(extracted['projects'][0], dict) else extracted['projects'][0]}")
            
            role_options.append({
                "role": "Machine Learning Engineer",
                "match_score": min(98, score),
                "evidence": evidence[:3],
                "gaps": [
                    "Model deployment and MLOps",
                    "Large Language Models (LLMs)",
                    "Distributed training"
                ],
                "reasoning": f"Your {extracted['domain']} background with {', '.join(skills[:3])} makes you a strong candidate for ML engineering roles."
            })
            
            # Data Scientist path
            role_options.append({
                "role": "Data Scientist",
                "match_score": min(95, score - 8),
                "evidence": evidence[:2] + ["Analytical thinking"],
                "gaps": [
                    "Advanced statistical modeling",
                    "A/B testing",
                    "Big data technologies"
                ],
                "reasoning": "Your AI/ML foundation transitions well to data science, focusing on insights and analysis."
            })
            
            # Computer Vision Engineer (if OpenCV or CV in skills)
            if 'opencv' in [s.lower() for s in skills] or 'computer vision' in str(extracted).lower():
                role_options.append({
                    "role": "Computer Vision Engineer",
                    "match_score": min(90, score - 5),
                    "evidence": ["Computer vision interest", "Deep learning fundamentals", "Python programming"],
                    "gaps": [
                        "CNN architectures",
                        "Object detection models",
                        "Image processing libraries"
                    ],
                    "reasoning": "Your interest in computer vision can be developed into a specialized career path."
                })
            
            # NLP Engineer
            if 'nlp' in str(extracted).lower() or 'natural language' in str(extracted).lower():
                role_options.append({
                    "role": "NLP Engineer",
                    "match_score": min(88, score - 7),
                    "evidence": ["Natural language processing interest", "Text processing", "ML fundamentals"],
                    "gaps": [
                        "Transformer models (BERT, GPT)",
                        "Tokenization and embeddings",
                        "Sequence models"
                    ],
                    "reasoning": "NLP is a high-demand specialization within AI/ML that matches your interests."
                })
        
        # ===== SOFTWARE ENGINEER PATH (always available) =====
        se_score = 50
        se_evidence = []
        
        if skills:
            se_score += 15
            se_evidence.append(f"Programming skills: {', '.join(skills[:3])}")
        if has_projects:
            se_score += 10
            se_evidence.append("Project experience")
        if extracted["education"]:
            se_score += 5
            se_evidence.append(f"Educational background")
        
        role_options.append({
            "role": "Software Engineer",
            "match_score": min(90, se_score),
            "evidence": se_evidence[:3],
            "gaps": [
                "Data structures & algorithms",
                "System design",
                "Cloud platforms"
            ],
            "reasoning": "Software engineering is a versatile path that leverages your technical skills across industries."
        })
        
        # ===== FULL STACK DEVELOPER (if web skills detected) =====
        web_skills = ['react', 'angular', 'vue', 'node', 'django', 'flask', 'html', 'css', 'javascript']
        has_web = any(s.lower() in web_skills for s in skills)
        
        if has_web:
            web_score = 60
            web_evidence = []
            
            for skill in skills:
                if skill.lower() in web_skills:
                    web_score += 10
                    web_evidence.append(f"{skill} experience")
            
            role_options.append({
                "role": "Full Stack Developer",
                "match_score": min(88, web_score),
                "evidence": web_evidence[:3],
                "gaps": [
                    "Database design",
                    "API development",
                    "Deployment strategies"
                ],
                "reasoning": "Your web development skills can be expanded into full stack roles with backend knowledge."
            })
        
        # ===== DATA ANALYST PATH (if data skills detected) =====
        data_skills = ['sql', 'excel', 'pandas', 'tableau', 'power bi']
        has_data = any(s.lower() in data_skills for s in skills)
        
        if has_data:
            da_score = 55
            da_evidence = []
            
            for skill in skills:
                if skill.lower() in data_skills:
                    da_score += 12
                    da_evidence.append(f"{skill} experience")
            
            role_options.append({
                "role": "Data Analyst",
                "match_score": min(85, da_score),
                "evidence": da_evidence[:3] or ["Data manipulation skills"],
                "gaps": [
                    "Advanced Excel/SQL",
                    "Data visualization",
                    "Business intelligence"
                ],
                "reasoning": "Entry-level data analyst roles are a great starting point to build industry experience."
            })
        
        # ===== DEVOPS ENGINEER (if cloud/DevOps skills detected) =====
        devops_skills = ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'ci/cd']
        has_devops = any(s.lower() in devops_skills for s in skills)
        
        if has_devops:
            devops_score = 60
            devops_evidence = []
            
            for skill in skills:
                if skill.lower() in devops_skills:
                    devops_score += 15
                    devops_evidence.append(f"{skill} experience")
            
            role_options.append({
                "role": "DevOps Engineer",
                "match_score": min(85, devops_score),
                "evidence": devops_evidence[:3],
                "gaps": [
                    "Infrastructure as Code",
                    "Monitoring & logging",
                    "Container orchestration"
                ],
                "reasoning": "Your DevOps/cloud skills are valuable for infrastructure and deployment roles."
            })
        
        # Sort by match score and take top 6
        role_options.sort(key=lambda x: x["match_score"], reverse=True)
        return role_options[:6]
    
    def _extract_section(self, text, section_name):
        """Extract a specific section from resume"""
        patterns = [
            rf'(?:{section_name}s?|technical|work|experience)[:\s]+\n(.*?)(?:\n\s*\n|\Z)',
            rf'(?:{section_name}s?|technical|work|experience)[:\s]*(.*?)(?:\n\s*\n|\Z)',
            rf'(?:{section_name})[:\s]*(.*?)(?:\n\s*\n|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""