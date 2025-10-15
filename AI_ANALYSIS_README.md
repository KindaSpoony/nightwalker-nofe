# AI Analysis Integration

This document explains how AI analysis is integrated into the NOFE pipeline to enhance CHAOS reports with AI-powered insights.

## Overview

The NOFE pipeline now includes optional AI analysis capability that:
- Uses OpenAI's API to analyze CHAOS reports
- Provides executive-level insights and geopolitical analysis
- Gracefully handles missing API credentials
- Supports both inline and separate file output modes

## Configuration

AI analysis is controlled by settings in `src/config.yaml`:

```yaml
# AI analysis settings
enable_ai_analysis: true        # Enable/disable AI analysis
ai_analysis_inline: false      # Inline vs separate file output
ai_model: "GPT-5"              # OpenAI model to use (optional)
```

### Settings Explained

- **`enable_ai_analysis`**: When `true`, the pipeline will attempt to generate AI analysis for each CHAOS report
- **`ai_analysis_inline`**: 
  - `false`: Creates separate `AI_CHAOS_YYYYMMDD.md` files
  - `true`: Appends AI analysis to the main CHAOS report
- **`ai_model`**: Specifies which OpenAI model to use (defaults to "GPT-5")

## API Key Setup

The AI analysis requires an OpenAI API key. You can provide it in two ways:

### Environment Variable (Recommended)
```bash
export OPENAI_API_KEY=your_api_key_here
python -m nofe.pipeline
```

### Configuration File
Add to `src/nofe/config.yaml`:
```yaml
openai_api_key: your_api_key_here
```

## Usage

### Basic Pipeline Execution
```bash
# With AI analysis enabled (requires OPENAI_API_KEY)
cd nightwalker-nofe
python src/nofe/pipeline.py
```

### Standalone AI Analysis
You can also run AI analysis on existing CHAOS reports:

```bash
# Analyze an existing report
python src/nofe/ai_analysis.py reports/CHAOS_20250819.md

# Specify custom output path
python src/nofe/ai_analysis.py reports/CHAOS_20250819.md --output_path custom_analysis.md
```

## Output Formats

### Separate File Mode (`ai_analysis_inline: false`)
- Main report: `reports/CHAOS_YYYYMMDD.md`
- AI analysis: `reports/AI_CHAOS_YYYYMMDD.md`

### Inline Mode (`ai_analysis_inline: true`)
- Combined report: `reports/CHAOS_YYYYMMDD.md` (includes AI analysis section)

## AI Analysis Content

The AI analysis provides:
- **Executive Summary**: Key insights and implications
- **Geopolitical Risk Assessment**: Regional and global security concerns
- **Entity Cross-References**: Connections between mentioned entities
- **Misinformation Flags**: Potential issues with information reliability
- **Follow-up Questions**: Suggested areas for deeper investigation

## Error Handling

The system gracefully handles various scenarios:

- **Missing API Key**: Returns "AI analysis skipped: missing OPENAI_API_KEY."
- **API Errors**: Falls back from new OpenAI SDK to legacy SDK if needed
- **Rate Limits**: Basic error handling for API rate limiting
- **Large Reports**: Automatically truncates input to 120,000 characters

## Testing

Use the included test script to verify functionality:

```bash
# Test without API key (fallback mode)
python test_ai_integration.py

# Test with API key (full functionality)
OPENAI_API_KEY=your_key_here python test_ai_integration.py
```

## Integration Details

The AI analysis is integrated at the pipeline level in `src/nofe/pipeline.py`:

1. After generating the standard CHAOS report
2. Check if `enable_ai_analysis` is true
3. Call `generate_ai_analysis()` with the report content
4. Output results based on `ai_analysis_inline` setting

## Security Notes

- API keys are read from environment variables or config files
- No API keys are logged or stored in generated reports
- Report content is truncated to prevent excessive API usage
- All API calls include reasonable timeout and error handling

## Troubleshooting

### AI Analysis Not Generated
1. Check that `enable_ai_analysis: true` in config
2. Verify OPENAI_API_KEY is set
3. Check console output for error messages

### API Key Issues
- Ensure the API key is valid and has sufficient credits
- Check for any firewall or network restrictions
- Verify the API key has access to the specified model

### Output Format Issues
- Check the `ai_analysis_inline` setting
- Verify write permissions to the reports directory
- Ensure sufficient disk space for output files