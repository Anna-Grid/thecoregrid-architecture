"""
ThecoreGrid.dev Architecture Snippet: Bypassing Linux ARG_MAX limits.
Instead of passing large HTML content as command-line arguments (which gets truncated),
we stream the generated article directly into WordPress Core via STDIN ('-').
"""
import subprocess

def create_wp_draft_via_stdin(title, html_content, author_id, wp_path):
    cmd = [
        "/usr/local/bin/wp", "post", "create", "-", 
        f"--post_title={title}", 
        "--post_status=draft", 
        f"--post_author={author_id}", 
        "--allow-root", 
        f"--path={wp_path}"
    ]
    
    # Securely stream HTML content directly into WordPress database
    res = subprocess.run(cmd, input=html_content, capture_output=True, text=True)
    
    if res.returncode != 0:
        print(f"Error streaming to WP-CLI: {res.stderr}")
        return None
        
    return "Draft created successfully via STDIN."
