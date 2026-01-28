#include <iostream>
#include <iomanip>
#include <chrono>

int main() {
    const int iterations = 200000000;   // 200 million
    const int param1 = 4;
    const int param2 = 1;

    auto start = std::chrono::high_resolution_clock::now();

    double result = 1.0;
    int j1 = param1 - param2;   // 3
    int j2 = param1 + param2;   // 5

    for (int i = 1; i <= iterations; ++i) {
        result -= 1.0 / j1;
        result += 1.0 / j2;
        j1 += param1;           // increment by 4 each loop
        j2 += param1;
    }

    result *= 4.0;

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    std::cout << std::fixed << std::setprecision(12)
              << "Result: " << result << '\n';
    std::cout << std::fixed << std::setprecision(6)
              << "Execution Time: " << elapsed.count() << " seconds\n";

    return 0;
}