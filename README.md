# Synology virtual machine

This a *custom component* for [Home Assistant](https://www.home-assistant.io/).
The `synology_vmm` integration allows you to observe and control [Synology DSM](http://www.synology.com/).

There is currently support for the following device types within Home Assistant:
*Switch Sensor with virtual machine status (stop/start)
*Cpu and Memory sensors
*Service to set machine (mount/unmount usb drive , resize , rename , add disk , add network , ...)
  
## Configuration

The preferred way to setup the Synology VMM platform is by enabling via the Integration menu.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=synology_vmm)

![GitHub release](https://img.shields.io/github/release/Cyr-ius/hass-synovmm)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
