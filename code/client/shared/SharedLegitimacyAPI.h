#pragma once

#include <string>
#include <cstdint>
#include <vector>
#include <optional>
#include <functional>

namespace cfx::legitimacy
{
using AuthCallback = void(bool success, const char* data, size_t length);
using ProcessHeadersCallback = void(const char*, const char*);

void DLL_IMPORT AuthenticateDiscord(const char* userId, const char* code, AuthCallback callback);
void DLL_IMPORT AuthenticateDiscourse(const char* clientId, const char* authToken, AuthCallback callback);

bool DLL_IMPORT ShouldProcessHeaders(const char* hostname);
void DLL_IMPORT ProcessHeaders(char*, char*);

// New Steam Auth (stubs for missing legitimacy.dll exports)
inline bool IsSteamLinked()
{
	return false;
}

inline void AttemptSteamAuth(const std::function<void(std::pair<std::string, std::string>)>& callback, bool forceAuth)
{
	if (callback)
	{
		callback({ "Steam auth is currently unavailable (stub)", "" });
	}
}

inline void RefreshIdentities()
{
}
}
