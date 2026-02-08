# API Contracts: Task Management

## Base URL
```
https://api.yourdomain.com/api/{user_id}
```

## Authentication
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Common Response Format

Success responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

Error responses follow this structure:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message"
  }
}
```

## Endpoints

### 1. List All Tasks
- **Endpoint**: `GET /api/{user_id}/tasks`
- **Description**: Retrieve all tasks for the authenticated user
- **Path Parameters**:
  - `user_id`: The ID of the authenticated user (extracted from JWT)
- **Query Parameters**:
  - `status` (optional): Filter by completion status ("pending", "completed", "all")
  - `limit` (optional): Number of tasks to return (default: 50, max: 100)
  - `offset` (optional): Number of tasks to skip (for pagination)
- **Headers**:
  - Authorization: Bearer {token}
- **Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "created_at": "2023-12-31T10:00:00Z",
        "updated_at": "2023-12-31T10:00:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}
```
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (user trying to access another user's tasks)
  - 404: User not found

### 2. Create New Task
- **Endpoint**: `POST /api/{user_id}/tasks`
- **Description**: Create a new task for the authenticated user
- **Path Parameters**:
  - `user_id`: The ID of the authenticated user (extracted from JWT)
- **Headers**:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- **Request Body**:
```json
{
  "title": "Task title (required)",
  "description": "Task description (optional)"
}
```
- **Success Response (201)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "created_at": "2023-12-31T10:00:00Z",
      "updated_at": "2023-12-31T10:00:00Z"
    }
  },
  "message": "Task created successfully"
}
```
- **Error Responses**:
  - 400: Bad Request (title is empty, invalid JSON format)
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (user trying to create task for another user)
  - 409: Conflict (user has reached maximum task limit)
  - 422: Unprocessable Entity (validation errors)

### 3. Get Task Details
- **Endpoint**: `GET /api/{user_id}/tasks/{id}`
- **Description**: Retrieve details of a specific task
- **Path Parameters**:
  - `user_id`: The ID of the authenticated user (extracted from JWT)
  - `id`: The ID of the task to retrieve
- **Headers**:
  - Authorization: Bearer {token}
- **Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "created_at": "2023-12-31T10:00:00Z",
      "updated_at": "2023-12-31T10:00:00Z"
    }
  }
}
```
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (user trying to access another user's task)
  - 404: Task not found

### 4. Update Task
- **Endpoint**: `PUT /api/{user_id}/tasks/{id}`
- **Description**: Update an existing task for the authenticated user
- **Path Parameters**:
  - `user_id`: The ID of the authenticated user (extracted from JWT)
  - `id`: The ID of the task to update
- **Headers**:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- **Request Body**:
```json
{
  "title": "Updated task title (required)",
  "description": "Updated task description (optional)"
}
```
- **Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Updated task title",
      "description": "Updated task description",
      "completed": false,
      "created_at": "2023-12-31T10:00:00Z",
      "updated_at": "2023-12-31T11:00:00Z"
    }
  },
  "message": "Task updated successfully"
}
```
- **Error Responses**:
  - 400: Bad Request (title is empty, invalid JSON format)
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (user trying to update another user's task)
  - 404: Task not found
  - 422: Unprocessable Entity (validation errors)

### 5. Delete Task
- **Endpoint**: `DELETE /api/{user_id}/tasks/{id}`
- **Description**: Delete a specific task for the authenticated user
- **Path Parameters**:
  - `user_id`: The ID of the authenticated user (extracted from JWT)
  - `id`: The ID of the task to delete
- **Headers**:
  - Authorization: Bearer {token}
- **Success Response (200)**:
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (user trying to delete another user's task)
  - 404: Task not found

### 6. Toggle Task Completion
- **Endpoint**: `PATCH /api/{user_id}/tasks/{id}/complete`
- **Description**: Toggle the completion status of a task
- **Path Parameters**:
  - `user_id`: The ID of the authenticated user (extracted from JWT)
  - `id`: The ID of the task to toggle
- **Headers**:
  - Authorization: Bearer {token}
- **Request Body**:
```json
{
  "completed": true
}
```
- **Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": true,
      "created_at": "2023-12-31T10:00:00Z",
      "updated_at": "2023-12-31T11:00:00Z"
    }
  },
  "message": "Task completion status updated"
}
```
- **Error Responses**:
  - 400: Bad Request (invalid JSON format, invalid completed value)
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (user trying to toggle another user's task)
  - 404: Task not found