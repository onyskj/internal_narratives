// ------------> Generic content for questions <---------------
let nQ = 14

let question_preamble = `<div id="qs_preamble"><p id="qs_preamble_q_p"><u>Question <span id="qs_preamble_q_no"></span> of <span id="qs_preamble_q_max"></span></u></p>
    <h4><u>` + "Please answer the following question in detail by writing text in the box below." + `</u></h4>
    <p id="qs_preamble_disclosure">(You have <b>` + oq_timelimit_text + `</b> to answer)</p>
    <div id="qs_timeleft">
    You have <span id="qs_timeleft_sec">` + warning_time.toString() + `</span> seconds left.
    </div>
    </div>`

let avoid_label = "If you'd rather not say, check this box and return your submission."
let uncheck_label = "If you would like to continue, please uncheck the box."
let avoid_answer = `<div id="qs_avoid">
        <label>
            <input type="checkbox" id="qs_preamble_na_check">
                <span>` + avoid_label + `</span> 
        </label>
    </div>
    `

let avoid_answer_qsn = `<div id="qs_avoid_qsn">
        <label>
            <input type="checkbox" id="qs_preamble_na_check">
                <span>` + avoid_label + `</span> 
        </label>
    </div>
    `

let time_word = `<div id="qs_words">
    Please write at least <span id="qs_words_left">` + min_words + `</span> more words.
    </div>
    `

let lvl_x_question_button_label = "Click here once you are happy with your answer"
let return_button = 'Click here to return your submission to Prolific'


// ------------> Level 1 questions <---------------

let lvl1_q1 = "<p>In the past two weeks, how would you describe your overall emotional well-being, including your mood, feelings, thoughts about yourself, and any changes in your behaviour or daily functioning?</p><p>Please provide examples of situations or experiences that best illustrate these aspects.</p>"
let lvl1_q1_spec = "<p>In the past two weeks, have you been bothered by your overall emotional well-being, including your mood, motivation, enjoyment, thoughts about yourself, and any changes in your behaviour or daily functioning?</p><p>Please share typical situations in your life that exemplify some of these.</p>"
let lvl1_qs = []
if (subversion === '_s') {
    // lvl1_qs = [lvl1_q1_spec]
    lvl1_qs = [lvl1_q1_spec]
} else {
    lvl1_qs = [lvl1_q1]
}
let lvl1_question_array = [{
    prompt: `<div id="qs_instr">` + lvl1_qs[0] + `</div>` + avoid_answer + time_word,
    rows: 8,
    required: qs_ans_required,
    columns: 100,
    name: 'lvl1_q1'
}]
// ----------------------------------------------------------

// ------------> Level 2 questions <---------------
let lvl2_q1 = "<p>Can you describe how you felt when doing activities and how your mood has been generally in the past two weeks?</p><p>Can you provide typical examples that would best capture your feelings?</p>"
let lvl2_q2 = "<p>In the past two weeks, how have your sleep patterns, energy levels, appetite, focus and cognitive abilities been?</p><p>Are there any occasions that you could share where they have been affected in any way?</p>"
let lvl2_q3 = "<p>Please provide typical examples of your thoughts and feelings about yourself and your sense of self-worth that you've had over the last two weeks.</p>"
let lvl2_q1_spec = "<p>How much have you been bothered by your overall mood, motivation, enjoyment and feelings about yourself in the past two weeks?</p><p>Can you provide typical examples that would best capture your feelings?</p>"
let lvl2_q2_spec = "<p>In the past two weeks, have you been bothered by your sleep patterns, energy levels, concentration and appetite?</p><p>Are there any occasions that you could share where they have been affected in any way?</p>"
let lvl2_q3_spec = "<p>How much have you been bothered by your thoughts about yourself and your sense of self-worth over the last two weeks?</p><p>Please provide typical examples that support this.</p>"

let lvl2_catch_q = "<p>This is an attention check. Please write the two words at the end of this sentence, in lower-case, without apostrophe: 'five carrots'.</p>"
let lvl2_catch_ans = 'five carrots'
let lvl2_qs = []
if (subversion === '_s') {
    lvl2_qs = [lvl2_q1_spec, lvl2_q2_spec, lvl2_q3_spec]
} else {
    lvl2_qs = [lvl2_q1, lvl2_q2, lvl2_q3]
}

let lvl2_question_array = []

