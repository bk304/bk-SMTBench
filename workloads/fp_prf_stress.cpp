#include <stdint.h>
#include <stdio.h>
#include <cinttypes>
#include <cstdint>

#include "../workload.h"

const char* name = "fp_prf_stress";

#define BUFSIZE (64UL * 1024 * 1024)   // > LLC
#define OUTER   64                    // pressão ajustável

static uint8_t* bigbuf = nullptr;
volatile double sink_fp = 0.0;

static inline uint64_t xorshift64(uint64_t* s) {
    uint64_t x = *s;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *s = x;
    return x;
}

void workload() {
    uint64_t iters = 0;
    uint64_t state = (uint64_t)time(nullptr) ^ (uintptr_t)&state;

    if (!bigbuf) {
        void* p = nullptr;
        posix_memalign(&p, 4096, BUFSIZE);
        bigbuf = (uint8_t*)p;
        for (size_t i = 0; i < BUFSIZE; i += 4096)
            bigbuf[i] = (uint8_t)i;
    }

    do {
        size_t off = xorshift64(&state) % (BUFSIZE - 64);
        uint8_t* addr = bigbuf + off;

        // 1) Retire blocker (long-latency load)
        asm volatile(
            "movq (%0), %%r11\n\t"
            :
            : "r"(addr)
            : "r11", "memory"
        );

        // 2) Flood FP physical registers
        for (int o = 0; o < OUTER; o++) {
            asm volatile(
                "pxor %%xmm0, %%xmm0\n\t"
                "pxor %%xmm1, %%xmm1\n\t"
                "pxor %%xmm2, %%xmm2\n\t"
                "pxor %%xmm3, %%xmm3\n\t"
                "pxor %%xmm4, %%xmm4\n\t"
                "pxor %%xmm5, %%xmm5\n\t"
                "pxor %%xmm6, %%xmm6\n\t"
                "pxor %%xmm7, %%xmm7\n\t"
                "pxor %%xmm8, %%xmm8\n\t"
                "pxor %%xmm9, %%xmm9\n\t"
                "pxor %%xmm10, %%xmm10\n\t"
                "pxor %%xmm11, %%xmm11\n\t"
                "pxor %%xmm12, %%xmm12\n\t"
                "pxor %%xmm13, %%xmm13\n\t"
                "pxor %%xmm14, %%xmm14\n\t"
                "pxor %%xmm15, %%xmm15\n\t"
                :
                :
                : "xmm0","xmm1","xmm2","xmm3",
                  "xmm4","xmm5","xmm6","xmm7",
                  "xmm8","xmm9","xmm10","xmm11",
                  "xmm12","xmm13","xmm14","xmm15",
                  "memory"
            );
        }

        iters++;
    } while (alive);

    printf("%s | Result: %lu\n", name, iters);
}

int main(int argc, char* argv[]) {
    int durationSeconds;
    if (argc != 2 || !parse_int(argv[1], durationSeconds)) {
        fprintf(stderr, "Invalid parameter.\n");
        return -1;
    }

    init_workload(durationSeconds);
    workload();
    fini_workload();

    return 0;
}
