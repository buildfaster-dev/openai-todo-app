# Project Constitution

## Overview

This document establishes the governing principles and development guidelines for the OpenAI Todo App project.

## Core Principles

### 1. OpenAI Apps SDK First
- The application must be designed primarily for integration with OpenAI's ChatGPT via the Apps SDK
- All features should work seamlessly through conversational interfaces
- The MCP (Model Context Protocol) is the backbone of the architecture

### 2. Developer Experience
- Fast, reproducible development environments using Nix
- Modern Python tooling with `uv` for dependency management
- Simple task automation with `just` commands
- Clear, documented APIs and code structure

### 3. Progressive Enhancement
- Start with core functionality (CRUD operations)
- Build in layers from simple to complex
- Each feature should be independently testable
- Maintain backward compatibility

### 4. Modern Stack
- Python 3.11+ for backend services
- FastAPI for high-performance web framework
- Pydantic for robust data validation
- In-memory storage for simplicity (can be extended)

### 5. User Experience
- Beautiful, responsive UI widgets
- Real-time updates and interactivity
- Clear visual feedback (status icons, colors, animations)
- Accessible from both ChatGPT and web browser

### 6. Code Quality
- Type hints throughout the codebase
- Clear separation of concerns (models, storage, server, UI)
- Comprehensive error handling
- Follow Python best practices (PEP 8)

## Technical Constraints

### Must Have
- Stateless HTTP mode for MCP server (for serverless deployment)
- CORS support for cross-origin widget access
- Environment variable configuration (PUBLIC_URL)
- UUID-based todo identification

### Should Have
- JSON serialization for datetime fields
- Proper HTTP status codes
- Request validation with Pydantic
- Clean REST API design

### Nice to Have
- Sample data for demonstration
- Priority-based sorting
- Tag filtering capabilities
- Statistics dashboard

## Development Workflow

### Phases
1. **Foundation**: Core data models and storage
2. **API Layer**: REST endpoints for CRUD operations
3. **MCP Integration**: Tool definitions and handlers
4. **Widget Development**: Interactive HTML components
5. **Polish**: Statistics, filters, and enhanced UX

### Quality Standards
- All features must be tested manually
- Code must be readable and maintainable
- Documentation should be clear and concise
- Commit messages should be descriptive

## Integration Patterns

### OpenAI Apps SDK
- Use `ui://widget/*.html` URI scheme for resources
- Implement `text/html+skybridge` MIME type for widgets
- Include proper metadata (`openai/outputTemplate`, `openai/toolInvocation/*`)
- Support both widget-based and text-based tool responses

### MCP Protocol
- Register tools with proper input schemas
- Provide resources for widget HTML
- Handle tool calls with structured responses
- Support resource templates for dynamic content

## Security Considerations

- CORS is open for development (should be restricted in production)
- Input validation on all endpoints
- No authentication (add as needed for production)
- UUIDs prevent enumeration attacks

## Extensibility Points

The architecture supports extension in several areas:
- Storage backend (can swap to PostgreSQL, MongoDB, etc.)
- Authentication and authorization
- Additional todo fields (attachments, comments, etc.)
- Notification systems
- Collaboration features

## Success Criteria

A successful implementation must:
1. ✅ Work seamlessly in ChatGPT via OpenAI Apps SDK
2. ✅ Provide a beautiful standalone web interface
3. ✅ Support full CRUD operations on todos
4. ✅ Display interactive widgets with real-time updates
5. ✅ Be easy to deploy and configure
6. ✅ Serve as a reference for building OpenAI Apps

---

*This constitution guides all technical decisions and ensures consistency throughout the project lifecycle.*
