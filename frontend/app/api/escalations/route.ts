import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';

export const revalidate = 0;

export async function GET() {
  try {
    const dbPath = path.resolve(process.cwd(), '../backend/caller_data.db');
    if (!fs.existsSync(dbPath)) {
      return NextResponse.json({ escalations: [] });
    }

    const { DatabaseSync } = await import('node:sqlite');
    const db = new DatabaseSync(dbPath);

    // Ensure table exists
    db.exec(`
      CREATE TABLE IF NOT EXISTS escalations (
          reference_id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          caller_name TEXT NOT NULL,
          reason_category TEXT NOT NULL,
          what_happened TEXT NOT NULL,
          agent_checks TEXT NOT NULL,
          urgency_level TEXT NOT NULL,
          language_preference TEXT NOT NULL,
          preferred_followup TEXT NOT NULL,
          status TEXT DEFAULT 'OPEN',
          created_at TEXT NOT NULL
      );
    `);

    const query = db.prepare('SELECT * FROM escalations ORDER BY created_at DESC');
    const rows = query.all();
    db.close();

    return NextResponse.json({ escalations: rows });
  } catch (error: any) {
    console.error('Error fetching escalations:', error);
    return NextResponse.json({ error: error.message, escalations: [] }, { status: 500 });
  }
}

export async function PATCH(req: Request) {
  try {
    const { reference_id, status } = await req.json();
    if (!reference_id || !status) {
      return NextResponse.json({ error: 'Missing reference_id or status' }, { status: 400 });
    }

    const dbPath = path.resolve(process.cwd(), '../backend/caller_data.db');
    const { DatabaseSync } = await import('node:sqlite');
    const db = new DatabaseSync(dbPath);

    const stmt = db.prepare('UPDATE escalations SET status = ? WHERE reference_id = ?');
    const result = stmt.run(status, reference_id);
    db.close();

    return NextResponse.json({ success: true, changes: result.changes });
  } catch (error: any) {
    console.error('Error updating escalation status:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
