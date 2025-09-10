# Quickstart Guide: Document & Article Summarization

This guide demonstrates the document summarization functionality of hlpr.

## Prerequisites

- Python 3.11+ installed
- hlpr CLI installed: `pip install hlpr`
- (Optional) Local LLM server like Ollama running on localhost:11434

## Quick Setup

### 1. Initial Configuration

```bash
# Check installation
hlpr --version

# Set up local LLM (if using Ollama)
hlpr providers add local --type local --model llama2 --endpoint http://localhost:11434

# Or set up OpenAI
hlpr providers add openai --type openai --model gpt-4 --default
# (will prompt for API key, stored securely in system keyring)
```

## Core Workflows

### Document Summarization

#### Summarize a PDF Report

```bash
# Create a test document
echo "This is a sample document with important information about quarterly sales. The revenue increased by 15% compared to last quarter. Key challenges include supply chain delays and increased competition. Action items: review pricing strategy, improve delivery times, conduct market analysis." > sample-report.txt

# Summarize the document
hlpr summarize document sample-report.txt

# Expected output (rich terminal formatting):
```
📄 Document Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary:
The quarterly sales report shows positive growth with 15% revenue increase despite challenges 
from supply chain delays and competition. Strategic focus needed on pricing and delivery 
improvements.

🔑 Key Points:
• Revenue growth: 15% quarter-over-quarter
• Challenges: Supply chain delays, increased competition  
• Action items identified for strategic improvements

📈 Stats: 45 words processed in 1.2s using local provider
```

#### Save Summary with Different Formats

```bash
# Save as markdown
hlpr summarize document sample-report.txt --save --format md --output summary.md

# Save as JSON for programmatic use
hlpr summarize document sample-report.txt --save --format json --output summary.json
```

### Large Document Processing

```bash
# Process large document with custom chunking
hlpr summarize document large-report.pdf --chunk-size 4096 --chunk-overlap 512 --provider openai

# The CLI will show progress:
```
📄 Processing large-report.pdf
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Document Analysis:
• Size: 2.4 MB (45,000 words)
• Chunks: 12 sections
• Estimated time: 2-3 minutes

Processing chunks: [████████████████████████████████] 12/12 chunks complete

Generating final summary...
[████████████████████████████████] Summary complete
```

### API Integration

```bash
# Start API server
hlpr api start --port 8000

# Use with curl
curl -X POST "http://localhost:8000/summarize/document" \
  -F "file=@report.pdf" \
  -H "Content-Type: multipart/form-data"
```

## Configuration Management

### View Current Settings

```bash
# Show all configuration
hlpr config show

# Show specific setting
hlpr config get default_llm
```

### Customize Settings

```bash
# Set default provider
hlpr config set default_llm anthropic

# Configure local LLM endpoint
hlpr config set local_llm_endpoint http://localhost:8080
```

## Troubleshooting

### Common Issues

#### Provider Not Available

```bash
# Test provider connection
hlpr providers test local
# If fails: check if Ollama is running on localhost:11434

hlpr providers test openai  
# If fails: check API key with `hlpr config get openai.api_key`
```

#### Document Processing Errors

```bash
# Check file format and size
file sample.pdf
ls -lh sample.pdf

# Try with different provider
hlpr summarize document sample.pdf --provider openai

# Enable verbose output for debugging
hlpr --verbose summarize document sample.pdf
```

This quickstart guide demonstrates the key document summarization workflows. For detailed API documentation, see the OpenAPI specification in `contracts/api-spec.yaml`.