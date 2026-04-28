// Supabase Configuration for multiple projects
const supabaseConfigs = [
  {
    projectUrl: process.env.SUPABASE_URL_1 || process.env.SUPABASE_URL,
    anonKey: process.env.SUPABASE_ANON_KEY_1 || process.env.SUPABASE_ANON_KEY,
    serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY_1 || process.env.SUPABASE_SERVICE_ROLE_KEY
  }
];

module.exports = { supabaseConfigs };
