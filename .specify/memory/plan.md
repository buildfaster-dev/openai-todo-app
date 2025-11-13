# Implementation Plan

## Overview

This document outlines the technical implementation strategy for the OpenAI Todo App, translating the specification into concrete technical decisions and architecture.

---

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Web Framework**: FastAPI (high-performance, async support)
- **Data Validation**: Pydantic v2 (type safety, JSON schemas)
- **MCP SDK**: FastMCP from official Python MCP SDK
- **ASGI Server**: Uvicorn (for FastAPI)

### Frontend (Widgets)
- **Framework**: Vanilla JavaScript (no build step needed)
- **Styling**: Inline CSS (self-contained widgets)
- **API Communication**: Fetch API

### Development Tools
- **Package Manager**: uv (fast, modern Python dependency manager)
- **Environment**: Nix (reproducible development environment)
- **Task Runner**: just (command runner)
- **Tunneling**: ngrok (expose local server)

### Storage
- **Type**: In-memory Python dict
- **Rationale**: Simple, fast, suitable for prototype/demo
- **Extension Path**: Can swap to PostgreSQL, MongoDB, Redis later

---

## Project Structure

```
openai-todo-app/
├── src/todo_app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI app + REST routes + CORS
│   ├── mcp_server.py         # MCP server + tools + widgets
│   ├── models.py             # Pydantic data models
│   ├── storage.py            # In-memory storage implementation
│   └── ui_components.py      # UI component helpers (legacy)
├── .specify/
│   ├── memory/
│   │   ├── constitution.md   # Project principles
│   │   ├── specification.md  # Functional requirements
│   │   └── plan.md          # This file
│   └── tasks/               # Implementation tasks
├── pyproject.toml           # Python dependencies
├── justfile                 # Task automation
├── shell.nix / flake.nix    # Nix environment
├── ngrok.yml                # ngrok configuration
└── README.md                # User documentation
```

---

## Implementation Phases

### Phase 1: Data Models (`models.py`)

#### TodoStatus Enum
```python
class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

#### TodoPriority Enum
```python
class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

#### TodoItem Model
Full representation with all fields:
- `id: str` - UUID identifier
- `title: str` - Required title
- `description: Optional[str]` - Optional description
- `status: TodoStatus` - Current status (default: PENDING)
- `priority: TodoPriority` - Priority level (default: MEDIUM)
- `created_at: datetime` - Auto-generated
- `updated_at: datetime` - Auto-generated
- `due_date: Optional[datetime]` - Optional deadline
- `tags: list[str]` - List of tags (default: empty)

#### TodoCreate Model
Input model for creating todos:
- Required: `title`
- Optional: `description`, `priority`, `due_date`, `tags`

#### TodoUpdate Model
Partial update model:
- All fields optional (except implicitly the ID from the path)

**Key Decision**: Use `model_dump(mode='json')` for datetime serialization to JSON-compatible format.

---

### Phase 2: Storage Layer (`storage.py`)

#### TodoStorage Class
Singleton class managing in-memory storage.

##### Data Structure
```python
self._todos: Dict[str, TodoItem] = {}
```

##### Methods
- `create(todo_create: TodoCreate) -> TodoItem`
  - Generate UUID
  - Create TodoItem instance
  - Store in dict
  - Return created item

- `get(todo_id: str) -> Optional[TodoItem]`
  - Simple dict lookup
  - Return None if not found

- `list(status: Optional[TodoStatus], tag: Optional[str]) -> List[TodoItem]`
  - Get all todos
  - Filter by status if provided
  - Filter by tag if provided
  - Sort by priority (high→low) then created_at

- `update(todo_id: str, todo_update: TodoUpdate) -> Optional[TodoItem]`
  - Get todo from dict
  - Update fields from TodoUpdate (using model_dump exclude_unset)
  - Update `updated_at` timestamp
  - Return updated item or None

- `delete(todo_id: str) -> bool`
  - Remove from dict if exists
  - Return success/failure

- `get_stats() -> dict`
  - Count totals by status
  - Count high priority items
  - Return dict with statistics

##### Sample Data
Initialize with 3 sample todos demonstrating:
- Different priorities
- Development/setup related items
- Relevant tags

**Global Instance**: Create `storage = TodoStorage()` for singleton access.

---

### Phase 3: REST API (`main.py`)

#### FastAPI Application
Base application with CORS middleware.

#### Endpoints

##### GET /api/todos
```python
async def get_todos(request: Request) -> JSONResponse
```
- Extract query params: `status`, `tag`
- Convert status string to enum if present
- Call `storage.list(status, tag)`
- Return JSON array of todos

