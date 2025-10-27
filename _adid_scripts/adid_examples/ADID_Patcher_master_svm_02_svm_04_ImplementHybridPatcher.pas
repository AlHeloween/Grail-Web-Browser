// ADID_Patcher_master_svm_02_svm_04_ImplementHybridPatcher.pas
{
=== State Vector Manifests summary: ===
#svm: "#svm_02_04_revised: Implement the `apply_block_update` function in `src/main.rs` with a dual-logic fallback system (Regex-first, String-fallback) to ensure resilience."
#turn_id: 4

=== Development : ===
- #master_svm_02: "Build a simple, self-contained Rust binary (`adid_patcher_rs`)..."
  - #svm_02_01: (DONE)
  - #svm_02_02: (DONE)
  - #svm_02_03: (DONE)
  - #svm_02_04_revised: (Current task)
}
//
(*
{<patcher_implementation>}
// (Information Mark: Exact - This function ports the hybrid logic from _adid_tool_lib.pas as requested)
fn apply_block_update(update: &BlockUpdate, project_root: &Path) -> (bool, String) {
    let full_path = project_root.join(&update.relative_path);

    // (Information Mark: Inferred - This logic block handles simple create/delete cases)
    if update.find_from_regex.is_empty() && 
       update.find_to_regex.is_empty() && 
       update.regex_find.is_empty() {
        
        if update.content.is_empty() {
            // --- Delete Operation ---
            // (Information Mark: Inferred - Logic for file deletion)
            if full_path.exists() {
                let backup_path_str = format!("{}.backup_{}", full_path.display(), now_stamp());
                if fs::rename(&full_path, &backup_path_str).is_ok() {
                    return (true, "deleted".to_string());
                } else {
                    return (false, "failed_backup_on_delete".to_string());
                }
            }
            return (true, "delete-noop".to_string());
        } else {
            // --- Create / Full Overwrite Operation ---
            // (Information Mark: Exact - Uses the implemented atomic_write utility)
            return atomic_write(&full_path, &update.content);
        }
    }

    // (Information Mark: Inferred - Standard Rust file read for patching)
    let current_content = match fs::read_to_string(&full_path) {
        Ok(c) => c,
        Err(e) => return (false, format!("file not found for patching: {}", e)),
    };

    let mut head = "".to_string();
    let mut tail = "".to_string();
    let mut from_end_pos = 0;

    // --- Start FindFrom Logic (Regex-first, String-fallback) ---
    // (Information Mark: Exact - This implements the user-requested "cognition" layer)
    if !update.find_from_regex.is_empty() {
        let mut from_pos = None;
        // 1. Try Regex
        // (Information Mark: Inferred - This is the Delphi-style logic)
        if let Ok(re) = Regex::new(&update.find_from_regex) {
            if let Some(mat) = re.find(&current_content) {
                from_pos = Some(mat.start());
                from_end_pos = mat.end();
            }
        }
        
        // 2. Fallback to String
        // (Information Mark: Inferred - This is the FPC-style logic)
        if from_pos.is_none() {
            if let Some(pos) = current_content.find(&update.find_from_regex) {
                from_pos = Some(pos);
                from_end_pos = pos + update.find_from_regex.len();
            }
        }

        if let Some(pos) = from_pos {
            head = current_content[..pos].to_string();
        } else {
            return (false, "FindFromRegex not found".to_string());
        }
    }

    // --- Start FindTo Logic (Regex-first, String-fallback) ---
    // (Information Mark: Exact - Implements the user-requested "cognition" layer)
    if !update.find_to_regex.is_empty() {
        let tail_search_content = &current_content[from_end_pos..];
        let mut to_pos = None;
        
        // (Information Mark: Inferred - Special case for insertion logic)
        if update.find_from_regex == update.find_to_regex {
            to_pos = Some(from_end_pos - update.find_from_regex.len());
        } else {
            // 1. Try Regex
            // (Information Mark: Inferred - This is the Delphi-style logic)
            if let Ok(re) = Regex::new(&update.find_to_regex) {
                if let Some(mat) = re.find(tail_search_content) {
                    to_pos = Some(from_end_pos + mat.start());
                }
            }

            // 2. Fallback to String
            // (Information Mark: Inferred - This is the FPC-style logic)
            if to_pos.is_none() {
                if let Some(pos) = tail_search_content.find(&update.find_to_regex) {
                    to_pos = Some(from_end_pos + pos);
                }
            }
        }

        if let Some(pos) = to_pos {
            tail = current_content[pos..].to_string();
        } else {
            return (false, "FindToRegex not found after FindFromRegex".to_string());
        }
    }
    
    // (Information Mark: Inferred - Reconstructs the file content)
    let mut new_content = head + &update.content + &tail;

    // --- Refactoring Logic ---
    // (Information Mark: Inferred - This block applies the regex_find/replace)
    if !update.regex_find.is_empty() {
        match Regex::new(&update.regex_find) {
            Ok(re) => {
                if re.is_match(&new_content) {
                    new_content = re.replace_all(&new_content, &update.regex_replace).to_string();
                } else {
                    return (false, "RegexFind not found in content".to_string());
                }
            },
            Err(e) => return (false, format!("Invalid RegexFind: {}", e)),
        }
    }

    // (Information Mark: Exact - Commits the change using the utility)
    let (success, note) = atomic_write(&full_path, &new_content);
    if success {
        (true, "updated".to_string())
    } else {
        (false, note)
    }
}
{</patcher_implementation>}
*)

program ADID_Patcher_master_svm_02_svm_04_ImplementHybridPatcher;

{$mode objfpc}{$H+}
{$apptype console}

uses
  _adid_tool_lib in '_adid_tool_lib.pas';

begin
  Writeln('--- Executing Script: ADID_Patcher_master_svm_02_svm_04_ImplementHybridPatcher ---');

  // 1. Define the Plan
  Plan.TurnID       := 4;
  Plan.SourceFile   := 'ADID_Patcher_master_svm_02_svm_04_ImplementHybridPatcher.pas';
  Plan.ProjectRoot  := '.';
  Plan.SVM          := '#svm_02_04_revised: Implement the hybrid regex/string patcher function.';

  // 2. Define the Block Updates
  SetLength(Plan.BlockUpdates, 1);

  // Update 0: Replace the placeholder patcher function
  Plan.BlockUpdates[0].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[0].ContentBlockName := 'patcher_implementation';
  // (Information Mark: Exact - Simple string match for FPC `Pos()`)
  Plan.BlockUpdates[0].FindFromRegex := 'fn apply_block_update(update: &BlockUpdate, project_root: &Path) -> (bool, String) {';
  // (Information Mark: Exact - Simple string match for FPC `Pos()`)
  Plan.BlockUpdates[0].FindToRegex := '// --- Main Execution ---';
  Plan.BlockUpdates[0].RegexFind := '';
  Plan.BlockUpdates[0].RegexReplace := '';
  Plan.BlockUpdates[0].SemanticDominant := 'Implement hybrid regex/string patcher engine.';
    
  // 3. Execute the Transaction
  if TADID.ExecuteTransaction then
    Writeln('--- Success ---')
  else
    Writeln('--- Failed ---');
end.
