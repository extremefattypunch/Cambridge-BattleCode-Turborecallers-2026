// Draft: deterministic priority list (tb_merge_b draft.py, the second PRIORITY list).
#include <cambc.h>

#include <array>
#include <cstring>
#include <iostream>
#include <vector>

#include "draft.h"

void play_draft()
{
	using D = cambc::champion_draft;
	static constexpr std::array<D, 12> PRIORITY{ D::vesper_vale, D::vendetta, D::marcella, D::heart_of_ruin,
												 D::ryth,        D::tavi,     D::varg,     D::ren,
												 D::willow,      D::stellar,  D::prism,    D::cassi_and_issac };
	const auto chosen = cambc::draft::current_draft(cambc::team::ally);
	static constexpr char MEM[] = "tb_splitfarm v1";
	cambc::detail::sdk_bc_submit_draft_memory(MEM, std::strlen(MEM));
	for (auto pick : PRIORITY)
	{
		bool taken = false;
		for (auto c : chosen)
			if (c == pick) taken = true;
		if (taken) continue;
		if (cambc::detail::sdk_draft_champion(static_cast<std::int32_t>(pick)) == 0) return;
		debug_block({ std::cout << "draft pick failed " << static_cast<int>(pick) << '\n'; });
	}
}