let q = 0
for (let lvl2_q of lvl2_qs) {
    q += 1
    let tmp_json = {
        prompt: `<div id="qs_instr">` + lvl2_q + `</div>` + avoid_answer + time_word,
        rows: 8,
        required: qs_ans_required,
        columns: 100,
        name: 'lvl2_q' + q.toString(),
    }
    lvl2_question_array.push(tmp_json)

    // catch question level 2
    if (q === 2) {
        let catch_json = {
            prompt: `<div id="qs_instr">` + lvl2_catch_q + `</div>` + avoid_answer + time_word,
            rows: 8,
            required: qs_ans_required,
            columns: 100,
            name: 'lvl2_q_catch',
        }
        lvl2_question_array.push(catch_json)
    }
}
// ----------------------------------------------------------

// ------------> Level 3 questions <---------------
// General version
let lvl3_q1 = "<p>Could you share any activities or events from the past two weeks that made you feel bothered because of a lack of interest or pleasure in doing them?</p>";
let lvl3_q2 = "<p>For the past two weeks, have you been bothered by your mood and how you felt generally?</p><p>Were there any situations when you felt down, depressed, or hopeless?</p>";
let lvl3_q3 = "<p>Can you provide examples of how your sleep has been in the past two weeks?</p><p>Have you been bothered by challenges with falling asleep, staying asleep, or even sleeping too much?</p>";
let lvl3_q4 = "<p>Have you been bothered by your energy levels over the past two weeks?</p><p>Can you recall situations when it comes to feeling tired/lively or low/high on energy?</p>";
let lvl3_q5 = "<p>In the past two weeks, have you been bothered about your appetite?</p><p>Can you describe your typical attitude towards food - maybe you have noticed something unusual, like changes in how much you're eating or not eating?</p>";
let lvl3_q6 = "<p>In the past two weeks, have you been bothered by feelings about yourself?</p><p>In what situations did you feel proud or like a failure? Did you feel you met your own and your family's expectations, or let them down?</p>";
let lvl3_q7 = "<p>In the past two weeks, have you been bothered by your ability to concentrate and focus?</p><p>Please describe how it felt to do things that require you to concentrate for a while, like working, reading, or watching movies?</p>";
let lvl3_q8 = "<p>Can you describe situations over the past two weeks when you were bothered by feeling slower than usual in terms of thinking, speaking, or just acting - or situations where you felt fidgety and restless?</p>";

//Specific version
let lvl3_q1_spec = "<p>In the past two weeks, have you been bothered by having little interest or enjoyment in doing things?</p><p>Could you give examples of activities or events that capture this?</p>";
let lvl3_q2_spec = "<p>For the past two weeks, how much have you been bothered by feeling down, depressed or hopeless?</p><p>What would be typical examples of this?</p>";
let lvl3_q3_spec = "<p>Can you provide examples of how your sleep has been in the past two weeks - have you been bothered by any challenges with falling asleep, staying asleep, or even sleeping too much?</p>";
let lvl3_q4_spec = "<p>Please provide a description of situations that capture your energy levels over the past two weeks - how much have you been bothered by feeling tired or low on energy?</p>";
let lvl3_q5_spec = "<p>In the past two weeks, have you been bothered by your appetite?</p><p>Can you describe your typical attitude towards food - is there something unusual, like changes in how much you're eating or not eating?</p>";
let lvl3_q6_spec = "<p>In the past two weeks, how much have you been bothered by feeling bad about yourself?</p><p>In what situations did you feel proud or like a failure? Did you feel you met your own and your family's expectations, or let them down?</p>";
let lvl3_q7_spec = "<p>In the past two weeks, have you been bothered by your ability to concentrate and focus?</p><p>Please describe how it felt to do things that require you to concentrate for a while, like working, reading or watching movies?</p>";
let lvl3_q8_spec = "<p>Over the past two weeks, how much have you been bothered by moments of feeling slower than usual in terms of thinking, speaking, or just acting - or feeling fidgety and restless?</p><p>Can you give some examples?</p>";

