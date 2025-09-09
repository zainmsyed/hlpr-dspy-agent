# Quickstart Guide: hlpr AI Assistant

This guide demonstrates the core functionality of hlpr through practical examples.

## Prerequisites

- Python 3.11+ installed
- hlpr CLI installed: `pip install hlpr`
- (Optional) Local LLM server like Ollama running on localhost:11434

## Quick Setup

### 1. Initial Configuration

```bash
# Check installation
hlpr --version

# Show default configuration
hlpr config show

# Set up local LLM (if using Ollama)
hlpr providers add local --type local --model llama2 --endpoint http://localhost:11434

# Or set up OpenAI
hlpr providers add openai --type openai --model gpt-4 --default
# (will prompt for API key, stored securely in system keyring)
```

### 2. Configure Email Account (Optional)

```bash
# Add Gmail account (requires app password)
hlpr email accounts add personal --provider gmail --username your.email@gmail.com
# (will prompt for app password)

# Test the connection
hlpr email accounts test personal
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

### Meeting Notes Processing

#### Process Meeting Transcript

```bash
# Create sample meeting notes
cat > meeting-notes.txt << EOF
Team Standup - September 9, 2025

Attendees: Alice, Bob, Charlie, Diana

Alice: Completed user authentication feature, working on password reset
Bob: Finished database migration, starting on API endpoints  
Charlie: Reviewed pull requests, found performance issue in search
Diana: Updated documentation, planning user testing session

Action Items:
- Alice to fix password reset bug by Friday
- Bob to optimize search performance
- Diana to schedule user testing for next week
- Team to review security audit report

Next meeting: September 16, 2025
EOF

# Process the meeting notes
hlpr summarize meeting meeting-notes.txt --title "Team Standup"
```

Expected output:
```
📅 Meeting Summary: Team Standup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Overview:
Regular team standup covering completed work, current tasks, and action items for 
the development team.

🎯 Key Points:
• Authentication feature completed
• Database migration finished
• Performance issue identified in search functionality
• Documentation updates completed

👥 Participants:
Alice, Bob, Charlie, Diana

✅ Action Items:
🔹 Alice: Fix password reset bug (Due: Friday)
🔹 Bob: Optimize search performance  
🔹 Diana: Schedule user testing session (Due: Next week)
🔹 Team: Review security audit report

📅 Next Meeting: September 16, 2025
```

### Email Processing

#### Process Recent Emails

```bash
# Process unread emails from personal account
hlpr email process personal --limit 10

# Expected output (table format):
```
📧 Email Processing Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Processing emails from personal@gmail.com...
[████████████████████████████████] 10/10 emails processed

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Sender               ┃ Subject                                 ┃ Date                  ┃ Classification ┃ Priority ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ boss@company.com     │ Quarterly Review Meeting               │ 2025-09-09 09:15     │ WORK          │ HIGH     │
│ newsletter@news.com  │ Weekly Tech Updates                     │ 2025-09-09 08:30     │ NEWSLETTER    │ LOW      │
│ friend@email.com     │ Weekend Plans                           │ 2025-09-08 19:45     │ PERSONAL      │ MEDIUM   │
│ support@service.com  │ Your Account Statement                  │ 2025-09-08 16:20     │ IMPORTANT     │ HIGH     │
└──────────────────────┴─────────────────────────────────────────┴───────────────────────┴───────────────┴──────────┘

📊 Summary:
• Total processed: 10 emails
• WORK: 3, PERSONAL: 2, NEWSLETTER: 3, IMPORTANT: 2
• HIGH priority: 2, MEDIUM: 3, LOW: 5
```

#### Filter and Export Results

```bash
# Process work emails from last week, save to CSV
hlpr email process work --since 2025-09-02 --save --format csv --output work-emails.csv

# Process emails from specific sender
hlpr email process personal --from "important@company.com" --format json
```

## Advanced Usage

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

### Batch Operations

```bash
# Process multiple documents
for file in reports/*.pdf; do
    hlpr summarize document "$file" --save --format md
done

# Process emails from multiple accounts
hlpr email process personal --save --format json --output personal-emails.json
hlpr email process work --save --format json --output work-emails.json
```

### Provider Management

```bash
# List all configured providers
hlpr providers list

# Add backup provider
hlpr providers add anthropic --type anthropic --model claude-3-sonnet

# Test provider connectivity
hlpr providers test local
hlpr providers test openai
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

# Set default output format
hlpr config set default_output_format md
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

#### Email Authentication Fails

```bash
# Test email account
hlpr email accounts test personal
# If fails: verify app password or username

# Re-add account with new credentials
hlpr email accounts remove personal
hlpr email accounts add personal --provider gmail --username new@gmail.com
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

### Log Analysis

```bash
# Set debug logging
export HLPR_LOG_LEVEL=DEBUG

# Check logs (location varies by OS)
# Linux: ~/.local/share/hlpr/logs/
# macOS: ~/Library/Logs/hlpr/
# Windows: %APPDATA%/hlpr/logs/
```

## Integration Examples

### Use with Scripts

```bash
#!/bin/bash
# Auto-process daily emails

# Process unread emails and save results
hlpr email process personal --unread-only --save --format json --output daily-emails.json

# Generate summary report
python scripts/generate_email_report.py daily-emails.json
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

This quickstart guide demonstrates the key workflows and features of hlpr. For detailed API documentation, see the OpenAPI specification in `contracts/api-spec.yaml`.