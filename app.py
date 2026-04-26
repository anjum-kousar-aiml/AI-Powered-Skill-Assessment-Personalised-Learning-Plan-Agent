from dotenv import load_dotenv
load_dotenv()
import os
import json
from flask import Flask, request, jsonify, render_template, session
from groq import Groq
from prompts import SKILL_EXTRACTION_PROMPT

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "catalyst-dev-secret-2024")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


# ================= LLM HELPERS =================

def ask_llm(system_prompt, user_message):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def ask_llm_json(system_prompt, user_message):
    raw = ask_llm(system_prompt, user_message)
    clean = raw.strip()

    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]

    clean = clean.strip().rstrip("```").strip()
    return json.loads(clean)


# ================= SCORING =================

def score_answer(answer, skill_name):
    words = answer.lower().split()
    char_count = len(answer)

    # LENGTH SCORE (30 marks only → less weight)
    max_chars = 100
    length_score = min(char_count, max_chars) / max_chars * 30

    # CONTENT SCORE (70 marks → more important)
    skill_keywords = skill_name.lower().split()
    keyword_matches = sum(1 for w in words if w in skill_keywords)

    tech_words = [
        "model", "data", "algorithm", "training",
        "accuracy", "api", "deployment", "feature",
        "prediction", "classification", "decision making", "intelligence", 
        "machine learning", "artificial intelligence", "project", "built"
    ]
    tech_matches = sum(1 for w in words if w in tech_words)

    content_score = min(keyword_matches * 10 + tech_matches * 5, 70)

    return int(length_score + content_score)


# ================= ROUTES =================

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/assess")
def assess():
    if "required_skills" not in session:
        return render_template("index.html", error="Please start from the beginning.")
    return render_template("assess.html")


@app.route("/results")
def results():
    if "report" not in session:
        return render_template("index.html", error="No report found.")
    return render_template("results.html")


# ================= API =================

@app.route("/api/parse", methods=["POST"])
def parse():
    data = request.get_json()
    jd_text = data.get("jd", "").strip()
    resume_text = data.get("resume", "").strip()

    user_message = f"""
JOB DESCRIPTION:
{jd_text}

CANDIDATE RESUME:
{resume_text}
"""

    result = ask_llm_json(SKILL_EXTRACTION_PROMPT, user_message)

    session["required_skills"] = result.get("required_skills", [])
    session["current_skill_index"] = 0
    session["answers"] = []   # store answers

    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    skills = session.get("required_skills", [])
    idx = session.get("current_skill_index", 0)

    # store answers
    if user_message:
        session["answers"].append(user_message)

    if idx >= len(skills):
        return jsonify({"status": "assessment_complete"})

    # first question
    if not user_message:
        question = f"Tell me about your experience with {skills[idx]['name']}."
        return jsonify({"status": "question", "message": question})

    # move next
    idx += 1
    session["current_skill_index"] = idx

    if idx >= len(skills):
        return jsonify({
            "status": "assessment_complete",
            "message": "Assessment complete!"
        })

    next_question = f"Now tell me about {skills[idx]['name']}."
    return jsonify({"status": "question", "message": next_question})


@app.route("/api/report", methods=["POST"])
def generate_report():
    skills = session.get("required_skills", [])
    answers = session.get("answers", [])

    skill_scores = []

    for i, skill in enumerate(skills):
        ans = answers[i] if i < len(answers) else ""
        score = score_answer(ans, skill["name"])

        skill_scores.append({
            "skill_name": skill["name"],
            "score": score
        })

    overall = sum(s["score"] for s in skill_scores) // len(skill_scores)

    # identify weak skills
    weak_skills = [s["skill_name"] for s in skill_scores if s["score"] < 70]

    # build roadmap
    roadmap = []
    for skill in weak_skills:
        roadmap.append({
            "skill": skill,
            "plan": [
                f"Learn fundamentals of {skill}",
                f"Build a project using {skill}",
                f"Practice interview questions on {skill}",
                f"Apply {skill} in a real-world scenario"
            ]
        })

    report = {
        "gap_analysis": {
            "overall_score": overall,
            "critical_gaps": [
                {"skill": s, "gap": "Needs improvement"} for s in weak_skills
            ]
        },
        "skill_scores": skill_scores,
        "learning_plan": {
            "roadmap": roadmap,
            "timeline": "4–6 weeks"
        }
    }

    session["report"] = report
    return jsonify({"report": report})


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)