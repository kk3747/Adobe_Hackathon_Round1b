How to Build and Run

1. Build the Docker image:

docker build -t adobe_round1b .


2. Run the analysis:

docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe_round1b


Input PDFs and persona/job configs go in input/.

The structured report is written as output/output.json.


Inside the container, the script automatically runs:

python main.py --input_folder input --persona_file input/persona.txt --job_file input/job.txt --output_json output/output.json