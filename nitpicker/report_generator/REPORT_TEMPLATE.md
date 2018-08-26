# ${header}

**Generated At**: ${generated_at}

**QA directory**: ${qa_dir}

${"## Test plans"}

% for plan in plans:
${"### " + plan['name']}
    
| TestCase | Description |Author | Run Count | Last Run |
|----------|-------------|-------|-----------|----------|    
    %for case in plan['cases']:
| ${case['name']} | ${case['desc']} | ${case['author']} | ${case['count']} | ${case['last_run']} |
    %endfor 
    
% endfor