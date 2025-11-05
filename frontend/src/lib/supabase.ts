import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://idaenyycsiewbvxtdecn.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlkYWVueXljc2lld2J2eHRkZWNuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5MzYwODAsImV4cCI6MjA3NjUxMjA4MH0.lzleHPrcveQZPcXeziA92rFgjFz-ojBmQrLRU6vNeAo'

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

