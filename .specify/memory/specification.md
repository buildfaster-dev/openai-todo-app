# OpenAI Todo App Specification

## Introduction

This specification defines the functional requirements for building a Todo application integrated with the OpenAI Apps SDK. The requirements are organized incrementally, from basic to advanced features.

---

## Phase 1: Foundation - Data Model

### User Story
As a developer, I need a solid data foundation to represent todos with all necessary attributes.

### Requirements

#### 1.1 Todo Item Structure
A todo must have:
- ✅ **Unique identifier** (UUID)
- ✅ **Title** (required, non-empty string)
- ✅ **Description** (optional text)
- ✅ **Status** (pending, in_progress, completed)
- ✅ **Priority** (low, medium, high)
- ✅ **Timestamps** (created_at, updated_at)
- ✅ **Due date** (optional datetime)
- ✅ **Tags** (list of strings for organization)

#### 1.2 Validation Rules
- Title must be at least 1 character long
- Status must be one of the allowed enum values
- Priority must be one of the allowed enum values
- Timestamps must be valid datetime objects
- Tags must be a list (can be empty)

#### 1.3 Data Models
Provide three model types:
- `TodoItem`: Full todo representation
- `TodoCreate`: Input model for creating todos
- `TodoUpdate`: Partial update model (all fields optional except ID)

---

## Phase 2: Storage Layer

### User Story
As a developer, I need a way to persist and retrieve todo items.

### Requirements

#### 2.1 Basic CRUD Operations
The storage layer must support:
- ✅ **Create**: Add new todo with generated UUID
- ✅ **Read**: Get todo by ID
- ✅ **Update**: Modify todo fields (partial updates supported)
- ✅ **Delete**: Remove todo by ID
- ✅ **List**: Get all todos

#### 2.2 Filtering Capabilities
- ✅ Filter todos by status (pending/in_progress/completed)
- ✅ Filter todos by tag
- ✅ Sort by priority (high first) and creation date

#### 2.3 Statistics
Provide aggregated data:
- ✅ Total count of todos
- ✅ Count by status (pending, in_progress, completed)
- ✅ Count of high priority items

#### 2.4 Sample Data
- ✅ Initialize with 3 sample todos for demonstration
- ✅ Sample todos should showcase different priorities and statuses

---

## Phase 3: REST API

### User Story
As a client application, I need HTTP endpoints to interact with todos.

### Requirements

#### 3.1 Todo Endpoints
- ✅ `GET /api/todos` - List all todos (with optional status/tag filters)
- ✅ `POST /api/todos` - Create new todo
- ✅ `GET /api/todos/{id}` - Get specific todo
- ✅ `PATCH /api/todos/{id}` - Update todo (partial updates)
- ✅ `DELETE /api/todos/{id}` - Delete todo

#### 3.2 Statistics Endpoint
- ✅ `GET /api/stats` - Get todo statistics

#### 3.3 HTTP Standards
- ✅ Proper status codes (200, 201, 404, etc.)
- ✅ JSON request/response format
- ✅ Error messages for not found resources
- ✅ CORS headers for cross-origin access

#### 3.4 Request Validation
- ✅ Validate incoming JSON against Pydantic models
- ✅ Return clear error messages for invalid data
- ✅ Handle enum conversions (string to enum)

---

## Phase 4: MCP Server Integration

### User Story
As ChatGPT, I need MCP tools to manage todos through conversation.

### Requirements

#### 4.1 MCP Tools - Basic Operations
Define tools for:
- ✅ **create_todo**: Create todo with title, description, priority
- ✅ **list_todos**: List todos with optional status filter
- ✅ **get_todo**: Get specific todo by ID
- ✅ **update_todo**: Update todo status or title
- ✅ **delete_todo**: Delete todo by ID

#### 4.2 Tool Metadata
Each tool must have:
- ✅ Clear name and title
- ✅ Descriptive text explaining what it does
- ✅ JSON schema for input validation
- ✅ Proper annotations (destructiveHint, readOnlyHint)

#### 4.3 Tool Responses
- ✅ Text content for conversational feedback
- ✅ Structured content with full data payload
- ✅ Error handling with isError flag
- ✅ Appropriate success messages

#### 4.4 Stateless HTTP Mode
- ✅ MCP server must support stateless HTTP transport
- ✅ All state managed server-side (not in MCP session)
- ✅ Works with OpenAI Apps SDK architecture

---

## Phase 5: Widget System - Basic Widgets

### User Story
As a ChatGPT user, I want to see beautiful visual interfaces for my todos.

### Requirements

#### 5.1 Widget Resources
- ✅ Define `ui://widget/todo-app.html` resource
- ✅ Define `ui://widget/todo-stats.html` resource
- ✅ Use `text/html+skybridge` MIME type
- ✅ Register resources with MCP server

#### 5.2 Widget Tools
Create tools that display widgets:
- ✅ **show_todo_app**: Display full todo list interface
- ✅ **show_todo_stats**: Display statistics dashboard

#### 5.3 OpenAI Metadata
Each widget tool must include:
- ✅ `openai/outputTemplate`: URI to widget resource
- ✅ `openai/toolInvocation/invoking`: Loading message
- ✅ `openai/toolInvocation/invoked`: Success message
- ✅ `openai/widgetAccessible`: true
- ✅ `openai/resultCanProduceWidget`: true

#### 5.4 Static Widget Display
- ✅ Show todos in a formatted list
- ✅ Display status icons (✅ ⏳ 📝)
- ✅ Color-code by priority (red=high, orange=medium, blue=low)
- ✅ Show statistics in card layout

---

## Phase 6: Interactive Widgets

### User Story
As a user, I want to interact with todos directly in the widget without leaving ChatGPT.

