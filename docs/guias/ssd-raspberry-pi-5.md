# Guía · Poner un SSD en Raspberry Pi 5 (NVMe por PCIe)

Por qué: la Raspberry Pi 5 **sí tiene PCIe**, así que puedes usar un **SSD NVMe**
real (mucho más rápido y fiable que la microSD o que un USB‑SATA). Es la opción
recomendada para este proyecto en RPi5, donde PostgreSQL y modelos GGUF más
grandes se benefician del almacenamiento rápido.

> La RPi5 también admite SSD por USB 3.0 (igual que la RPi4); esta guía cubre la
> vía recomendada: **NVMe sobre PCIe con el M.2 HAT+**.

## 1. Material recomendado

- **M.2 HAT+ oficial de Raspberry Pi** (u otro HAT PCIe compatible). El HAT+
  oficial admite SSD de formato **2230 o 2242** (cortos). Los NVMe de escritorio
  **2280** (80 mm) **no caben** en el HAT+ oficial; para 2280 usa un HAT de
  terceros (Pimoroni, Geekworm, Pineberry/52Pi, etc.).
- **SSD NVMe M.2 M‑key** (PCIe), tamaño 2230/2242 para el HAT+ oficial. 256 GB
  sobran para este proyecto.
- **Fuente oficial de 27 W USB‑C (5 V/5 A)**: el conjunto Pi 5 + NVMe consume
  más; una fuente insuficiente provoca inestabilidad.
- Cable FFC (viene con el HAT) y separadores/tornillos incluidos.

## 2. Montaje del HAT y el SSD

1. Apaga la Pi y desconéctala.
2. Inserta el **NVMe** en el M.2 HAT+ y fíjalo con el tornillo del tamaño
   correcto (2230 o 2242).
3. Conecta el **cable FFC** entre el conector PCIe de la Pi 5 y el HAT (presta
   atención a la orientación de los contactos).
4. Monta el HAT sobre el conector GPIO con los separadores.

## 3. Actualizar el firmware EEPROM (necesario para arrancar desde NVMe)

Arranca desde la microSD y actualiza:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo rpi-eeprom-update -a
sudo reboot
```

Las EEPROM anteriores a mediados de 2023 **no** soportan arranque PCIe; por eso
es importante actualizar.

## 4. Grabar el sistema en el NVMe

Opción A — **Raspberry Pi Imager** desde la propia Pi (con la SD puesta):

1. Abre Imager → **Raspberry Pi OS Lite (64‑bit)** → destino: el **NVMe** →
   graba. (Usa **Lite**: sin escritorio, deja RAM al LLM.)

Opción B — **clonar** la microSD al NVMe (entorno gráfico: *SD Card Copier*, o
`rpi-clone`) si quieres conservar la instalación.

## 5. Habilitar PCIe y el orden de arranque

Activa la interfaz PCIe y pon el NVMe primero en el arranque:

```bash
sudo raspi-config
# Advanced Options → Boot Order → NVMe/USB Boot
```

Si tu HAT lo requiere, añade en `/boot/firmware/config.txt`:

```
dtparam=pciex1
```

(Opcional, **no oficial**) Forzar **PCIe Gen 3** (~2x ancho de banda, puede dar
inestabilidad con algunos SSD; por defecto es Gen 2 ≈ 500 MB/s):

```
# /boot/firmware/config.txt
dtparam=pciex1_gen=3
```

Apaga, retira la microSD y arranca desde el NVMe:

```bash
sudo poweroff
```

## 6. Verificar

```bash
lsblk -o NAME,SIZE,TRAN,MOUNTPOINT     # debe aparecer 'nvme0n1' y la raíz en él
findmnt /
sudo hdparm -t /dev/nvme0n1            # ≈450 MB/s en Gen2; ~800+ en Gen3
```

## 7. Ajustes finales para el proyecto

- `DB_DATA_DIR` (en `env.py`) en el NVMe (lo está si el repo vive en el NVMe).
- TRIM periódico: `sudo systemctl enable --now fstrim.timer`.
- Coloca `models/` (GGUF) en el NVMe; con modelos 3B/7B la carga es mucho más
  ágil.

## Notas

- PCIe de la Pi 5 es **Gen 2 x1** por defecto (oficial y estable); Gen 3 es
  experimental.
- El HAT+ oficial es solo 2230/2242. Verifica el tamaño de tu SSD antes de
  comprarlo.

## Fuentes

- [Raspberry Pi — M.2 HAT+ (documentación oficial)](https://www.raspberrypi.com/documentation/accessories/m2-hat-plus.html)
- [Raspberry Pi — Using the M.2 HAT+ with Raspberry Pi 5](https://www.raspberrypi.com/news/using-m-2-hat-with-raspberry-pi-5/)
- [Jeff Geerling — NVMe SSD boot with the Raspberry Pi 5](https://www.jeffgeerling.com/blog/2023/nvme-ssd-boot-raspberry-pi-5/)
