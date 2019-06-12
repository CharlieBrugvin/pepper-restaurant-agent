import config as cfg
import json
import tablet_interaction.tablet_interaction_config as tablet_cfg
import threading
import speech.speech_config as speech_cfg
import urllib2


class TabletManager:
    def __init__(self, app, say_method):
        if cfg.robot_stream:
            self.tabletService = app.session.service("ALTabletService")
        self.say = say_method
        self.signalID1 = None
        self.signalID2 = None
        self.on_fail = None
        self.on_success = None
        self.timer = None
        self.running = False

    def on_interaction_intent(self, intent):
        if cfg.robot_stream and self.running:
            if intent == speech_cfg.NEXT_INTENT or intent == speech_cfg.PREVIOUS_INTENT:
                script = "document.getElementById(\"" + intent + "\").submit()"
                self.tabletService.executeJS(script)

    def get_reminders_count(self, target, on_success=None, on_fail=None):
        parsed_json = json.loads(urllib2.urlopen(tablet_cfg.REMINDERS_COUNT_URL).read())
        return int(parsed_json["count"])

    def display_health(self, url, on_success=None, on_fail=None):
        if cfg.robot_stream:
            self.on_success = on_success
            self.on_fail = on_fail
            if self.tabletService:
                self.tabletService.showWebview(url)
                self.timer = threading.Timer(tablet_cfg.TIME_SHOWING_HEALTH_MEASUREMENTS, self.on_timeout, [on_success])
                self.timer.start()
            else:
                self.on_fail()
                self.clear_attrs()
        else:
            self.timer = threading.Timer(10, self.on_timeout, [on_success])
            self.timer.start()

    def on_timeout(self, on_success):
        self.timer = None
        if on_success:
            on_success()
        self.clear_display()

    def display_reminders(self, target, on_success=None, on_fail=None):
        if cfg.robot_stream:
            self.on_success = on_success
            self.on_fail = on_fail
            self.running = True
            if self.tabletService:
                self.signalID1 = self.tabletService.onJSEvent.connect(self.get_reminder)
                self.signalID2 = self.tabletService.onPageFinished.connect(self.page_finished)
                self.tabletService.showWebview(target + '/0')
                print("Showing webview")
            else:
                self.on_fail()
                self.clear_attrs()

    def get_url_for_target(self, target):
        if target in tablet_cfg.HEALTH_MEASUREMENTS_URL:
            return tablet_cfg.HEALTH_MEASUREMENTS_URL[target]

    def get_reminder(self, reminder_text):
        self.say(reminder_text)

    def page_finished(self):
        script = """
            var reminder = document.getElementById("reminderValue").innerText;
            ALTabletBinding.raiseEvent(reminder);
        """
        self.tabletService.executeJS(script)

    def get_url_for_person(self, target):
        return tablet_cfg.REMINDERS_URL

    def clear_display(self):
        if self.timer:
            self.timer.cancel()
        self.timer = None
        if cfg.robot_stream:
            if self.signalID2 and self.signalID1:
                self.tabletService.onPageFinished.disconnect(self.signalID1)
                self.tabletService.onJSEvent.disconnect(self.signalID2)
            if self.tabletService:
                self.tabletService.hideWebview()
                self.clear_attrs()

    def clear_attrs(self):
        self.on_success = None
        self.on_fail = None
        self.timer = None
        self.running = False
        self.signalID1 = None
        self.signalID2 = None