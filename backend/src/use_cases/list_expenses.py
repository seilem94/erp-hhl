"""List project and operational expenses through the repository."""

from src.domain.entities.expense import Expense
from src.domain.repositories.expense_repository import ExpenseRepository


class ListExpensesUseCase:
    def __init__(self, expense_repo: ExpenseRepository) -> None:
        self._expense_repo = expense_repo

    def execute(self) -> list[Expense]:
        return self._expense_repo.list_all()
