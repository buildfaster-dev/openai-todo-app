# Implementation Tasks

This document breaks down the implementation into actionable tasks, following the phases defined in the specification and plan.

---

## Phase 1: Foundation - Data Models

### Task 1.1: Create Enums
- [ ] Define `TodoStatus` enum (pending, in_progress, completed)
- [ ] Define `TodoPriority` enum (low, medium, high)

### Task 1.2: Create Data Models
- [ ] Implement `TodoItem` model with all fields
- [ ] Implement `TodoCreate` model for input
- [ ] Implement `TodoUpdate` model for partial updates
- [ ] Add field validation and descriptions
- [ ] Configure JSON schema examples

### Task 1.3: Test Models
- [ ] Test model instantiation
- [ ] Test validation rules
- [ ] Test JSON serialization with datetime fields

**Status**: ✅ Completed

---

## Phase 2: Storage Layer

### Task 2.1: Create Storage Class
- [ ] Implement `TodoStorage` class
- [ ] Initialize empty todos dictionary
- [ ] Create global storage instance

### Task 2.2: Implement CRUD Operations
- [ ] Implement `create()` method with UUID generation
- [ ] Implement `get()` method for single todo lookup
- [ ] Implement `list()` method with filtering
- [ ] Implement `update()` method with partial updates
- [ ] Implement `delete()` method

### Task 2.3: Add Statistics
- [ ] Implement `get_stats()` method
- [ ] Calculate counts by status
- [ ] Calculate high priority count

### Task 2.4: Add Sample Data
- [ ] Create `_initialize_sample_data()` method
- [ ] Add 3 sample todos demonstrating features

**Status**: ✅ Completed

---

## Phase 3: REST API

### Task 3.1: Setup FastAPI Application
- [ ] Create FastAPI app instance
- [ ] Import necessary models and storage

### Task 3.2: Implement Todo Endpoints
- [ ] Create `GET /api/todos` endpoint with filters
- [ ] Create `POST /api/todos` endpoint
- [ ] Create `GET /api/todos/{id}` endpoint
- [ ] Create `PATCH /api/todos/{id}` endpoint
- [ ] Create `DELETE /api/todos/{id}` endpoint

### Task 3.3: Implement Stats Endpoint
- [ ] Create `GET /api/stats` endpoint

### Task 3.4: Add CORS Middleware
- [ ] Configure CORS to allow all origins
- [ ] Set proper CORS headers

### Task 3.5: Test REST API
- [ ] Test each endpoint with curl
- [ ] Verify status codes
- [ ] Test error cases (404, validation)

**Status**: ✅ Completed

---

## Phase 4: MCP Server Integration

### Task 4.1: Initialize MCP Server
- [ ] Install FastMCP SDK
- [ ] Create `mcp` instance with stateless_http=True
- [ ] Configure server name

### Task 4.2: Create Input Schemas
- [ ] Define `CreateTodoInput` model
- [ ] Define `UpdateTodoInput` model with alias
- [ ] Define `DeleteTodoInput` model
- [ ] Define `GetTodoInput` model

### Task 4.3: Implement Tool Handlers
- [ ] Implement `create_todo` tool handler
- [ ] Implement `list_todos` tool handler
- [ ] Implement `get_todo` tool handler
- [ ] Implement `update_todo` tool handler
- [ ] Implement `delete_todo` tool handler

### Task 4.4: Register Tools
- [ ] Create `_list_tools()` handler
- [ ] Register all 5 basic tools with proper schemas
- [ ] Add tool annotations (destructiveHint, readOnlyHint)

### Task 4.5: Implement Tool Call Handler
- [ ] Create `_call_tool_request()` handler
- [ ] Route calls to appropriate tool logic
- [ ] Add error handling (ValidationError, exceptions)
- [ ] Return proper CallToolResult structures

**Status**: ✅ Completed

---

## Phase 5: Widget System - Basic Widgets

### Task 5.1: Define Widget Configuration
- [ ] Create `TodoWidget` dataclass
- [ ] Define widget list (todo-app, todo-stats)
- [ ] Create widget lookup dictionaries

### Task 5.2: Create Widget Metadata Helper
- [ ] Implement `_tool_meta()` function
- [ ] Add all OpenAI metadata fields

