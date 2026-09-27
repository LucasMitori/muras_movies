"""Minimal TMDB v3 client.

Non-commercial use requires attribution per TMDB's terms
(https://developer.themoviedb.org/docs/faq). This client only reads data —
it never assumes redistribution rights beyond what TMDB's API grants.
"""

from __future__ import annotations

import httpx
from django.conf import settings


class TMDBError(Exception):
    pass


class TMDBNotConfigured(TMDBError):
    pass


class TMDBClient:
    def __init__(self, api_key: str | None = None, timeout: float = 10.0):
        self.api_key = api_key or settings.TMDB_API_KEY
        if not self.api_key:
            raise TMDBNotConfigured("TMDB_API_KEY is not set. Add it to backend/.env.")
        self._client = httpx.Client(
            base_url=settings.TMDB_API_BASE_URL,
            timeout=timeout,
            headers={"Accept": "application/json"},
            params={"api_key": self.api_key},
        )

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._client.close()

    def _get(self, path: str, **params) -> dict:
        response = self._client.get(path, params=params)
        if response.status_code == 404:
            raise TMDBError(f"Not found: {path}")
        response.raise_for_status()
        return response.json()

    def movie(self, tmdb_id: int, language: str = "pt-BR") -> dict:
        return self._get(f"/movie/{tmdb_id}", language=language)

    def series(self, tmdb_id: int, language: str = "pt-BR") -> dict:
        return self._get(f"/tv/{tmdb_id}", language=language)

    def popular_movies(self, page: int = 1, language: str = "pt-BR") -> dict:
        return self._get("/movie/popular", page=page, language=language)

    def popular_series(self, page: int = 1, language: str = "pt-BR") -> dict:
        return self._get("/tv/popular", page=page, language=language)
