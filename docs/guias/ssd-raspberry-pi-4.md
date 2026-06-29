# Guía · Poner un SSD en Raspberry Pi 4

Por qué: en este proyecto la tarjeta microSD es el cuello de botella y el punto
de fallo más probable. PostgreSQL (clúster local en `data/postgres`) y los
modelos GGUF castigan mucho la SD: lecturas lentas y desgaste. Un **SSD por USB
3.0** mejora rendimiento y fiabilidad de forma drástica.

La Raspberry Pi 4 **no tiene PCIe/NVMe**: el SSD se conecta por **USB 3.0** (los
puertos azules) mediante un adaptador USB‑SATA o una caja M.2‑USB.

## 1. Material recomendado

- **SSD**: 2,5" SATA (p. ej. 240 GB+) o M.2 SATA/NVMe dentro de una **caja
  USB 3.0**. Para este proyecto, 120–256 GB sobran (modelos + BD + staging).
- **Adaptador/caja USB‑SATA con soporte UASP** y, preferiblemente, chipset
  **ASMedia ASM1153/ASM235CM** o **JMicron JMS578**. Evita cajas baratas sin
  UASP o con chipsets problemáticos (algunos JMicron antiguos dan errores).
- **Fuente oficial de 5 V/3 A USB‑C**. Un SSD consume más que una SD; con
  alimentación pobre aparecen cortes y corrupción.
- Conéctalo siempre a un **puerto USB 3.0 (azul)**, nunca al 2.0.

## 2. Actualizar sistema y bootloader (para arrancar desde USB)

En la Pi ya arrancada desde la SD actual:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo rpi-eeprom-update -a      # actualiza el firmware/bootloader
sudo reboot
```

La RPi4 admite **arranque por USB** con un bootloader reciente (lo normal hoy).

## 3. Grabar el sistema en el SSD

Opción A — **Raspberry Pi Imager** (lo más simple):

1. Conecta el SSD por USB 3.0 a la Pi (o a tu PC).
2. Abre Raspberry Pi Imager → elige **Raspberry Pi OS Lite (64‑bit)** → elige el
   SSD como destino → graba. (Usa **Lite**: sin escritorio, más RAM para el LLM.)
3. En los ajustes del Imager, configura ya hostname, SSH, usuario y red.

Opción B — **clonar** la SD actual al SSD con `rpi-clone` o
`SD Card Copier` (entorno gráfico) si quieres conservar la instalación.

## 4. Configurar el orden de arranque (USB primero)

```bash
sudo raspi-config
# Advanced Options → Boot Order → USB Boot
```

Apaga, **retira la microSD** y arranca solo con el SSD:

```bash
sudo poweroff
```

## 5. Verificar

```bash
lsblk -o NAME,SIZE,TRAN,MOUNTPOINT     # el disco debe aparecer como 'usb'
findmnt /                              # raíz montada en el SSD (sd?)
sudo hdparm -t /dev/sda                # lectura secuencial (≈300–400 MB/s en USB3)
```

## 6. Si el adaptador da problemas (quirks UASP)

Algunos adaptadores fallan con UASP (errores `uas` en `dmesg`). Solución:
forzar el modo `usb-storage` añadiendo el ID del dispositivo a los quirks.

```bash
lsusb                                  # anota idVendor:idProduct, p. ej. 152d:0578
sudo nano /boot/firmware/cmdline.txt   # en la MISMA línea, añade:
#   usb-storage.quirks=152d:0578:u
sudo reboot
```

## 7. Ajustes finales para el proyecto

- Confirma que `DB_DATA_DIR` (en `env.py`) apunta a una ruta del SSD
  (`./data/postgres` ya lo está si el repo vive en el SSD).
- Activa **TRIM** periódico: `sudo systemctl enable --now fstrim.timer`.
- Coloca también `models/` (GGUF) en el SSD: las cargas del modelo se notan.

## Notas

- La RPi4 limita el USB a ~3,2 Gbps reales; un SSD USB3 rinde muy por encima de
  cualquier microSD igualmente.
- No uses hubs USB sin alimentación para el SSD.

## Fuentes

- [Raspberry Pi — USB mass storage boot](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [Raspberry Pi OS / rpi-eeprom](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-boot-eeprom)
