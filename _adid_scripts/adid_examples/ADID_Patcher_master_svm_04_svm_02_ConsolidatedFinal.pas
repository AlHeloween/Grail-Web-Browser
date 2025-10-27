// ADID_Patcher_master_svm_04_svm_02_ConsolidatedFinal.pas
{
=== State Vector Manifests summary: ===
#svm: "#svm_04_02: Finalize and validate adid_patcher_rs. This script consolidates the text logger, integration test, and all cargo warning fixes into a single, robust update."
#turn_id: 8

=== Development : ===
- #master_svm_04: "Validate the feature-complete adid_patcher_rs tool..."
  - #svm_04_02: (Current task)
}
//
(*
{<cargo_fix_use_read>}
use std::io::Write;
{</cargo_fix_use_read>}

{<cargo_fix_dead_code>}
    #[allow(dead_code)]
    semantic_dominant: String,
{</cargo_fix_dead_code>}

{<test_plan_update>}
impl Plan {
    fn new() -> Self {
        // (Information Mark: Hypothetical - This plan is now a real test case)
        Plan {
            turn_id: 8,
            svm: "#svm_04_02: Final Integration Test".to_string(),
            // (Information Mark: Inferred - The script must read itself to find content blocks)
            source_file: "adid_patcher_rs/src/main.rs".to_string(), 
            project_root: ".".to_string(),
            block_updates: vec![
                // (Information Mark: Exact - This is the test task)
                BlockUpdate {
                    relative_path: "adid_patcher_rs/test_target.txt".to_string(),
                    find_from_regex: "FindFromMarker".to_string(),
                    find_to_regex: "FindToMarker".to_string(),
                    content_block_name: "test_content".to_string(),
                    regex_find: "".to_string(),
                    regex_replace: "".to_string(),
                    semantic_dominant: "Run integration test patch".to_string(),
                    content: "".to_string(), // Will be populated by parser
                },
            ],
        }
    }
}
{</test_plan_update>}

{<log_function>}
// (Information Mark: Exact - New function as per user request for text log)
fn now_iso_stamp() -> String {
    // (Information Mark: Inferred - Standard Rust chrono formatting for a human-readable log)
    Local::now().format("%Y-%m-%dT%H:%M:%S").to_string()
}

// (Information Mark: Exact - Implements robot-readable text log)
fn log_transaction(plan: &Plan, status: &str) {
    let adid_dir = PathBuf::from(&plan.project_root).join(".adid");
    if !adid_dir.exists() {
        if let Err(e) = fs::create_dir_all(&adid_dir) {
            println!("[Logger Error] Failed to create .adid directory: {}", e);
            return;
        }
    }
    
    let log_file_path = adid_dir.join("protocol.log");
    // (Information Mark: Exact - This format is simple, parsable, and human-readable)
    let log_message = format!(
        "[{}] [Turn: {}] [{}] SVM: {}\n",
        now_iso_stamp(),
        plan.turn_id,
        status,
        plan.svm
    );

    // (Information Mark: Inferred - Standard Rust append-to-file logic)
    let mut file = match fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(&log_file_path)
    {
        Ok(f) => f,
        Err(e) => {
            println!("[Logger Error] Failed to open protocol.log: {}", e);
            return;
        }
    };

    if let Err(e) = file.write_all(log_message.as_bytes()) {
        println!("[Logger Error] Failed to write to protocol.log: {}", e);
    }
}

{</log_function>}

{<main_logger_update>}
    if all_success {
        log_transaction(&plan, "Success");
        println!("--- Success ---");
    } else {
        log_transaction(&plan, "Failed");
        println!("--- Failed ---");
    }
{</main_logger_update>}

{<test_target_content>}
# Test Target File

This is the file to be patched.

FindFromMarker
PatchShouldGoHere
FindToMarker

...
End of file.
{</test_target_content>}

{<content_block_definition>}

{<test_content>}

This is the new content block.
It was successfully inserted by the ADID patcher.

{</test_content>}
{</content_block_definition>}
*)

program ADID_Patcher_master_svm_04_svm_02_ConsolidatedFinal;

{$mode objfpc}{$H+}
{$apptype console}

uses
  _adid_tool_lib in '_adid_tool_lib.pas';

