# atlas/backend/test_memory_insert.py
import uuid
from sentence_transformers import SentenceTransformer
from backend.db.connection import SessionLocal, init_db
from backend.db.models import Fact

init_db()
print("model downloading")
model = SentenceTransformer("all-MiniLM-L6-v2")  

facts_to_store = [
    ("User's wedding is in Rishikesh, Dec 2026 to Feb 2027", "wedding"),
    ("User prefers non-bass-heavy audio in earbuds", "preference"),
    ("User is preparing for placement interviews at Google and Amazon", "work"),
]

session = SessionLocal()

for text, category in facts_to_store:
    embedding = model.encode(text).tolist()   # numpy array -> plain Python list
    fact = Fact(
        id=str(uuid.uuid4()),
        user_id="rajnil",
        fact_text=text,
        embedding=embedding,
        category=category,
    )
    session.add(fact)

session.commit()
print("Inserted 3 real facts with real embeddings into Postgres.")

# Now: real similarity search, done BY Postgres itself
query = "Where is the user getting married?"
query_vector = model.encode(query).tolist()

results = (
    session.query(Fact)
    .order_by(Fact.embedding.cosine_distance(query_vector))
    .limit(1)
    .all()
)

print(f"\nQuery: '{query}'")
print(f"Most relevant fact (found BY Postgres): '{results[0].fact_text}'")

session.close()