// ADID_Patcher_master_svm_03_svm_02_ImplementTextLog_FIX.pas
{
=== State Vector Manifests summary: ===
#svm: "#svm_03_02: Implement the 'robot-readable' text protocol log in `adid_patcher_rs/src.main.rs` (Strict-Match Fix)."
#turn_id: 6
#fix_for_turn: 6 (Corrects weak match in previous script)

=== Development : ===
- #master_svm_03: "Incorporate new philosophical insights... and refactor the `adid_patcher_rs` tool to use a simple text-based protocol log..."
  - #svm_03_01: (DONE)
  - #svm_03_02: (Current task)
}
//
(*
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
        plan->turn_id,
        status,
        plan->svm
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

{<main_call_success>}
    if all_success {
        log_transaction(&plan, "Success");
        println!("--- Success ---");
{</main_call_success>}

{<main_call_fail>}
    } else {
        log_transaction(&plan, "Failed");
        println!("--- Failed ---");
{</main_call_fail>}
*)

program ADID_Patcher_master_svm_03_svm_02_ImplementTextLog_FIX;

{$mode objfpc}{$H+}
{$apptype console}

uses
  _adid_tool_lib in '_adid_tool_lib.pas';

begin
  Writeln('--- Executing Script: ADID_Patcher_master_svm_03_svm_02_ImplementTextLog_FIX ---');

  // 1. Define the Plan
  Plan.TurnID       := 6;
  Plan.SourceFile   := 'ADID_Patcher_master_svm_03_svm_02_ImplementTextLog_FIX.pas';
  Plan.ProjectRoot  := '.';
  Plan.SVM          := '#svm_03_02: Implement the simple text-based protocol.log (Strict-Match Fix).';

  // 2. Define the Block Updates
  SetLength(Plan.BlockUpdates, 3);

  // Update 0: Insert the new log_transaction function
  Plan.BlockUpdates[0].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[0].ContentBlockName := 'log_function';
  // (Information Mark: Exact - Inserts before main() using FPC `Pos()` 'insert' logic)
  Plan.BlockUpdates[0].FindFromRegex := 'fn main() {';
  Plan.BlockUpdates[0].FindToRegex := 'fn main() {';
  Plan.BlockUpdates[0].RegexFind := '';
  Plan.BlockUpdates[0].RegexReplace := '';
  Plan.BlockUpdates[0].SemanticDominant := 'Implement the new text-based log_transaction function.';
  
  // Update 1: Replace the 'Success' branch
  Plan.BlockUpdates[1].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[1].ContentBlockName := 'main_call_success';
  // (Information Mark: Exact - This is a strict, unambiguous boundary)
  Plan.BlockUpdates[1].FindFromRegex := 'if all_success {';
  Plan.BlockUpdates[1].FindToRegex := '} else {';
  Plan.BlockUpdates[1].RegexFind := '';
  Plan.BlockUpdates[1].RegexReplace := '';
  Plan.BlockUpdates[1].SemanticDominant := 'Hook logger into the main success path.';
  
  // Update 2: Replace the 'Failed' branch
  Plan.BlockUpdates[2].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[2].ContentBlockName := 'main_call_fail';
  // (Information Mark: Exact - This is a strict, unambiguous boundary)
  Plan.BlockUpdates[2].FindFromRegex := '} else {';
  // (Information Mark: Exact - Corrected to use the comment block as a strict anchor)
  Plan.BlockUpdates[2].FindToRegex := '/*';
  Plan.BlockUpdates[2].RegexFind := '';
  Plan.BlockUpdates[2].RegexReplace := '';
  Plan.BlockUpdates[2].SemanticDominant := 'Hook logger into the main fail path (Strict).';
    
  // 3. Execute the Transaction
  if TADID.ExecuteTransaction then
    Writeln('--- Success ---')
  else
    Writeln('--- Failed ---');
end.