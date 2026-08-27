# ==============================================================================
# Makefile — Asistente de Emergencias y Supervivencia (Cádiz)
# ==============================================================================
# Centraliza las operaciones frecuentes de desarrollo, despliegue y validación.
# ==============================================================================

.PHONY: help sync up down ps logs restart test check e2e rag-list rag-update export-conv clean

# Variables por defecto
PI_HOST ?= pi@172.18.1.121
PI_DIR  ?= /home/pi/bot-ia-auxiliar
API_URL ?= http://172.18.1.121:8870
TOKEN   ?= 4d7a1d7affbeb459814d1fa220b2a70b

help: ## Muestra este resumen de comandos disponibles
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

sync: ## Sincroniza el código fuente con la Raspberry Pi 5 vía rsync
	@echo "==> Sincronizando repositorio con $(PI_HOST):$(PI_DIR)..."
	rsync -avz --exclude='.env' --exclude='data/' --exclude='.venv/' --exclude='__pycache__/' ./ $(PI_HOST):$(PI_DIR)/
	ssh $(PI_HOST) "cd $(PI_DIR) && git reset --hard HEAD"

up: ## Inicia o actualiza los contenedores Docker en segundo plano
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose up -d"

down: ## Detiene todos los contenedores Docker
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose down"

ps: ## Muestra el estado de los contenedores Docker
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose ps"

logs: ## Muestra los logs en tiempo real de todos los contenedores
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose logs -f"

restart: ## Reinicia los contenedores bot-api y bot-web
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose restart api web"

test: ## Ejecuta la suite de pruebas unitarias en el contenedor API
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose exec -e PYTHONPATH=/app/src:/app api python3 -m unittest discover -s tests -p 'test_*.py' -v"

check: ## Ejecuta validaciones locales de sintaxis y linters
	./scripts/check.sh

e2e: ## Lanza la suite de pruebas de integración E2E en vivo
	python3 scripts/test_e2e.py --url $(API_URL) --token $(TOKEN)

rag-list: ## Lista todas las fuentes de conocimiento del RAG y su estado
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose exec api python3 scripts/actualizar_fuente.py --list"

rag-update: ## Actualiza todas las fuentes del RAG en PostgreSQL
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose exec api python3 scripts/actualizar_fuente.py --todas"

export-conv: ## Exporta las conversaciones registradas a un archivo JSONL
	ssh $(PI_HOST) "cd $(PI_DIR) && docker compose exec api python3 scripts/exportar_conversaciones.py --formato jsonl --salida /app/data/conversaciones.jsonl"
	@echo "Conversaciones exportadas en el host en /var/ia/bot-emergencias/conversaciones.jsonl"

clean: ## Limpia archivos de caché y compilación temporal de Python
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
