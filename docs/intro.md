# ITViec Job AI Assistant

FastAPI, LangChain, FAISS, DeepSeek, Hugging Face E5, BeautifulSoup, Docker, HTML/CSS/JavaScript

- Built a retrieval-augmented job recommendation assistant for AI, machine learning, LLM, and data roles using FastAPI, FAISS, LangChain, and DeepSeek.
- Crawled and structured `219` ITviec job postings from `155` companies into a reusable dataset covering titles, locations, skills, descriptions, requirements, and benefits.
- Implemented an embedding and retrieval pipeline with `intfloat/multilingual-e5-base` and top-`10` FAISS search to ground answers in relevant job evidence.
- Delivered a lightweight web chat interface and API workflow for Vietnamese job-search queries, including role matching, requirement summaries, and direct application links.
- Containerized the application with Docker and documented a reproducible local workflow for crawling, indexing, serving, and demoing the system.