### Task 5.3: Implement Resource Handlers
- [ ] Create `_list_resources()` handler
- [ ] Create `_list_resource_templates()` handler
- [ ] Create `_handle_read_resource()` handler

### Task 5.4: Register Widget Tools
- [ ] Add `show_todo_app` to tool list
- [ ] Add `show_todo_stats` to tool list
- [ ] Include widget metadata in tool definitions

### Task 5.5: Create Basic HTML Templates
- [ ] Create `_get_todo_list_html()` stub
- [ ] Create `_get_stats_html()` stub
- [ ] Test resource serving

**Status**: ✅ Completed

---

## Phase 6: Interactive Todo List Widget

### Task 6.1: Design Widget HTML Structure
- [ ] Create header section
- [ ] Create stats cards section
- [ ] Create add todo form
- [ ] Create filters section
- [ ] Create todos list container

### Task 6.2: Style Widget with CSS
- [ ] Style header and typography
- [ ] Style stats cards with gradients
- [ ] Style form inputs and buttons
- [ ] Style filter buttons
- [ ] Style todo items with priority colors

### Task 6.3: Implement Core JavaScript Functions
- [ ] Implement `renderTodos()` function
- [ ] Implement `filterTodos()` function
- [ ] Set up initial state variables

### Task 6.4: Implement Add Todo Feature
- [ ] Create form HTML structure
- [ ] Implement `addTodo()` function with fetch
- [ ] Clear form after successful add
- [ ] Update UI after add

### Task 6.5: Implement Status Update Feature
- [ ] Add status buttons to todo items
- [ ] Implement `updateStatus()` function
- [ ] Update UI after status change

### Task 6.6: Implement Delete Feature
- [ ] Add delete button to todo items
- [ ] Implement `deleteTodo()` with confirmation
- [ ] Update UI after delete

### Task 6.7: Implement Inline Edit Feature
- [ ] Implement `startEdit()` to show edit form
- [ ] Implement `saveEdit()` to update todo
- [ ] Implement `cancelEdit()` to hide form
- [ ] Update UI after edit

### Task 6.8: Implement Stats Loading
- [ ] Implement `loadStats()` function
- [ ] Update stats display after changes
- [ ] Handle fetch errors

### Task 6.9: Add Keyboard Support
- [ ] Add Enter key handler for add todo form

### Task 6.10: Test Widget Interactivity
- [ ] Test all CRUD operations
- [ ] Test filter functionality
- [ ] Test inline editing
- [ ] Verify stats updates

**Status**: ✅ Completed

---

## Phase 7: Statistics Dashboard Widget

### Task 7.1: Design Stats Widget HTML
- [ ] Create header with refresh button
- [ ] Create stats grid (2x2)
- [ ] Create progress section
- [ ] Create insights section

### Task 7.2: Style Stats Widget
- [ ] Style stat cards with gradients
- [ ] Style progress bar
- [ ] Style refresh button
- [ ] Add hover effects

### Task 7.3: Implement Server-Side Data Injection
- [ ] Fetch stats in `_get_stats_html()`
- [ ] Calculate completion percentage
- [ ] Inject into HTML template

### Task 7.4: Implement Refresh Functionality
- [ ] Implement `refreshStats()` function
- [ ] Update all stat displays
- [ ] Update progress bar
- [ ] Regenerate insights HTML

### Task 7.5: Add Dynamic Insights
- [ ] Display task counts with pluralization
- [ ] Show completion message when 100%

### Task 7.6: Test Stats Widget
- [ ] Verify initial stats display
- [ ] Test refresh button
- [ ] Verify progress calculation

**Status**: ✅ Completed

---

## Phase 8: Enhanced User Experience

### Task 8.1: Refine Visual Design
- [ ] Ensure consistent color scheme
- [ ] Verify proper spacing and typography
- [ ] Check responsive layout

### Task 8.2: Add Status Icons
- [ ] Use 📝 for pending
- [ ] Use ⏳ for in_progress
- [ ] Use ✅ for completed

### Task 8.3: Implement Priority Visual Indicators
- [ ] Red left border for high priority
- [ ] Orange left border for medium priority
- [ ] Blue left border for low priority

### Task 8.4: Add Interactive Feedback
- [ ] Button hover states
- [ ] Input focus states
- [ ] Loading indicators
- [ ] Success/error alerts

