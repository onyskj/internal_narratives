// Script that specifies useful variables and defines jsPsych and user classes
let print_error = true
var should_be_in_fullscreen = true;
const load_exp_minDelay = 100 * 10; // *7 1 second in milliseconds
const load_exp_maxDelay = 300 * 6; // 3 seconds in milliseconds

let condList = ["MH", "ML"]

// Useful variables
let subversion = ''
let firestore_task = 'qs-intervention-v3' + subversion
let base_url = "https://app.prolific.com/submissions/complete?cc=" // for prolific redirects
var dur_experiment = `21`; // duration of experiment in minutes
var study_subname = 'Understanding introspection and self-report' // subtitle of the study
let uid; // variable storing firebase uid

// Group condition from url or random
let cName = new URLSearchParams(window.location.search).get('cName')
if (cName == null || cName.toString().length === 0) {
    // cName = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
    cName = condList[Math.floor(Math.random() * condList.length)];
}
// let cName = 'MH'
// console.log(cName)

let gName = new URLSearchParams(window.location.search).get('gName')
if (gName == null || gName.toString().length === 0) {
    // gName = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
    gName = ["H","D"][Math.floor(Math.random() * 2)];
}
// let gName = 'MH'
// console.log('group:', gName)

// Intertrial interval times
let type_gap_low = 300
let type_gap_high = 800
let type_gap_delta = type_gap_high - type_gap_low

// Boolean values
// let do_online = false // whether to run online or offline 
let do_online = true

// let allow_completed = false // for LIVE
let allow_completed = true // for TEST

// let quick_consent = true // whether to do quick consent (1st option only required)
let quick_consent = false

let run_sim = false // whether to run in simulation mode

let audio_full = true // Whether to play audio fully, without option to skip
// let audio_full = false

// Specs
let attention_threshold = 1 // max number of attention fails allowed to pass
let end_study_duration = 2000 // waiting time for participants at the end of study
let trigger_end_duration = 5 * 60 // time to display the option to seek help (seconds)
let feedback_duration = 3 * 60 / 25 // time to display feedback form (seconds)
let dur_buffer = 0.3

// Error codes
let no_consent_error = 'E_NC1' // return when no consent is given
let prolific_ids_error = 'E_PID1' // Prolific IDS don't match
let study_completed_error = 'E_SC1' // Study already completed before
let saving_error_doc = 'E_SV1' // Study already completed before
let saving_error_user = 'E_SV2' // Study already completed before
let code_retrieve_error = 'E_CR1' // error when retrieving code

// Timeouts and warnings
let timeout_alert_duration = 4 // 4  duration of the timeout/empty  alert
let max_timeout = 4 // max number of timeouts or empty responses allowed (next one kicks ppt out)
let warning_text = `You've timed out or haven't provided a full response!`
let warning_text_pr_type = `You've timed out or haven't provided a correct response!`
let warning_last_chance = `<br><br>This is your <b>last warning</b>, next time you <u>will be asked to return your submission.</u>`
let max_fs = 2 // 2 Max full-screen warnings

let warned_code = 'WARNED'
let warned_code_pr = 'WARNED_PR'
let warned_code_fs = 'WARNED_FS'
let return_code = "C16OSXBH"
let return_url=  `https://app.prolific.com/submissions/complete?cc=${return_code}`


// Initialise jsPsych
let my_jsPsych_init = function () {
    // let currentUser;
    let jsPsych = initJsPsych({
        override_safe_mode: true,
    });
    return jsPsych
}

// User class
class User {
    constructor(uid) {
        this.uid = uid; // firebase id
        this.consent = null // consent status

        // track attention checks
        this.attention_check1 = 0
        this.attention_check2 = 0
        this.attention_check = 0

        this.count_fs = 0 // count how many times quit full screen

        this.timeout_count = 0 // count how many timeouts
        this.empty_count = 0 // count how many missed responses
        this.warning_count = 0 // counts timeouts or missed responses for the whole experiment

        this.last_checked = null //whether user indicated they don't want to provide responses
        this.do_return = false // whether used confirmed they want to return submission

        this.word_limit_ok = false //track if met the word limit
        this.act_word_limit_ok = false//

        this.time_left = null // keeping track how much time is left

        this.do_submit = false // whether user submitted resopns in the type trial

        this.count_pr = 0 // count failed attempt in the practice trial
        this.vas_pr_inrange = false //whether practice vas response was in range

        this.count_type = 0 // keep track how many recreate trials

        // this.audio_file_min_words = null // dynamic min words for typing

        this.store_vas_loc = [] // store all vas clicks
        this.store_vas_rt = [] // store all vas clicks

        this.count_w_list = 0


    }

    // Sets requisite IDs in class based on URL or random if not specified - adds to jsPsych data property
    get_ids(jsPsych_instance) {
        let prolificID = jsPsych_instance.data.getURLVariable('PROLIFIC_PID');
        let studyID = jsPsych_instance.data.getURLVariable('STUDY_ID')
        let sessionID = jsPsych_instance.data.getURLVariable('SESSION_ID')
        // let cName = jsPsych_instance.data.getURLVariable('cName')

        // handle empty URL variables
        if (prolificID == null || prolificID.toString().length === 0) {
            // prolificID = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
            prolificID = this.uid
        }
        if (studyID == null || studyID.toString().length === 0) {
            // studyID = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
            studyID = this.uid
        }
        if (sessionID == null || sessionID.toString().length === 0) {
            // sessionID = Array.from(Array(20), () => Math.floor(Math.random() * 36).toString(36)).join('');
            sessionID = this.uid
        }

        this.PID = prolificID;
        this.ST_ID = studyID;
        this.SE_ID = sessionID;
        this.cName = cName;
        this.gName = gName;

        jsPsych_instance.data.addProperties({
            uid: this.uid,
            PID: prolificID,
            ST_ID: studyID,
            SE_ID: sessionID,
            cName: cName,
            gName: gName,
        })

    }

}

// Study files
let images = ["imgs/playing.gif", "imgs/submit.svg"] // include gif
// let audio_attn = ["audio/attn/dogs_att.mp3", "audio/attn/juice_att.mp3",]
let audio_attn = ["audio/attn/dogs_att.mp3"]

let audios = {
    // 'MH': Array.from({length: 9}, (_, i) => `audio/mh/mh_${i + 1}.mp3`),// ["audio/mh/mh_1.mp3"],
    'MH': Array.from({length: 4}, (_, i) => `audio/mh/mh_${i + 1}_v6.mp3`),// ["audio/mh/mh_1.mp3"],
    'ML': Array.from({length: 4}, (_, i) => `audio/ml/ml_${i + 1}_v6.mp3`),// ["audio/mh/mh_1.mp3"],
    'EH': Array.from({length: 4}, (_, i) => `audio/mh/eh_${i + 1}_v6.mp3`),// ["audio/mh/mh_1.mp3"],
    'EL': Array.from({length: 4}, (_, i) => `audio/ml/el_${i + 1}_v6.mp3`),// ["audio/mh/mh_1.mp3"],
}

let audio_condition = audios[cName]
let all_audio = audio_attn.concat(audio_condition)
// console.log(all_audio)



