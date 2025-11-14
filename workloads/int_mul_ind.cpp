#include <stdint.h>
#include <stdio.h>

#include "../workload.h"

const char* name = "int_mul_ind";

void workload() {
    uint64_t i = 0, count0 = 1, count1 = 1, count2 = 1, count3 = 1, count4 = 1,
             count5 = 1, count6 = 1, count7 = 1;

    do {
      asm volatile("imul %0, %0" : "=r"(count0) : "0"(count0) :);
      asm volatile("imul %0, %0" : "=r"(count1) : "0"(count1) :);
      asm volatile("imul %0, %0" : "=r"(count2) : "0"(count2) :);
      asm volatile("imul %0, %0" : "=r"(count3) : "0"(count3) :);
      asm volatile("imul %0, %0" : "=r"(count4) : "0"(count4) :);
      asm volatile("imul %0, %0" : "=r"(count5) : "0"(count5) :);
      asm volatile("imul %0, %0" : "=r"(count6) : "0"(count6) :);
      asm volatile("imul %0, %0" : "=r"(count7) : "0"(count7) :);

      asm volatile("imul %0, %0" : "=r"(count0) : "0"(count0) :);
      asm volatile("imul %0, %0" : "=r"(count1) : "0"(count1) :);
      asm volatile("imul %0, %0" : "=r"(count2) : "0"(count2) :);
      asm volatile("imul %0, %0" : "=r"(count3) : "0"(count3) :);
      asm volatile("imul %0, %0" : "=r"(count4) : "0"(count4) :);
      asm volatile("imul %0, %0" : "=r"(count5) : "0"(count5) :);
      asm volatile("imul %0, %0" : "=r"(count6) : "0"(count6) :);
      asm volatile("imul %0, %0" : "=r"(count7) : "0"(count7) :);

      asm volatile("imul %0, %0" : "=r"(count0) : "0"(count0) :);
      asm volatile("imul %0, %0" : "=r"(count1) : "0"(count1) :);
      asm volatile("imul %0, %0" : "=r"(count2) : "0"(count2) :);
      asm volatile("imul %0, %0" : "=r"(count3) : "0"(count3) :);
      asm volatile("imul %0, %0" : "=r"(count4) : "0"(count4) :);
      asm volatile("imul %0, %0" : "=r"(count5) : "0"(count5) :);
      asm volatile("imul %0, %0" : "=r"(count6) : "0"(count6) :);
      asm volatile("imul %0, %0" : "=r"(count7) : "0"(count7) :);

      asm volatile("imul %0, %0" : "=r"(count0) : "0"(count0) :);
      asm volatile("imul %0, %0" : "=r"(count1) : "0"(count1) :);
      asm volatile("imul %0, %0" : "=r"(count2) : "0"(count2) :);
      asm volatile("imul %0, %0" : "=r"(count3) : "0"(count3) :);
      asm volatile("imul %0, %0" : "=r"(count4) : "0"(count4) :);
      asm volatile("imul %0, %0" : "=r"(count5) : "0"(count5) :);
      asm volatile("imul %0, %0" : "=r"(count6) : "0"(count6) :);
      asm volatile("imul %0, %0" : "=r"(count7) : "0"(count7) :);
      i++;
    } while (alive);

    volatile int64_t avoidOtimization =
        count0 + count1 + count2 + count3 + count4 + count5 + count6 + count7;
    (void)avoidOtimization;

    printf("%s | Result: %lu\n", name, i);
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
