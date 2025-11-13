#include <stdio.h>
#include <stdint.h>

#include "../workload.h"

const char* name = "int_add_ind";

void workload(){
  printf("%s\n", name);
  uint64_t i = 0, count0 = 0, count1 = 0, count2 = 0, count3 = 0, count4 = 0,
           count5 = 0, count6 = 0, count7 = 0;

  do {
    asm volatile("add %0, %0" : "=r"(count0) : "0"(count0) :);
    asm volatile("add %0, %0" : "=r"(count1) : "0"(count1) :);
    asm volatile("add %0, %0" : "=r"(count2) : "0"(count2) :);
    asm volatile("add %0, %0" : "=r"(count3) : "0"(count3) :);
    asm volatile("add %0, %0" : "=r"(count4) : "0"(count4) :);
    asm volatile("add %0, %0" : "=r"(count5) : "0"(count5) :);
    asm volatile("add %0, %0" : "=r"(count6) : "0"(count6) :);
    asm volatile("add %0, %0" : "=r"(count7) : "0"(count7) :);

    asm volatile("add %0, %0" : "=r"(count0) : "0"(count0) :);
    asm volatile("add %0, %0" : "=r"(count1) : "0"(count1) :);
    asm volatile("add %0, %0" : "=r"(count2) : "0"(count2) :);
    asm volatile("add %0, %0" : "=r"(count3) : "0"(count3) :);
    asm volatile("add %0, %0" : "=r"(count4) : "0"(count4) :);
    asm volatile("add %0, %0" : "=r"(count5) : "0"(count5) :);
    asm volatile("add %0, %0" : "=r"(count6) : "0"(count6) :);
    asm volatile("add %0, %0" : "=r"(count7) : "0"(count7) :);

    asm volatile("add %0, %0" : "=r"(count0) : "0"(count0) :);
    asm volatile("add %0, %0" : "=r"(count1) : "0"(count1) :);
    asm volatile("add %0, %0" : "=r"(count2) : "0"(count2) :);
    asm volatile("add %0, %0" : "=r"(count3) : "0"(count3) :);
    asm volatile("add %0, %0" : "=r"(count4) : "0"(count4) :);
    asm volatile("add %0, %0" : "=r"(count5) : "0"(count5) :);
    asm volatile("add %0, %0" : "=r"(count6) : "0"(count6) :);
    asm volatile("add %0, %0" : "=r"(count7) : "0"(count7) :);

    asm volatile("add %0, %0" : "=r"(count0) : "0"(count0) :);
    asm volatile("add %0, %0" : "=r"(count1) : "0"(count1) :);
    asm volatile("add %0, %0" : "=r"(count2) : "0"(count2) :);
    asm volatile("add %0, %0" : "=r"(count3) : "0"(count3) :);
    asm volatile("add %0, %0" : "=r"(count4) : "0"(count4) :);
    asm volatile("add %0, %0" : "=r"(count5) : "0"(count5) :);
    asm volatile("add %0, %0" : "=r"(count6) : "0"(count6) :);
    asm volatile("add %0, %0" : "=r"(count7) : "0"(count7) :);
    i++;
  } while (alive);

  volatile int64_t avoidOtimization = count0 + count1 + count2 + count3 + count4 + count5 + count6 + count7;
  (void)avoidOtimization;
  
  printf("%s | Result: %lu\n", name, i);
}

int main(int argc, char* argv[]) {

  int durationSeconds;
  if(argc != 2 || !parse_int(argv[1], durationSeconds)){
    fprintf(stderr, "Invalid parameter.\n");
    return -1;
  }

  init_workload(durationSeconds);
  workload();
  fini_workload();
  
  return 0;
}