let lvl3_qs = []
if (subversion === '_s') {
    lvl3_qs = [lvl3_q1_spec, lvl3_q2_spec, lvl3_q3_spec, lvl3_q4_spec, lvl3_q5_spec, lvl3_q6_spec, lvl3_q7_spec, lvl3_q8_spec]
} else {
    lvl3_qs = [lvl3_q1, lvl3_q2, lvl3_q3, lvl3_q4, lvl3_q5, lvl3_q6, lvl3_q7, lvl3_q8]
}
let lvl3_question_array = []
q = 0
for (let lvl3_q of lvl3_qs) {
    q += 1
    let tmp_json = {
        prompt: `<div id="qs_instr">` + lvl3_q + `</div>` + avoid_answer + time_word,
        rows: 8,
        required: qs_ans_required,
        columns: 100,
        name: 'lvl3_q' + q.toString(),
    }
    lvl3_question_array.push(tmp_json)
}


// ------------> Repeat level 2 question <---------------
let rep_lvl2_q1 = lvl2_qs[0];

let rep_question_array = [{
    prompt: `<div id="qs_instr">` + rep_lvl2_q1 + `</div>` + avoid_answer + time_word,
    rows: 8,
    required: qs_ans_required,
    columns: 100,
    name: 'rep_lvl2_q1'
}]
// ----------------------------------------------------------

// ------------> Level 1 open closed version questions <---------------
let lvl1_closed_preamble = `<div id="qs_preamble"><h3><u>Please select a response that best describes you over the last 2 weeks.</u></h3>
<!--            <h4>Indicate your answer to each question and then submit by clicking the button at the bottom of the page.</h4>-->
<!--        <p id='qs_preamble_disclosure'>(You can click on the question/statement to reset your answer.)</p>-->
        <p id="qsn_time">You have <span id="qsn_time_left"></span> seconds left</p>
                                ` + avoid_answer_qsn + `
        
        </div>
        `

let lvl1_q1_closed = "My overall emotional well-being, including my mood feelings, thoughts about myself, and any changes in my behaviour or daily functioning have been: "
let lvl1_q1_closed_spec = "My overall emotional well-being, including my mood, motivation, enjoyment, thoughts about myself, and any changes in my behaviour or daily functioning have been:"


let lvl1_closed_qs = []
if (subversion === '_s') {
    lvl1_closed_qs = [lvl1_q1_closed_spec]
} else {
    lvl1_closed_qs = [lvl1_q1_closed]
}

let lvl1_closed_array = []
q = 0
for (let lvl1_closed_q of lvl1_closed_qs) {
    q += 1
    let q_string = q.toString() + ". "
    let tmp_json = {
        prompt: q_string + lvl1_closed_qs[q - 1],
        name: 'lvl1_closed_q' + q.toString(),
        options: ['Very Good', 'Good', 'Bad', 'Very Bad'],
        required: false,
        horizontal: false
    }
    lvl1_closed_array.push(tmp_json)
}
// ----------------------------------------------------------

// ------------> Level 2 open closed version questions <---------------
let lvl2_closed_preamble = `<div id="qs_preamble"><h3><u>Please select a response that best describes you over the last 2 weeks.</u></h3>
<!--            <h4>Indicate your answer to each question and then submit by clicking the button at the bottom of the page.</h4>-->
<!--        <p id='qs_preamble_disclosure'>(You can click on the question/statement to reset your answer.)</p>-->
        <p id='qs_preamble_disclosure'>(You might need to scroll down to see all the questions.)</p>
        <p id="qsn_time">You have <span id="qsn_time_left"></span> seconds left</p>
                                ` + avoid_answer_qsn + `
        </div>
        `

let lvl2_q1_closed = "My feelings when doing activities and my overall mood have been: "
let lvl2_q2_closed = "My sleep patterns, energy levels, appetite, focus and cognitive abilities have been: "
let lvl2_q3_closed = "My thoughts and feelings about myself and my sense of self-worth have been: "
let lvl2_q1_closed_spec = "My overall mood, motivation, enjoyment and feelings about myself have been: "
let lvl2_q2_closed_spec = "My sleep patterns, energy levels, concentration and appetite have been: "
let lvl2_q3_closed_spec = "My thoughts about myself and my sense of self-worth have been: "
let lvl2_closed_qs = []
if (subversion === '_s') {
    lvl2_closed_qs = [lvl2_q1_closed_spec, lvl2_q2_closed_spec, lvl2_q3_closed_spec]
} else {
    lvl2_closed_qs = [lvl2_q1_closed, lvl2_q2_closed, lvl2_q3_closed]
}

