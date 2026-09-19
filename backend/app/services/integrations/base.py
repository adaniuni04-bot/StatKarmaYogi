from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LearningProvider(ABC):
    @abstractmethod
    async def get_courses(self) -> List[Dict[str, Any]]:
        """Fetch course catalogue from learning provider."""
        pass

    @abstractmethod
    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Fetch individual course details."""
        pass

    @abstractmethod
    async def sync_catalog(self, db_session: Any) -> int:
        """Sync remote courses into local resources table."""
        pass


class TrainingProvider(ABC):
    @abstractmethod
    async def get_programmes(self) -> List[Dict[str, Any]]:
        """Fetch academy training programme calendar."""
        pass

    @abstractmethod
    async def sync_calendar(self, db_session: Any) -> int:
        """Sync academy calendar into local database."""
        pass
