import glob
import os
from document_parser import extract_sections
from relevance_ranker import compute_section_relevance, extract_subsections
from output_writer import write_output

def run(input_folder, persona, job, output_json, model_path=None):
    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_folder}.")
        return

    all_sections = []
    for pdf in pdf_files:
        print(f"Parsing: {pdf}")
        sections = extract_sections(pdf)
        all_sections.extend(sections)

    if not all_sections:
        print("No valid sections extracted from documents!")
        return

    ranked_sections, model = compute_section_relevance(all_sections, persona, job, model_path)
    context = f"{persona}. {job}"

    subsections_ranked = []
    for section in ranked_sections[:10]:  # Extract finer granularity for top 10 sections
        subs = extract_subsections(section, context, model, max_snippets=5)
        subsections_ranked.extend(subs)

    write_output(output_json, pdf_files, persona, job, ranked_sections, subsections_ranked, score_threshold=0.15)
    print(f"Output written to {output_json}.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Persona-driven document intelligence extracting and ranking relevant sections and subsections.")
    parser.add_argument("--input_folder", required=True, help="Folder containing PDF files")
    parser.add_argument("--persona", default=None, help="Persona description string")
    parser.add_argument("--job", default=None, help="Job-to-be-done description string")
    parser.add_argument("--persona_file", default=None, help="Path to persona.txt containing persona text")
    parser.add_argument("--job_file", default=None, help="Path to job.txt containing job-to-do text")
    parser.add_argument("--output_json", default="output.json", help="Output JSON file path")
    parser.add_argument("--model_path", default=None, help="Optional: path to local sentence-transformer model folder for offline usage")
    args = parser.parse_args()

    if args.persona_file:
        with open(args.persona_file, "r", encoding="utf-8") as f:
            persona = f.read().strip()
    if args.job_file:
        with open(args.job_file, "r", encoding="utf-8") as f:
            job = f.read().strip()

    if not persona or not job:
        print("Error: Persona and job descriptions must be provided either via arguments or files.")
        exit(1)

    run(args.input_folder, persona, job, args.output_json, args.model_path)
