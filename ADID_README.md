# ADID: Unified Code Database and Patcher

**ADID** is the "Ultimate Tool" for managing code evolution, combining two powerful concepts into a single, robust binary:

1.  **A Content-Addressed Database (Code-as-DB):** Treats fenced code blocks (`{<TAG ...>}...{</TAG>}`) within scripts as versioned data, storing them immutably in a local `.adid/` directory structure.
2.  **A Legacy-Compatible Fuzzy Patcher:** Applies patch instructions from legacy Pascal scripts directly to the filesystem using a sophisticated 5-step fuzzy-matching algorithm.

This unified tool provides a seamless bridge between modern, database-centric code management and the need to apply older, imperative patch scripts reliably.

----

## Key Features ✨

* **Code-as-DB:** Ingest code blocks with unique IDs (`UUID`) and timestamps (`ISO8601`) into a content-addressed store.
* **Robust Patching:** Apply legacy patches with tolerance for whitespace changes and single-character typos using Hamming distance and Needleman-Wunsch alignment fallbacks (with safety limits).
* **Immutable History:** Every ingested block revision is stored by its `SHA256` hash, ensuring data integrity.
* **Detailed Auditing:** All operations (`ingest`, `apply`, `checkout`) are logged with timestamps and relevant metadata (including applied code fragments) in `.adid/runs/`.
* **Flexible Checkout:** Restore specific block revisions by exact hash, timestamp (`--as-of`), or the last known good state (`--last-good`).
* **Legacy Support:** Handles older script formats lacking explicit `id` and `ts` attributes in fences during ingestion (configurable via `--legacy`).
* **Selectable Regex Engines:** Choose between the full-featured **PCRE2** engine (default) or Rust's faster, built-in **`regex`** crate (`--fast-regex`) for parsing and refactoring.
* **Atomic Operations:** File writes use atomic operations (with backups for patching/checkout) to prevent data corruption.

---

## Workflows 🚀

ADID supports two primary workflows:

### 1. The "Code-as-DB" Workflow (Modern)

Treat your code like versioned data. Use `ingest` to store blocks and `checkout` to retrieve specific versions.

1.  **Ingest:** Store blocks from a script into the `.adid` database.
    ```bash
    # Ingest a script, auto-generating IDs/timestamps for any legacy blocks
    adid ingest --legacy annotate my_script_with_code_blocks.pas
    ```
2.  **Checkout:** Restore a specific version of a block to a file.
    ```bash
    # Get the latest version of the "MainCode" block as of end-of-year 2025
    adid checkout --id "YOUR-BLOCK-UUID" --tag "MainCode" --as-of "2026-01-01T00:00:00Z" --path "src/current_main.rs"

    # Get the last known "good" version (requires health log)
    adid checkout --id "YOUR-BLOCK-UUID" --last-good --path "src/stable_main.rs"
    ```

### 2. The "Patcher" Workflow (Legacy)

Apply changes directly to the filesystem using legacy patch scripts.

1.  **Apply:** Parse a patch script and execute its instructions.
    ```bash
    # Apply a legacy patch script
    adid apply --script my_legacy_patch.pas
    ```

---

## Installation 📦

Currently, build from source:

1.  **Install Rust:** If you don't have it, get it from [rustup.rs](https://rustup.rs/).
2.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd adid
    ```
3.  **Build the Release Binary:**
    ```bash
    cargo build --release
    ```
4.  **Copy the Binary:** The executable will be in `./target/release/adid`. Copy it to a location in your system's `PATH` (e.g., `/usr/local/bin` or `C:\Windows`).

---

## Usage ⌨️

The basic command structure is:

```bash
adid [GLOBAL_OPTIONS] <COMMAND> [COMMAND_OPTIONS]
````

### Global Options

These options apply to all commands:

  * `--root <PATH>`: Sets the project root containing the `.adid/` directory (default: current directory).
  * `--legacy <POLICY>`: Policy for handling blocks without `id`/`ts` during `ingest`.
      * `forbid`: (Default) Error out.
      * `accept`: Generate `id`/`ts` silently.
      * `annotate`: Generate `id`/`ts` and add a "legacy-annotated" note to the run log.
  * `--fast-regex`: Use Rust's standard `regex` engine instead of PCRE2 for all operations. Faster, but lacks features like lookarounds.

### Commands

#### `ingest`

Stores fenced blocks from `.pas` script(s) into the database.

