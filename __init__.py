from mycroft import MycroftSkill

import RPi.GPIO as GPIO

__author__ = 'smartgic'


class WakeWordLedGpio(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

        # By default the skill requires configuration
        self.configured = False

    def _setup(self):
        # By default the GPIO module will be configured with BCM
        # https://raspberrypi.stackexchange.com/a/12967
        self.pin_mode = self.settings.get('pin_mode', 'bcm').upper()
        self.pin_number = self.settings.get('pin_number')

        if not self.pin_number:
            self.speak_dialog('error.setup', data={"field": "pin"})
            self.log.warning('PIN number is not configured')
        else:
            self.configured = True
            self.log.info('LED PIN number set to {}'.format(self.pin_number))

        self.log.info('PIN mode set to {}'.format(self.pin_mode))

    # See https://bit.ly/37pwxIC (Mycroft documentation about skill lifecycle)
    def initialize(self):
        # Callback when setting changes are detected from home.mycroft.ai
        self.settings_change_callback = self.on_websettings_changed
        self.on_websettings_changed()

    # What to do in case of setting changes detected
    def on_websettings_changed(self):
        self._setup()
        self._run()

    def _run(self):
        # Run only when the skill is properly configured
        if self.configured:
            try:
                # Setup GPIO
                GPIO.setmode(eval('GPIO.{}'.format(self.pin_mode)))
                GPIO.setwarnings(False)
                GPIO.setup(self.pin_number, GPIO.OUT)

                # Catch event
                self.add_event('recognizer_loop:record_begin',
                               self._handle_listener_started)
                self.add_event('recognizer_loop:record_end',
                               self._handle_listener_ended)
            except Exception:
                self.log.error('Cannot initialize GPIO - skill will not load')
                self.speak_dialog('error.initialize')

    # Turn on LED
    def _handle_listener_started(self, message):
        GPIO.output(self.pin_number, GPIO.HIGH)

    # Turn off LED
    def _handle_listener_ended(self, message):
        GPIO.output(self.pin_number, GPIO.LOW)


def create_skill():
    return WakeWordLedGpio()
