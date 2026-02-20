import os
import json
import re
import requests
import concurrent.futures
import random

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def extract_text_from_pdf(file_obj):
    """Extract text from a PDF file object using pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_docx(file_obj):
    """Extract text from a DOCX file object using python-docx."""
    try:
        from docx import Document
        doc = Document(file_obj)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[DOCX extraction error: {e}]"


def analyze_resume_with_ai(resume_text: str, career_path: str = "", goal: str = "") -> dict:
    """
    Send resume text to OpenRouter API and get structured analysis + roadmap.
    Returns a dict with keys: strengths, weaknesses, missing_skills, job_matches, roadmap, summary
    """

    system_prompt = """You are an expert career coach and resume analyst with deep knowledge of industry hiring standards, technical skills, and learning resources.

Your task is to analyze the provided resume and return a comprehensive, structured JSON response. Be specific, actionable, and include real URLs for learning resources.

IMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no extra text — just raw JSON.
Do NOT use placeholders like "{{ STR_VALUE }}" or "string". Real content is required.

The JSON schema must be exactly:
{
  "candidate_name": "Name from resume",
  "summary": "2-3 sentence overall assessment",
  "score": integer (0-100, overall resume quality),
  "strengths": [
    {"title": "Strength Title", "description": "Specific detail about the strength"}
  ],
  "weaknesses": [
    {"title": "Weakness Title", "description": "Specific detail about the weakness"}
  ],
  "missing_skills": [
    {
      "skill": "Specific missing skill (e.g. 'Docker')",
      "importance": "High",  // Must be literally: "High", "Medium", or "Low"
      "why_needed": "Explanation of why this skill is critical for the target role"
    }
  ],
  "job_matches": [
    {
      "role": "Job Title",
      "match_percent": integer,
      "reason": "Why this matches"
    }
  ],
  "roadmap": [
    {
      "phase": "Phase 1: Foundation (Week 1-4)",
      "goal": "Phase Goal",
      "tasks": [
        {
          "skill": "Topic to learn",
          "type": "Video", // Must be: "Video", "Course", "Book", "Project", or "Article"
          "title": "Resource Title",
          "url": "https://...",
          "duration": "Duration (e.g. '2 hours')",
          "why": "Why this resource helps"
        }
      ]
    }
  ]
}

Rules for content:
- NO PLACEHOLDERS. Generate specific, personalized content based on the resume.
- "importance" MUST be exactly one of: "High", "Medium", "Low".
- "type" MUST be exactly one of: "Video", "Course", "Book", "Project", "Article".


Rules for roadmap resources:
- Videos: Use real YouTube links (youtube.com/watch?v=...)
- Courses: Use real links from Coursera, Udemy, edX, freeCodeCamp, Pluralsight
- Books: Use Google Books, Goodreads, or O'Reilly links
- Articles: Use real blogs, Medium, dev.to, or documentation links
- Include at least 3 phases in the roadmap
- Each phase should have 3-5 tasks
- Total roadmap should cover 3-6 months of learning
"""

    user_prompt = f"""Please analyze this resume and generate a comprehensive career roadmap.

{"Career Aspiration: " + career_path if career_path else ""}
{"Primary Goal: " + goal if goal else ""}

RESUME:
{resume_text[:6000]}