```bash
adid ingest [OPTIONS] <FILES...>
```

  * `<FILES...>`: One or more Pascal script files to process.
  * **Examples:**
    ```bash
    # Ingest a single modern script
    adid ingest script.pas

    # Ingest multiple legacy scripts, generating v7 UUIDs
    adid ingest --legacy accept --uuidver v7 old_script1.pas old_script2.pas
    ```

#### `apply`

Applies a legacy patch script to the filesystem.

```bash
adid apply --script <SCRIPT_PATH> [OPTIONS]
```

  * `--script <SCRIPT_PATH>`: The `.pas` file containing patch instructions *and* content blocks.
  * **Examples:**
    ```bash
    # Apply a patch
    adid apply --script patch_001.pas

    # Apply a patch using the faster regex engine
    adid --fast-regex apply --script patch_002.pas
    ```

#### `blocks-list`

Lists blocks stored in the database.

```bash
adid blocks-list [OPTIONS]
```

  * `--tag <TAG>`: Filter by block tag.
  * `--id <UUID>`: Filter by block UUID.
  * **Examples:**
    ```bash
    # List all blocks
    adid blocks-list

    # List only blocks tagged "SourceCode"
    adid blocks-list --tag "SourceCode"

    # Find a specific block by ID across all tags
    adid blocks-list --id "d8a4f8..."
    ```

#### `blocks-show`

Shows the revision history for a specific block ID.

```bash
adid blocks-show --id <UUID> [OPTIONS]
```

  * `--id <UUID>`: The UUID of the block to show.
  * `--tag <TAG>`: (Optional) Specify the tag to speed up the search.
  * **Examples:**
    ```bash
    # Show history for a block ID
    adid blocks-show --id "d8a4f8..."

    # Show history specifically for the block tagged "Config"
    adid blocks-show --id "d8a4f8..." --tag "Config"
    ```

#### `checkout`

Restores a specific block revision to a file.

```bash
adid checkout --id <UUID> --path <TARGET_PATH> [SELECTOR_OPTIONS] [OPTIONS]
```

  * `--id <UUID>`: The UUID of the block to check out.
  * `--path <TARGET_PATH>`: The file path to write the content to.
  * `--tag <TAG>`: (Optional) Specify the tag to speed up the search.
  * **Selector Options (Choose ONE):**
      * `--sha256 <HASH>`: Select by exact content hash.
      * `--as-of <TIMESTAMP>`: Select the latest revision *before* this ISO 8601 timestamp (e.g., `"2025-10-26T12:00:00Z"`).
      * `--last-good`: Select the latest revision marked "good" in `.adid/health.jsonl`.
  * `--dry-run`: Show which revision would be selected but don't write the file.
  * **Examples:**
    ```bash
    # Restore the version matching a specific hash
    adid checkout --id "..." --sha256 "a1b2..." --path file.txt

    # Restore the latest version before midday on Oct 26, 2025 UTC
    adid checkout --id "..." --as-of "2025-10-26T12:00:00Z" --path file.txt

    # Restore the last known good version
    adid checkout --id "..." --last-good --path file.txt

    # See what --last-good would restore without changing the file
    adid checkout --id "..." --last-good --path file.txt --dry-run
    ```

#### `scan`

Rebuilds the `.adid/index.json` file.

```bash
adid scan [OPTIONS]
```

  * **Example:**
    ```bash
    # Rebuild the index if it's missing or corrupt
    adid scan
    ```

-----

## The `.adid` Directory 📁

ADID stores all its data within the `.adid` directory in your project root:

  * **`objects/`**: Contains the stored block data.
      * `objects/<tag>/<uuid>/<sha256>.blob` : Raw block content.
      * `objects/<tag>/<uuid>/<sha256>.meta.json`: Metadata (tag, id, ts, attrs, size, hash).
  * **`runs/`**: Contains timestamped JSONL files logging every operation (`ingest`, `apply`, `checkout`). This provides a complete audit trail.
  * **`index.json`**: An index of all blocks and their revisions for faster lookups (rebuildable with `adid scan`).
  * **`health.jsonl`**: (Optional) A log file where external processes can record the "health" (e.g., "good", "bad", "tested") of specific block revisions (`sha256`). Used by `checkout --last-good`.
  * **`protocol.log`**: (Legacy) The original log file used by the standalone `adid-patcher`. The `apply` command still writes basic status here for compatibility.

-----
