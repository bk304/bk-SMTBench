#include <stdint.h>
#include <cinttypes>
#include <cstdint>

#include "../workload.h"

const char* name = "int_prf_stress";

#define BUFSIZE (64UL * 1024 * 1024)   // 64 MiB (LLC +)
#define UNROLL  32                    // writes per inner loop
#define OUTER   64                    // total writes = UNROLL * OUTER = 2048

static uint8_t* bigbuf = nullptr;
volatile uint64_t sink = 0;

// simple PRNG
static inline uint64_t xorshift64(uint64_t* s) {
    uint64_t x = *s;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *s = x;
    return x;
}

void workload() {
    uint64_t state = (uint64_t)time(nullptr) ^ (uintptr_t)&state;

    if (!bigbuf) {
        void* p = nullptr;
        posix_memalign(&p, 4096, BUFSIZE);
        bigbuf = (uint8_t*)p;

        // Touch pages so they exist, but aren't hot
        for (size_t i = 0; i < BUFSIZE; i += 4096)
            bigbuf[i] = (uint8_t)i;
    }

    do {
        size_t off = xorshift64(&state) % (BUFSIZE - 64);
        uint8_t* addr = bigbuf + off;

        // 1) long-latency load (LLC miss)
        asm volatile(
            "movq (%0), %%r11\n\t"
            :
            : "r"(addr)
            : "r11", "memory"
        );

        // 2) flood integer physical registers
        for (int o = 0; o < OUTER; o++) {
            asm volatile(
                "movq $1, %%r12\n\t"
                "movq $2, %%r13\n\t"
                "movq $3, %%r14\n\t"
                "movq $4, %%r15\n\t"
                "movq $5, %%rax\n\t"
                "movq $6, %%rbx\n\t"
                "movq $7, %%rcx\n\t"
                "movq $8, %%rdx\n\t"
                "movq $9, %%rsi\n\t"
                "movq $10, %%rdi\n\t"
                "movq $11, %%rbp\n\t"
                "movq $12, %%r8\n\t"
                "movq $13, %%r9\n\t"
                :
                :
                : "rax","rbx","rcx","rdx","rsi","rdi","rbp",
                  "r8","r9","r12","r13","r14","r15","memory"
            );
        }
    } while (alive);
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
