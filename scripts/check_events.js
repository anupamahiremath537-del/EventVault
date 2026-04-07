require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

async function check() {
  const SUPABASE_URL = process.env.SUPABASE_URL;
  const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

  const { data, error } = await supabase.from('events').select('*').limit(5);
  if (error) {
    console.error('Error:', error.message);
  } else {
    console.log('Events found:', data.length);
    if (data.length > 0) {
        console.log('Sample event keys:', Object.keys(data[0]));
    }
  }
}
check();
