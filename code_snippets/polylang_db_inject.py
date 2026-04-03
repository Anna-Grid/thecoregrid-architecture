"""
ThecoreGrid.dev Architecture Snippet: Forcing Taxonomy across Plugins.
Bypassing high-level plugin API restrictions (e.g., Polylang forcing default languages on post creation) 
by injecting raw PHP execution directly via WP-CLI.
"""
import subprocess

def force_post_language(post_id, lang_slug, wp_path):
    if not post_id: return
    
    # Executing native PHP function directly in the server terminal
    php_code = f"if(function_exists('pll_set_post_language')){{ pll_set_post_language({post_id}, '{lang_slug}'); }}"
    
    cmd = [
        "/usr/local/bin/wp", "eval", php_code, 
        "--allow-root", 
        f"--path={wp_path}"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Taxonomy Injection Error: {res.stderr}")
