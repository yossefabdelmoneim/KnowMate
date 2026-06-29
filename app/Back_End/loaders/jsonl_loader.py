import json


def load_jsonl(file_path: str):
    """
    Load a JSONL FAQ dataset.
    Each question-answer pair is returned
    as a separate document.
    """

    documents = []

    with open(file_path, "r", encoding="utf-8") as file:

        for line in file:

            if not line.strip():
                continue

            record = json.loads(line)

            messages = record.get("messages", [])

            question = ""
            answer = ""

            for message in messages:

                if message["role"] == "user":
                    question = message["content"]

                elif message["role"] == "assistant":
                    answer = message["content"]

            if question and answer:

                documents.append(
                    f"""Question:
{question}

Answer:
{answer}"""
                )

    print(f"Number of documents: {len(documents)}")

    return documents