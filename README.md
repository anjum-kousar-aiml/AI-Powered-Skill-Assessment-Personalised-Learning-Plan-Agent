# Catalyst — AI Skill Assessment & Learning Agent

Catalyst is an AI system that evaluates a candidate’s real skills through a short conversational interview and generates a personalized learning roadmap based on identified gaps.

---

## What it does

- Extracts skills from **Job Description + Resume**
- Conducts a **chat-based assessment**
- Scores answers based on:
  - Content relevance  
  - Response quality  
- Identifies weak areas  
- Generates a **personalized roadmap**

---

## How it works

JD + Resume → Skill Extraction → Chat Assessment → Scoring → Gap Analysis → Learning Plan

---

## Key Features

- Conversational assessment (not form-based)
- Smart scoring (not random)
- No strict input limits (guided responses)
- Personalized learning roadmap

---

## Sample Output

**Score: 74%**

**Weak Skills:**
- NLP  
- Deployment  

**Roadmap:**
- Week 1–2: Learn NLP basics  
- Week 3–4: Build project  
- Week 5: Learn deployment  

---

## Tech Stack

- Python (Flask)  
- HTML, CSS, JavaScript  
- Groq (LLaMA 3.3 70B)

---

## Run Locally

```bash
python app.py