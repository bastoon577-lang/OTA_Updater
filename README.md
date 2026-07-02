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
