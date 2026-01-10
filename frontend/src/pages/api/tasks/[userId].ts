import type { NextApiRequest, NextApiResponse } from 'next';
import { withAuth } from '../../../middleware/auth';
import { getDatabaseConnection } from '../../../lib/database';
import { Task, User } from '../../../models';

// Handler for GET /api/tasks/[userId]
async function getTasksHandler(req: NextApiRequest, NextApiResponse) {
  try {
    const { userId } = req.query;
    const { status, limit = 50, offset = 0 } = req.query;

    // Validate user ID
    const numericUserId = parseInt(userId as string, 10);
    if (isNaN(numericUserId)) {
      return res.status(400).json({ error: 'Invalid user ID' });
    }

    // Get database connection
    const db = await getDatabaseConnection();

    // Build query based on status filter
    let query = `
      SELECT id, title, description, completed, created_at, updated_at
      FROM task
      WHERE user_id = ?
    `;
    const params: any[] = [numericUserId];

    if (status === 'pending') {
      query += ' AND completed = FALSE';
    } else if (status === 'completed') {
      query += ' AND completed = TRUE';
    }

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(parseInt(limit as string, 10), parseInt(offset as string, 10));

    // Execute query to get tasks
    const tasks = await db.query(query, params);

    // Get total count
    const countQuery = `
      SELECT COUNT(*) as total
      FROM task
      WHERE user_id = ?
    `;
    const countParams = [numericUserId];

    if (status === 'pending') {
      countQuery += ' AND completed = FALSE';
    } else if (status === 'completed') {
      countQuery += ' AND completed = TRUE';
    }

    const countResult = await db.query(countQuery, countParams);
    const total = countResult[0]?.total || 0;

    // Format datetime strings
    const formattedTasks = tasks.map(task => ({
      ...task,
      created_at: new Date(task.created_at).toISOString(),
      updated_at: new Date(task.updated_at).toISOString(),
    }));

    return res.status(200).json({
      tasks: formattedTasks,
      total,
      limit: parseInt(limit as string, 10),
      offset: parseInt(offset as string, 10),
    });
  } catch (error) {
    console.error('Error fetching tasks:', error);
    return res.status(500).json({ error: 'Failed to fetch tasks' });
  }
}

// Handler for POST /api/tasks/[userId] (create task)
async function createTaskHandler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { userId } = req.query;
    const { title, description } = req.body;

    // Validate inputs
    if (!title || title.trim().length === 0) {
      return res.status(400).json({ error: 'Title is required' });
    }

    const numericUserId = parseInt(userId as string, 10);
    if (isNaN(numericUserId)) {
      return res.status(400).json({ error: 'Invalid user ID' });
    }

    // Get database connection
    const db = await getDatabaseConnection();

    // Insert new task
    const insertQuery = `
      INSERT INTO task (title, description, user_id, completed, created_at, updated_at)
      VALUES (?, ?, ?, FALSE, NOW(), NOW())
    `;
    const insertParams = [title, description || '', numericUserId];

    const result = await db.execute(insertQuery, insertParams);

    // Fetch the created task
    const selectQuery = `
      SELECT id, title, description, completed, created_at, updated_at
      FROM task
      WHERE id = ?
    `;
    const task = await db.query(selectQuery, [result.insertId]);

    if (task.length > 0) {
      const formattedTask = {
        ...task[0],
        created_at: new Date(task[0].created_at).toISOString(),
        updated_at: new Date(task[0].updated_at).toISOString(),
      };

      return res.status(201).json(formattedTask);
    } else {
      return res.status(500).json({ error: 'Failed to create task' });
    }
  } catch (error) {
    console.error('Error creating task:', error);
    return res.status(500).json({ error: 'Failed to create task' });
  }
}

// Main handler that routes based on method
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Apply authentication middleware
  const authResult = await withAuth(req, res);
  if (!authResult.authenticated) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Ensure the authenticated user can only access their own data
  const { userId } = req.query;
  const numericUserId = parseInt(userId as string, 10);
  if (authResult.user.id !== numericUserId) {
    return res.status(403).json({ error: 'Forbidden: Cannot access other users tasks' });
  }

  switch (req.method) {
    case 'GET':
      return getTasksHandler(req, res);
    case 'POST':
      return createTaskHandler(req, res);
    default:
      return res.status(405).json({ error: 'Method not allowed' });
  }
}