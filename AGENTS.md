# ABSOLUTE RULE:
1. if face errors - **USE** --help
2. never delete backup files they are important for adid lookups and later agent trainngs because such information are highly structured and tollerant to cause->effect LLM problems.
3. prior saying that some component missing during tests - read pyproject.toml

# Link Redirector Workspace Guidance
read `./ADID_Framework_14_0.md` (Framework)
we use `./_adid_scripts/adid_rn.sh` [./_adid_scripts/script_name].pas
in './adid_scripts/.adid/ - located history and indexes information about our activity
every transaction has time and uuid
`./adid_readme.md` contains instructions how to use tool
Examples located at `./_adid_scripts/adid_examples/`
keep plans in `/_plans/'
keep update scripts in '_scripts'
every activity has its own SV (Framework.I.2)

# Interface: 
- Every file io input must have directory browser
- Every control must have hinting about its purpose
- Text input/output information must have select, select all, copy, paste (if applicable).
- Control groups must be resizable
- Application state must be saved upon exit and restored after opening

# Planning expectations
Durring Progress, create/update: 
1. `_developent_plan.md` 
  a. [TIMESTAMP]
  b. SVM (Framework.II)
  c. Tasks [COMPLETION] (Task considered completed if tests related to such tasks successfully accomplished)
2. `_progress_log.md` summarising the workflow include:
  a. [TIMESTAMP]
  b. Cause: Reason of Activity
  c. Script: APPNAME_GoalId_SessionId_TurnId_TaskName.js
  d. Script Output: /logs/APPNAME_GoalId_SessionId_TurnId_TaskName.log
  - GoalId: 2 digits number
  - SesstingID: 2 digits number
  - Turn_Id: 2 digits number

# ENSURE THAT DEVELOPMENT CYCLE PROPERLY IMPLEMENTED 
- Any modifications has to be implemented through scripts
- Any results of scripts must be in logs 
- No random reasoning modifications walks
- At start of every work, after framework rules understaded read `_development_plan.md`
- Fractal reasoning kernel - framework I.15

