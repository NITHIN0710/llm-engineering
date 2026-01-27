#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    const int iterations = 200'000'000;
    const double param1 = 4.0;
    const double param2 = 1.0;

    auto start = chrono::high_resolution_clock::now();

    double result = 1.0;
    for (int i = 1; i <= iterations; ++i) {
        double i4 = i * param1;
        result -= 1.0 / (i4 - param2);
        result += 1.0 / (i4 + param2);
    }
    result *= 4.0;

    auto end = chrono::high_resolution_clock::now();
    double elapsed = chrono::duration<double>(end - start).count();

    cout << fixed << setprecision(12) << "Result: " << result << "\n";
    cout << fixed << setprecision(6) << "Execution Time: " << elapsed << " seconds\n";
    return 0;
}
