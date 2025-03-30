#!/bin/bash

# Script de instalación para la API Ultra-rápida de MongoDB
echo "=========================================================="
echo "  Instalación del servicio MongoDB API Ultra-rápida"
echo "=========================================================="

# Verificar que se ejecute con permisos de sudo
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, ejecute este script con sudo:"
  echo "  sudo ./install.sh"
  exit 1
fi

# Obtener la ruta actual
CURRENT_DIR=$(pwd)

# Crear el archivo de servicio systemd
echo "Creando archivo de servicio systemd..."
cat > mongo-api.service << EOL
[Unit]
Description=MongoDB API Ultra-rápida
After=network.target

[Service]
User=$(logname)
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/run.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

echo "Copiando archivo de servicio a /etc/systemd/system/..."
cp mongo-api.service /etc/systemd/system/

echo "Recargando daemon systemd..."
systemctl daemon-reload

echo "Habilitando servicio para inicio automático..."
systemctl enable mongo-api.service

echo "Iniciando servicio..."
systemctl start mongo-api.service

# Verificar que el servicio esté funcionando
sleep 3
if systemctl is-active --quiet mongo-api.service; then
    echo "El servicio mongo-api.service está ejecutándose correctamente."
    echo "Puedes acceder a la API en http://localhost:28000/"
    echo "La documentación está disponible en http://localhost:28000/docs"
else
    echo "¡Error! El servicio no se pudo iniciar. Comprueba los logs con:"
    echo "  sudo journalctl -u mongo-api.service"
fi

echo "=========================================================="
echo "  Comandos útiles:"
echo "    sudo systemctl start/stop/restart mongo-api.service"
echo "    sudo systemctl status mongo-api.service"
echo "    sudo journalctl -u mongo-api.service -f"
echo "==========================================================" 