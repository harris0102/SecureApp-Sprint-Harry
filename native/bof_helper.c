/* bof_helper.c - CWE-120 buffer overflow demo + fix (one binary, two modes).
 * Vulnerable + ASAN:  gcc -fsanitize=address -g -fno-stack-protector native/bof_helper.c -o native/bof_asan
 * Hardened:           gcc -fstack-protector-strong -D_FORTIFY_SOURCE=2 -O2 native/bof_helper.c -o native/bof_hardened
 */
#include <stdio.h>
#include <string.h>

static void vulnerable_process(const char *input) {
    char buffer[64];
    strcpy(buffer, input);                 /* no bounds check */
    printf("[vuln]   processed: %s\n", buffer);
}
static void secure_process(const char *input) {
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%s", input);
    buffer[sizeof(buffer) - 1] = '\0';
    printf("[secure] processed (bounded to %zu bytes): %s\n", sizeof(buffer) - 1, buffer);
}
int main(int argc, char *argv[]) {
    if (argc < 3) { fprintf(stderr, "Usage: %s <vuln|secure> <input>\n", argv[0]); return 2; }
    if (strcmp(argv[1], "secure") == 0) secure_process(argv[2]);
    else vulnerable_process(argv[2]);
    return 0;
}