let lvl2_closed_array = []
q = 0
for (let lvl2_closed_q of lvl2_closed_qs) {
    q += 1
    let q_string = q.toString() + ". "
    let tmp_json = {
        prompt: q_string + lvl2_closed_qs[q - 1],
        name: 'lvl2_closed_q' + q.toString(),
        options: ['Very Good', 'Good', 'Bad', 'Very Bad'],
        required: false,
        horizontal: false
    }
    lvl2_closed_array.push(tmp_json)
}
// ----------------------------------------------------------


// ------------> Open question trial function <---------------
function question_trial(qs_list, q_index = 0, q_count, save_fn, save_fn_user, auth_instance, currentUser_instance, jsPsych_instance) {
    return {
        type: jsPsychSurveyText,
        preamble: question_preamble,
        button_label: lvl_x_question_button_label,
        questions: [qs_list[q_index]],
        css_classes: ['lvlx_qs'],
        trial_duration: 1000 * (writing_time + qs_read_time),
        on_load: function () {
            // preamble margin-top style if in simulation mod
            if (!run_sim) {
                let q_name = qs_list[q_index]['name']

                // initialise checked property
                currentUser_instance.last_checked = false

                // style instruction preamble depending on question number being odd/even
                let instr_el = document.getElementById('qs_instr');
                let q_no_el = document.getElementById('qs_preamble_q_p');
                if (q_index % 2 === 0) {
                    instr_el.style.background = `rgb(211, 211, 211, 0.5)`
                    q_no_el.style.color = `rgb(65, 105, 225)`
                } else {
                    instr_el.style.background = `rgb(85, 85, 85, 0.4)`
                    q_no_el.style.color = `blue`
                }

                // Question progress
                let q_max_el = document.getElementById('qs_preamble_q_max');
                q_max_el.innerHTML = nQ.toString()
                let q_no_item = document.getElementById("qs_preamble_q_no")
                q_no_item.textContent = (q_count).toString()

                // start timer count down
                let time_display = document.querySelector('#qs_timeleft')
                let time_left = document.querySelector('#qs_timeleft_sec')
                time_display.style.visibility = 'hidden'
                let minute_instr = document.getElementById('qs_preamble_disclosure')
                startTimer_sec(writing_time, time_display, time_left, warning_time, minute_instr)

                // get elements to adjust
                let preamble = document.getElementById("qs_preamble").clientHeight
                let lvlx_el = document.getElementsByClassName("lvlx_qs")[0]

                lvlx_el.style.marginTop = (preamble * 1.025).toString() + 'px'
                try {
                    // adapt preamble when resizing window
                    window.addEventListener('resize', function () {
                        let preamble = document.getElementById("qs_preamble").clientHeight
                        let lvlx_el = document.getElementsByClassName("lvlx_qs")[0]
                        lvlx_el.style.marginTop = (preamble * 1.025).toString() + 'px'
                    })
                } catch (error) {
                    console.error('resize issues')
                }


                // checkbox objects
                let na_check = document.getElementById("qs_preamble_na_check")
                // let qs_avoid_text = document.querySelector("#qs_avoid span")

                // Prevent checking the checkbox with a key
                na_check.addEventListener('keydown', function (event) {
                    event.preventDefault();
                });

                // get the word counter relevant elements
                let my_txt_area = document.getElementsByTagName('textarea')[0]
                let counter = document.getElementById('qs_words_left')
                let div_counter = document.getElementById('qs_words')
                let submit_bttn = document.getElementById('jspsych-survey-text-next')

                // hide submit button at the start
                submit_bttn.style.visibility = "hidden"

                // prevent pasting into textbox
                if (prevent_paste) {
                    my_txt_area.addEventListener('paste', e => e.preventDefault());
                }

                if (q_name === 'lvl2_q_catch') {
                    // if a catch question
                    let catch_resp = my_txt_area.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
                    jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
                }

                // Checkbox alert object
                let alert_el = document.getElementById('formAlert')

                // 'Rather not say' checkbox handling - hide/show the submit button and textarea text - including catch question handling
                na_check.addEventListener('change', function () {
                    currentUser_instance.last_checked = na_check.checked
                    let words_left = Number(document.getElementById("qs_words_left").innerText)
                    if (na_check.checked) { // when checked
                        na_check.disabled = true; // disable checkbox
                        submit_bttn.style.visibility = 'hidden'
                        alert_el.style.visibility = 'visible'
                        div_counter.style.visibility = "hidden"
                        my_txt_area.style["content-visibility"] = "hidden"
                        my_txt_area.style.background = `rgb(211, 211, 211, 0.5)`;
                        my_txt_area.readOnly = true
                        if (q_name === 'lvl2_q_catch') {
                            // if a catch question
                            let catch_resp = my_txt_area.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
                            jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
                        }

                        document.getElementById('close_alert').addEventListener('click', function (event) {
                            event.preventDefault()
                            na_check.checked = false;
                            na_check.disabled = false;
                            currentUser_instance.last_checked = na_check.checked

                            alert_el.style.visibility = 'hidden'
                            submit_bttn.style.visibility = 'visible'

                            my_txt_area.readOnly = false
                            my_txt_area.style["content-visibility"] = "visible"
                            my_txt_area.style.background = `rgb(255, 255, 255, 1)`;
                            div_counter.style.visibility = "hidden"
                            if (words_left > 0) {
                                submit_bttn.style.visibility = "hidden"
                                div_counter.style.visibility = "visible"
                                if (q_name === 'lvl2_q_catch') {
                                    let catch_resp = my_txt_area.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
                                    jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
                                    if (catch_resp) {
                                        submit_bttn.style.visibility = "visible"
                                        div_counter.style.visibility = "hidden"
                                    } else {
                                        submit_bttn.style.visibility = "hidden"
                                        div_counter.style.visibility = "visible"
                                    }
                                }
                            } else {
                                if (q_name === 'lvl2_q_catch') {
                                    let catch_resp = my_txt_area.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
                                    jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
                                }
                            }
                        });
                        document.getElementById('return_alert').addEventListener('click', (event) => {
                            event.preventDefault()
                            // na_check.disabled = false; // disable checkbox
                            alert_el.style.visibility = 'hidden'
                            submit_bttn.style.visibility = 'hidden'
                            // document.getElementById('jspsych-experiment').innerHTML = ''
                            jsPsych_instance.finishTrial()
                        });
                    } else {
                        my_txt_area.readOnly = false
                        my_txt_area.style["content-visibility"] = "visible"
                        my_txt_area.style.background = `rgb(255, 255, 255, 1)`;
                        if (words_left > 0) {
                            submit_bttn.style.visibility = "hidden"
                            div_counter.style.visibility = "visible"
                            if (q_name === 'lvl2_q_catch') {
                                let catch_resp = my_txt_area.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
                                jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
                                if (catch_resp) {
                                    submit_bttn.style.visibility = "visible"
                                    div_counter.style.visibility = "hidden"
                                } else {
                                    submit_bttn.style.visibility = "hidden"
                                    div_counter.style.visibility = "visible"
                                }
                            }
                        } else {
                            submit_bttn.style.visibility = "visible"
                            div_counter.style.visibility = "hidden"
                            if (q_name === 'lvl2_q_catch') {
                                let catch_resp = my_txt_area.value.replace(/\s+/g, ' ').trim() === lvl2_catch_ans
                                jsPsych_instance.data.addProperties({'lvl2_attention': catch_resp})
                            }
                        }
                    }
                })


                // Enable word counting
                my_txt_area.addEventListener('input', function () {
                    separateWords(my_txt_area, counter, div_counter, submit_bttn, q_name, jsPsych_instance);
                })
            }


        },
        on_finish: function (data) {
            // console.log(data)
            let q_name = qs_list[q_index]['name']
            let na_check = currentUser_instance.last_checked
            // return submission checkbox
            if (na_check) {
                // if rather not say, then ask to return submission
                if (no_skip) {
                    save_fn_user(auth_instance, currentUser_instance, {
                        completed: "Yes", returned: "Yes", code: 'RETURNED'
                    }).catch(() => {
                        document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    })
                    jsPsych_instance.abortExperiment(return_text)
                }
            } else {
                // check for timeout
                currentUser_instance.timeout_count += data['timeout'] * 1
                // console.log('timeout count: ', currentUser_instance.timeout_count)

                // check if empty response - count words
                let words = data['response'][q_name].replace(/\s\s+/g, ' ').split(" ")
                if (words.length > 0) {
                    if (words[words.length - 1] === " ") {
                        words.pop()
                    }
                    if (words[words.length - 1] === "") {
                        words.pop()
                    }
                }
                let n_words = words.length
                let empty_response = n_words < min_words

                // Attention check - adapt empty if attention check trial was correct
                if (q_name === 'lvl2_q_catch') {
                    let catch_resp = data['lvl2_attention']
                    if (catch_resp) {
                        currentUser_instance.attention_check1 = catch_resp * 1
                        empty_response = false
                    }
                    // if (catch_resp) {
                    //     console.log('Attention check passed')
                    // } else {
                    //     console.log('Attention check failed')
                    // }
                    save_fn_user(auth_instance, currentUser_instance, {lvl2_attention_check: catch_resp}).catch(() => {
                    })
                }

                currentUser_instance.empty_count += empty_response * 1
                // console.log('empty count: ', currentUser_instance.empty_count)

                // Process and save data
                // Create data objects for firebase
                let tmp_obj = {
                    ['responses_' + q_name]: data['response'],
                    ['is_empty_' + q_name]: empty_response, // ['na_checked_' + q_name]: na_check,
                }
                let tmp_obj_rt = {
                    ['rts_' + q_name]: data['rt'], ['timeout_' + q_name]: data['timeout'],
                }
                let tmp_obj_dump = {
                    ['z_dump_' + q_name]: data
                }

                // save responses
                save_fn(auth_instance, currentUser_instance, tmp_obj, 'questions', 'open_questions').catch(error => {
                    console.log('Issue saving data')
                    console.log(error)
                })

                // save reaction times
                save_fn(auth_instance, currentUser_instance, tmp_obj_rt, 'questions', 'open_questions_rts').catch(error => {
                    console.log('Issue saving data')
                    console.log(error)
                })
                // dump data
                save_fn(auth_instance, currentUser_instance, tmp_obj_dump, 'questions', 'open_questions_dump').catch(error => {
                    console.log('Issue saving data')
                    console.log(error)
                })
                save_fn_user(auth_instance, currentUser_instance, {
                    empty_count: currentUser_instance.empty_count, timeout_count: currentUser_instance.timeout_count
                }).catch(() => {
                })

                // count warn about timeouts or empty responses
                if (data['timeout'] || empty_response) {
                    currentUser_instance.warning_count += 1
                    save_fn_user(auth_instance, currentUser_instance, {warning_count: currentUser_instance.warning_count}).catch(() => {
                    })
                    if (currentUser_instance.warning_count > max_timeout && no_skip) {
                        save_fn_user(auth_instance, currentUser_instance, {
                            completed: "Yes", returned: "Yes", code: 'WARNED'
                        }).catch(() => {
                            document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                        jsPsych_instance.abortExperiment(return_timeout_text)

                    } else {
                        showAlert(jsPsych_instance, currentUser_instance)
                    }
                }
            }

        }

    }
}

// ----------------------------------------------------------

// ------------> Questionnaire trial function <---------------

function qsn_trial(preamble_text, question_array, duration, type_name, catch_name = null, catch_ans, auth_instance, save_fn, save_fn_user, currentUser_instance, jsPsych_instance) {
    return {
        type: jsPsychSurveyMultiChoice,
        confirm_if_empty: true,
        preamble: preamble_text,
        questions: question_array,
        button_label: lvl_x_question_button_label,
        trial_duration: (duration + qsn_preamble_duration + 2) * 1000,
        css_classes: ['qs_trial'],
        data: {
            type: type_name + '_qs',
        },
        on_load: function () {
            // console.log(form_el)
            if (!run_sim) {
                let preamble = document.getElementById("qs_preamble").clientHeight
                document.getElementsByClassName("qs_trial")[0].style.marginTop = (preamble * 1.025).toString() + 'px'
            }

            document.querySelectorAll("form p").forEach((item) => {
                item.addEventListener("click", () => {
                    let tmp_q = item.firstChild['data'].replace(/\D/g, '')
                    let obj_to_reset = document.querySelectorAll(`div[data-name=` + type_name + `_q${tmp_q}] input`)
                    obj_to_reset.forEach((item) => {
                        item.checked = false
                    })
                })
            })

            // start timer count down
            let time_display = document.querySelector('#qsn_time')
            let time_left = document.querySelector('#qsn_time_left')
            time_display.style.visibility = 'hidden'
            startTimer_sec(duration + qsn_preamble_duration, time_display, time_left, Math.min(qsn_duration_countdown, duration))


            // initialise checked property
            currentUser_instance.last_checked = false
            let na_check = document.getElementById("qs_preamble_na_check")

            na_check.addEventListener('keydown', function (event) {
                event.preventDefault();
            });

            let submit_bttn = document.getElementById('jspsych-survey-multi-choice-next')

            // hide submit button at the start
            // submit_bttn.style.visibility = "hidden"

            // Checkbox alert object
            let alert_el = document.getElementById('formAlert')
            let alert_q_list_el = document.getElementById('oq_list')
            na_check.addEventListener('change', function () {
                currentUser_instance.last_checked = na_check.checked

                if (na_check.checked) { // when checked
                    na_check.disabled = true; // disable checkbox
                    submit_bttn.style.visibility = 'hidden'
                    alert_el.style.visibility = 'visible'
                    alert_q_list_el.style.visibility = 'hidden'


                    document.getElementById('close_alert').addEventListener('click', function (event) {
                        event.preventDefault()
                        na_check.checked = false;
                        na_check.disabled = false;
                        currentUser_instance.last_checked = na_check.checked

                        alert_q_list_el.style.visibility = 'hidden'
                        alert_el.style.visibility = 'hidden'
                        submit_bttn.style.visibility = 'visible'
                    });
                    document.getElementById('return_alert').addEventListener('click', (event) => {
                        event.preventDefault()
                        // na_check.disabled = false; // disable checkbox
                        alert_q_list_el.style.visibility = 'hidden'
                        alert_el.style.visibility = 'hidden'
                        submit_bttn.style.visibility = 'hidden'
                        // document.getElementById('jspsych-experiment').innerHTML = ''
                        jsPsych_instance.finishTrial()
                    });

                }


            })


        },


        on_finish: function (data) {
            let na_check = currentUser_instance.last_checked
            // Process and save data
            let responses = data['response']
            // let any_empty = data['any_empty']
            let empty_return = data['empty_return']
            currentUser_instance.timeout_count += data['timeout'] * 1
            // console.log('timeout count:', currentUser_instance.timeout_count)
            currentUser_instance.empty_count += data['any_empty'] * 1
            // console.log('empty count: ', currentUser_instance.empty_count)
            if ((empty_return && !data['timeout']) || na_check) { // not full set of responses
                if (no_skip) {
                    save_fn_user(auth_instance, currentUser_instance, {
                        completed: "Yes", returned: "Yes", code: 'RETURNED'
                    }).catch(() => {
                        document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    })
                    jsPsych_instance.abortExperiment(return_text)
                }
                // if rather not say, then ask to return submission
            } else {
                // attention check
                if (catch_name !== null) {
                    let catch_resp = responses[catch_name] === catch_ans
                    if (catch_name === 'phq9_q_catch') {
                        currentUser_instance.attention_check2 = catch_resp * 1
                    }
                    save_fn_user(auth_instance, currentUser_instance, {[catch_name]: catch_resp}).catch(() => {
                    })
                    save_fn(auth_instance, currentUser_instance, {[catch_name]: catch_resp}, 'questions', type_name + '_questions').catch(() => {
                        console.log('Issue saving data')
                    })
                }

                let tmp_obj = {
                    responses: data['response'],
                    rt: data['rt'],
                    z_dump: data,
                    ['timeout_' + type_name]: data['timeout'],
                    ['is_empty_' + type_name]: data['any_empty']
                }
                save_fn(auth_instance, currentUser_instance, tmp_obj, 'questions', type_name + '_questions').catch(() => {
                    console.log('Issue saving data')
                })
                save_fn_user(auth_instance, currentUser_instance, {
                    empty_count: currentUser_instance.empty_count, timeout_count: currentUser_instance.timeout_count
                }).catch(() => {
                })

                if (data['timeout'] || data['any_empty']) {
                    currentUser_instance.warning_count += 1
                    save_fn_user(auth_instance, currentUser_instance, {warning_count: currentUser_instance.warning_count}).catch(() => {
                    })
                    if (currentUser_instance.warning_count > max_timeout && no_skip) {
                        save_fn_user(auth_instance, currentUser_instance, {
                            completed: "Yes", returned: "Yes", code: 'WARNED'
                        }).catch(() => {
                            document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                        jsPsych_instance.abortExperiment(return_timeout_text)

                    } else {
                        showAlert(jsPsych_instance, currentUser_instance)
                    }
                }
            }

        }
    }
}

// ----------------------------------------------------------

