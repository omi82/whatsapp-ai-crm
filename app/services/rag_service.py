from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer


# =========================================================
# CUSTOM EMBEDDING CLASS
# =========================================================

class SentenceTransformerEmbeddings(Embeddings):

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed_documents(
        self,
        texts
    ):

        return (
            self.model
            .encode(texts)
            .tolist()
        )

    def embed_query(
        self,
        text
    ):

        return (
            self.model
            .encode(text)
            .tolist()
        )


# =========================================================
# EMBEDDING MODEL
# =========================================================

embedding_model = (
    SentenceTransformerEmbeddings()
)


# =========================================================
# BUILD VECTOR DATABASE
# =========================================================

def build_vector_store():

    loader = TextLoader(
        "app/data/company_knowledge.txt",
        encoding="utf-8"
    )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(
        documents
    )

    vector_store = FAISS.from_documents(
        chunks,
        embedding_model
    )

    return vector_store


# =========================================================
# LOAD VECTOR STORE ON APP STARTUP
# =========================================================

VECTOR_STORE = build_vector_store()


# =========================================================
# SEARCH KNOWLEDGE BASE
# =========================================================

def search_company_knowledge(
    question: str,
    k: int = 3
):

    try:

        docs = (
            VECTOR_STORE
            .similarity_search(
                question,
                k=k
            )
        )

        context = "\n\n".join(
            [
                doc.page_content
                for doc in docs
            ]
        )

        return context

    except Exception as e:

        print(
            "RAG SEARCH ERROR:",
            str(e)
        )

        return ""


# =========================================================
# TEST FUNCTION
# =========================================================

if __name__ == "__main__":

    result = search_company_knowledge(
        "What services do you provide?"
    )

    print(result)