import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';

export const revalidate = 0;

export async function GET() {
  try {
    const dbPath = path.resolve(process.cwd(), '../backend/caller_data.db');
    if (!fs.existsSync(dbPath)) {
      return NextResponse.json({
        metrics: {
          total_calls: 0,
          successful_calls: 0,
          failed_calls: 0,
          avg_duration: 0,
        },
        calls: [],
      });
    }

    const { DatabaseSync } = await import('node:sqlite');
    const db = new DatabaseSync(dbPath);

    // Ensure calls table exists
    db.exec(`
      CREATE TABLE IF NOT EXISTS calls (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          call_id TEXT UNIQUE NOT NULL,
          caller_name TEXT DEFAULT 'Citizen',
          language TEXT DEFAULT 'Hindi',
          duration_seconds INTEGER DEFAULT 0,
          status TEXT NOT NULL CHECK(status IN ('success', 'failed')),
          summary TEXT,
          created_at TEXT NOT NULL
      );
    `);

    // Fetch aggregate stats
    const statsStmt = db.prepare(`
      SELECT
        COUNT(*) as total_calls,
        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_calls,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_calls,
        ROUND(AVG(duration_seconds), 1) as avg_duration
      FROM calls;
    `);
    const statsRow: any = statsStmt.get() || {};

    // Fetch recent calls
    const callsStmt = db.prepare('SELECT * FROM calls ORDER BY created_at DESC LIMIT 50');
    const rows = callsStmt.all();
    db.close();

    return NextResponse.json({
      metrics: {
        total_calls: Number(statsRow.total_calls || 0),
        successful_calls: Number(statsRow.successful_calls || 0),
        failed_calls: Number(statsRow.failed_calls || 0),
        avg_duration: Number(statsRow.avg_duration || 0),
      },
      calls: rows,
    });
  } catch (error: any) {
    console.error('Error fetching analytics:', error);
    return NextResponse.json(
      {
        error: error.message,
        metrics: {
          total_calls: 0,
          successful_calls: 0,
          failed_calls: 0,
          avg_duration: 0,
        },
        calls: [],
      },
      { status: 500 }
    );
  }
}