##### POST /api/todos
```python
async def create_todo_endpoint(request: Request) -> JSONResponse
```
- Parse JSON body
- Validate with TodoCreate
- Call `storage.create()`
- Return 201 with created todo

##### GET /api/todos/{todo_id}
```python
async def get_todo(request: Request) -> JSONResponse
```
- Extract todo_id from path
- Call `storage.get(todo_id)`
- Return 404 if not found
- Return todo JSON

##### PATCH /api/todos/{todo_id}
```python
async def update_todo_endpoint(request: Request) -> JSONResponse
```
- Extract todo_id from path
- Parse JSON body
- Convert status string to enum if present
- Validate with TodoUpdate
- Call `storage.update()`
- Return 404 if not found
- Return updated todo

##### DELETE /api/todos/{todo_id}
```python
async def delete_todo_endpoint(request: Request) -> JSONResponse
```
- Extract todo_id from path
- Call `storage.delete()`
- Return 404 if not found
- Return success message

##### GET /api/stats
```python
async def get_stats(request: Request) -> JSONResponse
```
- Call `storage.get_stats()`
- Return statistics dict

#### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Phase 4: MCP Server Integration (`mcp_server.py`)

#### FastMCP Initialization
```python
mcp = FastMCP(
    name="openai-todo-app",
    stateless_http=True,  # Critical for OpenAI Apps SDK
)
```

#### Tool Input Schemas
Pydantic models for tool validation:
- `CreateTodoInput`: title, description, priority
- `UpdateTodoInput`: todoId (alias), status, title
- `DeleteTodoInput`: todoId (alias)
- `GetTodoInput`: todoId (alias)

**Key Decision**: Use `alias="todoId"` with `populate_by_name=True` for camelCase compatibility with OpenAI.

#### Tool Definitions

##### Regular Tools
Register 5 basic MCP tools using `@mcp._mcp_server.list_tools()`:

1. **create_todo**
   - Input: title (required), description, priority
   - Action: Create new todo
   - Response: Text + structured todo object

2. **list_todos**
   - Input: status (optional filter)
   - Action: List todos
   - Response: Text + structured array + count

3. **get_todo**
   - Input: todoId
   - Action: Get specific todo
   - Response: Text + structured todo object
   - Error handling: isError=True if not found

4. **update_todo**
   - Input: todoId, status, title
   - Action: Update todo
   - Response: Text + structured updated todo
   - Error handling: isError=True if not found

5. **delete_todo**
   - Input: todoId
   - Action: Delete todo
   - Response: Success message
   - Error handling: isError=True if not found
   - Annotation: destructiveHint=True

##### Widget-Based Tools
Register 2 widget tools:

1. **show_todo_app**
   - Display full interactive todo list
   - Links to `ui://widget/todo-app.html`
   - Metadata: outputTemplate, toolInvocation messages

2. **show_todo_stats**
   - Display statistics dashboard
   - Links to `ui://widget/todo-stats.html`
   - Metadata: outputTemplate, toolInvocation messages

#### Widget Configuration
```python
@dataclass(frozen=True)
class TodoWidget:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    response_text: str
```

#### OpenAI Metadata Helper
```python
def _tool_meta(widget: TodoWidget) -> Dict[str, Any]:
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }
```

#### Resource Handlers

##### List Resources
Register widget HTML resources:
```python
@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]
```
- Return resource definitions for each widget
- MIME type: `text/html+skybridge`

##### Read Resource
Handle resource read requests:
```python
async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult
```
- Match URI to widget
- Generate HTML (call helper functions)
- Return HTML with proper MIME type and metadata

#### Tool Call Handler
```python
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult
```
- Route tool calls to appropriate handlers
- Widget tools: return todos + stats with metadata
- Regular tools: perform CRUD operations
- Error handling: ValidationError, general exceptions

---

### Phase 5: Widget HTML Generation

#### Widget: Todo List (`_get_todo_list_html()`)

##### Server-Side Generation
- Fetch all todos: `storage.list()`
- Fetch stats: `storage.get_stats()`
- Serialize to JSON for JavaScript
- Inject into HTML template

##### HTML Structure
- **Header**: "📝 Your Todo App"
- **Stats Cards**: 4 cards (total, pending, in_progress, completed)
- **Add Todo Form**: Title, description, priority fields + submit button
- **Filters**: Buttons for all/pending/in_progress/completed
- **Todo List**: Dynamic rendering of todos

##### CSS Styling
- Gradient cards for stats (purple/blue)
- Priority color-coding on left border (red/orange/blue)
- Form styling with focus states
- Button variations (primary, success, danger, secondary)
- Responsive grid layout

##### JavaScript Functionality

