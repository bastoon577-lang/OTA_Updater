<p align="center">
  <!-- Ko-fi badge -->
  <a href="https://Ko-fi.com/bastoon577lang">
    <img src="https://img.shields.io/badge/Ko--fi-Support%20Me-ff5e5b?logo=ko-fi&logoColor=white" alt="Ko-fi">
  </a>

  <!-- Buy Me a Coffee badge -->
  <a href="https://buymeacoffee.com/bastoon577lang">
    <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-yellow?logo=buymeacoffee&logoColor=white" alt="Buy Me a Coffee">
  </a>

  <!-- PayPal badge -->
  <a href="https://www.paypal.com/donate?hosted_button_id=4CDVJA8LLUR78">
    <img src="https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal&logoColor=white" alt="PayPal">
  </a>
</p>

# OTA_Updater

That tool allows to update ESP8266 equipments by using OTA protocole via a graphical user interface and developed exclusively for my needs.
I literally reused espota.py from [Arduino repository](https://github.com/esp8266/Arduino/blob/master/tools/espota.py), so I know my code isn't clean.

# How to rebuild it

I've worked on Debian system, but i'm conscious that this software will be used by noobs.
So, if you want to rebuild Windows executable from OTA_Updater script, following that process.

Make sure you are in `su` :
```
su
```

## Install docker
```
apt update
apt install docker.io -y
```

## Pull repository
```
git clone https://github.com/bastoon577-lang/Water_pump_ZOE.git
cd OTA_Updater/
```

## Build it in docker
```
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-windows "pyinstaller --clean --windowed --onefile OTA_Updater.py"
```

## Extract Windows executable

You will look for windows executable in `/dist`, so extract it in `root` before pushing on repository :
```
cp dist/OTA_Updater.exe .
```

#### Auteur : *Sébastien DALIGAULT*. 
