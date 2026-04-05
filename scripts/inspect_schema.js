require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

async function inspect() {
  const SUPABASE_URL = process.env.SUPABASE_URL;
  const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;

  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
    return;
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

  console.log('Inspecting columns of "otps" table...');
  const sql = `
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'otps';
  `;

  const { data, error } = await supabase.rpc('exec_sql', { sql });

  if (error) {
    console.error('Error inspecting schema:', error.message);
  } else {
    console.log('Columns in "events":');
    console.log(JSON.stringify(data, null, 2));
  }
  
  console.log('Inspecting other tables...');
  const sql2 = `
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
  `;
  const { data: tables, error: tablesError } = await supabase.rpc('exec_sql', { sql: sql2 });
  if (tablesError) {
     console.error('Error listing tables:', tablesError.message);
  } else {
     console.log('Tables in public schema:');
     console.log(JSON.stringify(tables, null, 2));
  }
}

inspect();