**State Management:**
```javascript
let todos = {initial_todos_json};
let currentFilter = 'all';
let editingId = null;
const API_BASE = '{PUBLIC_URL}/api';
```

**Core Functions:**
- `renderTodos()`: Render filtered todo list
- `filterTodos(filter)`: Update filter and re-render
- `addTodo()`: POST to /api/todos
- `updateStatus(id, status)`: PATCH status update
- `deleteTodo(id)`: DELETE with confirmation
- `startEdit(id)`: Show inline edit form
- `saveEdit(id)`: PATCH title/description
- `cancelEdit(id)`: Hide edit form
- `loadStats()`: Refresh statistics display

**Real-time Updates:**
- After each mutation (add/update/delete):
  1. Update local todos array
  2. Call `loadStats()` to refresh statistics
  3. Call `renderTodos()` to update UI

**Keyboard Support:**
- Enter key on title input triggers addTodo()

#### Widget: Statistics (`_get_stats_html()`)

##### Server-Side Generation
- Fetch stats: `storage.get_stats()`
- Calculate completion percentage
- Inject into HTML template

##### HTML Structure
- **Header**: "📊 Todo Statistics" + Refresh button
- **Stats Grid**: 4 stat cards (2x2 grid)
- **Progress Section**: Progress bar with percentage
- **Insights**: Text descriptions with task counts

##### CSS Styling
- Large stat cards with gradient backgrounds
- Animated progress bar with gradient fill
- Hover effects and transitions

##### JavaScript Functionality

**Core Functions:**
- `refreshStats()`: Fetch fresh stats from /api/stats
  - Update stat numbers
  - Update progress bar width and text
  - Regenerate insights HTML
  - Error handling

**Dynamic Content:**
- Progress bar percentage calculation
- Pluralization (task vs tasks)
- Celebration message when 100% complete

---

### Phase 6: Application Assembly (`main.py`)

#### MCP + REST Integration
```python
# Get MCP app
app = mcp.streamable_http_app()

# Add REST routes
app.routes.extend([...])

# Add CORS middleware
app.add_middleware(CORSMiddleware, ...)
```

**Key Decision**: MCP server provides base Starlette app, we extend it with REST API routes.

#### MCP Endpoint
- Automatically served at `/mcp` by FastMCP
- Handles MCP protocol (tools, resources)

#### REST Endpoints
- Served at `/api/*`
- Enable widget interactivity

---

## Configuration & Environment

### Environment Variables

#### PUBLIC_URL
```python
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")
```

**Usage:**
- Injected into widget HTML as `API_BASE`
- All widget fetch calls use this URL
- Must be set to ngrok URL for ChatGPT access

**Setup:**
1. Set in `.env` file or environment
2. For local dev: `http://localhost:8000`
3. For ngrok: `https://your-id.ngrok.io`

### Load Environment
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Development Workflow

### Setup Commands

```bash
# Enter Nix environment
nix-shell  # or: nix develop

# Initialize project
just init

# Start development server
just dev

# Start ngrok tunnel
just tunnel
```

### Running the Server

**Local:**
```bash
uvicorn src.todo_app.main:app --reload --host 0.0.0.0 --port 8000
```

**With ngrok:**
1. Start server: `just dev`
2. In another terminal: `just tunnel`
3. Copy ngrok HTTPS URL
4. Set PUBLIC_URL to ngrok URL
5. Restart server

### Testing Flow

1. **Local Web UI**: Visit http://localhost:8000
2. **API Testing**: Use curl or Postman on /api endpoints
3. **MCP Testing**: Point MCP client to http://localhost:8000/mcp
4. **ChatGPT Integration**:
   - Use ngrok URL
   - Configure in OpenAI Apps platform
   - Test in ChatGPT

---

## Key Technical Decisions

### 1. Stateless HTTP for MCP
**Decision**: Use `stateless_http=True` in FastMCP
**Rationale**: Required for serverless deployment and OpenAI Apps SDK compatibility
**Impact**: All state managed server-side, not in MCP session

### 2. Single Starlette App
**Decision**: Extend MCP's Starlette app with REST routes
**Rationale**: Single process, single port, easier deployment
**Impact**: Both MCP and REST API served from same application

### 3. In-Memory Storage
**Decision**: Use Python dict for storage
**Rationale**: Simple, fast, suitable for prototype
**Trade-off**: Data lost on restart (acceptable for demo)
**Extension**: Easy to swap to database later

### 4. Inline Widget JavaScript
**Decision**: Embed JavaScript directly in HTML strings
**Rationale**: Self-contained widgets, no build step
**Trade-off**: Harder to maintain than separate files
**Benefit**: Widgets work anywhere, easy to debug

