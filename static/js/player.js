(function () {
    "use strict";

    // DOM elements
    const setupScreen = document.getElementById("setup-screen");
    const playerScreen = document.getElementById("player-screen");
    const durationSlider = document.getElementById("duration-slider");
    const durationDisplay = document.getElementById("duration-display");
    const brefToggle = document.getElementById("bref-toggle");
    const prepareBtn = document.getElementById("prepare-btn");
    const lyricsContainer = document.getElementById("lyrics-container");
    const progressBarContainer = document.getElementById("progress-bar-container");
    const progressBarFill = document.getElementById("progress-bar-fill");
    const progressBarHandle = document.getElementById("progress-bar-handle");
    const timeElapsed = document.getElementById("time-elapsed");
    const timeTotal = document.getElementById("time-total");
    const playPauseBtn = document.getElementById("play-pause-btn");
    const backBtn = document.getElementById("back-btn");

    // State
    let timingData = null;
    let flatWords = [];
    let isPlaying = false;
    let startTimestamp = 0;
    let pauseOffset = 0;
    let currentWordIndex = -1;
    let animFrameId = null;
    let totalDuration = 0;

    // Format time like anthem_utils.seconds_to_minutes
    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = (totalSeconds % 60).toFixed(1).padStart(4, "0");
        return minutes + ":" + seconds;
    }

    // Duration slider
    durationSlider.addEventListener("input", function () {
        durationDisplay.textContent = this.value;
    });

    // Prepare Track button
    prepareBtn.addEventListener("click", function () {
        const duration = parseFloat(durationSlider.value);
        const bref = brefToggle.checked;

        prepareBtn.textContent = "Loading...";
        prepareBtn.disabled = true;

        fetch("/api/timing?duration=" + duration + "&bref=" + bref)
            .then(function (res) { return res.json(); })
            .then(function (data) {
                timingData = data;
                totalDuration = data.duration;
                buildLyrics(data);
                showPlayer();
            })
            .catch(function (err) {
                alert("Error loading timing data: " + err.message);
            })
            .finally(function () {
                prepareBtn.textContent = "Prepare Track";
                prepareBtn.disabled = false;
            });
    });

    function buildLyrics(data) {
        lyricsContainer.innerHTML = "";
        flatWords = [];

        data.lines.forEach(function (line) {
            var lineDiv = document.createElement("div");
            lineDiv.className = "lyric-line";

            line.words.forEach(function (w) {
                var span = document.createElement("span");
                span.className = "word upcoming";
                span.textContent = w.word;
                lineDiv.appendChild(span);
                lineDiv.appendChild(document.createTextNode(" "));

                flatWords.push({
                    startTime: w.startTime,
                    endTime: w.endTime,
                    element: span,
                    lineElement: lineDiv,
                });
            });

            lyricsContainer.appendChild(lineDiv);
        });

        timeTotal.textContent = formatTime(totalDuration);
        timeElapsed.textContent = formatTime(0);
    }

    function showPlayer() {
        setupScreen.classList.remove("active");
        playerScreen.classList.add("active");
        resetPlayback();
    }

    function showSetup() {
        stopPlayback();
        playerScreen.classList.remove("active");
        setupScreen.classList.add("active");
    }

    function resetPlayback() {
        stopPlayback();
        pauseOffset = 0;
        currentWordIndex = -1;
        isPlaying = false;
        playPauseBtn.textContent = "Play";
        updateProgressBar(0);
        timeElapsed.textContent = formatTime(0);

        // Reset all words to upcoming
        flatWords.forEach(function (fw) {
            fw.element.className = "word upcoming";
        });
        updateLineHighlighting(-1);
    }

    function stopPlayback() {
        if (animFrameId !== null) {
            cancelAnimationFrame(animFrameId);
            animFrameId = null;
        }
        isPlaying = false;
    }

    // Play/Pause
    playPauseBtn.addEventListener("click", togglePlayPause);

    function togglePlayPause() {
        if (isPlaying) {
            pause();
        } else {
            play();
        }
    }

    function play() {
        if (pauseOffset >= totalDuration * 1000) {
            // Already finished, restart
            pauseOffset = 0;
            currentWordIndex = -1;
        }
        startTimestamp = performance.now() - pauseOffset;
        isPlaying = true;
        playPauseBtn.textContent = "Pause";
        tick();
    }

    function pause() {
        pauseOffset = performance.now() - startTimestamp;
        stopPlayback();
        playPauseBtn.textContent = "Play";
    }

    function tick() {
        if (!isPlaying) return;

        var now = performance.now();
        var elapsedMs = now - startTimestamp;
        var elapsed = Math.min(elapsedMs / 1000, totalDuration);

        // Find active word via binary search
        var activeIdx = findActiveWord(elapsed);

        if (activeIdx !== currentWordIndex) {
            updateWordStates(activeIdx);
            currentWordIndex = activeIdx;
        }

        updateProgressBar(elapsed / totalDuration);
        timeElapsed.textContent = formatTime(elapsed);

        if (elapsed >= totalDuration) {
            // Playback complete
            isPlaying = false;
            playPauseBtn.textContent = "Replay";
            pauseOffset = totalDuration * 1000;
            // Mark all words as sung
            flatWords.forEach(function (fw) {
                fw.element.className = "word sung";
            });
            updateLineHighlighting(-1);
            return;
        }

        animFrameId = requestAnimationFrame(tick);
    }

    // Binary search: find last word where startTime <= elapsed
    function findActiveWord(elapsed) {
        if (flatWords.length === 0) return -1;

        var lo = 0;
        var hi = flatWords.length - 1;
        var result = -1;

        while (lo <= hi) {
            var mid = (lo + hi) >>> 1;
            if (flatWords[mid].startTime <= elapsed) {
                result = mid;
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }

        return result;
    }

    function updateWordStates(activeIdx) {
        flatWords.forEach(function (fw, i) {
            if (i < activeIdx) {
                fw.element.className = "word sung";
            } else if (i === activeIdx) {
                fw.element.className = "word active";
            } else {
                fw.element.className = "word upcoming";
            }
        });

        if (activeIdx >= 0) {
            updateLineHighlighting(activeIdx);
        }
    }

    function updateLineHighlighting(activeIdx) {
        var activeLine = activeIdx >= 0 ? flatWords[activeIdx].lineElement : null;
        var allLines = lyricsContainer.querySelectorAll(".lyric-line");

        var activeLineIdx = -1;
        allLines.forEach(function (line, i) {
            line.classList.remove("active-line", "adjacent-line");
            if (line === activeLine) {
                activeLineIdx = i;
            }
        });

        if (activeLineIdx >= 0) {
            allLines[activeLineIdx].classList.add("active-line");
            if (activeLineIdx > 0) {
                allLines[activeLineIdx - 1].classList.add("adjacent-line");
            }
            if (activeLineIdx < allLines.length - 1) {
                allLines[activeLineIdx + 1].classList.add("adjacent-line");
            }
        }
    }

    function updateProgressBar(fraction) {
        var pct = Math.max(0, Math.min(100, fraction * 100));
        progressBarFill.style.width = pct + "%";
        progressBarHandle.style.left = pct + "%";
    }

    // Seeking
    var isSeeking = false;

    function seekFromEvent(e) {
        var rect = progressBarContainer.getBoundingClientRect();
        var fraction = (e.clientX - rect.left) / rect.width;
        fraction = Math.max(0, Math.min(1, fraction));
        var seekTime = fraction * totalDuration;

        pauseOffset = seekTime * 1000;
        currentWordIndex = -1;

        if (isPlaying) {
            startTimestamp = performance.now() - pauseOffset;
        }

        // Force immediate state update
        var activeIdx = findActiveWord(seekTime);
        updateWordStates(activeIdx);
        currentWordIndex = activeIdx;
        updateProgressBar(fraction);
        timeElapsed.textContent = formatTime(seekTime);

        // Reset replay button if seeking before end
        if (seekTime < totalDuration && !isPlaying) {
            playPauseBtn.textContent = "Play";
        }
    }

    progressBarContainer.addEventListener("mousedown", function (e) {
        isSeeking = true;
        seekFromEvent(e);
    });

    document.addEventListener("mousemove", function (e) {
        if (isSeeking) {
            seekFromEvent(e);
        }
    });

    document.addEventListener("mouseup", function () {
        isSeeking = false;
    });

    // Touch support for progress bar
    progressBarContainer.addEventListener("touchstart", function (e) {
        isSeeking = true;
        seekFromEvent(e.touches[0]);
        e.preventDefault();
    });

    document.addEventListener("touchmove", function (e) {
        if (isSeeking) {
            seekFromEvent(e.touches[0]);
        }
    });

    document.addEventListener("touchend", function () {
        isSeeking = false;
    });

    // Back button
    backBtn.addEventListener("click", showSetup);

    // Keyboard shortcut: space for play/pause
    document.addEventListener("keydown", function (e) {
        if (e.code === "Space" && playerScreen.classList.contains("active")) {
            e.preventDefault();
            togglePlayPause();
        }
    });
})();
