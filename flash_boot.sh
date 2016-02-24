while true; do
    read -p "Flash bootloader? [Yn]" yn
    case $yn in
        [Yy]* ) avrdude -v -p m32u4 -P usb -c usbtiny -U flash:w:/usr/share/arduino/hardware/arduino/bootloaders/caterina/Caterina-Micro.hex -U efuse:w:0xcb:m -U hfuse:w:0xd8:m -U lfuse:w:0xff:m;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
