"""Domain repository interfaces — pure ABCs, no infrastructure imports."""

from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.project_repository import ProjectRepository

__all__ = ["ExpenseRepository", "ProjectRepository"]
