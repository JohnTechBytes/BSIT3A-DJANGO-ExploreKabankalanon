/* ExploreKabankalan shared voice search.
 *
 * One implementation for every search field: the Web Speech API writes the
 * recognised words into the input while the visitor is still talking, then
 * stops on request, on submit, or when the browser ends the session.
 *
 * Usage:
 *   window.EAVoiceSearch.attach({ input, button, status });
 *
 * The button must contain an element with class "ea-voice-text" (optional) and
 * should start with the `hidden` attribute: it is only revealed when the
 * browser actually exposes speech recognition.
 */
(function (window, document) {
  "use strict";

  var DEFAULT_LANG = "en-PH";
  var FALLBACK_LANG = "en-US";

  var ERROR_MESSAGES = {
    "not-allowed": "Microphone access was blocked. Allow it in your browser settings and try again.",
    "service-not-allowed": "Microphone access was blocked by the browser.",
    "no-speech": "I did not catch that. Tap Speak and try again.",
    "audio-capture": "No microphone was found on this device.",
    "language-not-supported": "This browser cannot transcribe English. Type your search instead.",
    network: "Voice search needs a connection. Check your internet and retry."
  };

  function attach(options) {
    var settings = options || {};
    var input = settings.input;
    var button = settings.button;
    var status = settings.status;

    if (!input || !button) return null;

    var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    function setStatus(message, isError) {
      if (!status) return;
      status.textContent = message || "";
      status.classList.toggle("is-error", Boolean(isError));
    }

    if (!Recognition) {
      // No support: keep the button out of the way, the field still works.
      setStatus("Voice search needs Chrome or Edge. Typing still works everywhere.");
      return null;
    }

    button.hidden = false;

    var recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = settings.lang || DEFAULT_LANG;

    var listening = false;
    var baseText = "";
    var finalTranscript = "";
    var triedFallbackLanguage = false;

    function label(text) {
      var element = button.querySelector(".ea-voice-text, .ea6-voice-text");
      if (element) element.textContent = text;
      button.setAttribute("aria-label", text === "Listening"
        ? "Listening, tap to stop voice search" : "Speak to search by voice");
    }

    function start() {
      if (listening) return;
      baseText = input.value.trim();
      if (baseText) baseText += " ";
      finalTranscript = "";
      try {
        recognition.start();
      } catch (error) {
        setStatus("Voice search could not start. Try again.", true);
      }
    }

    recognition.addEventListener("start", function () {
      listening = true;
      button.classList.add("is-listening");
      button.setAttribute("aria-pressed", "true");
      label("Listening");
      setStatus("Listening… say a place, café or activity.");
    });

    recognition.addEventListener("result", function (event) {
      var interim = "";

      for (var i = event.resultIndex; i < event.results.length; i += 1) {
        var result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      // Write straight into the field while the visitor speaks.
      input.value = (baseText + finalTranscript + interim)
        .replace(/\s+/g, " ")
        .trim();
      input.dispatchEvent(new Event("input", { bubbles: true }));
      setStatus("“" + input.value + "”");
    });

    recognition.addEventListener("error", function (event) {
      var code = event.error;

      if (code === "aborted") return;

      if (code === "language-not-supported" && !triedFallbackLanguage) {
        triedFallbackLanguage = true;
        recognition.lang = settings.fallbackLang || FALLBACK_LANG;
        // The failed session is still winding down, so stop it and restart on
        // the next tick instead of racing its state.
        try {
          recognition.stop();
        } catch (error) {
          /* already stopped */
        }
        window.setTimeout(function () {
          try {
            recognition.start();
          } catch (error) {
            setStatus("Voice search could not start.", true);
          }
        }, 250);
        return;
      }

      setStatus(ERROR_MESSAGES[code] || "Voice search stopped. Try again.", true);
    });

    recognition.addEventListener("end", function () {
      listening = false;
      button.classList.remove("is-listening");
      button.setAttribute("aria-pressed", "false");
      label("Speak");

      if (status && !status.classList.contains("is-error")) {
        setStatus(input.value
          ? "Press Enter to search “" + input.value + "”."
          : "Tap Speak and say a place or activity.");
      }
    });

    button.addEventListener("click", function () {
      if (listening) {
        recognition.stop();
      } else {
        start();
      }
    });

    if (input.form) {
      input.form.addEventListener("submit", function () {
        if (listening) recognition.stop();
      });
    }

    setStatus("Tap Speak and say a place or activity.");

    return {
      stop: function () {
        if (listening) recognition.stop();
      },
      isListening: function () {
        return listening;
      }
    };
  }

  window.EAVoiceSearch = { attach: attach };
})(window, document);
