#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <array>
#include <iostream>
#include <string_view>

// cpp_bench: tb_merge_b's draft order, so the benchmarked champions match the real roster.
void play_draft() {
    using D = cambc::champion_draft;
    static constexpr std::array priority{ D::vesper_vale, D::vendetta, D::marcella, D::heart_of_ruin, D::ryth,
        D::tavi, D::varg, D::ren, D::willow, D::stellar, D::prism, D::cassi_and_issac };
    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    if (cambc::is_draft() && chosen.empty()) {
        const auto f0 = cambc::fuel_remaining();
        auto groups = cambc::map::camp_groups();
        const auto f1 = cambc::fuel_remaining();
        std::cout << "DRAFT fuel_now=" << f0 << " camp_groups_load=" << (f0 - f1) << " groups=" << groups.size() << '\n';
        cambc::draft_memory = std::string_view("cpp_bench");
    }
    for (auto pick : priority) {
        if (std::find(chosen.begin(), chosen.end(), pick) != chosen.end()) continue;
        try {
            cambc::draft::pick(pick);
            return;
        } catch (const std::exception& e) {
            std::cout << "draft pick failed " << static_cast<int>(pick) << ' ' << e.what() << '\n';
        }
    }
}
