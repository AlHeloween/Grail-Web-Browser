// ADID_Patcher_master_svm_02_svm_02_ImplementUtilities.pas
{
=== State Vector Manifests summary: ===
#svm: "Implement the core utility functions in `src/main.rs`: `now_stamp()` (using `chrono` for backup timestamps) and `atomic_write()` (using `std::fs` for safe file I/O and backup creation)."
#turn_id: 2

=== Development : ===
- #master_svm_02: "Build a simple, self-contained Rust binary (`adid_patcher_rs`) that mimics the core patching and backup functionality of the Pascal script..."
  - #svm_02_01: (DONE)
  - #svm_02_02: (Current task)
}
//
(*
{<main_rs_utilities_impl>}
// (Information Mark: Exact - Required for backup timestamp generation, ported from Pascal lib)
fn now_stamp() -> String {
    // (Information Mark: Inferred - Standard Rust chrono formatting for a unique stamp)
    Local::now().format("%Y%m%dT%H%M%S%f").to_string()
}

// (Information Mark: Exact - Core logic for safe file writes and backups, ported from Pascal lib)
fn atomic_write(file_path: &Path, content: &str) -> (bool, String) {
    // (Information Mark: Inferred - Ensures the target directory exists before writing)
    if let Some(parent) = file_path.parent() {
        if !parent.exists() {
            if let Err(e) = fs::create_dir_all(parent) {
                return (false, format!("Failed to create directory {:?}: {}", parent, e));
            }
        }
    }

    let mut note = "created".to_string();
    // (Information Mark: Inferred - Backup logic ported from Pascal 'AtomicWrite')
    if file_path.exists() {
        let backup_path_str = format!("{}.backup_{}", file_path.display(), now_stamp());
        let backup_path = PathBuf::from(backup_path_str);
        if let Err(e) = fs::rename(file_path, &backup_path) {
            return (false, format!("Failed to create backup {:?}: {}", backup_path, e));
        }
        println!("[backup] {} -> {}", file_path.display(), backup_path.display());
        note = "overwritten".to_string();
    }

    // (Information Mark: Inferred - Standard Rust file write operation)
    let mut file = match File::create(file_path) {
        Ok(file) => file,
        Err(e) => return (false, format!("Failed to create file {:?}: {}", file_path, e)),
    };

    if let Err(e) = file.write_all(content.as_bytes()) {
        return (false, format!("Failed to write to file {:?}: {}", file_path, e));
    }

    (true, note)
}

{</main_rs_utilities_impl>}
*)

program ADID_Patcher_master_svm_02_svm_02_ImplementUtilities;

{$mode objfpc}{$H+}
{$apptype console}

uses
  _adid_tool_lib in '_adid_tool_lib.pas';

begin
  Writeln('--- Executing Script: ADID_Patcher_master_svm_02_svm_02_ImplementUtilities ---');

  // 1. Define the Plan
  Plan.TurnID       := 2;
  Plan.SourceFile   := 'ADID_Patcher_master_svm_02_svm_02_ImplementUtilities.pas';
  Plan.ProjectRoot  := '.';
  Plan.SVM          := '#svm_02_02: Implement core utility functions now_stamp and atomic_write.';

  // 2. Define the Block Updates
  SetLength(Plan.BlockUpdates, 1);

  // Update 0: Insert utility functions into adid_patcher_rs/src/main.rs
  Plan.BlockUpdates[0].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[0].ContentBlockName := 'main_rs_utilities_impl';
  // (Information Mark: Exact - Inserts the new functions before the placeholder section)
  Plan.BlockUpdates[0].FindFromRegex := '// --- ADID Core Logic (Placeholders) ---';
  Plan.BlockUpdates[0].FindToRegex := '// --- ADID Core Logic (Placeholders) ---';
  Plan.BlockUpdates[0].RegexFind := '';
  Plan.BlockUpdates[0].RegexReplace := '';
  Plan.BlockUpdates[0].SemanticDominant := 'Implement Rust utility functions now_stamp and atomic_write.';
    
  // 3. Execute the Transaction
  if TADID.ExecuteTransaction then
    Writeln('--- Success ---')
  else
    Writeln('--- Failed ---');
end.