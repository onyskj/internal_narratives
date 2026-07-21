function showAlertType(jsPsych_instance, currentUser_instance) {
    timerControl.alertActivated = true
    timerControl.trialStartedAlert = performance.now()

    let alert_text = `
                   <div id="customAlert">
                   ` + warning_text_pr_type + `<br> You have used <b>` + currentUser_instance.count_type + ` out of ` + (max_timeout) + ` chances</b>.
                   `
    let extra_time = 0
    if (currentUser_instance.count_type === max_timeout) {
        // alert_text += warning_last_chance + '<br><br>The experiment will resume shortly.</div>'
        alert_text += warning_last_chance + '<br><br>Try again!<br><br>The experiment will resume shortly.</div>'
        extra_time = 2
    } else {
        alert_text += '<br><br>Try again!<br><br>The experiment will resume shortly.</div>'
    }
    document.getElementById('jspsych-experiment').innerHTML = alert_text
    // document.getElementsByClassName("jspsych-display-element").innerHTML = alert_text
    // document.body.innerHTML = alert_text

    let alertBox = document.getElementById("customAlert");
    alertBox.style.display = "block";  // Show the alert box

    jsPsych_instance.pauseExperiment()

    let remainingTime = (timeout_alert_duration + extra_time) * 1000 - (performance.now() - timerControl.trialStartedAlert)
    timerControl.trialRemainingAlert = remainingTime

    window.resumeTrialTimerAlert = () => {
        timerControl.trialTimeoutAlert = setTimeout(function () {
            alertBox.style.display = "none";
            document.getElementById('jspsych-experiment').innerHTML = ''
            timerControl.alertActivated = false
            jsPsych_instance.resumeExperiment()
            // window.resumeTrialTimer()
        }, timerControl.trialRemainingAlert);
    }
    // Hide the alert  and resume Experiment after set time
    timerControl.trialTimeoutAlert = setTimeout(function () {
        alertBox.style.display = "none";
        document.getElementById('jspsych-experiment').innerHTML = ''
        timerControl.alertActivated = false
        jsPsych_instance.resumeExperiment()
        // window.resumeTrialTimer()
    }, (timerControl.trialRemainingAlert));



    // setTimeout(function () {
    //     alertBox.style.display = "none";
    //     jsPsych_instance.resumeExperiment()
    // }, (timeout_alert_duration + extra_time) * 1000);

}


function showAlert(jsPsych_instance, currentUser_instance) {
    // let timer_started = performance.now()

    // if (timerControl.paused) return;
    timerControl.alertActivated = true
    timerControl.trialStartedAlert = performance.now()

    let alert_text = `
                   <div id="customAlert">
                   ` + warning_text + `<br> You have used <b>` + currentUser_instance.warning_count + ` out of ` + (max_timeout) + ` chances</b>.
                   `
    let extra_time = 0
    if (currentUser_instance.warning_count === max_timeout) {
        alert_text += warning_last_chance + '<br><br>The experiment will resume shortly.</div>'
        extra_time = 2
    } else {
        alert_text += '<br><br>The experiment will resume shortly.</div>'
    }
    document.getElementById('jspsych-experiment').innerHTML = alert_text

    let alertBox = document.getElementById("customAlert");
    alertBox.style.display = "block";  // Show the alert box

    jsPsych_instance.pauseExperiment()

    let remainingTime = (timeout_alert_duration + extra_time) * 1000 - (performance.now() - timerControl.trialStartedAlert)
    timerControl.trialRemainingAlert = remainingTime

    window.resumeTrialTimerAlert = () => {
        timerControl.trialTimeoutAlert = setTimeout(function () {
            alertBox.style.display = "none";
            document.getElementById('jspsych-experiment').innerHTML = ''
            timerControl.alertActivated = false
            jsPsych_instance.resumeExperiment()
            // window.resumeTrialTimer()
        }, timerControl.trialRemainingAlert);
    }
    // Hide the alert  and resume Experiment after set time
    timerControl.trialTimeoutAlert = setTimeout(function () {
        alertBox.style.display = "none";
        document.getElementById('jspsych-experiment').innerHTML = ''
        timerControl.alertActivated = false
        jsPsych_instance.resumeExperiment()
        // window.resumeTrialTimer()
    }, (timerControl.trialRemainingAlert));

    // // Hide the alert  and resume Experiment after set time
    // setTimeout(function () {
    //     alertBox.style.display = "none";
    //     jsPsych_instance.resumeExperiment()
    // }, (timeout_alert_duration + extra_time) * 1000);
}


function na_return_check(jsPsych_instance, user_instance, button_el) {

    let na_check = document.getElementById("qs_preamble_na_check")
    // let current_button_state = button_el.disabled
    // let qs_avoid_text = document.querySelector("#qs_avoid span")

    // Prevent checking the checkbox with a key
    na_check.addEventListener('keydown', function (event) {
        event.preventDefault();
    });
    // Checkbox alert object
    let alert_el = document.getElementById('formAlert')
    // 'Rather not say' checkbox handling - hide/show the submit button and textarea text - including catch question handling
    na_check.addEventListener('change', function () {
        user_instance.last_checked = na_check.checked
        if (na_check.checked) { // when checked
            let current_button_state = document.getElementById(button_el.id).disabled;
            button_el.disabled = true;
            na_check.disabled = true; // disable checkbox
            // submit_bttn.style.visibility = 'hidden'
            alert_el.style.visibility = 'visible'

            document.getElementById('close_alert').addEventListener('click', function (event) {
                button_el.disabled = current_button_state;
                // console.log(current_button_state);
                event.preventDefault()
                na_check.checked = false;
                na_check.disabled = false;
                // button_el.disabled = true;
                user_instance.last_checked = na_check.checked

                alert_el.style.visibility = 'hidden'

            });
            document.getElementById('return_alert').addEventListener('click', (event) => {
                event.preventDefault()
                user_instance.do_return = true
                // na_check.disabled = false; // disable checkbox
                alert_el.style.visibility = 'hidden'
                // document.getElementById('jspsych-experiment').innerHTML = ''
                jsPsych_instance.finishTrial()
            });
        }
    })

}

function prevent_return(e) {
    if (e.keyCode === 13) {
        e.preventDefault();
    }
}

