Persona-Driven Document Intelligence

This solution is my submission for the Adobe Hackathon Round 1B, "Connect What Matters — For the User Who Matters." The problem asks for a general, CPU-friendly pipeline to analyze a set of PDFs and, given a user persona and job-to-be-done, extract and prioritize the most relevant document sections and fine-grained text snippets, outputting structured JSON.

My Project Structure

    adobe_round1b/
    ├── input/
    │   ├── *.pdf               # Input PDF documents
    │   ├── persona.txt         # Persona configuration
    │   └── job.txt             # Job-to-be-done configuration
    ├── output/
    │   └── output.json         # Final extracted results
    ├── main.py                 # Pipeline orchestrator
    ├── document_parser.py      # Section detection & text normalization
    ├── relevance_ranker.py     # Embedding, ranking, and snippet extraction
    ├── output_writer.py        # JSON formatter
    ├── requirements.txt        # All dependencies
    ├── Dockerfile              # For containerized, portable build
    ├── README.md               # explain how to run the code
    └── approach_explanation.md # explain the approach


My Approach:

PDF Parsing & Section Detection:

I use pdfplumber to extract text and structure from each document, segmenting text into logical sections via regex heading detection. I normalize and validate section titles, merging noisy or invalid sections into adjacent context.


Persona & Job Context Modeling:

The persona and job descriptions (from persona.txt/job.txt) are merged into a semantic query representing the user's information intent.

Semantic Ranking with Embeddings:

Using sentence-transformers with the efficient all-MiniLM-L6-v2 model, I obtain embeddings for both query and sections. Cosine similarity is computed via scikit-learn to rank all sections for persona-task relevance.


Fine-Grained Subsection Extraction:

For each top-ranked section, I split the content into sentences, again compute semantic relevance, and select the best-matching snippets. I use wordninja to fix spacing in concatenated or corrupted text, a common artifact of PDF extraction.


Output Construction:

Results are saved to output/output.json and include:

Metadata (input docs, persona, job, timestamp)


List of extracted sections (with clean titles/page numbers/importance rank):

Nested relevant refined_texts for each section (each snippet with its text and page number)

Models and Libraries Used:

pdfplumber for text extraction with page awareness

sentence-transformers (model: all-MiniLM-L6-v2) for fast, semantic embeddings

scikit-learn, numpy for similarity and vector math

wordninja for word boundary repair in noisy PDF outputs

argparse for command-line execution


All dependencies are in requirements.txt and installed during Docker image build.


This implements the hackathon's requirements: CPU-only, ≤1GB model size, fully offline, runs on arbitrary PDF collections and personas, and yields clean, review-ready output.