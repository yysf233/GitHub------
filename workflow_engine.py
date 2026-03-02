import json
import os
import sys
import traceback
import io
import contextlib
import subprocess

def log(message):
    print(f"[LOG] {message}")

def execute_workflow(wf):
    name = wf.get('name', 'Untitled')
    script = wf.get('script', '')
    pip_deps = wf.get('pip', '') # 'pandas, beautifulsoup4'

    if not script.strip():
        log(f"Skipping {name}: No script content")
        return

    log(f"--- Running Workflow: {name} ---")

    # Install Dependencies
    if pip_deps:
        pkgs = [p.strip() for p in pip_deps.split(',') if p.strip()]
        if pkgs:
            log(f"Installing dependencies: {', '.join(pkgs)}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + pkgs)
                log("Dependencies installed successfully.")
            except Exception as e:
                log(f"Error installing dependencies: {e}")

    try:
        # Execute the script
        exec(script, {'__name__': '__main__'})
    except Exception as e:
        log(f"Error running workflow {name}: {e}")
        traceback.print_exc()
        
    log(f"--- Workflow Finished ---")

def main():
    try:
        with open('workflows.json', 'r', encoding='utf-8') as f:
            workflows = json.load(f)
    except FileNotFoundError:
        log("No workflows.json found.")
        return

    # Get current event name (schedule or workflow_dispatch)
    event_name = os.environ.get('EVENT_NAME', 'unknown')
    log(f"Triggered by event: {event_name}")

    # Filter by specific task name if provided
    target_task = os.environ.get('TASK_NAME')
    if target_task:
        log(f"--- Targeted Execution: {target_task} ---")
        workflows = [w for w in workflows if w.get('name') == target_task]
        if not workflows:
            log(f"Warning: Task '{target_task}' not found in workflows.json")
    
    for wf in workflows:
        if not wf.get('enabled', True):
            continue
        
        # Check explicit trigger settings
        run_on_schedule = wf.get('run_on_schedule', True)
        run_on_dispatch = wf.get('run_on_dispatch', True)

        if event_name == 'schedule' and not run_on_schedule:
            log(f"Skipping {wf.get('name')} (Disabled for schedule)")
            continue
        
        # Time-based scheduling check (Beijing Time)
        schedule_time = wf.get('schedule_time', '')
        if event_name == 'schedule' and run_on_schedule and schedule_time:
            try:
                # Calculate current Beijing Time
                import datetime
                utc_now = datetime.datetime.utcnow()
                beijing_now = utc_now + datetime.timedelta(hours=8)
                current_hm = beijing_now.strftime("%H:%M")
                
                # Check if we are in the 5-minute window of the target time
                # Target: HH:MM
                # We simply check if current_hour == target_hour and abs(current_min - target_min) < 5
                # But easiest is: Does current HH:MM match target? 
                # Since cron runs every 5 mins, one of them SHOULD match or be remarkably close.
                # Let's try direct match first to see if 08:00 hits 08:00
                # But if action runs at 08:02, exact match fails.
                
                target_h, target_m = map(int, schedule_time.split(':'))
                curr_h, curr_m = beijing_now.hour, beijing_now.minute
                
                # Logic: Is the current time within [target, target+5) minutes?
                # Example: Target 08:00. Action at 08:00, 08:01...08:04 -> Run.
                # Action at 08:05 -> Too late (next cycle).
                # Action at 07:55 -> Too early.
                
                diff_minutes = (curr_h * 60 + curr_m) - (target_h * 60 + target_m)
                
                # Handle day wrap if needed (e.g. 23:59 vs 00:01), but simplistic for now.
                if 0 <= diff_minutes < 5:
                    log(f"Time match: Current {current_hm} is within window of {schedule_time}")
                else:
                    log(f"Skipping {wf.get('name')} (Scheduled for {schedule_time}, current {current_hm})")
                    continue
            except Exception as e:
                log(f"Error parsing schedule time: {e}")
                # Fallback: run it or skip? Skip is safer to avoid spam.
                continue

        if event_name == 'workflow_dispatch' and not run_on_dispatch:
            log(f"Skipping {wf.get('name')} (Disabled for manual dispatch)")
            continue
            
        execute_workflow(wf)

if __name__ == "__main__":
    main()
