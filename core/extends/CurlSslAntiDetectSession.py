"""
Monkey-patcher for requests library to use curl_cffi with SSL/TLS anti-detection

This module patches the standard requests library to use curl_cffi's Session
which provides better SSL/TLS fingerprinting and browser impersonation.

Features:
- Automatic JA3 fingerprint rotation
- Multiple browser profile impersonation
- Drop-in replacement for requests.Session
- Transparent patching of requests module

Usage:
    # In bootstrap or early initialization
    from core.extends.CurlSslAntiDetectSession import install_anti_detect_session
    install_anti_detect_session()

    # Then use requests normally
    import requests
    response = requests.get('https://example.com')  # Uses curl_cffi
"""

#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

import random
import threading
from typing import Optional, List, Dict, Any
from curl_cffi.requests import Session as CurlSession
from curl_cffi import requests as curl_requests
import requests as original_requests
from core.Logging import logger


class BrowserProfile:
    """Browser profile configuration for impersonation"""

    chromeVersions = ['chrome110', 'chrome116', 'chrome119', 'chrome120', 'chrome123', 'chrome124', 'chrome99']
    edgeVersions = ['edge101', 'edge99']
    safariVersions = ['safari15_3', 'safari15_5', 'safari17_0']
    allProfiles = chromeVersions + edgeVersions + safariVersions

    @classmethod
    def getRandomProfile(cls) -> str:
        """Get random browser profile"""
        return random.choice(cls.allProfiles)

    @classmethod
    def getRandomChrome(cls) -> str:
        """Get random Chrome profile"""
        return random.choice(cls.chromeVersions)

    @classmethod
    def getRandomSafari(cls) -> str:
        """Get random Chrome profile"""
        return random.choice(cls.safariVersions)


class AntiDetectSession(CurlSession):
    """
    Drop-in replacement for requests.Session with anti-detection features

    This session automatically rotates JA3 fingerprints by using different
    browser profiles for impersonation.
    """

    _lock = threading.Lock()
    _global_profile_rotation = True
    _profile_pool: List[str] = BrowserProfile.allProfiles.copy()
    _current_profile_index = 0

    def __init__(self, impersonate: Optional[str] = None, autoRotate: bool = False, profilePool: Optional[List[str]] = None, **kwargs):
        """
        Initialize AntiDetectSession
        Args:
            impersonate: Browser profile to impersonate. If None, uses random profile
            auto_rotate: If True, rotate profile on each request
            profile_pool: Custom list of profiles to rotate through
            **kwargs: Additional arguments passed to curl_cffi.Session
        """
        if impersonate is None:
            impersonate = self._get_next_profile()
        super().__init__(impersonate=impersonate, **kwargs)
        self._auto_rotate = autoRotate
        self._profile_pool = profilePool or BrowserProfile.allProfiles
        self._current_impersonate = impersonate
        logger.debug(f'AntiDetectSession initialized with profile: {impersonate}')

    @classmethod
    def _get_next_profile(cls) -> str:
        """Get next profile from rotation pool (thread-safe)"""
        with cls._lock:
            if not cls._global_profile_rotation:
                return BrowserProfile.getRandomProfile()
            profile = cls._profile_pool[cls._current_profile_index]
            cls._current_profile_index = (cls._current_profile_index + 1) % len(cls._profile_pool)
            return profile

    def rotateProfile(self, profile: Optional[str] = None) -> str:
        """
        Rotate to a new browser profile
        Args:
            profile: Specific profile to switch to. If None, gets next from pool
        Returns:
            The new profile name
        """
        if profile is None:
            profile = self._get_next_profile()
        self.close()
        super().__init__(impersonate=profile)
        self._current_impersonate = profile
        logger.debug(f'Rotated to profile: {profile}')
        return profile

    def request(self, method: str, url: str, **kwargs) -> Any:
        """
        Make HTTP request with optional auto-rotation
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional request parameters
        Returns:
            Response object
        """
        if self._auto_rotate:
            self.rotateProfile()
        return super().request(method, url, **kwargs)

    @property
    def currentProfile(self) -> str:
        """Get current browser profile"""
        return self._current_impersonate

    @classmethod
    def configureRotation(cls, enabled: bool = True, profilePool: Optional[List[str]] = None):
        """
        Configure global profile rotation
        Args:
            enabled: Enable/disable global rotation
            profile_pool: Custom profile pool for rotation
        """
        with cls._lock:
            cls._global_profile_rotation = enabled
            if profilePool:
                cls._profile_pool = profilePool
                cls._current_profile_index = 0
            logger.info(f'Profile rotation configured: enabled={enabled}, pool_size={len(cls._profile_pool)}')


def installAntiDetectSession(autoRotate: bool = False, profilePool: Optional[List[str]] = None):
    """
    Install anti-detect session by monkey-patching requests module
    This replaces requests.Session with AntiDetectSession and patches
    module-level convenience functions (get, post, etc.) to use curl_cffi.
    Args:
        auto_rotate: Enable auto-rotation for all sessions
        profile_pool: Custom profile pool for rotation
    Example:
        >>> from core.extends import install_anti_detect_session
        >>> install_anti_detect_session(auto_rotate=True)
        >>> import requests
        >>> response = requests.get('https://httpbin.org/headers')
        >>> print(response.status_code)
    """
    if profilePool:
        AntiDetectSession.configureRotation(enabled=True, profilePool=profilePool)
    originalRequests.Session = AntiDetectSession
    originalRequests.session = lambda: AntiDetectSession(autoRotate=autoRotate)
    for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
        setattr(originalRequests, method, getattr(curlRequests, method))
    logger.info(f'Anti-detect session installed: auto_rotate={autoRotate}, profile_pool_size={(len(profilePool) if profilePool else len(BrowserProfile.allProfiles))}')


def createAntiDetectSession(impersonate: Optional[str] = None, autoRotate: bool = False, profilePool: Optional[List[str]] = None) -> AntiDetectSession:
    """
    Create a new AntiDetectSession instance
    Args:
        impersonate: Browser profile to impersonate
        auto_rotate: Enable auto-rotation
        profile_pool: Custom profile pool
    Returns:
        Configured AntiDetectSession
    """
    return AntiDetectSession(impersonate=impersonate, autoRotate=autoRotate, profilePool=profilePool)


def getAvailableProfiles() -> Dict[str, List[str]]:
    """Get all available browser profiles grouped by browser"""
    return {'chrome': BrowserProfile.chromeVersions, 'edge': BrowserProfile.edgeVersions, 'safari': BrowserProfile.safariVersions, 'all': BrowserProfile.allProfiles}
