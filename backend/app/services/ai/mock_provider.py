import hashlib
import math
import random
from typing import List, Optional, Dict, Any
from app.services.ai.base import LLMProvider, EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _generate_vector(self, text: str) -> List[float]:
        """
        Generates a deterministic pseudo-random unit vector based on sha256 hash of text.
        Words in text influence specific dimensions so similar topics cluster together!
        """
        vec = [0.0] * self.dimension
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.dimension
            vec[pos] += 1.0 + (idx * 0.05)

        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        else:
            vec[0] = 1.0
        return vec

    async def embed_text(self, text: str) -> List[float]:
        return self._generate_vector(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]


class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        prompt_lower = prompt.lower()

        if "stratified" in prompt_lower or "sampling" in prompt_lower:
            return (
                "**Stratified Sampling in Official Statistics:**\n\n"
                "In stratified sampling, the target population is partitioned into non-overlapping subpopulations called *strata* "
                "(e.g., geographic regions, urban/rural sectors, or enterprise size classes). Independent probability samples are then "
                "selected from each stratum using Simple Random Sampling (SRS) or Probability Proportional to Size (PPS).\n\n"
                "**Household Survey Example (MoSPI NSS/PLFS):**\n"
                "In the Periodic Labour Force Survey (PLFS), districts are first stratified into Rural and Urban sectors. "
                "Within each sector, villages or Urban Frame Survey (UFS) blocks act as First Stage Units (FSUs), ensuring that both "
                "affluent and informal settlement demographics are adequately represented.\n\n"
                "**Common Pitfall:**\n"
                "A frequent operational error is failing to apply the correct sample weights (inflation factors/multipliers) "
                "during aggregation, which leads to biased parameter estimates if sampling fractions vary across strata."
            )
        elif "sql" in prompt_lower:
            return (
                "**SQL for Official Survey Data Processing:**\n\n"
                "When processing survey microdata in PostgreSQL or Oracle, aggregate statistics must account for sample weights. "
                "For example, when calculating weighted average household consumption expenditure:\n\n"
                "```sql\n"
                "SELECT state_code, \n"
                "       SUM(expenditure * multiplier) / SUM(multiplier) AS weighted_avg_exp\n"
                "FROM nss_consumer_expenditure\n"
                "GROUP BY state_code\n"
                "ORDER BY state_code;\n"
                "```\n\n"
                "Ensure that missing codes (such as 999 or -1) are explicitly filtered out before computing averages."
            )
        elif "gsbpm" in prompt_lower or "business process" in prompt_lower:
            return (
                "**The Generic Statistical Business Process Model (GSBPM 5.1):**\n\n"
                "GSBPM defines 8 core phases for official statistical production:\n"
                "1. **Specify Needs** - Consult stakeholders and establish statistical requirements.\n"
                "2. **Design** - Define concepts, methodology, questionnaires, and sampling design.\n"
                "3. **Build** - Develop collection instruments and processing workflows.\n"
                "4. **Collect** - Execute field operations and capture administrative records.\n"
                "5. **Process** - Validate, clean, impute, and code raw data.\n"
                "6. **Analyse** - Prepare estimates, examine trends, and validate consistency.\n"
                "7. **Disseminate** - Publish official tables, open datasets, and metadata.\n"
                "8. **Evaluate** - Conduct post-survey review and identify continuous improvements."
            )
        else:
            return (
                "Under the **Fundamental Principles of Official Statistics** (adopted by the UN General Assembly and MoSPI), "
                "official statistical systems must preserve professional independence, scientific integrity, and user confidentiality. "
                "Every official metric should be fully documented with comprehensive National Quality Assurance Framework (NQAF) metadata."
            )

    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Mock structured MCQ generator."""
        return {
            "questions": [
                {
                    "question_text": "In stratified random sampling, what is the primary condition that defines how strata should be formed?",
                    "question_type": "SINGLE_CHOICE",
                    "options": [
                        "Units within each stratum must be as homogeneous as possible, while strata should be heterogeneous between each other.",
                        "Units within each stratum must be completely heterogeneous, while strata means should be identical.",
                        "Strata must always contain an equal number of First Stage Units (FSUs).",
                        "The sampling fraction must be 100% across all designated sub-populations."
                    ],
                    "correct_option_index": 0,
                    "explanation": "Effective stratification minimizes within-stratum variance (homogeneity) and maximizes between-strata variance, ensuring lower standard errors for overall survey estimates.",
                    "competency_code": "SAMPLING",
                    "subcompetency_code": "STRATIFIED_SAMPLING",
                    "difficulty": "INTERMEDIATE",
                    "source_reference": "MoSPI Sampling Techniques Manual (Section 4.1)"
                },
                {
                    "question_text": "Under the UN National Quality Assurance Framework (NQAF), which dimension assesses the degree to which statistical information reflects the actual reality of the phenomena it is designed to measure?",
                    "question_type": "SINGLE_CHOICE",
                    "options": [
                        "Timeliness",
                        "Accuracy and Reliability",
                        "Accessibility and Clarity",
                        "Comparability over Time"
                    ],
                    "correct_option_index": 1,
                    "explanation": "Accuracy refers to the closeness between the estimated value and the true unknown population value, incorporating both sampling and non-sampling errors.",
                    "competency_code": "DATA_QUALITY",
                    "subcompetency_code": "NQAF_FRAMEWORK",
                    "difficulty": "FOUNDATION",
                    "source_reference": "UN NQAF Guidelines for Official Statistics"
                }
            ]
        }

    async def summarize(self, text: str, max_words: int = 150) -> str:
        words = text.split()[:max_words]
        return " ".join(words) + ("..." if len(text.split()) > max_words else "")
