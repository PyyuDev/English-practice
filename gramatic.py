import json
import os
import urllib.request

JSON_FILE = "./gramatic/topics.json"
OLLAMA_MODEL = "llama3.2:latest"  # Change to "qwen2.5", "mistral", or your model of choice
OLLAMA_URL = "http://localhost:11434/api/generate"

TOPICS = [
    "Passive Voice (Present, Past, & Future)",
    "Relative Clauses (Defining & Non-Defining)",
    "Present Perfect Continuous vs. Present Perfect Simple",
    "Second & Third Conditionals (Hypotheticals)",
    "Modals of Deduction & Speculation (Must, Might, Could, Can't)",
    "Linking Words & Discourse Markers (Contrast, Cause, Result)",
    "Gerunds vs. Infinitives after Verbs",
    "Reported Speech & Indirect Questions",
    "Future Forms (Future Continuous & Future Perfect)",
    "Participle Clauses"
]

def load_progress():
    if not os.path.exists(JSON_FILE):
        data = {"current_index": 0, "total_topics": len(TOPICS), "topics": TOPICS}
        save_progress(data)
        return data
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_progress(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def stream_ollama(prompt):
    payload = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    print(chunk.get("response", ""), end="", flush=True)
            print("\n")
    except Exception as e:
        print(f"\n[Error connecting to Ollama]: {e}")
        print("Ensure Ollama is running (`ollama serve`).")

def run_study_session():
    data = load_progress()
    idx = data.get("current_index", 0)
    topic_name = TOPICS[idx]
    
    print(f"\n=== [Topic #{idx + 1} of {len(TOPICS)}: {topic_name}] ===\n")
    
    prompt = (
        f"Act as my B2 English tutor. Today, I want to master {topic_name}. "
        "Give me a 2-minute explanation of the rule, 3 examples related to software "
        "development or tech, and then ask me to write 3 sentences using this rule."
    )
    
    print("Fetching lesson from Ollama...\n" + "-"*50 + "\n")
    stream_ollama(prompt)
    
    # Auto-increment index and loop back to 0 using modulo
    data["current_index"] = (idx + 1) % len(TOPICS)
    save_progress(data)

if __name__ == "__main__":
    run_study_session()