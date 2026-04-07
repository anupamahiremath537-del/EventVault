require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

async function check() {
  const SUPABASE_URL = process.env.SUPABASE_URL;
  const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;
  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

  const { data, error } = await supabase.from('events').select('title, issupportiveteam').limit(20);
  if (error) {
    console.error('Error:', error.message);
  } else {
    console.log('Events found:', data.length);
    data.forEach(e => {
        console.log(`- ${e.title}: issupportiveteam = ${e.issupportiveteam} (${typeof e.issupportiveteam})`);
    });
  }
}
check();
