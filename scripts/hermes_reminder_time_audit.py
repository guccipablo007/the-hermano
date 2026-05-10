#!/usr/bin/env python3
from __future__ import annotations
import os, re, subprocess, sys
from pathlib import Path
SCRIPTS = Path('/root/.hermes/scripts')
if str(SCRIPTS) not in sys.path: sys.path.insert(0, str(SCRIPTS))
try:
    from hermes_time_context import format_china_time, now_china
except Exception:
    def now_china():
        from datetime import datetime
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo('Asia/Shanghai'))
    def format_china_time(dt=None):
        dt = dt or now_china()
        return dt.strftime('%A, %Y-%m-%d %I:%M %p China time (Asia/Shanghai, UTC+08:00)')
ROOTS = [Path('/root/.hermes/scripts'), Path('/root/.hermes/skills'), Path('/root/.hermes/rebuild_notes'), Path('/usr/local/lib/hermes-agent/gateway')]
REMINDER_PAT = re.compile(r'(reminder|remind|cron|crontab|schedule|next_run|next run|upload reminder)', re.I)
AMBIG_CST_PAT = re.compile(r'\bCST\b', re.I)
US_OR_CHINA_CLEAR_PAT = re.compile(r'(u\.s\. central|us central|central time usa|central time us|america/chicago|chicago time|cdt|China Standard Time|China time|Asia/Shanghai|UTC\+8|UTC\+08:00)', re.I)
EVERYDAY_MULTI_HOUR_CRON = re.compile(r'^\s*0\s+12,15,17\s+\*\s+\*\s+\*\b')
SUNDAY_WORD = re.compile(r'\bSunday\b|\bsun\b', re.I)
SKIP_DIRS = {'.git','__pycache__','file_outputs','newcoin_outputs','tokens','logs'}
MAX_FILES = 2500

def iter_text_files():
    seen = 0
    for root in ROOTS:
        if not root.exists(): continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith('.bak')]
            for name in filenames:
                path = Path(dirpath) / name
                if '.bak_' in name or name.endswith('.pyc') or path.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.pptx','.docx','.pdf','.zip'}:
                    continue
                seen += 1
                if seen > MAX_FILES: return
                yield path

def active_crontab():
    proc = subprocess.run(['crontab','-l'], text=True, capture_output=True, timeout=20)
    return proc.returncode, proc.stdout or '', proc.stderr or ''

def main() -> int:
    warnings=[]; critical=[]; reminder_files=[]
    print('CURRENT_CHINA_TIME=' + format_china_time(now_china()))
    for path in iter_text_files():
        try: text = path.read_text(errors='ignore')
        except Exception: continue
        if REMINDER_PAT.search(text):
            reminder_files.append(str(path))
            if AMBIG_CST_PAT.search(text) and not US_OR_CHINA_CLEAR_PAT.search(text):
                warnings.append('AMBIGUOUS_CST_TEXT=' + str(path))
    print('REMINDER_FILES_FOUND=' + str(len(reminder_files)))
    for item in reminder_files[:80]: print('REMINDER_FILE=' + item)
    rc, cron_out, cron_err = active_crontab()
    if rc == 0:
        print('ACTIVE_CRONTAB=FOUND')
        tz_clear = False
        for raw in cron_out.splitlines():
            line = raw.strip()
            if not line or line.startswith('#'): continue
            print('CRON_ENTRY=' + line)
            if line.startswith('CRON_TZ=Asia/Shanghai') or line.startswith('TZ=Asia/Shanghai'): tz_clear=True
            if EVERYDAY_MULTI_HOUR_CRON.search(line): critical.append('CRON_EVERY_DAY_NOT_SUNDAY_ONLY=' + line)
            if SUNDAY_WORD.search(line) and not re.search(r'\s(0|7)\s*(#.*)?$', line): warnings.append('SUNDAY_TEXT_WITHOUT_SUNDAY_CRON_FIELD=' + line)
        if cron_out.strip() and not tz_clear: warnings.append('CRON_TIMEZONE_UNCLEAR_NO_CRON_TZ_ASIA_SHANGHAI')
    else:
        print('ACTIVE_CRONTAB=NONE_OR_UNAVAILABLE')
        if cron_err.strip(): print('CRONTAB_INFO=' + cron_err.strip().splitlines()[-1])
    for warning in warnings: print('WARNING=' + warning)
    for item in critical: print('CRITICAL=' + item)
    if critical:
        print('NOT VERIFIED')
        return 1
    print('REMINDER_TIME_AUDIT=PASSED')
    return 0
if __name__ == '__main__': raise SystemExit(main())