Analyze this resume thoroughly and return the structured JSON response as specified.
Focus on practical, actionable recommendations with real learning resources and URLs."""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "CareerPath Resume Analyzer",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        raw_content = data["choices"][0]["message"]["content"].strip()

        # Strip markdown code fences if present
        raw_content = re.sub(r'^```(?:json)?\s*', '', raw_content, flags=re.MULTILINE)
        raw_content = re.sub(r'\s*```$', '', raw_content, flags=re.MULTILINE)
        raw_content = raw_content.strip()

        # Find JSON object in the response
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            raw_content = match.group(0)

        result = json.loads(raw_content)
        result = clean_ai_response(result)
        return {"success": True, "data": result}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "The AI model took too long to respond. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API connection error: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Could not parse AI response. Please try again. ({str(e)})"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def clean_ai_response(data):
    """
    Sanitize the AI response to remove placeholders and ensure valid values.
    """
    if not isinstance(data, dict):
        return data

    # Clean missing skills
    if 'missing_skills' in data and isinstance(data['missing_skills'], list):
        cleaned_skills = []
        for skill in data['missing_skills']:
            if not isinstance(skill, dict):
                continue
            
            # Fix importance
            imp = skill.get('importance', 'Medium')
            if imp not in ['High', 'Medium', 'Low']:
                if 'high' in str(imp).lower(): imp = 'High'
                elif 'low' in str(imp).lower(): imp = 'Low'
                else: imp = 'Medium'
            skill['importance'] = imp

            # Remove placeholders
            if '{{' in str(skill.get('skill', '')) or 'string' in str(skill.get('skill', '')):
                continue
                
            cleaned_skills.append(skill)
        data['missing_skills'] = cleaned_skills

    return data


def generate_role_resources(role: str) -> dict:
    """
    Generate a structured learning path and resources for a specific job role.
    """
    system_prompt = """You are an expert technical career coach.
Create a detailed, structured learning roadmap for the specified job role.
Include real, high-quality learning resources (Courses, Books, Videos, Articles) with actual URLs.
Avoid generic advice; be specific about tools, frameworks, and skills.

IMPORTANT: Return ONLY valid JSON.
Do NOT use placeholders like "{{ VALUE }}". Provide real content.

JSON Schema:
{
  "role": "Role Name",
  "description": "Brief description of the role",
  "avg_salary": "e.g. $100k - $150k",
  "key_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
  "roadmap": [
    {
      "level": "Phase 1: Beginner",
      "focus": "Foundational concepts and tools",
      "topics": ["Topic 1", "Topic 2"],
      "resources": [
        {
          "type": "Course | Book | Video | Article",
          "title": "Title of resource",
          "url": "https://...",
          "author": "Author/Platform"
        }
      ]
    },
    { "level": "Phase 2: Intermediate", ... },
    { "level": "Phase 3: Advanced", ... }
  ]
}
"""

    user_prompt = f"Create a learning roadmap for the role: {role}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "CareerPath Resource Generator",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 3000,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        raw_content = data["choices"][0]["message"]["content"].strip()
        
        # Clean markdown
        raw_content = re.sub(r'^```(?:json)?\s*', '', raw_content, flags=re.MULTILINE)
        raw_content = re.sub(r'\s*```$', '', raw_content, flags=re.MULTILINE)
        raw_content = raw_content.strip()
        
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            raw_content = match.group(0)
            
        return {"success": True, "data": json.loads(raw_content)}

    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_questions(topic: str, difficulty: str, count: int) -> list:
    """Helper to fetch a batch of questions for a specific difficulty."""
    system_prompt = f"""You are an expert technical interviewer.
Create exactly {count} multiple-choice questions on the topic: "{topic}".
Difficulty Level: {difficulty}.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON.
- Create EXACTLY {count} unique questions.
- Each question must have 4 options.
- The correct_index must be 0-3.
- Questions must be strictly related to the topic.
- No negative marking, just standard MCQs.

JSON Schema:
{{
  "questions": [
    {{
      "text": "Question text?",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0,
      "explanation": "Short explanation."
    }}
  ]
}}
"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
         "HTTP-Referer": "http://localhost:8000",
        "X-Title": "CareerPath App"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate {count} {difficulty} questions for {topic}."}
        ],
        "temperature": 0.7,
        "max_tokens": 4000  # Increased for larger batches
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
        # We don't raise status here to handle partial failures gracefully in the main function if needed
        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
        data = response.json()
        if 'choices' not in data:
            return []
            
        content = data['choices'][0]['message']['content']
        raw_content = content.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(raw_content)
        return parsed.get('questions', [])
    except Exception as e:
        print(f"Error fetching {difficulty} questions: {e}")
        return []






