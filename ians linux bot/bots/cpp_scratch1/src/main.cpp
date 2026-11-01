// Dispatch draft and gameplay; a failed turn is logged and still yields.
#include <cambc.h>

#include <iostream>

#include "bot.h"
#include "draft.h"

int main()
{
	Bot bot;
	while (true)
	{
		try
		{
			if (cambc::is_draft())
				play_draft();
			else
			{
				debug_block({ g_prof.reset(); });
				PROF("start");
				bot.play_turn();
				PROF("play_turn");
				bot.build_static_fields();
				PROF("static");
				debug_block({
					if (g_prof.n >= 2 && g_prof.fuel[0] - g_prof.fuel[g_prof.n - 1] > 60000)
					{
						std::cout << "PROF r" << cambc::round_number() << " used " << (g_prof.fuel[0] - g_prof.fuel[g_prof.n - 1]);
						for (int i = 1; i < g_prof.n; ++i)
							std::cout << ' ' << g_prof.name[i] << '=' << (g_prof.fuel[i - 1] - g_prof.fuel[i]);
						std::cout << std::endl;
					}
				});
			}
		}
		catch (const std::exception& error)
		{
			std::cout << "bot error: " << error.what() << std::endl;
		}
		catch (...)
		{
			std::cout << "bot error: unknown exception" << std::endl;
		}
		cambc::end_turn();
	}
}
