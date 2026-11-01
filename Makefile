.PHONY: check-backend check-frontend check-all

check-backend:
	cd backend && ruff check . && ruff format --check . && mypy src/

check-frontend:
	cd frontend && npm run lint && npm run type-check

check-all: check-backend check-frontend