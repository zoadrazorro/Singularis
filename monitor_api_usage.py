"""
Real-time API usage monitor for Singularis AGI.

Analyzes logs to track Gemini/Claude API call rates and detect rate limiting.
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import time

def parse_log_line(line):
    """Extract timestamp and API call info from log line."""
    # Match Gemini calls
    gemini_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Gemini.*attempt (\d)/3', line)
    if gemini_match:
        timestamp_str, attempt = gemini_match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return {'time': timestamp, 'api': 'gemini', 'attempt': int(attempt)}
    
    # Match Claude calls
    claude_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Claude reasoning', line)
    if claude_match:
        timestamp_str = claude_match.group(1)
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return {'time': timestamp, 'api': 'claude', 'attempt': 1}
    
    # Match 429 errors
    error_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*429.*Too Many Requests', line)
    if error_match:
        timestamp_str = error_match.group(1)
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return {'time': timestamp, 'api': 'gemini', 'error': True}
    
    return None

def analyze_logs(log_text):
    """Analyze API usage from logs."""
    lines = log_text.split('\n')
    
    calls = []
    for line in lines:
        parsed = parse_log_line(line)
        if parsed:
            calls.append(parsed)
    
    if not calls:
        return None
    
    # Calculate RPM (requests per minute)
    gemini_calls = [c for c in calls if c['api'] == 'gemini' and not c.get('error')]
    claude_calls = [c for c in calls if c['api'] == 'claude']
    errors = [c for c in calls if c.get('error')]
    
    # Group by minute
    gemini_by_minute = defaultdict(int)
    claude_by_minute = defaultdict(int)
    errors_by_minute = defaultdict(int)
    
    for call in gemini_calls:
        minute = call['time'].replace(second=0, microsecond=0)
        gemini_by_minute[minute] += 1
    
    for call in claude_calls:
        minute = call['time'].replace(second=0, microsecond=0)
        claude_by_minute[minute] += 1
    
    for error in errors:
        minute = error['time'].replace(second=0, microsecond=0)
        errors_by_minute[minute] += 1
    
    return {
        'total_gemini': len(gemini_calls),
        'total_claude': len(claude_calls),
        'total_errors': len(errors),
        'gemini_by_minute': dict(gemini_by_minute),
        'claude_by_minute': dict(claude_by_minute),
        'errors_by_minute': dict(errors_by_minute),
        'avg_gemini_rpm': sum(gemini_by_minute.values()) / max(len(gemini_by_minute), 1),
        'avg_claude_rpm': sum(claude_by_minute.values()) / max(len(claude_by_minute), 1),
        'peak_gemini_rpm': max(gemini_by_minute.values()) if gemini_by_minute else 0,
        'peak_claude_rpm': max(claude_by_minute.values()) if claude_by_minute else 0,
    }

def print_report(stats):
    """Print formatted usage report."""
    print("\n" + "="*70)
    print("API USAGE REPORT")
    print("="*70)
    
    print(f"\n📊 TOTAL CALLS:")
    print(f"  Gemini:  {stats['total_gemini']:4d} calls")
    print(f"  Claude:  {stats['total_claude']:4d} calls")
    print(f"  Errors:  {stats['total_errors']:4d} (429 rate limit)")
    
    print(f"\n⚡ RATE METRICS:")
    print(f"  Gemini Average: {stats['avg_gemini_rpm']:5.1f} RPM")
    print(f"  Gemini Peak:    {stats['peak_gemini_rpm']:5d} RPM")
    print(f"  Gemini Limit:   30 RPM")
    
    gemini_status = "🔴 OVER LIMIT" if stats['peak_gemini_rpm'] > 30 else "🟢 OK"
    print(f"  Status: {gemini_status}")
    
    print(f"\n  Claude Average: {stats['avg_claude_rpm']:5.1f} RPM")
    print(f"  Claude Peak:    {stats['peak_claude_rpm']:5d} RPM")
    print(f"  Claude Limit:   100 RPM")
    
    claude_status = "🔴 OVER LIMIT" if stats['peak_claude_rpm'] > 100 else "🟢 OK"
    print(f"  Status: {claude_status}")
    
    if stats['total_errors'] > 0:
        error_rate = stats['total_errors'] / max(stats['total_gemini'], 1) * 100
        print(f"\n⚠️  ERROR RATE: {error_rate:.1f}% of Gemini calls failed")
    
    # Show peak minutes
    if stats['gemini_by_minute']:
        print(f"\n🔥 PEAK USAGE MINUTES (Gemini):")
        sorted_minutes = sorted(stats['gemini_by_minute'].items(), key=lambda x: x[1], reverse=True)
        for minute, count in sorted_minutes[:5]:
            status = "🔴" if count > 30 else "🟡" if count > 20 else "🟢"
            print(f"  {status} {minute.strftime('%H:%M')}: {count:3d} calls")
    
    print("\n" + "="*70)

def monitor_live(log_file_path, interval=5):
    """Monitor logs in real-time."""
    print(f"Monitoring: {log_file_path}")
    print(f"Update interval: {interval}s")
    print("Press Ctrl+C to stop\n")
    
    last_size = 0
    
    try:
        while True:
            if Path(log_file_path).exists():
                current_size = Path(log_file_path).stat().st_size
                
                if current_size > last_size:
                    # Read new content
                    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(last_size)
                        new_content = f.read()
                    
                    # Analyze
                    stats = analyze_logs(new_content)
                    if stats:
                        print_report(stats)
                    
                    last_size = current_size
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def main():
    """Main entry point."""
    print("="*70)
    print("SINGULARIS API USAGE MONITOR")
    print("="*70)
    print()
    
    # Try to find log file
    log_patterns = [
        "skyrim_agi.log",
        "logs/skyrim_agi.log",
        "*.log"
    ]
    
    log_file = None
    for pattern in log_patterns:
        matches = list(Path(".").glob(pattern))
        if matches:
            log_file = matches[0]
            break
    
    if not log_file:
        print("No log file found. Please provide path:")
        log_path = input("Log file path: ").strip()
        log_file = Path(log_path)
    
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        return
    
    print(f"Analyzing: {log_file}")
    
    # Read and analyze
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    stats = analyze_logs(content)
    
    if not stats:
        print("No API calls found in logs.")
        return
    
    print_report(stats)
    
    # Offer live monitoring
    print("\nWould you like to monitor in real-time?")
    monitor = input("[y/N]: ").strip().lower()
    
    if monitor == 'y':
        monitor_live(log_file)

if __name__ == "__main__":
    main()
