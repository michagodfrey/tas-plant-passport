# Tasmanian PlantPassport Agent

## Purpose

This micro-repo is a **regulatory assistant** that provides structured, accurate answers about Tasmanian import conditions ("Import Requirements" / "IRs") for plant commodities. It combines:

- Structured data from the Tasmanian Plant Quarantine Manual (PQM)
- Semantic search capabilities for flexible querying
- State-specific pest presence information
- Clear, consistent response formatting

## Core Components

| Path                            | Purpose                                                                                                                                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pdfs/tas_pqm.pdf`              | Tasmanian Plant Quarantine Manual - 2024 ed. The authoritative source of import requirements. Download at https://nre.tas.gov.au/biosecurity-tasmania/plant-biosecurity/plant-biosecurity-manual |
| `tas_index.py`                  | Creates a searchable index of the PQM by:<br>• Splitting the PDF into 800-token chunks<br>• Generating embeddings with OpenAI<br>• Storing in a FAISS vector database                            |
| `tas_data.py`                   | Manages structured data about:<br>• Commodities and their types<br>• Pest presence by state<br>• Import Requirements (IRs)<br>• ICA equivalents<br>• Phylloxera zones                            |
| `tas_tools.py`                  | Provides the `tas_manual_lookup` tool that:<br>• Combines structured data with semantic search<br>• Formats responses with citations<br>• Handles state-specific requirements                    |
| `agent_setup_tas.py`            | Configures the LangChain agent with:<br>• Zero-shot reasoning capabilities<br>• Structured response formatting<br>• Consistent pre-entry reminders                                               |
| `data/table2.json` _(optional)_ | Machine-readable copy of PQM Table 2 (commodity <-> IR cross-index) for faster lookups.                                                                                                          |
| `.env`                          | Stores API keys (never commit this).                                                                                                                                                             |

## API Configuration

This project uses a **hybrid approach**:

- **OpenAI API**: Used for embeddings (vector search) - Gemini doesn't provide embeddings
- **Google AI API**: Used for text generation (Gemini Pro model)

### Required API Keys

1. **OpenAI API Key** (for embeddings):

   - Get from: https://platform.openai.com/api-keys
   - Used only for creating and searching the vector database

2. **Google AI API Key** (for text generation):
   - Get from: https://makersuite.google.com/app/apikey
   - Used for the main LLM responses

### Environment Setup

Create a `.env` file with:

```
OPENAI_API_KEY=sk-...  # For embeddings only
GOOGLE_API_KEY=...      # For text generation
```

## How It Works

1. **User Query** → e.g., "Can I bring table grapes from NSW to Tasmania?"
2. **Agent Processing**:
   - Identifies the commodity and its type
   - Determines origin state
   - Considers state-specific pest presence
3. **Tool Usage** - `tas_manual_lookup`:
   - First tries structured data lookup
   - Falls back to semantic search if needed
   - Formats response with citations
4. **Response Structure**:

   ```
   Commodity Type: [fruit/plant/seed/etc.]

   Import Requirements:
   • IR 42: [Title] (Section X, Page Y)
   • Applicable ICAs: [List with status]

   Pest Considerations:
   • Relevant pests: [List from Table 1]
   • State-specific presence: [Details]

   Additional Requirements:
   • Special conditions (e.g., phylloxera zones)
   • Treatment requirements

   ⚠️  Pre-entry paperwork reminder...
   ```

## Quick Start

```bash
# 1. Clone the repository
git clone [repo-url]
cd plantpassport-tas

# 2. Set up Python environment (Python >=3.10)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API keys
echo "OPENAI_API_KEY=sk-..." > .env
echo "GOOGLE_API_KEY=..." >> .env

# 5. Build the search index (one-time)
python tas_index.py

# 6. Test the agent
python agent_setup_tas.py
```

## Extending the System

| Task                            | Implementation                                                          |
| ------------------------------- | ----------------------------------------------------------------------- |
| **Add new commodities**         | Update `tas_data.py` with new `CommodityInfo` entries                   |
| **Modify import requirements**  | Update the structured data in `tas_data.py` and rebuild the index       |
| **Add new pest information**    | Update the pest information in `data/table_1.py`                        |
| **Customize response format**   | Modify the agent prompt in `agent_setup_tas.py`                         |
| **Add new lookup capabilities** | Extend `tas_tools.py` with new tools and update the agent configuration |

## Known Limitations

- Semantic search may return incomplete information if the chunk splitter cuts a clause in half
- Some complex requirements may require manual verification
- Area freedom logic is not fully implemented
- Response formatting is fixed to ensure consistency
- Requires both OpenAI and Google AI API keys (hybrid approach)

## Future Enhancements

1. **Improved Search**:

   - Implement better chunk splitting
   - Add cross-reference capabilities
   - Improve citation accuracy

2. **Extended Data**:

   - Complete Table 2 ingestion
   - Add more commodity aliases
   - Include treatment schedules

3. **Enhanced Features**:
   - Add area freedom checks
   - Implement treatment lookup
   - Add validation for common errors

## Credits

Built by Michael G. with ChatGPT and Cursor assistance. Not an official Tasmanian Government product.
