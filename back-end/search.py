import json
import string
with open("knowledge.json", "r") as file:
    knowledge_base=json.load(file)

def search_question(question):
    question = question.lower()
    punctuation = string.punctuation.replace("?","")
    question = question.translate(str.maketrans("", "", punctuation))
    print(question)

    best_match = None
    best_action = None
    best_score = 0
    best_position = float("inf")
    for key in knowledge_base:
        entry = knowledge_base[key]
        score=0
        position = float("inf")

        for keyword in entry["keywords"]:
            if keyword.lower() in question:
                score += 1
                position = question.find(keyword.lower())

        if score > best_score or (score == best_score and position < best_position):
            best_score = score
            best_position = position
            best_match = entry["answer"]
            best_action = entry.get("action")

    return {"answer": best_match, "action": best_action}