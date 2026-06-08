from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    TODO — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_blocks.append(f"[Chunk {i} — {chunk['game']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_blocks)

    system_message = system_message = """You are a board game rules expert. 
Answer the user's question using ONLY the rules excerpts provided. 
Always state which game the rule comes from naturally in your answer (e.g. 'In Monopoly, ...').
Never reference chunk numbers or excerpts directly in your answer.
If the answer is not found in the excerpts, say "I don't have enough information in the loaded rules to answer that." 
Do not use any outside knowledge beyond what is provided."""

    user_message = f"""RULES EXCERPTS:

{context}

---

User Question: {query}"""

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
    )

    return response.choices[0].message.content
