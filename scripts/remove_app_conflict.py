from pathlib import Path
p=Path('app.py')
s=p.read_text(encoding='utf-8', errors='replace')
start='<<<<<<< HEAD'
end='>>>>>>> copilot/improve-agent-ui-features'
if start in s and end in s:
    before,rest=s.split(start,1)
    _,after=rest.split(end,1)
    new=before+after
    p.write_text(new,encoding='utf-8')
    print('Removed conflict block in app.py')
else:
    print('Markers not found')
