"""Caching layer for AI job analysis results."""

import hashlib
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict

import structlog

from src.schemas.ai_analysis import AIJobAnalysisResult

logger = structlog.get_logger(__name__)

# Cache TTL in seconds (24 hours)
CACHE_TTL = 24 * 60 * 60


@dataclass
class CacheEntry:
    """A cached analysis result with metadata."""

    result: AIJobAnalysisResult
    created_at: float = field(default_factory=time.time)
    description_hash: str = ""

    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return time.time() - self.created_at > CACHE_TTL


class AnalysisCache:
    """In-memory LRU cache for AI analysis results."""

    def __init__(self, max_size: int = 500):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._access_order: list[str] = []

    def _compute_key(self, job_id: str, description: str | None) -> str:
        """Compute cache key from job ID and description hash."""
        desc_hash = self._hash_description(description)
        return f"{job_id}:{desc_hash}"

    def _hash_description(self, description: str | None) -> str:
        """Hash the job description for cache key."""
        if not description:
            return "empty"
        return hashlib.sha256(description.encode()).hexdigest()[:16]

    def get(self, job_id: str, description: str | None) -> AIJobAnalysisResult | None:
        """
        Get cached analysis result if valid.

        Args:
            job_id: The job's UUID as string
            description: The job's description text

        Returns:
            Cached AIJobAnalysisResult or None if not found/expired
        """
        key = self._compute_key(job_id, description)
        entry = self._cache.get(key)

        if entry is None:
            logger.debug("cache_miss", job_id=job_id, reason="not_found")
            return None

        if entry.is_expired():
            logger.debug("cache_miss", job_id=job_id, reason="expired")
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return None

        # Move to end of access order (most recently used)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        logger.debug("cache_hit", job_id=job_id)
        return entry.result

    def set(
        self,
        job_id: str,
        description: str | None,
        result: AIJobAnalysisResult,
    ) -> None:
        """
        Cache an analysis result.

        Args:
            job_id: The job's UUID as string
            description: The job's description text
            result: The analysis result to cache
        """
        key = self._compute_key(job_id, description)

        # Evict oldest entries if cache is full
        while len(self._cache) >= self._max_size and self._access_order:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._cache:
                del self._cache[oldest_key]
                logger.debug("cache_evict", key=oldest_key)

        self._cache[key] = CacheEntry(
            result=result,
            description_hash=self._hash_description(description),
        )
        self._access_order.append(key)

        logger.debug("cache_set", job_id=job_id, cache_size=len(self._cache))

    def invalidate(self, job_id: str) -> None:
        """
        Invalidate all cache entries for a job.

        Args:
            job_id: The job's UUID as string
        """
        keys_to_remove = [k for k in self._cache if k.startswith(f"{job_id}:")]
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)

        if keys_to_remove:
            logger.debug("cache_invalidate", job_id=job_id, count=len(keys_to_remove))

    def clear(self) -> None:
        """Clear the entire cache."""
        count = len(self._cache)
        self._cache.clear()
        self._access_order.clear()
        logger.info("cache_clear", count=count)

    def stats(self) -> dict:
        """Get cache statistics."""
        expired_count = sum(1 for entry in self._cache.values() if entry.is_expired())
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "expired_count": expired_count,
            "ttl_seconds": CACHE_TTL,
        }


# Singleton instance
analysis_cache = AnalysisCache()