### 5. Dynamic API_BASE
**Decision**: Inject PUBLIC_URL into widget HTML
**Rationale**: Widgets work in both local and ngrok environments
**Benefit**: No hardcoded URLs, flexible deployment

### 6. CORS Open Policy
**Decision**: Allow all origins in development
**Rationale**: Widgets may be served from ChatGPT domains
**Production Note**: Should be restricted to known origins

### 7. JSON Mode for Serialization
**Decision**: Use `model_dump(mode='json')` everywhere
**Rationale**: Proper datetime serialization to ISO format
**Impact**: All timestamps are JSON-compatible strings

### 8. UUID Identifiers
**Decision**: Use UUIDs instead of auto-incrementing IDs
**Rationale**:
- No enumeration attacks
- Globally unique
- No database-specific logic needed

---

## Error Handling Strategy

### API Level
- 404 for resource not found
- 400 for validation errors (Pydantic)
- 200 for successful GET/PATCH/DELETE
- 201 for successful POST

### MCP Level
- `isError=True` in CallToolResult for errors
- Structured error messages in text content
- ValidationError handling for input schemas

### Widget Level
- Try-catch around all fetch calls
- Alert user on errors
- Console.error for debugging
- Loading states while fetching

---

## Performance Considerations

### Backend
- In-memory storage: O(1) lookups, O(n) list operations
- FastAPI async handlers for concurrent requests
- Uvicorn ASGI server for high throughput

### Frontend
- Minimal JavaScript, no frameworks
- Direct DOM manipulation
- Local state management (no Redux needed)
- Batch updates (loadStats + renderTodos)

### Network
- REST API calls only when needed
- No polling (user-initiated updates)
- JSON payloads kept small

---

## Testing Strategy

### Manual Testing Checklist

#### REST API
- [ ] Create todo via POST
- [ ] List todos via GET
- [ ] Filter by status
- [ ] Update todo via PATCH
- [ ] Delete todo via DELETE
- [ ] Get stats via GET
- [ ] Test 404 responses
- [ ] Test validation errors

#### MCP Tools
- [ ] Call create_todo tool
- [ ] Call list_todos tool
- [ ] Call update_todo tool
- [ ] Call delete_todo tool
- [ ] Call show_todo_app tool
- [ ] Call show_todo_stats tool

#### Widgets - Todo App
- [ ] View todos list
- [ ] Add new todo
- [ ] Filter by status
- [ ] Update todo status
- [ ] Edit todo inline
- [ ] Delete todo
- [ ] Verify stats update

#### Widgets - Statistics
- [ ] View statistics
- [ ] Verify progress bar
- [ ] Test refresh button
- [ ] Check completion message

#### ChatGPT Integration
- [ ] Widget displays correctly
- [ ] Can interact with widgets
- [ ] Tools work via conversation
- [ ] Metadata displays properly

---

## Deployment Considerations

### Local Development
- Use `just dev` command
- Access at http://localhost:8000
- No PUBLIC_URL needed (defaults to localhost)

### ngrok Deployment
1. Set NGROK_AUTHTOKEN in environment
2. Run `just tunnel`
3. Set PUBLIC_URL to ngrok HTTPS URL
4. Restart server
5. Configure in OpenAI Apps platform

### Production Deployment
Would require:
- Database instead of in-memory storage
- Restricted CORS policy
- Authentication/authorization
- HTTPS/SSL certificates
- Environment-based configuration
- Logging and monitoring
- Rate limiting
- Error tracking (Sentry)

---

## Extension Points

The architecture supports future enhancements:

### Storage Backend
Replace `TodoStorage` with:
- SQLAlchemy + PostgreSQL
- MongoDB with Motor (async)
- Redis for caching
- SQLite for simple persistence

### Authentication
Add middleware:
- JWT token validation
- OAuth integration
- User-scoped storage

### Features
- WebSocket for real-time sync
- Batch operations endpoint
- Search/filter API
- Export/import functionality

### Monitoring
- Prometheus metrics
- Structured logging
- APM integration
- Health check endpoints

---

## Success Metrics

Implementation is successful when:

1. ✅ All 5 MCP tools work correctly
2. ✅ Both widgets display and function in ChatGPT
3. ✅ REST API passes all manual tests
4. ✅ Widgets support full CRUD operations
5. ✅ Statistics update in real-time
6. ✅ Application starts with `just dev`
7. ✅ Works with ngrok tunnel
8. ✅ No errors in console during normal operation
9. ✅ Code passes linting checks
10. ✅ Documentation is complete and accurate

---

*This implementation plan provides the technical blueprint for building the OpenAI Todo App according to the specification and constitution.*
