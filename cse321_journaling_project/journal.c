#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define FS_MAGIC 0x56534653U
#define JOURNAL_MAGIC 0x4A524E4CU

#define BLOCK_SIZE        4096U
#define INODE_SIZE         128U
#define JOURNAL_BLOCK_IDX    1U
#define JOURNAL_BLOCKS      16U
#define INODE_BLOCKS         2U
#define DATA_BLOCKS         64U
#define INODE_BMAP_IDX     (JOURNAL_BLOCK_IDX + JOURNAL_BLOCKS)
#define DATA_BMAP_IDX      (INODE_BMAP_IDX + 1U)
#define INODE_START_IDX    (DATA_BMAP_IDX + 1U)
#define DATA_START_IDX     (INODE_START_IDX + INODE_BLOCKS)
#define TOTAL_BLOCKS       (DATA_START_IDX + DATA_BLOCKS)
#define DEFAULT_IMAGE "vsfs.img"

#define REC_DATA   1
#define REC_COMMIT 2

struct superblock {
    uint32_t magic;
    uint32_t block_size;
    uint32_t total_blocks;
    uint32_t inode_count;
    uint32_t journal_block;
    uint32_t inode_bitmap;
    uint32_t data_bitmap;
    uint32_t inode_start;
    uint32_t data_start;
    uint8_t  _pad[128 - 9 * 4];
};

struct inode {
    uint16_t type;
    uint16_t links;
    uint32_t size;
    uint32_t direct[8];
    uint32_t ctime;
    uint32_t mtime;
    uint8_t _pad[128 - (2 + 2 + 4 + 8 * 4 + 4 + 4)];
};

struct dirent {
    uint32_t inode;
    char name[28];
};

struct journal_header {
    uint32_t magic;
    uint32_t nbytes_used;
};

struct rec_header {
    uint16_t type;
    uint16_t size;
};

struct data_record {
    struct rec_header hdr;
    uint32_t block_no;
    uint8_t data[BLOCK_SIZE];
};

struct commit_record {
    struct rec_header hdr;
};

