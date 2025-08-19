# NX-Pipline

## Locations 
In order to get the pipeline up and running you have to edit the Fixed Locations in the 

> batch_run_nx.py"

## Run Pipeline
### manually 
1. Open Up  
    > Tool - NX Command Prompt

2. Go to 
    > C:\Program Files\Siemens\NX2212\NXBIN

3. run the command
    > run_journal.exe C:\nx-pipeline\bin\batch_run_nx.py

4. Review output, output must be like:
    > Wrote: C:\nx-pipeline\web\data\latest.json

    > Backup: C:\nx-pipeline\reports\2025-08-20_01-14-53\prt_checks.json

    > Files processed: 1


## Run Report
1. Go to 
    > nx-pipeline\web
2. run the command
    > python -m http.server8080
3. open url in browser
    > http://localhost:8080/