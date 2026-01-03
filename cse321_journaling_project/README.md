# CSE321 Project: Journaling File System

## Overview
This project implements a **metadata journaling system** for the VSFS (Very Simple File System). The journaling mechanism provides crash consistency by logging metadata changes before applying them to the filesystem.

## Project Structure

### Files
- **journal.c** - Main implementation of the journaling system
- **mkfs.c** - Filesystem creation utility (provided)
- **validator.c** - Filesystem consistency checker (provided)
- **vsfs.img** - Filesystem image file (generated)

### Executables
- `./mkfs` - Creates a new VSFS filesystem
- `./journal` - Journaling utility (create/install commands)
- `./validator` - Validates filesystem consistency

## How It Works

### Metadata Journaling
The implementation uses **write-ahead logging** where metadata changes are:
1. First written to a journal area
2. Marked as committed with a commit record
3. Later applied to the actual filesystem locations
4. Journal is cleared after successful installation

### Journal Structure
- **Location**: Blocks 1-16 (16 blocks = 65,536 bytes)
- **Header**: Contains magic number (0x4A524E4C) and bytes used
- **Records**: 
  - DATA records: Contain block number and 4KB of data
  - COMMIT records: Mark transaction completion

## Implementation Details

### Command: `./journal create <filename>`

**What it does:**
1. Reads current filesystem metadata (inode bitmap, inode table, root directory)
2. Finds a free inode for the new file
3. Finds a free directory entry in root directory
4. Updates metadata in memory (allocates inode, creates directory entry)
5. Writes modified blocks to journal as DATA records
6. Appends COMMIT record to mark transaction complete
7. **Does NOT modify the actual filesystem** - only the journal

**Blocks journaled:**
- Inode bitmap block (1 block)
- Inode table blocks (2 blocks)
- Root directory data block (1 block)
- Total: 4 blocks per transaction

**Output:** `Logged creation of "<filename>" to journal.`

### Command: `./journal install`

**What it does:**
1. Reads journal header and all journal blocks
2. Scans for COMMIT records to find complete transactions
3. Applies all committed DATA records to their target blocks
4. Clears the entire journal (checkpoint)

**Output:** 
- `Installed 1 Commited Transaction from Journal` (for 1 transaction)
- `Installed N Commited Transactions from Journal` (for N transactions)

### Transaction Atomicity
- Incomplete transactions (without COMMIT) are never applied
- Multiple transactions can accumulate in the journal
- All transactions are applied atomically during install
- Journal is cleared only after successful installation

## Usage Examples

### Basic Workflow
```bash
# Create filesystem
./mkfs

# Create a file in journal (doesn't modify filesystem yet)
./journal create hello.txt

# Verify filesystem is unchanged
./validator

# Apply journal changes
./journal install

# Verify file now exists
./validator
```

### Multiple Files (Sequential Install)
```bash
./mkfs
./journal create file1.txt
./journal install              # Installs 1 transaction, clears journal
./journal create file2.txt
./journal install              # Installs 1 transaction
```

### Multiple Files (Batch Install)
```bash
./mkfs
./journal create file1.txt     # Journal has 1 transaction
./journal create file2.txt     # Journal has 2 transactions
./journal install              # Installs 2 transactions, then clears
```

## Key Design Decisions

### 1. Empty File Creation
Files are created with size=0 and no data blocks. This simplifies the implementation and focuses on metadata journaling.

### 2. Transaction Capacity
Each transaction uses approximately 16,428 bytes (4 data blocks + commit record). The 65KB journal can hold approximately 3 complete transactions.

