"""Domain-level enumerations.

All enums are pure Python StrEnum — no framework dependencies.
"""

from enum import StrEnum


class Currency(StrEnum):
    """Supported monetary units; use enum members throughout the core."""

    CLP = "CLP"


class ResourceType(StrEnum):
    PROJECT = "project"
    EXPENSE = "expense"


class CommandType(StrEnum):
    CREATE_PROJECT = "create_project"
    REGISTER_EXPENSE = "register_expense"
    UPDATE_PROJECT = "update_project"

    @property
    def resource_type(self) -> ResourceType:
        if self is CommandType.REGISTER_EXPENSE:
            return ResourceType.EXPENSE
        return ResourceType.PROJECT


class OperationState(StrEnum):
    """A confirmed operation may retain metadata after its payload is purged."""

    RESERVED = "reserved"
    CONFIRMED = "confirmed"


class ProjectStatus(StrEnum):
    """Lifecycle states of an electrical project/obra."""

    PLANNING = "planning"  # Cotización o planificación inicial
    IN_PROGRESS = "in_progress"  # Obra en ejecución
    PAUSED = "paused"  # Pausada (esperando materiales, permisos, etc.)
    COMPLETED = "completed"  # Finalizada y entregada
    CANCELLED = "cancelled"  # Cancelada formalmente


class ExpenseCategory(StrEnum):
    """Categories of expenses for both project-direct costs (CapEx) and
    general operational costs (OPEX)."""

    MATERIALS = "materials"  # Cables, tableros, automáticos, canalizaciones
    TRANSPORT = "transport"  # Combustible, peajes, estacionamiento, fletes
    FOOD = "food"  # Almuerzos y colaciones de cuadrilla en terreno
    TOOLS = "tools"  # Herramientas menores, insumos (cintas, brocas)
    MAINTENANCE = "maintenance"  # Mantención vehicular, calibración, servicio técnico
    SERVICES = "services"  # Subcontratos, alquiler de andamios/grúa
    OTHER = "other"  # Imprevistos varios
