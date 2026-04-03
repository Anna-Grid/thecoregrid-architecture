"""
ThecoreGrid.dev Architecture Snippet: AIOps Watchdog.
Extracts raw Linux logs via journalctl and feeds them to an LLM for human-readable 
system diagnostics, filtering out false positives.
"""
import subprocess
from openai import OpenAI

ai_client = OpenAI(api_key="HIDDEN_IN_ENV")

def get_system_pulse():
    # 1. Extract last 30 lines from Linux systemd logs
    ai_logs = subprocess.run(["journalctl", "-u", "coregrid_ai.service", "-n", "30", "--no-pager"], capture_output=True, text=True).stdout
    
    # 2. Feed raw machine logs to LLM for diagnostic
    prompt = f"""
    You are a Senior SRE. Analyze these raw Linux logs.
    CRITICAL RULES:
    1. Check chronology. If an error occurred but the service successfully restarted later, the status is STABLE.
    2. Ignore development server warnings from Flask.
    
    Output format (HTML):
    <b>SYSTEM PULSE: [Stable / Errors]</b>
    <b>Diagnosis:</b> [Brief human-readable summary of the logs]
    
    Raw Logs:
    {ai_logs}
    """
    response = ai_client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}], 
        temperature=0.1
    )
    return response.choices[0].message.content.strip()