### 3. Overwriting Behavior
Since all creates allocate the same inode (#1) and directory slot, multiple creates before install will result in only the last file being present. This is expected behavior.

### 4. Error Handling
The implementation includes checks for:
- Journal full conditions
- Duplicate filenames
- No free inodes
- No free directory entries
- Invalid journal magic

### 5. Bitmap Management
Uses standard bitmap operations to track allocated inodes:
- `bitmap_test()` - Check if bit is set
- `bitmap_set()` - Set a bit to mark allocation

## Technical Specifications

### Filesystem Layout
```
Block 0:        Superblock
Blocks 1-16:    Journal (16 blocks)
Block 17:       Inode Bitmap
Block 18:       Data Bitmap
Blocks 19-20:   Inode Table (2 blocks, 64 inodes)
Blocks 21-84:   Data Blocks (64 blocks)
```

### Data Structures

**journal_header**: 8 bytes
- magic: 4 bytes
- nbytes_used: 4 bytes

**data_record**: 4,104 bytes
- type: 2 bytes (REC_DATA = 1)
- size: 2 bytes
- block_no: 4 bytes
- data: 4,096 bytes

**commit_record**: 4 bytes
- type: 2 bytes (REC_COMMIT = 2)
- size: 2 bytes

## Compilation

```bash
gcc -o mkfs mkfs.c
gcc -o validator validator.c
gcc -o journal journal.c
```

Or with warnings:
```bash
gcc -Wall -Wextra -o journal journal.c
```

## Testing

### Test 1: Basic Create and Install
```bash
./mkfs
./journal create test.txt
./journal install
./validator  # Should show consistent
```

### Test 2: Multiple Transactions
```bash
./mkfs
./journal create file1.txt
./journal create file2.txt
./journal install
./validator
```

### Test 3: Error - Duplicate File
```bash
./mkfs
./journal create test.txt
./journal install
./journal create test.txt  # Should error: File already exists
```

### Test 4: Incomplete Transaction
If you manually create journal records without a COMMIT, install will skip them with message: "No complete transaction to install"

## Why This Approach?

### Crash Consistency
If the system crashes:
- **After create, before install**: No changes applied, filesystem consistent
- **During install**: Only complete transactions applied, filesystem consistent
- **After install**: Journal cleared, filesystem has all changes

### Advantages
1. **Atomicity**: Either all metadata changes apply or none
2. **Durability**: Changes persisted in journal before modifying filesystem
3. **Consistency**: Always maintainedthrough commit records
4. **Recovery**: Simple - just replay committed transactions

### Limitations
1. **No data journaling**: Only metadata is logged
2. **Fixed journal size**: Limited to 16 blocks
3. **No complex directory operations**: Only root directory supported
4. **No file deletion**: Not implemented in this version

## Understanding the Output

### "Logged creation of..."
Indicates metadata has been written to journal but NOT yet applied to filesystem. The actual filesystem remains unchanged.

### "Installed N Commited Transaction(s)..."
Indicates N complete transactions were found in the journal, all their DATA records were applied to the filesystem, and the journal was cleared.

### Transaction vs Blocks
- **Transaction**: One complete create operation (4 DATA records + 1 COMMIT record)
- **Blocks**: Individual 4KB units being modified

When you see "Installed 1 Commited Transaction", it actually wrote 4 blocks (inode bitmap, 2 inode blocks, root directory).

## Common Issues and Solutions

### Issue: "Journal full"
**Cause**: Too many transactions without installing
**Solution**: Run `./journal install` to clear the journal

### Issue: "File already exists"
**Cause**: File with same name already in filesystem
**Solution**: Use different filename or delete existing file

### Issue: "No complete transaction to install"
**Cause**: Journal has DATA records but no COMMIT
**Solution**: This is correct behavior - incomplete transactions are ignored

## Code Organization

### Main Functions

**create command:**
1. Read current filesystem state
2. Find free resources (inode, directory entry)
3. Prepare updated metadata in memory
4. Write to journal with commit record

**install command:**
1. Read and validate journal
2. Scan for complete transactions
3. Apply all DATA records
4. Clear journal

### Helper Functions
- `read_block()` / `write_block()` - Block I/O
- `bitmap_test()` / `bitmap_set()` - Bitmap operations
- `die()` - Error handling

## Performance Considerations

### Journal Size
16 blocks can hold ~3 transactions. For production use, this would be configurable and much larger.

### Synchronous Writes
All journal writes are synchronous (blocking). In production, this would use barriers and asynchronous I/O.

### Memory Usage
The entire journal (65KB) is read into memory during install. This is acceptable for small journals but would need optimization for larger ones.

## Future Enhancements

1. **Data journaling**: Log file contents, not just metadata
2. **File deletion**: Implement unlink operation
3. **Larger directories**: Support multi-block directories
4. **Journal wrapping**: Circular journal buffer
5. **Selective journaling**: Only log changed fields
6. **Checksums**: Validate journal integrity

## References

- VSFS (Very Simple File System) specification
- ext3/ext4 journaling implementations
- Write-Ahead Logging (WAL) principles

## Author
CSE321 Student - January 2026

## License
Educational use only