### Task 8.5: Polish Details
- [ ] Smooth transitions
- [ ] Proper cursor styles
- [ ] Disabled states where appropriate

**Status**: ✅ Completed

---

## Phase 9: Configuration & Deployment

### Task 9.1: Environment Configuration
- [ ] Add dotenv support
- [ ] Load PUBLIC_URL from environment
- [ ] Set fallback to localhost

### Task 9.2: Inject PUBLIC_URL into Widgets
- [ ] Add API_BASE variable in widget JavaScript
- [ ] Use PUBLIC_URL in fetch calls
- [ ] Test with both localhost and ngrok

### Task 9.3: Document Configuration
- [ ] Add PUBLIC_URL to README
- [ ] Document ngrok setup
- [ ] Create environment variable guide

### Task 9.4: Create Development Commands
- [ ] Set up justfile with common commands
- [ ] Test init, dev, tunnel commands

**Status**: ✅ Completed

---

## Phase 10: Integration & Assembly

### Task 10.1: Combine MCP and REST
- [ ] Get MCP app: `mcp.streamable_http_app()`
- [ ] Extend with REST routes
- [ ] Add CORS middleware

### Task 10.2: Test Full Integration
- [ ] Start server
- [ ] Test REST API endpoints
- [ ] Test MCP tools via MCP client
- [ ] Test widgets display

### Task 10.3: ngrok Integration
- [ ] Configure ngrok.yml
- [ ] Set PUBLIC_URL to ngrok URL
- [ ] Test widgets with ngrok

### Task 10.4: ChatGPT Integration
- [ ] Configure in OpenAI Apps platform
- [ ] Test tools via ChatGPT conversation
- [ ] Test widgets display in ChatGPT
- [ ] Verify interactivity works

**Status**: ✅ Completed

---

## Phase 11: Documentation

### Task 11.1: Create README
- [ ] Write project overview
- [ ] Document features
- [ ] Add setup instructions
- [ ] Document API endpoints
- [ ] Add OpenAI Apps SDK integration guide

### Task 11.2: Create OPENAI_APPS_SDK.md
- [ ] Document widget architecture
- [ ] Explain MCP integration
- [ ] Document PUBLIC_URL configuration
- [ ] Provide troubleshooting tips

### Task 11.3: Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add inline comments where needed
- [ ] Document non-obvious logic

**Status**: ✅ Completed

---

## Phase 12: Spec-Kit Documentation (This Phase)

### Task 12.1: Create Spec-Kit Structure
- [x] Create `.specify/` directory structure
- [x] Create `memory/` subdirectory
- [x] Create `tasks/` subdirectory

### Task 12.2: Apply Reverse Engineering
- [x] Analyze existing codebase
- [x] Document architecture decisions
- [x] Map features to requirements

### Task 12.3: Write Constitution
- [x] Define project principles
- [x] Document technical constraints
- [x] Establish development workflow
- [x] Define success criteria

### Task 12.4: Write Specification
- [x] Document Phase 1: Data Models
- [x] Document Phase 2: Storage Layer
- [x] Document Phase 3: REST API
- [x] Document Phase 4: MCP Integration
- [x] Document Phase 5: Basic Widgets
- [x] Document Phase 6: Interactive Widgets
- [x] Document Phase 7: Statistics Widget
- [x] Document Phase 8: Enhanced UX
- [x] Document Phase 9: Configuration
- [x] Define acceptance criteria

### Task 12.5: Write Implementation Plan
- [x] Document technology stack
- [x] Document project structure
- [x] Document implementation phases
- [x] Document key technical decisions
- [x] Document error handling strategy
- [x] Document extension points

### Task 12.6: Write Task Breakdown
- [x] Create this task list
- [x] Organize by phases
- [x] Mark completed tasks

### Task 12.7: Commit Spec-Kit Documentation
- [ ] Git add spec-kit files
- [ ] Create descriptive commit
- [ ] Push to branch

**Status**: 🔄 In Progress

---

## Summary

- **Total Phases**: 12
- **Completed Phases**: 11
- **Current Phase**: 12 (Spec-Kit Documentation)
- **Overall Progress**: ~95%

All implementation is complete. Only remaining task is committing the spec-kit documentation generated through reverse engineering.

---

*This task list serves as a retrospective breakdown of how the OpenAI Todo App was built, now documented through reverse engineering for spec-kit.*
