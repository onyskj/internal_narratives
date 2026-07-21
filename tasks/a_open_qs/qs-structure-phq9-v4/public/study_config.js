// Script that specifies useful variables and defines jsPsych and user classes

// Useful variables
let subversion = '_ddd'
let firestore_task = 'qs-structure-phq9-v4' + subversion
let base_url = "https://app.prolific.com/submissions/complete?cc=" // for prolific redirects
var dur_experiment = `20`; // duration of experiment in minutes
var study_subname = 'Understanding introspection and self-report' // subtitle of the study
let uid; // variable storing firebase uid

// Boolean values
let console_debug = true // whether to print to console
let do_online = true // whether to run online or offline
// let do_online = false
let no_skip = true // prevent skipping if no response or timeout

// let quick_consent = true // whether to do quick consent (1st option only required)
let quick_consent = false

let run_sim = false // whether to run in simulation mode

// Specs
let attention_threshold = 1 // minimum number of attention check required to pass
let end_study_duration = 2000 // waiting time for participants at the end of study

// Error codes
let no_consent_error = 'E_NC1' // return when no consent is given
let prolific_ids_error = 'E_PID1' // Prolific IDS don't match
let study_completed_error = 'E_SC1' // Study already completed before

const load_exp_minDelay = 100 * 7; // *7 1 second in milliseconds
const load_exp_maxDelay = 300 * 7; // 3 seconds in milliseconds
let feedback_duration = 3 * 60 // time to display feedback form (seconds)
let dur_buffer = 0.3

// Open-ended questions config
let min_words = 30 // 3<=================== CHANGE FOR LIVE
let qs_ans_required = false
let prevent_paste = true // <=================== CHANGE FOR LIVE
// let prevent_paste = false // <=================== CHANGE FOR LIVE
let writing_time = 90// 90
let warning_time = 30 // 30
let qs_read_time = 7 // extra time to read the question
let oq_timelimit_text = '1.5 minutes'

let emotion_duration = 30 //30
let per_question_duration = 10 //10
let lvl1_closed_duration = per_question_duration
let lvl2_closed_duration = per_question_duration * 3
let phq9_duration = per_question_duration * 9
let gad7_duration = per_question_duration * 7
let ids30_duration = (per_question_duration + 5) * 28 //+5
let sds_duration = (per_question_duration) * 20 //+5
let qsn_preamble_duration = 5 //5
let qsn_duration_countdown = 60

let timeout_alert_duration = 4 // duration of the timeout/empty  alert
let max_timeout = 4 // max number of timeouts or empty responses allowed (next one kicks ppt out)
let warning_text = `You've timed out or haven't provided a full response!`
let warning_last_chance = `<br><br>This is your <b>last warning</b>, next time you <u>will be asked to return your submission.</u>`

// Initialise jsPsych
let my_jsPsych_init = function () {
    return initJsPsych({
        override_safe_mode: true,
    });
}

// User class
class User {
    constructor(uid) {
        this.uid = uid;
        this.consent = null
        this.attention_check1 = 0
        this.attention_check2 = 0
        this.attention_check = 0
        this.empty_responses = false
        this.timeout_count = 0
        this.empty_count = 0
        this.warning_count = 0
        this.last_checked = null
    }

    // Sets requisite IDs in class based on URL or random if not specified - adds to jsPsych data property
    get_ids(jsPsych_instance) {
        let prolificID = jsPsych_instance.data.getURLVariable('PROLIFIC_PID');
        let studyID = jsPsych_instance.data.getURLVariable('STUDY_ID')
        let sessionID = jsPsych_instance.data.getURLVariable('SESSION_ID')

        // handle empty URL variables
        if (prolificID == null || prolificID.toString().length === 0) {
            prolificID = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
        }
        if (studyID == null || studyID.toString().length === 0) {
            studyID = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
        }
        if (sessionID == null || sessionID.toString().length === 0) {
            sessionID = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
        }
        this.PID = prolificID;
        this.ST_ID = studyID;
        this.SE_ID = sessionID;

        jsPsych_instance.data.addProperties({
            uid: this.uid,
            PID: prolificID,
            ST_ID: studyID,
            SE_ID: sessionID,
        })

    }

}


function separateWords(input, counter, div_counter, submit_bttn, q_name, jsPsych_instance) {
    // process text input
    let text = input.value
    text = text.replace(/\s\s+/g, ' ');

    // count words
    let words = text.split(" ");
    if (words.length > 0) {
        if (words[words.length - 1] === " ") {
            words.pop()
        }
        if (words[words.length - 1] === "") {
            words.pop()
        }
    }

    if (words.length >= min_words) {
        submit_bttn.style.visibility = "visible"
        div_counter.style.visibility = "hidden"
        counter.innerHTML = 0
    } else {
        if (q_name === 'lvl2_q_catch') {
            submit_bttn.style.visibility = "hidden"
            div_counter.style.visibility = "visible"
            counter.innerHTML = min_words - words.length

            // attention check case
            let catch_resp = input.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
            jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
            if (catch_resp) {
                submit_bttn.style.visibility = "visible"
                div_counter.style.visibility = "hidden"
            } else {
                submit_bttn.style.visibility = "hidden"
                div_counter.style.visibility = "visible"
            }
        } else {
            submit_bttn.style.visibility = "hidden"
            div_counter.style.visibility = "visible"
            counter.innerHTML = min_words - words.length
        }
    }
};

function startTimer_sec(duration, display, time_left, warning_time, min_instr = null) {
    var timer = duration, minutes, seconds;
    let timer_interval = setInterval(function () {
        seconds = parseInt(timer, 10);

        if (seconds <= warning_time && seconds > 0) {
            time_left.innerHTML = seconds
            display.style.visibility = 'visible'
            if (min_instr != null) {
                min_instr.style.visibility = "hidden"
            }
        } else if (seconds > warning_time && seconds > 0) {
            time_left.innerHTML = ''
            display.style.visibility = 'hidden'
        } else {
            time_left.innerHTML = ''
            display.style.visibility = 'hidden'
        }

        if (--timer < 0) {
            // timer = duration;
            timer = 0;
        }
    }, 1000);
}

function showAlert(jsPsych_instance, currentUser_instance) {
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

    // Hide the alert  and resume Experiment after set time
    setTimeout(function () {
        alertBox.style.display = "none";
        jsPsych_instance.resumeExperiment()
    }, (timeout_alert_duration + extra_time) * 1000);
}