### Requirements

#### 6.1 Interactive Todo List Widget
The todo-app widget must support:
- ✅ **View all todos** with status and priority indicators
- ✅ **Add new todos** via inline form
- ✅ **Update status** with quick action buttons
- ✅ **Edit todo** title and description inline
- ✅ **Delete todos** with confirmation
- ✅ **Filter by status** (all, pending, in_progress, completed)

#### 6.2 Widget Form Fields
Add todo form should have:
- ✅ Title input (required)
- ✅ Description input (optional)
- ✅ Priority selector (low/medium/high)
- ✅ Submit button with clear action

#### 6.3 Action Buttons
Each todo should display context-appropriate buttons:
- ✅ "In Progress" button (if not already in progress)
- ✅ "Complete" button (if not completed)
- ✅ "Reopen" button (if completed)
- ✅ "Edit" button (always)
- ✅ "Delete" button (always with confirmation)

#### 6.4 Real-time Updates
- ✅ Update todo list after any action
- ✅ Refresh statistics after changes
- ✅ Show loading states during API calls
- ✅ Display error messages for failed operations

#### 6.5 Inline Editing
- ✅ Click "Edit" to show edit form
- ✅ Edit form shows current title and description
- ✅ Save/Cancel buttons for the edit form
- ✅ Update UI without full page reload

---

## Phase 7: Statistics Dashboard Widget

### User Story
As a user, I want visual insights into my todo completion progress.

### Requirements

#### 7.1 Statistics Cards
Display cards showing:
- ✅ Total todos count
- ✅ Pending todos count
- ✅ In progress todos count
- ✅ Completed todos count

#### 7.2 Visual Progress
- ✅ Progress bar showing completion percentage
- ✅ Percentage text overlay on progress bar
- ✅ Gradient styling for visual appeal

#### 7.3 Insights Section
- ✅ Text descriptions of current status
- ✅ Count of tasks in each status with proper pluralization
- ✅ Celebration message when all tasks completed

#### 7.4 Interactive Features
- ✅ Refresh button to reload statistics
- ✅ Smooth animations and transitions
- ✅ Hover effects on cards

---

## Phase 8: Enhanced User Experience

### User Story
As a user, I want a polished, professional interface with great UX.

### Requirements

#### 8.1 Visual Design
- ✅ Modern, clean aesthetic with gradient accents
- ✅ Consistent color scheme (purple/blue gradient)
- ✅ Proper spacing and typography
- ✅ Responsive layout

#### 8.2 Status Icons
- ✅ 📝 for pending todos
- ✅ ⏳ for in-progress todos
- ✅ ✅ for completed todos
- ✅ Consistent icon usage throughout

#### 8.3 Priority Visual Indicators
- ✅ Red border for high priority
- ✅ Orange border for medium priority
- ✅ Blue border for low priority
- ✅ Border on left side of todo items

#### 8.4 Interactive Feedback
- ✅ Hover states on buttons
- ✅ Focus states on inputs
- ✅ Loading indicators during operations
- ✅ Success/error alerts

#### 8.5 Keyboard Support
- ✅ Enter key to submit new todo
- ✅ Tab navigation through forms
- ✅ Escape to cancel operations

---

## Phase 9: Configuration & Deployment

### User Story
As a developer, I need to deploy this app with proper configuration.

### Requirements

#### 9.1 Environment Configuration
- ✅ `PUBLIC_URL` environment variable for widget API calls
- ✅ Fallback to localhost for local development
- ✅ Load environment variables from .env file

#### 9.2 CORS Configuration
- ✅ Allow all origins for development
- ✅ Support OPTIONS preflight requests
- ✅ Include proper CORS headers

#### 9.3 Public URL Integration
- ✅ Widget HTML includes dynamic API_BASE from PUBLIC_URL
- ✅ All fetch calls use configurable base URL
- ✅ Works with ngrok or other tunneling services

#### 9.4 Documentation
- ✅ README with setup instructions
- ✅ OpenAI Apps SDK integration guide
- ✅ Environment variable documentation
- ✅ API endpoint documentation

---

## Non-Functional Requirements

### Performance
- Widget should load in under 1 second
- API responses should be under 100ms (in-memory storage)
- Support at least 1000 todos without performance degradation

### Reliability
- Proper error handling on all endpoints
- Graceful degradation if API calls fail
- Input validation prevents invalid data

### Usability
- Intuitive interface requiring no training
- Clear visual feedback for all actions
- Mobile-responsive design

### Maintainability
- Clean separation of concerns
- Type hints throughout
- Clear code comments and documentation
- Follows Python best practices

---

## Out of Scope (Future Enhancements)

The following features are NOT included in this version but could be added later:

- User authentication and authorization
- Persistent database storage
- Todo sharing and collaboration
- Recurring todos
- Todo attachments
- Comments and activity log
- Email notifications
- Mobile native apps
- Offline support
- Search functionality
- Bulk operations
- Categories/projects
- Time tracking
- Subtasks

---

## Acceptance Criteria

The application is considered complete when:

1. ✅ All Phase 1-9 requirements are implemented
2. ✅ ChatGPT can create, view, update, and delete todos via conversation
3. ✅ Widget displays correctly in ChatGPT interface
4. ✅ Interactive features work without page reloads
5. ✅ Statistics update in real-time
6. ✅ Application runs locally with `just dev`
7. ✅ Application works with ngrok tunnel for ChatGPT access
8. ✅ Documentation is clear and complete
9. ✅ No critical bugs or errors in normal usage
10. ✅ Code follows project constitution principles

---

*This specification serves as the source of truth for what the OpenAI Todo App should do and how it should behave.*
