from app.worker import app

@app.task
def evaluate(word: str):
    print(f"DEBUG EVAL {word}")