// ADID_Patcher_master_svm_02_svm_03_ImplementParser_FIX.pas
{
=== State Vector Manifests summary: ===
#svm: "Implement the `extract_content_blocks` function in `src/main.rs`. This function will read the `source_file` (itself) and use the `regex` crate to find all XML-style tags (e.g., `{<name>}...{</name>}`) and populate the content `HashMap`."
#turn_id: 3
#fix_for_turn: 2 (Failed script ADID_Patcher_master_svm_02_svm_03_ImplementParser.pas)

=== Development : ===
- #master_svm_02: "Build a simple, self-contained Rust binary (`adid_patcher_rs`)..."
  - #svm_02_01: (DONE)
  - #svm_02_02: (DONE)
  - #svm_02_03: (Current task)
}
//
(*
{<use_regex_import>}
use regex::Regex;
{</use_regex_import>}

{<parser_implementation>}
// (Information Mark: Exact - Replaces placeholder with functional regex parser)
fn extract_content_blocks(source_path: &Path) -> HashMap<String, String> {
    // (Information Mark: Inferred - Standard Rust file read operation)
    let content = match fs::read_to_string(source_path) {
        Ok(c) => c,
        Err(e) => {
            println!("[Parser Error] Failed to read source file {:?}: {}", source_path, e);
            return HashMap::new();
        }
    };

    let mut map = HashMap::new();
    
    // (Information Mark: Exact - This regex finds all `{<name>}content{</name>}` blocks)
    // (?s) = "dotall" mode, allows '.' to match newlines
    // \{<(\w+)>} = Captures the tag name (e.g., "cargo_toml") into group 1
    // (.*?) = Non-greedily captures the content into group 2
    // \{</\1>} = Matches the corresponding closing tag
    let re = match Regex::new(r"(?s)\{<(\w+)>}(.*?)\{</\1>}") {
        Ok(r) => r,
        Err(e) => {
            println!("[Regex Error] Failed to compile parser regex: {}", e);
            return HashMap::new();
        }
    };

    // (Information Mark: Inferred - Iterates over all matches and populates the map)
    for cap in re.captures_iter(&content) {
        if let (Some(name), Some(content_block)) = (cap.get(1), cap.get(2)) {
            map.insert(name.as_str().to_string(), content_block.as_str().to_string());
        }
    }

    map
}
{</parser_implementation>}
*)

program ADID_Patcher_master_svm_02_svm_03_ImplementParser_FIX;

{$mode objfpc}{$H+}
{$apptype console}

uses
  _adid_tool_lib in '_adid_tool_lib.pas';

begin
  Writeln('--- Executing Script: ADID_Patcher_master_svm_02_svm_03_ImplementParser_FIX ---');

  // 1. Define the Plan
  Plan.TurnID       := 3;
  Plan.SourceFile   := 'ADID_Patcher_master_svm_02_svm_03_ImplementParser_FIX.pas';
  Plan.ProjectRoot  := '.';
  Plan.SVM          := '#svm_02_03: Implement the regex-based content block parser (FPC String-Fix).';

  // 2. Define the Block Updates
  SetLength(Plan.BlockUpdates, 2);

  // Update 0: Import the Regex crate
  Plan.BlockUpdates[0].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[0].ContentBlockName := 'use_regex_import';
  // (Information Mark: Exact - Corrected to simple string for FPC `Pos()`)
  Plan.BlockUpdates[0].FindFromRegex := 'use std::process;';
  Plan.BlockUpdates[0].FindToRegex := 'use std::process;';
  Plan.BlockUpdates[0].RegexFind := '';
  Plan.BlockUpdates[0].RegexReplace := '';
  Plan.BlockUpdates[0].SemanticDominant := 'Import Rust regex crate.';
  
  // Update 1: Replace the placeholder parser function
  Plan.BlockUpdates[1].RelativePath := 'adid_patcher_rs\src\main.rs';
  Plan.BlockUpdates[1].ContentBlockName := 'parser_implementation';
  // (Information Mark: Exact - Corrected to simple string for FPC `Pos()`)
  Plan.BlockUpdates[1].FindFromRegex := 'fn extract_content_blocks(source_path: &Path) -> HashMap<String, String> {';
  // (Information Mark: Exact - Corrected to simple string for FPC `Pos()`)
  Plan.BlockUpdates[1].FindToRegex := 'fn apply_block_update(update: &BlockUpdate, project_root: &Path) -> (bool, String) {';
  Plan.BlockUpdates[1].RegexFind := '';
  Plan.BlockUpdates[1].RegexReplace := '';
  Plan.BlockUpdates[1].SemanticDominant := 'Implement regex content parser.';
    
  // 3. Execute the Transaction
  if TADID.ExecuteTransaction then
    Writeln('--- Success ---')
  else
    Writeln('--- Failed ---');
end.
