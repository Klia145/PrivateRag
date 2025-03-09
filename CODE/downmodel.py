from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer('paraphrase-MiniLM-L6-v2')
encoder.save_pretrained("./local_encoder")