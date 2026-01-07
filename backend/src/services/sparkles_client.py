"""
Sparkles RAG Client for meridian-job-tracker.

Connects to Sparkles Supabase database to perform semantic search over
Tom's 260+ career documents for personalized coaching insights.

Uses:
- OpenAI text-embedding-3-small for query embeddings (1536 dimensions)
- Supabase PostgreSQL + pgvector for vector search
- Hybrid search (vector similarity + keyword matching with RRF)
"""

import asyncio
from typing import Literal

import httpx
import structlog
from openai import OpenAI

from src.config import settings
from src.schemas.ai_analysis_coach import JDMatchResult, RAGEvidence, ResumeSearchResult

logger = structlog.get_logger(__name__)

MatchStrength = Literal["strong", "moderate", "weak", "none"]


def _get_match_strength(similarity: float) -> MatchStrength:
    """Determine match strength from similarity score."""
    if similarity >= 0.75:
        return "strong"
    if similarity >= 0.60:
        return "moderate"
    if similarity >= 0.45:
        return "weak"
    return "none"


class SparklesClient:
    """
    RAG client connecting to Sparkles resume data.

    Uses the same Supabase instance as Sparkles for semantic search
    over 260+ career documents including:
    - Master resume and role variants
    - Project case studies
    - Interview prep materials
    - Career analysis documents
    """

    def __init__(self):
        self.supabase_url = settings.sparkles_supabase_url
        self.supabase_key = settings.sparkles_supabase_service_key
        self.openai_key = settings.openai_api_key

        self._openai: OpenAI | None = None
        self._http_client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if Sparkles is properly configured."""
        return bool(self.supabase_url and self.supabase_key and self.openai_key)

    @property
    def openai(self) -> OpenAI:
        """Lazy-initialize OpenAI client."""
        if self._openai is None:
            if not self.openai_key:
                raise ValueError("OPENAI_API_KEY not configured")
            self._openai = OpenAI(api_key=self.openai_key)
        return self._openai

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for Supabase."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=f"{self.supabase_url}/rest/v1",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json",
                },
                timeout=settings.rag_timeout_seconds,
            )
        return self._http_client

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate OpenAI embedding for query text."""
        # Truncate to ~8000 chars to stay within token limits
        truncated = text[:8000]

        # Run in thread pool since OpenAI client is sync
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=truncated,
            ),
        )

        embedding = response.data[0].embedding
        if not embedding:
            raise ValueError("No embedding returned from OpenAI")

        return embedding

    async def search_resume_context(
        self,
        query: str,
        categories: list[str] | None = None,
        threshold: float | None = None,
        limit: int | None = None,
    ) -> list[ResumeSearchResult]:
        """
        Semantic search over career documents.

        Args:
            query: Search query text
            categories: Optional filter by document categories
            threshold: Minimum similarity threshold (default from settings)
            limit: Maximum results (default from settings)

        Returns:
            List of matching document chunks with similarity scores
        """
        if not self.is_configured:
            logger.warning("sparkles_not_configured")
            return []

        threshold = threshold or settings.rag_similarity_threshold
        limit = limit or settings.rag_max_results

        try:
            # Generate embedding for query
            embedding = await self._generate_embedding(query)
            embedding_str = f"[{','.join(str(x) for x in embedding)}]"

            # Call Supabase RPC function
            client = await self._get_http_client()

            if categories:
                rpc_name = "match_resume_chunks_by_category"
                payload = {
                    "query_embedding": embedding_str,
                    "categories": categories,
                    "query_text": query,
                    "match_threshold": threshold,
                    "match_count": limit,
                }
            else:
                rpc_name = "match_resume_chunks"
                payload = {
                    "query_embedding": embedding_str,
                    "query_text": query,
                    "match_threshold": threshold,
                    "match_count": limit,
                }

            response = await client.post(f"/rpc/{rpc_name}", json=payload)
            response.raise_for_status()
            data = response.json()

            # Parse results
            results = []
            for item in data or []:
                results.append(
                    ResumeSearchResult(
                        id=str(item.get("id", "")),
                        content=item.get("content", ""),
                        source=item.get("metadata", {}).get("source", "unknown"),
                        category=item.get("metadata", {}).get("category", "unknown"),
                        similarity=float(item.get("similarity", 0)),
                        section=item.get("metadata", {}).get("section"),
                    )
                )

            logger.info(
                "sparkles_search_complete",
                query_length=len(query),
                results_count=len(results),
            )
            return results

        except Exception as e:
            logger.error("sparkles_search_error", error=str(e))
            return []

    async def match_jd_requirements(
        self,
        requirements: list[str],
        threshold: float = 0.40,
        limit_per_req: int = 3,
    ) -> list[JDMatchResult]:
        """
        Match job requirements against resume context.

        Performs multi-query RAG search for each requirement to find
        evidence of matching skills/experience.

        Args:
            requirements: List of job requirements to match
            threshold: Minimum similarity for matches
            limit_per_req: Max results per requirement

        Returns:
            List of match results with evidence and strength indicators
        """
        if not self.is_configured:
            logger.warning("sparkles_not_configured_for_jd_match")
            return []

        results: list[JDMatchResult] = []

        # Process in batches of 5 for efficiency
        batch_size = 5
        for i in range(0, len(requirements), batch_size):
            batch = requirements[i : i + batch_size]

            # Process batch in parallel
            batch_results = await asyncio.gather(
                *[
                    self._match_single_requirement(req, threshold, limit_per_req)
                    for req in batch
                ],
                return_exceptions=True,
            )

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error("requirement_match_error", error=str(result))
                    continue
                results.append(result)

        logger.info(
            "jd_requirements_matched",
            total_requirements=len(requirements),
            strong=len([r for r in results if r.match_strength == "strong"]),
            moderate=len([r for r in results if r.match_strength == "moderate"]),
            weak=len([r for r in results if r.match_strength == "weak"]),
            none=len([r for r in results if r.match_strength == "none"]),
        )

        return results

    async def _match_single_requirement(
        self,
        requirement: str,
        threshold: float,
        limit: int,
    ) -> JDMatchResult:
        """Match a single requirement against resume."""
        try:
            matches = await self.search_resume_context(
                query=requirement,
                threshold=threshold,
                limit=limit,
            )

            # Calculate average similarity
            avg_similarity = (
                sum(m.similarity for m in matches) / len(matches) if matches else 0
            )

            # Extract evidence snippets
            evidence = []
            top_matches = []
            for m in matches:
                snippet = m.content[:200].replace("\n", " ").strip()
                if len(snippet) == 200:
                    snippet += "..."
                evidence.append(snippet)

                top_matches.append(
                    RAGEvidence(
                        requirement=requirement,
                        match_strength=_get_match_strength(m.similarity),
                        evidence_snippet=snippet,
                        source_document=m.source,
                        similarity_score=m.similarity,
                    )
                )

            return JDMatchResult(
                requirement=requirement,
                match_strength=_get_match_strength(avg_similarity),
                evidence=evidence,
                top_matches=top_matches,
                avg_similarity=avg_similarity,
            )

        except Exception as e:
            logger.error(
                "single_requirement_match_error",
                requirement=requirement[:50],
                error=str(e),
            )
            return JDMatchResult(
                requirement=requirement,
                match_strength="none",
                evidence=[],
                top_matches=[],
                avg_similarity=0,
            )

    async def get_coaching_context(
        self,
        job_title: str,
        requirements: list[str],
    ) -> str:
        """
        Build formatted context for Claude coaching prompt.

        Combines:
        1. General context about the role type
        2. JD requirement matches with evidence
        3. Relevant interview prep materials

        Args:
            job_title: The job title being analyzed
            requirements: List of job requirements

        Returns:
            Formatted markdown context string
        """
        if not self.is_configured:
            return ""

        sections: list[str] = []

        # 1. Match JD requirements
        jd_matches = await self.match_jd_requirements(requirements)
        if jd_matches:
            sections.append(self._format_jd_matches(jd_matches))

        # 2. Get role-specific context
        role_context = await self.search_resume_context(
            query=f"experience relevant to {job_title} leadership role",
            categories=["master-documents", "career-analysis"],
            limit=4,
        )
        if role_context:
            sections.append(self._format_context_section(role_context, "Role Experience"))

        # 3. Get interview prep context
        interview_context = await self.search_resume_context(
            query=f"interview talking points for {job_title}",
            categories=["interview-prep"],
            limit=4,
        )
        if interview_context:
            sections.append(
                self._format_context_section(interview_context, "Interview Prep")
            )

        if not sections:
            return ""

        return f"""## RELEVANT EXPERIENCE FROM TOM'S CAREER DOCUMENTS

The following excerpts are from Tom's personal career documents including
project details, case studies, and interview prep materials.

{chr(10).join(sections)}"""

    def _format_jd_matches(self, matches: list[JDMatchResult]) -> str:
        """Format JD matches into context section."""
        strong = [m for m in matches if m.match_strength == "strong"]
        moderate = [m for m in matches if m.match_strength == "moderate"]
        weak = [m for m in matches if m.match_strength == "weak"]
        gaps = [m for m in matches if m.match_strength == "none"]

        parts = ["### JD Requirements Analysis (RAG-Powered)\n"]

        if strong:
            parts.append("**Strong Matches (Clear evidence):**")
            for m in strong:
                evidence = m.evidence[0] if m.evidence else "Multiple sources"
                parts.append(f"- {m.requirement}\n  Evidence: {evidence}")

        if moderate:
            parts.append("\n**Moderate Matches (Related experience):**")
            for m in moderate:
                parts.append(f"- {m.requirement}")

        if weak:
            parts.append("\n**Weak Matches (Tangential):**")
            for m in weak:
                parts.append(f"- {m.requirement}")

        if gaps:
            parts.append("\n**Potential Gaps (Address in coaching):**")
            for m in gaps:
                parts.append(f"- {m.requirement}")

        parts.append(
            f"\n*Summary: {len(strong)} strong, {len(moderate)} moderate, "
            f"{len(weak)} weak, {len(gaps)} gaps*"
        )

        return "\n".join(parts)

    def _format_context_section(
        self, results: list[ResumeSearchResult], title: str
    ) -> str:
        """Format search results into a context section."""
        parts = [f"### {title}\n"]

        for result in results:
            source = result.source.replace(".md", "").replace("_", " ")
            section_info = f" - {result.section}" if result.section else ""
            relevance = f"{result.similarity * 100:.0f}%"

            parts.append(
                f"**{source}{section_info}** (Relevance: {relevance})\n{result.content[:400]}..."
            )

        return "\n\n".join(parts)

    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Singleton instance
sparkles_client = SparklesClient()
