#!/bin/bash
# ============================================
# Transibot - Scripts de ayuda
# ============================================

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "Transibot - Scripts de Gestión"
echo "============================================"
echo ""
echo "Selecciona una opción:"
echo ""
echo "1. Iniciar todos los servicios"
echo "2. Detener todos los servicios"
echo "3. Ver estado de servicios"
echo "4. Ver logs (todos)"
echo "5. Ver logs (servicio específico)"
echo "6. Reiniciar un servicio"
echo "7. Actualizar imágenes desde Docker Hub"
echo "8. Backup de datos"
echo "9. Limpiar todo (⚠️ elimina volúmenes)"
echo "10. Validar configuración"
echo "0. Salir"
echo ""
read -p "Opción: " option

case $option in
  1)
    echo -e "${GREEN}Iniciando servicios...${NC}"
    docker compose up -d
    echo ""
    echo -e "${GREEN}Esperando que los servicios estén listos...${NC}"
    sleep 10
    docker compose ps
    ;;
  2)
    echo -e "${YELLOW}Deteniendo servicios...${NC}"
    docker compose down
    echo -e "${GREEN}Servicios detenidos${NC}"
    ;;
  3)
    echo -e "${GREEN}Estado de servicios:${NC}"
    docker compose ps
    ;;
  4)
    echo -e "${GREEN}Logs de todos los servicios (Ctrl+C para salir):${NC}"
    docker compose logs -f
    ;;
  5)
    echo ""
    echo "Servicios disponibles:"
    echo "  - backrag"
    echo "  - apistool"
    echo "  - rasa"
    echo "  - routerback"
    echo "  - frontend"
    echo ""
    read -p "Nombre del servicio: " service
    echo -e "${GREEN}Logs de $service (Ctrl+C para salir):${NC}"
    docker compose logs -f $service
    ;;
  6)
    echo ""
    echo "Servicios disponibles:"
    echo "  - backrag"
    echo "  - apistool"
    echo "  - rasa"
    echo "  - routerback"
    echo "  - frontend"
    echo ""
    read -p "Nombre del servicio: " service
    echo -e "${YELLOW}Reiniciando $service...${NC}"
    docker compose restart $service
    echo -e "${GREEN}Servicio reiniciado${NC}"
    ;;
  7)
    echo -e "${GREEN}Descargando últimas imágenes desde Docker Hub...${NC}"
    docker compose pull
    echo ""
    echo -e "${YELLOW}¿Deseas reiniciar los servicios con las nuevas imágenes? (y/n)${NC}"
    read -p "> " restart
    if [ "$restart" = "y" ]; then
      docker compose up -d
      echo -e "${GREEN}Servicios actualizados y reiniciados${NC}"
    fi
    ;;
  8)
    echo -e "${GREEN}Creando backup...${NC}"
    mkdir -p backups
    DATE=$(date +%Y%m%d-%H%M%S)

    echo "Backup de BackRag data..."
    docker run --rm \
      -v transibot-backrag-data:/data \
      -v $(pwd)/backups:/backup \
      alpine tar czf /backup/backrag-data-$DATE.tar.gz /data

    echo "Backup de RASA models..."
    cp -r ./models ./backups/rasa-models-$DATE/

    echo -e "${GREEN}Backups completados en ./backups/${NC}"
    ls -lh backups/
    ;;
  9)
    echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará todos los contenedores, volúmenes y datos${NC}"
    read -p "¿Estás seguro? Escribe 'SI' para confirmar: " confirm
    if [ "$confirm" = "SI" ]; then
      echo -e "${RED}Eliminando todo...${NC}"
      docker compose down -v
      echo -e "${GREEN}Limpieza completada${NC}"
    else
      echo -e "${YELLOW}Operación cancelada${NC}"
    fi
    ;;
  10)
    echo -e "${GREEN}Validando configuración...${NC}"
    echo ""

    # Verificar .env
    if [ -f .env ]; then
      echo -e "${GREEN}✓${NC} Archivo .env encontrado"

      # Verificar variables críticas
      source .env

      if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-anthropic-api-key-here" ]; then
        echo -e "${RED}✗${NC} ANTHROPIC_API_KEY no configurado en .env"
      else
        echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY configurado"
      fi

      if [ -z "$SMTP_USER" ] || [ "$SMTP_USER" = "your_email@gmail.com" ]; then
        echo -e "${YELLOW}⚠${NC}  SMTP_USER no configurado (emails no funcionarán)"
      else
        echo -e "${GREEN}✓${NC} SMTP_USER configurado"
      fi

      if [ -z "$SMTP_PASSWORD" ] || [ "$SMTP_PASSWORD" = "your_app_password_here" ]; then
        echo -e "${YELLOW}⚠${NC}  SMTP_PASSWORD no configurado (emails no funcionarán)"
      else
        echo -e "${GREEN}✓${NC} SMTP_PASSWORD configurado"
      fi
    else
      echo -e "${RED}✗${NC} Archivo .env no encontrado. Copia .env.example a .env"
    fi

    echo ""

    # Verificar docker-compose
    echo "Validando docker-compose.yml..."
    if docker compose config > /dev/null 2>&1; then
      echo -e "${GREEN}✓${NC} docker-compose.yml es válido"
    else
      echo -e "${RED}✗${NC} docker-compose.yml tiene errores"
      docker compose config
    fi

    echo ""

    # Verificar modelos de RASA
    echo "Verificando modelos RASA..."
    if [ -f ./models/20251119-154152-denim-dove.tar.gz ]; then
      MODEL_SIZE=$(ls -lh ./models/20251119-154152-denim-dove.tar.gz | awk '{print $5}')
      echo -e "${GREEN}✓${NC} Modelo RASA encontrado (${MODEL_SIZE})"
    else
      echo -e "${RED}✗${NC} Modelo RASA no encontrado en ./models/"
      echo -e "  Se esperaba: ./models/20251119-154152-denim-dove.tar.gz"
    fi

    echo ""
    echo -e "${GREEN}Validación completada${NC}"
    ;;
  0)
    echo "Saliendo..."
    exit 0
    ;;
  *)
    echo -e "${RED}Opción inválida${NC}"
    ;;
esac