begin
  Writeln('--- Executing Script: ADID_Patcher_master_svm_04_svm_02_ConsolidatedFinal ---');

  // 1. Define the Plan
  Plan.TurnID       := 8;
  Plan.SourceFile   := 'ADID_Patcher_master_svm_04_svm_02_ConsolidatedFinal.pas';
  Plan.ProjectRoot  := '.';
  Plan.SVM          := '#svm_04_02: Finalize and validate adid_patcher_rs (Consolidated Fix).';

  // 2. Define the Block Updates
  SetLength(Plan.BlockUpdates, 7);

  // Update 0: Fix 'unused import' warning
  Plan.BlockUpdates[0].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[0].ContentBlockName := 'cargo_fix_use_read';
  Plan.BlockUpdates[0].FindFromRegex := 'use std::io::{Read, Write};';
  Plan.BlockUpdates[0].FindToRegex := 'use std::path::{Path, PathBuf};';
  Plan.BlockUpdates[0].RegexFind := '';
  Plan.BlockUpdates[0].RegexReplace := '';
  Plan.BlockUpdates[0].SemanticDominant := 'Fix cargo warning: remove unused import `Read`.';
  
  // Update 1: Fix 'dead_code' warning for semantic_dominant
  Plan.BlockUpdates[1].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[1].ContentBlockName := 'cargo_fix_dead_code';
  Plan.BlockUpdates[1].FindFromRegex := 'semantic_dominant: String,';
  Plan.BlockUpdates[1].FindToRegex := '// (Information Mark: Inferred';
  Plan.BlockUpdates[1].RegexFind := '';
  Plan.BlockUpdates[1].RegexReplace := '';
  Plan.BlockUpdates[1].SemanticDominant := 'Fix cargo warning: allow `dead_code` for `semantic_dominant`.';
  
  // Update 2: Update Plan::new() with test plan
  Plan.BlockUpdates[2].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[2].ContentBlockName := 'test_plan_update';
  Plan.BlockUpdates[2].FindFromRegex := 'impl Plan {';
  // (Information Mark: Exact - Strict match to `main.rs` file)
  Plan.BlockUpdates[2].FindToRegex := 'fn now_stamp() -> String {';
  Plan.BlockUpdates[2].RegexFind := '';
  Plan.BlockUpdates[2].RegexReplace := '';
  Plan.BlockUpdates[2].SemanticDominant := 'Update main.rs Plan with test task (Strict).';

  // Update 3: Insert the text logger function
  Plan.BlockUpdates[3].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[3].ContentBlockName := 'log_function';
  // (Information Mark: Exact - Strict match to `main.rs` file)
  Plan.BlockUpdates[3].FindFromRegex := '// --- Main Execution ---';
  Plan.BlockUpdates[3].FindToRegex := '// --- Main Execution ---';
  Plan.BlockUpdates[3].RegexFind := '';
  Plan.BlockUpdates[3].RegexReplace := '';
  Plan.BlockUpdates[3].SemanticDominant := 'Implement the new text-based log_transaction function.';

  // Update 4: Hook logger into main() success/fail
  Plan.BlockUpdates[4].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[4].ContentBlockName := 'main_logger_update';
  Plan.BlockUpdates[4].FindFromRegex := 'if all_success {';
  // (Information Mark: Exact - Strict match to `main.rs` file)
  Plan.BlockUpdates[4].FindToRegex := '/*';
  Plan.BlockUpdates[4].RegexFind := '';
  Plan.BlockUpdates[4].RegexReplace := '';
  Plan.BlockUpdates[4].SemanticDominant := 'Hook logger into main() and fix `turn_id`/`svm` warnings.';
  
  // Update 5: Create the test_target.txt file
  Plan.BlockUpdates[5].RelativePath := 'adid_patcher_rs\test_target.txt';
  Plan.BlockUpdates[5].ContentBlockName := 'test_target_content';
  Plan.BlockUpdates[5].FindFromRegex := '';
  Plan.BlockUpdates[5].FindToRegex := '';
  Plan.BlockUpdates[5].RegexFind := '';
  Plan.BlockUpdates[5].RegexReplace := '';
  Plan.BlockUpdates[5].SemanticDominant := 'Create test target file.';

  // Update 6: Append the test content block to main.rs
  Plan.BlockUpdates[6].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[6].ContentBlockName := 'content_block_definition';
  // (Information Mark: Exact - Strict match to `main.rs` file)
  Plan.BlockUpdates[6].FindFromRegex := '{</example_content>}';
  Plan.BlockUpdates[6].FindToRegex := '';
  Plan.BlockUpdates[6].RegexFind := '';
  Plan.BlockUpdates[6].RegexReplace := '';
  Plan.BlockUpdates[6].SemanticDominant := 'Append test_content block to main.rs.';
    
  // 3. Execute the Transaction
  if TADID.ExecuteTransaction then
    Writeln('--- Success ---')
  else
    Writeln('--- Failed ---');
end.
