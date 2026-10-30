#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// VULNERABLE FUNCTION: Unsafe strcpy susceptible to Buffer Overflow
void vulnerable_process(char *input) {
    char buffer[64];
    strcpy(buffer, input); // No bounds checking!
    printf("Processed input: %s\n", buffer);
}

// SECURED FUNCTION: Safe bounds checking using snprintf
void secure_process(char *input) {
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%s", input);
    printf("Safely processed input: %s\n", buffer);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <input_string>\n", argv[1]);
        return 1;
    }
    // Toggle between vulnerable_process and secure_process for lab demonstration
    vulnerable_process(argv[1]);
    return 0;
}
