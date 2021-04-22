// #pragma GCC optimize(3)
// #pragma GCC optimize("Ofast")
// #pragma GCC target("sse,sse2,sse3,ssse3,sse4,sse4.1,sse4.2,popcnt,abm,mmx,avx,avx2")
// #pragma GCC optimize("unroll-loops")
// #pragma GCC optimize("profile-values,profile-reorder-functions,tracer")
// #pragma GCC optimize("vpt")
// #pragma GCC optimize("rename-registers")
// #pragma GCC optimize("move-loop-invariants")
// #pragma GCC optimize("unswitch-loops")
// #pragma GCC optimize("function-sections")
// #pragma GCC optimize("data-sections")
// #pragma GCC optimize("branch-target-load-optimize")
// #pragma GCC optimize("branch-target-load-optimize2")
// #pragma GCC optimize("btr-bb-exclusive")
// #pragma GCC optimize("inline")
// #pragma GCC optimize("-fgcse")
// #pragma GCC optimize("-fgcse-lm")
// #pragma GCC optimize("-fipa-sra")
// #pragma GCC optimize("-ftree-pre")
// #pragma GCC optimize("-ftree-vrp")
// #pragma GCC optimize("-fpeephole2")
// #pragma GCC optimize("-ffast-math")
// #pragma GCC optimize("-fsched-spec")
// #pragma GCC optimize("-falign-jumps")
// #pragma GCC optimize("-falign-loops")
// #pragma GCC optimize("-falign-labels")
// #pragma GCC optimize("-fdevirtualize")
// #pragma GCC optimize("-fcaller-saves")
// #pragma GCC optimize("-fcrossjumping")
// #pragma GCC optimize("-fthread-jumps")
// #pragma GCC optimize("-freorder-blocks")
// #pragma GCC optimize("-fschedule-insns")
// #pragma GCC optimize("inline-functions")
// #pragma GCC optimize("-ftree-tail-merge")
// #pragma GCC optimize("-fschedule-insns2")
// #pragma GCC optimize("-fstrict-aliasing")
// #pragma GCC optimize("-falign-functions")
// #pragma GCC optimize("-fcse-follow-jumps")
// #pragma GCC optimize("-fsched-interblock")
// #pragma GCC optimize("-fpartial-inlining")
// #pragma GCC optimize("no-stack-protector")
// #pragma GCC optimize("-freorder-functions")
// #pragma GCC optimize("-findirect-inlining")
// #pragma GCC optimize("-fhoist-adjacent-loads")
// #pragma GCC optimize("-frerun-cse-after-loop")
// #pragma GCC optimize("inline-small-functions")
// #pragma GCC optimize("-finline-small-functions")
// #pragma GCC optimize("-ftree-switch-conversion")
// #pragma GCC optimize("-foptimize-sibling-calls")
// #pragma GCC optimize("-fexpensive-optimizations")
// #pragma GCC optimize("inline-functions-called-once")
// #pragma GCC optimize("-fdelete-null-pointer-checks")
// #define INTER

#include <bits/stdc++.h>

//----------------------------------------------------------------
typedef long long ll;
typedef long double ld;
typedef std::pair<ll, ll> pll;
typedef std::pair<int, int> pii;

std::random_device rd;
std::mt19937 randomizer(rd());
const int inf = 0x3f3f3f3f;
const ll llinf = 0x3f3f3f3f3f3f3f3f;
const ld eps = 1e-15;
const ll mod = 786433;

//----------------------------------------------------------------
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define fast_io std::ios::sync_with_stdio(false), std::cin.tie(0), std::cout.tie(0), std::cerr.tie(0);
#define debug(x) std::cerr << #x << ": " << x << '\n'
#define PROBLEM "task"
#define mp std::make_pair

template<typename T, typename T1>
inline T mx(T &a, T1 b) { return (a > b ? a : a = b); }

template<typename T, typename T1>
inline T mn(T &a, T1 b) { return (a < b ? a : a = b); }
//----------------------------------------------------------------

const int MAXN = 2e5;
const int K = 20;

int n;
int a[MAXN];
int jumps[K][MAXN];

int tree[2 * MAXN];
void upd(int v, int val) {
    v += MAXN;
    tree[v] = val;
    v /= 2;
    while(v > 0) {
        tree[v] = std::min(tree[2 * v], tree[2 * v + 1]);
        v /= 2;
    }
}

int get(int l, int r) {
    l += MAXN, r += MAXN;
    int ans = inf;
    while(l < r) {
        if(l & 1) mn(ans, tree[l]);
        if(!(r & 1)) mn(ans, tree[r]);
        l = (l + 1) / 2;
        r = (r - 1) / 2;
    }
    if(l == r) mn(ans, tree[l]);

    return ans;
}

int32_t main() {
#ifndef DEBUG
#ifndef INTER
    fast_io;
#endif
#endif

    std::cout << std::setprecision(15) << std::fixed;
    std::cerr << std::setprecision(15) << std::fixed;
    ld START_TIME = clock();

    memset(tree, inf, sizeof tree);
    int q;
    std::cin >> n >> q;
    for(int i = 0; i < n; i++) std::cin >> a[i];
    std::unordered_map<int, std::vector<int>> divs;
    for(int i = 0; i < n; i++) {
        int j = a[i];
        for(int k = 2; k * k <= j; k++) {
            if(j % k == 0) {
                divs[k].push_back(i);
                while(j % k == 0) j /= k;
            }
        }
        if(j > 1) divs[j].push_back(i);
    }

    std::fill(jumps[0], jumps[0] + n, n);

    for(auto &i : divs) {
        for(int j = 0; j < (int)i.second.size() - 1; j++) {
            mn(jumps[0][i.second[j]], i.second[j + 1]);
        }
    }

    for(int i = n - 1; i >= 0; i--) {
        upd(i, jumps[0][i]);
        upd(i, get(i, jumps[0][i]));
        jumps[0][i] = get(i, i);
    }

    for(int k = 1; k < K; k++) {
        for(int i = 0; i < n; i++) {
            if(jumps[k - 1][i] == n) jumps[k][i] = n;
            else jumps[k][i] = jumps[k - 1][jumps[k - 1][i]];
        }
    }

    while(q--) {
        int l, r;
        std::cin >> l >> r;
        l--, r--;
        int ans = 0;
        for(int k = K - 1; k >= 0; k--) {
            if(jumps[k][l] <= r) ans += (1 << k), l = jumps[k][l];
        }

        std::cout << ans + 1 << '\n';
    }

#ifdef DEBUG
    std::cerr << '\n';
    ld TIME = (clock() - START_TIME) / CLOCKS_PER_SEC;
    debug(TIME);
#endif
}
