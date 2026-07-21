let timer_code = `<div class="timer animatable">
        <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">                        
            <circle cx="50%" cy="50%" r="40"/>
            <circle cx="50%" cy="50%" r="40" pathLength="1"/>
            <text x="50%" y="60%" text-anchor="middle">
                <tspan id="timeLeft"></tspan>
            </text>
        </svg>
</div>`

let timerControl = {
    timeLeftMs: 0,
    paused: false,
    timerId: null,
    pauseTime: null,
    endTime: null,
    updateTimer: null,
    trialStarted: 0,
    trialTimeout: null,
    fsActivated: false,
};

let timer_fn = function (total_time = 60, y_pos = 80, x_pos = 50, startTime = total_time * 1000, time_res = 10) {
    let timer_el = document.querySelector('.timer')
    timer_el.style.top = y_pos + '%'
    timer_el.style.left = x_pos + '%'
    timer_el.style.transform = `translate(-${x_pos}%,-${y_pos}%)`


    let timeLeft = startTime / time_res // in 1e-2 seconds

    let timer = document.getElementById('timeLeft');

    // function isTimeLeft() {
    //     return timeLeft > -1;
    // }

    function runTimer(timerElement) {
        const timerCircle = timerElement.querySelector('svg > circle + circle');

        let startPoint = performance.now();
        let endPoint = startPoint + startTime;


        const normalizedTime = (total_time * (1000 / time_res) - timeLeft) / (total_time * (1000 / time_res));
        timerCircle.style.strokeDashoffset = normalizedTime;
        timer.innerHTML = Math.round(timeLeft / (1000 / time_res)).toString() + '';


        timerControl.endTime = endPoint;
        timerControl.timeLeftMs = startTime;

        function updateTimer() {
            if (timerControl.paused) return;


            const now = performance.now();
            // let timeLeftMs = Math.max(endPoint - now, 0);
            let timeLeftMs = Math.max(timerControl.endTime - now, 0);
            timerControl.timeLeftMs = timeLeftMs

            let normalizedTime = 1 - timeLeftMs / (total_time * 1000);

            timerCircle.style.strokeDashoffset = normalizedTime;
            timer.innerHTML = Math.round(timeLeftMs / 1000).toString();


            if (timeLeftMs > 0) {
                timerControl.timerId = setTimeout(updateTimer, time_res);
            } else {
                timerElement.classList.remove('animatable');
            }

        }

        timerControl.updateTimer = updateTimer;
        updateTimer();


    }


    runTimer(document.querySelector('.timer'));
}

function pauseTimer() {
    if (!timerControl.paused) {
        clearTimeout(timerControl.timerId);
        timerControl.paused = true;
        timerControl.pauseTime = performance.now();
    }
}

function resumeTimer() {
    if (timerControl.paused) {
        const pauseDuration = performance.now() - timerControl.pauseTime;
        timerControl.endTime += pauseDuration; // push back end time
        timerControl.paused = false;
        timerControl.updateTimer(); // resume loop
    }
}

let counter_code = `
<div id="word_counter">
<span id="n_words"></span><span>/</span><span id="min_words"></span>
</div>
`
let counter_code2 = `
<div id="word_counter2">
<span id="n_words2"></span><span>/</span><span id="min_words2"></span>
</div>
`

let counter_fn = function (n_words, min_words, y_pos = 80, x_pos = 50, v = '') {
    let counter_el = document.getElementById('word_counter' + v)
    // counter_el.style.top = y_pos + '%'
    // counter_el.style.left = x_pos + '%'
    // counter_el.style.transform = `translate(-${x_pos}%,-${y_pos}%)`

    let fillPercentage = Math.min((n_words / min_words) * 100, 100);

    let n_words_el = document.getElementById('n_words' + v);
    let min_words_el = document.getElementById('min_words' + v);
    n_words_el.innerHTML = n_words.toString();
    min_words_el.innerHTML = min_words.toString();
    // n_words_el.innerHTML = 150
    let bgColor;
    if (fillPercentage === 0) {
        if (v == "") {
            bgColor = "#9d9962";
        } else {
            bgColor = "#8ecae6";
        }
    } else if (fillPercentage > 0) {
        if (v == "") {
            bgColor = "#034748";
        } else {
            bgColor = "#fb8500";
        }
    }
    if (fillPercentage >= 100) {
        fillPercentage = 101
    }

    // } else if (fillPercentage < 80) {
    //     bgColor = "#FFD700"; // Gold (mid progress)
    // } else {
    //     bgColor = "#4CAF50"; // Green (close to or reached min_words)
    // }
    if (v == "") {
        counter_el.style.background = `linear-gradient(to right, ${bgColor} ${fillPercentage}%, #9d9962 ${fillPercentage}%)`;
    } else {
        counter_el.style.background = `linear-gradient(to right, ${bgColor} ${fillPercentage}%, #8ecae6 ${fillPercentage}%)`;
    }

    // counter_el.style.background = `linear-gradient(to right, #4CAF50 ${fillPercentage}%, transparent ${fillPercentage}%)`;

}