# Edit Agent Documentation

## Overview

The **Edit Agent** is an autonomous code editing agent that can modify existing code files based on:
- Bug fixes identified during code review
- User-directed natural language instructions
- Automated improvements and refactoring

## Features

### 🤖 Autonomous Editing
- Automatically fixes issues found by Code Review Agents
- Integrated into the main code generation workflow
- No user intervention required

### 👤 User-Directed Editing
- Edit specific files with natural language instructions
- Batch edit multiple files simultaneously
- Preview suggestions before applying

### 🔍 Workspace Analysis
- Scan entire workspace for potential improvements
- Identify common issues (print statements, bare except clauses, etc.)
- Generate actionable suggestions

### 🌐 Multi-Language Support
- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- HTML (.html)
- CSS (.css)
- JSON (.json)
- YAML (.yaml, .yml)
- Markdown (.md)

## Workflow Integration

The Edit Agent is automatically integrated into the code generation pipeline:

```
Code Generation → Code Review → Edit Agent (Auto-fix) → Testing → Documentation
```

### When Edit Agent Runs:
1. **After Code Review**: Automatically applies fixes for identified issues
2. **User Request**: On-demand via API or chat commands
3. **Analysis Mode**: Scans workspace and suggests improvements

## API Endpoints

### 1. Edit Single File
**POST** `/api/edit/file`

Edit a specific file with natural language instructions.

```json
{
  "file_path": "backend/app/core/ai_manager.py",
  "instructions": "Fix the bug where temperature parameter is incorrectly passed to API"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully edited backend/app/core/ai_manager.py",
  "file": "backend/app/core/ai_manager.py",
  "changes": {
    "old_lines": 450,
    "new_lines": 451,
    "lines_changed": 1,
    "size_change": 25
  }
}
```

### 2. Batch Edit
**POST** `/api/edit/batch`

Edit multiple files in a single request.

```json
{
  "edits": [
    {
      "file": "backend/app/api/chat.py",
      "instructions": "Remove all unused imports"
    },
    {
      "file": "frontend/src/App.tsx",
      "instructions": "Fix PropTypes warning by adding proper type definitions"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Completed 2/2 edits",
  "success_count": 2,
  "total_requests": 2,
  "results": [...]
}
```

### 3. Analyze Workspace
**POST** `/api/edit/analyze`

Analyze workspace and get suggestions without applying them.

```json
{
  "workspace_path": "/app/xionimus-ai"
}
```

**Response:**
```json
{
  "status": "success",
  "suggestions": [
    {
      "file": "backend/app/core/ai_manager.py",
      "issue": "Using print() instead of logging",
      "severity": "low",
      "suggestion": "Replace print() with proper logging"
    }
  ],
  "files_analyzed": 25
}
```

### 4. Status Check
**GET** `/api/edit/status`

Get Edit Agent status and capabilities.

```json
{
  "status": "active",
  "agent": "Edit Agent",
  "version": "1.0.0",
  "capabilities": [...],
  "supported_languages": [...]
}
```

## Usage Examples

### Example 1: Fix a Bug via Chat

Simply tell the AI:
```
"Edit the file backend/app/core/code_processor.py and fix the regex pattern to handle code blocks without trailing newlines"
```

The Edit Agent will:
1. Read the current file
2. Use Claude to generate the fix
3. Apply the changes
4. Report back with a summary

### Example 2: Autonomous Bug Fixing

When code is generated, the workflow automatically:
1. Generates code
2. Reviews code (Code Review Agents identify issues)
3. **Edit Agent auto-fixes issues**
4. Tests the fixed code
5. Generates documentation

### Example 3: Batch Refactoring

```bash
curl -X POST http://localhost:8001/api/edit/batch \
  -H "Content-Type: application/json" \
  -d '{
    "edits": [
      {"file": "backend/app/api/chat.py", "instructions": "Add type hints to all functions"},
      {"file": "backend/app/api/github.py", "instructions": "Add docstrings to all methods"},
      {"file": "backend/app/core/ai_manager.py", "instructions": "Add error handling for API calls"}
    ]
  }'
```

