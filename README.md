# On Air / Off Air

A beautiful LED sign with a corresponding website to let people know when you're in important meetings.

## Hardware

The Hardware side is based on the [Adafruit YouTube On Air Sign](https://learn.adafruit.com/rgb-matrix-automatic-youtube-on-air-sign).
The parts I'm using are the
* 64x32 RGB LED Matrix with 4mm pitch
* Adafruit Matrix Portal

Thanks to the Matrix Portal this is very plug&play.

## Software

### Sign
I used the Adafruit project as a starting point, there's a lot of example projects to run on the matrix, so you know the lights can blink.

Then I took the YouTube on air sign and adjusted the code to communicate with my server to get the current status and fetch the current time for night mode (see `/sign`).

To monitor the output you can use the `screen` command with your specific tty device.
```
screen /dev/tty.usbmodem1101 115200
```

### Server
This is using flask and a simple bootstrap template to give the user two buttons to press. So they can show if they are `ON AIR` or `OFF AIR`.

To get the server running use something like this:
```
python3 -m flask --debug run --host 0.0.0.0 --port 6006
```