static void die(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

static void read_block(int fd, uint32_t block_no, void *buf) {
    if (pread(fd, buf, BLOCK_SIZE, (off_t)block_no * BLOCK_SIZE) != BLOCK_SIZE) {
        die("pread");
    }
}

static void write_block(int fd, uint32_t block_no, const void *buf) {
    if (pwrite(fd, buf, BLOCK_SIZE, (off_t)block_no * BLOCK_SIZE) != BLOCK_SIZE) {
        die("pwrite");
    }
}

static int bitmap_test(const uint8_t *bitmap, uint32_t index) {
    return (bitmap[index / 8] >> (index % 8)) & 0x1;
}

static void bitmap_set(uint8_t *bitmap, uint32_t index) {
    bitmap[index / 8] |= (uint8_t)(1U << (index % 8));
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <create|install> [args]\n", argv[0]);
        return 1;
    }

    int fd = open(DEFAULT_IMAGE, O_RDWR);
    if (fd < 0) die("open");

    if (strcmp(argv[1], "create") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Usage: %s create <name>\n", argv[0]);
            return 1;
        }
        
        const char *filename = argv[2];
        
        if (strlen(filename) >= 28) {
            fprintf(stderr, "Filename too long (max 27 chars)\n");
            return 1;
        }
        
        struct superblock sb;
        uint8_t block[BLOCK_SIZE];
        read_block(fd, 0, &sb);
        
        uint8_t inode_bitmap[BLOCK_SIZE];
        read_block(fd, INODE_BMAP_IDX, inode_bitmap);
        
        uint8_t inode_blocks[INODE_BLOCKS * BLOCK_SIZE];
        for (uint32_t i = 0; i < INODE_BLOCKS; i++) {
            read_block(fd, INODE_START_IDX + i, inode_blocks + i * BLOCK_SIZE);
        }
        struct inode *inodes = (struct inode *)inode_blocks;
        
        uint8_t root_data[BLOCK_SIZE];
        read_block(fd, DATA_START_IDX, root_data);
        struct dirent *dirents = (struct dirent *)root_data;
        
        int free_inode = -1;
        for (uint32_t i = 0; i < sb.inode_count; i++) {
            if (!bitmap_test(inode_bitmap, i)) {
                free_inode = (int)i;
                break;
            }
        }
        
        if (free_inode == -1) {
            fprintf(stderr, "No free inodes\n");
            close(fd);
            return 1;
        }
        
        int free_dirent = -1;
        uint32_t max_dirents = BLOCK_SIZE / sizeof(struct dirent);
        for (uint32_t i = 0; i < max_dirents; i++) {
            if (dirents[i].inode == 0 && dirents[i].name[0] == '\0') {
                free_dirent = (int)i;
                break;
            }
        }
        
        if (free_dirent == -1) {
            fprintf(stderr, "No free directory entries\n");
            close(fd);
            return 1;
        }
        
        for (uint32_t i = 0; i < max_dirents; i++) {
            if (dirents[i].inode != 0 && strcmp(dirents[i].name, filename) == 0) {
                fprintf(stderr, "File already exists\n");
                close(fd);
                return 1;
            }
        }
        
        bitmap_set(inode_bitmap, (uint32_t)free_inode);
        
        memset(&inodes[free_inode], 0, sizeof(struct inode));
        inodes[free_inode].type = 1;
        inodes[free_inode].links = 1;
        inodes[free_inode].size = 0;
        inodes[free_inode].ctime = (uint32_t)time(NULL);
        inodes[free_inode].mtime = (uint32_t)time(NULL);
        
        dirents[free_dirent].inode = (uint32_t)free_inode;
        strncpy(dirents[free_dirent].name, filename, sizeof(dirents[free_dirent].name) - 1);
        dirents[free_dirent].name[sizeof(dirents[free_dirent].name) - 1] = '\0';
        
        inodes[0].size += sizeof(struct dirent);
        inodes[0].mtime = (uint32_t)time(NULL);
        
        uint8_t *journal_data = malloc(JOURNAL_BLOCKS * BLOCK_SIZE);
        if (!journal_data) die("malloc");
        
        for (uint32_t i = 0; i < JOURNAL_BLOCKS; i++) {
            read_block(fd, JOURNAL_BLOCK_IDX + i, journal_data + i * BLOCK_SIZE);
        }
        
        struct journal_header *jhdr = (struct journal_header *)journal_data;
        if (jhdr->magic != JOURNAL_MAGIC) {
            jhdr->magic = JOURNAL_MAGIC;
            jhdr->nbytes_used = sizeof(struct journal_header);
        }
        
        struct data_record rec;
        
        rec.hdr.type = REC_DATA;
        rec.hdr.size = sizeof(struct data_record);
        rec.block_no = INODE_BMAP_IDX;
        memcpy(rec.data, inode_bitmap, BLOCK_SIZE);
        
        if (jhdr->nbytes_used + sizeof(struct data_record) > JOURNAL_BLOCKS * BLOCK_SIZE) {
            fprintf(stderr, "Journal full\n");
            free(journal_data);
            close(fd);
            return 1;
        }
        
        memcpy(journal_data + jhdr->nbytes_used, &rec, sizeof(struct data_record));
        jhdr->nbytes_used += sizeof(struct data_record);
        
        for (uint32_t i = 0; i < INODE_BLOCKS; i++) {
            rec.block_no = INODE_START_IDX + i;
            memcpy(rec.data, inode_blocks + i * BLOCK_SIZE, BLOCK_SIZE);
            
            if (jhdr->nbytes_used + sizeof(struct data_record) > JOURNAL_BLOCKS * BLOCK_SIZE) {
                fprintf(stderr, "Journal full\n");
                free(journal_data);
                close(fd);
                return 1;
            }
            
            memcpy(journal_data + jhdr->nbytes_used, &rec, sizeof(struct data_record));
            jhdr->nbytes_used += sizeof(struct data_record);
        }
        
        rec.block_no = DATA_START_IDX;
        memcpy(rec.data, root_data, BLOCK_SIZE);
        
        if (jhdr->nbytes_used + sizeof(struct data_record) > JOURNAL_BLOCKS * BLOCK_SIZE) {
            fprintf(stderr, "Journal full\n");
            free(journal_data);
            close(fd);
            return 1;
        }
        
        memcpy(journal_data + jhdr->nbytes_used, &rec, sizeof(struct data_record));
        jhdr->nbytes_used += sizeof(struct data_record);
        
        struct commit_record crec;
        crec.hdr.type = REC_COMMIT;
        crec.hdr.size = sizeof(struct commit_record);
        
        if (jhdr->nbytes_used + sizeof(struct commit_record) > JOURNAL_BLOCKS * BLOCK_SIZE) {
            fprintf(stderr, "Journal full\n");
            free(journal_data);
            close(fd);
            return 1;
        }
        
        memcpy(journal_data + jhdr->nbytes_used, &crec, sizeof(struct commit_record));
        jhdr->nbytes_used += sizeof(struct commit_record);
        
        for (uint32_t i = 0; i < JOURNAL_BLOCKS; i++) {
            write_block(fd, JOURNAL_BLOCK_IDX + i, journal_data + i * BLOCK_SIZE);
        }
        
        free(journal_data);
        
        printf("Logged creation of \"%s\" to journal.\n", filename);
        
    } else if (strcmp(argv[1], "install") == 0) {
        uint8_t journal_block[BLOCK_SIZE];
        read_block(fd, JOURNAL_BLOCK_IDX, journal_block);
        struct journal_header *jhdr = (struct journal_header *)journal_block;
        
        if (jhdr->magic != JOURNAL_MAGIC) {
            printf("No journal entries to install\n");
            close(fd);
            return 0;
        }
        
        uint8_t *journal_data = malloc(JOURNAL_BLOCKS * BLOCK_SIZE);
        if (!journal_data) die("malloc");
        
        for (uint32_t i = 0; i < JOURNAL_BLOCKS; i++) {
            read_block(fd, JOURNAL_BLOCK_IDX + i, journal_data + i * BLOCK_SIZE);
        }
        
        uint32_t offset = sizeof(struct journal_header);
        int has_commit = 0;
        
        while (offset < jhdr->nbytes_used) {
            struct rec_header *rhdr = (struct rec_header *)(journal_data + offset);
            
            if (rhdr->type == REC_COMMIT) {
                has_commit = 1;
                break;
            } else if (rhdr->type == REC_DATA) {
                offset += sizeof(struct data_record);
            } else {
                fprintf(stderr, "Unknown record type %u\n", rhdr->type);
                break;
            }
        }
        
        if (!has_commit) {
            printf("No complete transaction to install\n");
            free(journal_data);
            close(fd);
            return 0;
        }
        
        offset = sizeof(struct journal_header);
        int transactions_applied = 0;
        int in_transaction = 1;
        
        while (offset < jhdr->nbytes_used) {
            struct rec_header *rhdr = (struct rec_header *)(journal_data + offset);
            
            if (rhdr->type == REC_COMMIT) {
                offset += sizeof(struct commit_record);
                transactions_applied++;
                in_transaction = 1;
            } else if (rhdr->type == REC_DATA) {
                if (in_transaction) {
                    struct data_record *drec = (struct data_record *)(journal_data + offset);
                    write_block(fd, drec->block_no, drec->data);
                }
                offset += sizeof(struct data_record);
            } else {
                fprintf(stderr, "Unknown record type %u\n", rhdr->type);
                break;
            }
        }
        
        memset(journal_data, 0, JOURNAL_BLOCKS * BLOCK_SIZE);
        for (uint32_t i = 0; i < JOURNAL_BLOCKS; i++) {
            write_block(fd, JOURNAL_BLOCK_IDX + i, journal_data + i * BLOCK_SIZE);
        }
        
        free(journal_data);
        
        if (transactions_applied == 1) {
            printf("Installed 1 Commited Transaction from Journal\n");
        } else {
            printf("Installed %d Commited Transactions from Journal\n", transactions_applied);
        }
        
    } else {
        fprintf(stderr, "Unknown command: %s\n", argv[1]);
        return 1;
    }

    close(fd);
    return 0;
}