## How It Works

### 1. File Reading
- Reads current file content
- Identifies file type and language

### 2. AI Generation
- Uses **Claude Sonnet 4.5** (as per project requirements)
- Provides context-aware instructions
- Preserves code style and structure

### 3. Smart Editing
- Maintains all existing functionality
- Applies only requested changes
- Validates syntax before saving

### 4. Change Tracking
- Tracks line changes
- Reports size differences
- Provides edit summaries

## Code Review Integration

The Edit Agent extracts fixable issues from code review feedback:

### From Debug Agent:
- High/Critical severity bugs
- Issues with line numbers and fix suggestions

### From Enhancement Agent:
- Auto-fixable enhancements
- Performance improvements
- Best practice violations

### Example Flow:
```
Code Review finds: "Unused import on line 15"
  ↓
Edit Agent: Automatically removes the import
  ↓
Testing Agent: Verifies code still works
  ↓
Documentation Agent: Updates docs
```

## Configuration

### Environment Variables
- No additional environment variables required
- Uses existing AI provider API keys (ANTHROPIC_API_KEY)

### Workspace Path
- Default: `/app/xionimus-ai`
- Can be overridden per request

## Best Practices

### ✅ Do:
- Provide clear, specific edit instructions
- Test changes after editing
- Review AI-generated edits in critical code
- Use batch editing for similar changes across files

### ❌ Don't:
- Request massive refactoring in a single edit
- Edit files outside workspace
- Override autonomous edits without reviewing
- Edit generated files manually (use Edit Agent instead)

## Error Handling

The Edit Agent handles common errors gracefully:

### File Not Found
```json
{
  "status": "error",
  "message": "File not found: backend/nonexistent.py"
}
```

### Failed to Generate Edit
```json
{
  "status": "error",
  "message": "Failed to generate edit",
  "file": "backend/app/core/broken.py"
}
```

### AI Provider Not Configured
- Falls back to graceful error
- Logs warning for missing API keys
- Returns informative error message

## Future Enhancements

Planned features for future versions:
- [ ] Git diff preview before applying
- [ ] Rollback capability for edits
- [ ] Visual diff in frontend UI
- [ ] Support for more languages (Go, Rust, Java)
- [ ] AI-powered code review before edit
- [ ] Integration with version control

## Technical Details

### Architecture
```
EditAgent
├── autonomous_edit()      # Auto-fix from code review
├── user_directed_edit()   # Manual editing
├── batch_edit()           # Multiple files
├── analyze_and_suggest()  # Workspace analysis
└── _generate_edit()       # AI-powered editing (Claude)
```

### Dependencies
- `aiofiles`: Async file I/O
- `anthropic`: Claude API integration
- `pathlib`: Path handling
- `re`: Pattern matching

### Code Location
- **Core Module**: `/app/backend/app/core/edit_agent.py`
- **API Routes**: `/app/backend/app/api/edit.py`
- **Integration**: `/app/backend/app/api/chat.py` (line ~715)

## Troubleshooting

### Issue: Edits Not Applied
**Solution**: Check backend logs for AI provider errors
```bash
tail -n 50 /var/log/supervisor/backend.err.log
```

### Issue: Wrong Edits Generated
**Solution**: Provide more specific instructions, include line numbers

### Issue: API Key Errors
**Solution**: Ensure ANTHROPIC_API_KEY is set in backend/.env

## Support

For issues or questions:
1. Check backend logs: `/var/log/supervisor/backend.err.log`
2. Review agent status: `GET /api/edit/status`
3. Test with simple edits first
4. Escalate to main development team

---

**Version**: 1.0.0  
**Last Updated**: 2025  
**Maintained by**: Xionimus AI Development Team
