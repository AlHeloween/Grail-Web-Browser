// ADID_Patcher_master_svm_04_svm_01_IntegrationTest_FIX.pas
{
=== State Vector Manifests summary: ===
#svm: "#svm_04_01: Perform the final integration test for `adid_patcher_rs` by creating a test file and updating the main.rs plan to patch it. (Strict-Match Fix)"
#turn_id: 7
#fix_for_turn: 7 (Corrects ambiguous match in previous script)

=== Development : ===
- #master_svm_04: "Validate the feature-complete `adid_patcher_rs` tool..."
  - #svm_04_01: (Current task)
}
//
(*
{<test_target_content>}
# Test Target File

This is the file to be patched.

FindFromMarker
PatchShouldGoHere
FindToMarker

...
End of file.
{</test_target_content>}

{<test_plan_update>}
impl Plan {
    fn new() -> Self {
        // (Information Mark: Hypothetical - This plan is now a real test case)
        Plan {
            turn_id: 7,
            svm: "#svm_04_01: Final Integration Test".to_string(),
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

{<content_block_definition>}

/*
--- Content Blocks (For future tasks) ---

{<test_content>}

This is the new content block.
It was successfully inserted by the ADID patcher.

{</test_content>}

*/
{</content_block_definition>}
*)

program ADID_Patcher_master_svm_04_svm_01_IntegrationTest_FIX;

{$mode objfpc}{$H+}
{$apptype console}

uses
  _adid_tool_lib in '_adid_tool_lib.pas';

begin
  Writeln('--- Executing Script: ADID_Patcher_master_svm_04_svm_01_IntegrationTest_FIX ---');

  // 1. Define the Plan
  Plan.TurnID       := 7;
  Plan.SourceFile   := 'ADID_Patcher_master_svm_04_svm_01_IntegrationTest_FIX.pas';
  Plan.ProjectRoot  := '.';
  Plan.SVM          := '#svm_04_01: Final integration test for adid_patcher_rs (Strict-Match Fix).';

  // 2. Define the Block Updates
  SetLength(Plan.BlockUpdates, 3);

  // Update 0: Create the test_target.txt file
  Plan.BlockUpdates[0].RelativePath := 'adid_patcher_rs\test_target.txt';
  Plan.BlockUpdates[0].ContentBlockName := 'test_target_content';
  Plan.BlockUpdates[0].FindFromRegex := '';
  Plan.BlockUpdates[0].FindToRegex := '';
  Plan.BlockUpdates[0].RegexFind := '';
  Plan.BlockUpdates[0].RegexReplace := '';
  Plan.BlockUpdates[0].SemanticDominant := 'Create test target file.';
  
  // Update 1: Update Plan::new() in main.rs to run the test
  Plan.BlockUpdates[1].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[1].ContentBlockName := 'test_plan_update';
  // (Information Mark: Exact - Replaces the placeholder Plan::new() function)
  Plan.BlockUpdates[1].FindFromRegex := 'impl Plan {';
  // (Information Mark: Exact - Corrected to a strict, unambiguous string match)
  Plan.BlockUpdates[1].FindToRegex := 'fn now_stamp() -> String {';
  Plan.BlockUpdates[1].RegexFind := '';
  Plan.BlockUpdates[1].RegexReplace := '';
  Plan.BlockUpdates[1].SemanticDominant := 'Update main.rs Plan with test task (Strict).';
  
  // Update 2: Append the test content block to main.rs
  Plan.BlockUpdates[2].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[2].ContentBlockName := 'content_block_definition';
  // (Information Mark: Exact - Appends to the end of the file using the last comment block as an anchor)
  Plan.BlockUpdates[2].FindFromRegex := '*/';
  Plan.BlockUpdates[2].FindToRegex := '';
  Plan.BlockUpdates[2].RegexFind := '';
  Plan.BlockUpdates[2].RegexReplace := '';
  Plan.BlockUpdates[2].SemanticDominant := 'Append test_content block to main.rs.';
    
  // 3. Execute the Transaction
  if TADID.ExecuteTransaction then
    Writeln('--- Success ---')
  else
    Writeln('--- Failed ---');
end.