#pragma once

#include <charconv>
#include <chrono>
#include <cstring>
#include <thread>

volatile bool alive = true;
std::thread *timer;

void killAfter(int timeSeconds){
    std::this_thread::sleep_for(std::chrono::seconds(timeSeconds));
    alive = false;
}

void init_workload(int durationSeconds){
    alive = true;
    timer = new std::thread(killAfter, durationSeconds);
}

void fini_workload(){
    timer->join();
}

bool parse_int(const char* s, int &out) {
    auto [ptr, ec] = std::from_chars(s, s + std::strlen(s), out);
    return ec == std::errc() && *ptr == '\0';
}
