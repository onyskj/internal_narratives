// List of emotional labels
// go emotions/jiazhou
var emotion_list = ["Admiration", "Amusement", "Anger", "Annoyance", "Approval", "Caring", "Confusion", "Curiosity", "Desire", "Disappointment", "Disapproval", "Disgust", "Embarrassment", "Excitement", "Fear", "Gratitude", "Grief", "Joy", "Love", "Nervousness", "Neutral", "Optimism", "Pride", "Realization", "Relief", "Remorse", "Sadness", "Surprise"]

// emotion question prompts
var emotion_prompt = `<div id='emo_prompt'><p><b>Which of the following emotions best describes what you are currently feeling?</b></p>
                                <p id="emo_subinstr">(Select all that apply)</p>
                                <p id='time_emotion_p'>You have <span id="time_emotion">` + emotion_duration + `</span> seconds left.<br></p>
                                ` + avoid_answer + `
                                </div>`

// function to create a trial
function emotion_trial(ref_q, save_fn, save_fn_user, auth_instance, currentUser_instance, jsPsych_instance) {
    return {
        type: jsPsychSurveyMultiSelect,
        trial_duration: (emotion_duration + 1) * 1000,
        css_classes: 'emotion_lab',
        questions: [{
            prompt: '',
            name: 'emotions_q_' + ref_q,
            options: emotion_list,
            required: false,
            horizontal: true,
        }],
        preamble: emotion_prompt,
        button_label: lvl_x_question_button_label,
        on_load: function () {
            currentUser_instance.last_checked = false

            // start countdown
            let time_display = document.querySelector('#time_emotion_p')
            let time_left = document.querySelector('#time_emotion')
            startTimer_sec(emotion_duration, time_display, time_left, emotion_duration)

            let label_buttons = document.getElementsByTagName("label")
            let submit_button = document.getElementsByTagName("button")
            submit_button[0].style.visibility = 'hidden'

            // handle selecting/unselecting
            let total_clicked = 0
            for (let label_el of label_buttons) {
                let input_el = label_el.childNodes[0]
                input_el.addEventListener('change', function () {
                    // console.log(label_buttons)
                    if (this.checked) {
                        total_clicked += 1
                        if (total_clicked > 0) {
                            submit_button[0].style.visibility = 'visible'
                        } else {
                            submit_button[0].style.visibility = 'hidden'
                        }
                        label_el.style.backgroundColor = '#eee'
                        if (this.value == 'None') {
                            total_clicked = 1
                            if (total_clicked > 0) {
                                submit_button[0].style.visibility = 'visible'
                            } else {
                                submit_button[0].style.visibility = 'hidden'
                            }
                            for (let label_el2 of label_buttons) {
                                let input_el2 = label_el2.childNodes[0]
                                if (input_el2.value !== 'None') {
                                    input_el2.checked = false
                                    label_el2.style.backgroundColor = 'white'
                                }
                            }
                        }
                        if (this.value !== 'None') {
                            for (let label_el2 of label_buttons) {
                                let input_el2 = label_el2.childNodes[0]
                                if (input_el2.value == 'None') {
                                    input_el2.checked = false
                                    label_el2.style.backgroundColor = 'white'
                                }
                            }
                        }
                    } else {
                        total_clicked += -1
                        if (total_clicked > 0) {
                            submit_button[0].style.visibility = 'visible'
                        } else {
                            submit_button[0].style.visibility = 'hidden'
                        }
                        label_el.style.backgroundColor = 'white'
                    }

                })
            }

            // na checkbox handling
            let na_check = document.getElementById("qs_preamble_na_check")

            // Prevent checking the checkbox with a key
            na_check.addEventListener('keydown', function (event) {
                event.preventDefault();
            });
            let alert_el = document.getElementById('formAlert')

            // hide/show labels if na-checkbox ticked
            na_check.addEventListener('change', function () {
                currentUser_instance.last_checked = na_check.checked
                if (na_check.checked) {
                    alert_el.style.visibility = 'visible'
                    na_check.disabled = true
                    submit_button[0].style.visibility = 'hidden'
                    // submit_button[0].innerHTML = return_button // change the button when no response is provided


                    document.getElementById('close_alert').addEventListener('click', (event) => {
                        event.preventDefault()
                        na_check.checked = false;
                        na_check.disabled = false;
                        currentUser_instance.last_checked = na_check.checked

                        alert_el.style.visibility = 'hidden'
                        // submit_button[0].value = lvl_x_question_button_label
                        submit_button[0].style.visibility = "hidden"

                        for (let label_el of label_buttons) {
                            let input_el = label_el.childNodes[0]
                            if (input_el.checked) {
                                submit_button[0].style.visibility = 'visible'
                                break
                            }
                        }
                    });

                    document.getElementById('return_alert').addEventListener('click', (event) => {
                        event.preventDefault()
                        alert_el.style.visibility = 'hidden'
                        submit_button[0].style.visibility = 'hidden'
                        document.getElementById('jspsych-experiment').innerHTML = ''
                        jsPsych_instance.finishTrial()
                    });

                } else {
                    submit_button[0].style.visibility = 'hidden'
                    // submit_button[0].innerHTML = lvl_x_question_button_label

                    // check whether emotions were selected before
                    for (let label_el of label_buttons) {
                        let input_el = label_el.childNodes[0]
                        if (input_el.checked) {
                            submit_button[0].style.visibility = 'visible'
                            break
                        }
                    }

                }
            })

        },
        on_finish: function (data) {
            currentUser_instance.timeout_count += data['timeout'] * 1
            // console.log('timeout count:', currentUser_instance.timeout_count)
            currentUser_instance.empty_count += data['is_empty'] * 1
            // console.log('empty count: ', currentUser_instance.empty_count)
            let na_check = currentUser_instance.last_checked
            // console.log(na_check)
            if (na_check) {
                data['rt'] = null
                if (no_skip) {
                    save_fn_user(auth_instance, currentUser_instance, {
                        completed: "Yes",
                        returned: "Yes",
                        code: 'RETURNED'
                    }).catch(() => {
                        document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    })
                    jsPsych_instance.abortExperiment(return_text)
                }
            } else {
                // Process and save data
                // Create data objects for firebase
                let tmp_obj = {
                    ['emotions_' + ref_q]: data['response']['emotions_q_' + ref_q],
                    // ['na_checked_emotions_' + ref_q]: na_check,
                    ['timeout_emotions_' + ref_q]: data['timeout'],
                    ['rts_emotions_' + ref_q]: data['rt'],
                    ['z_dump_emotions_' + ref_q]: data,
                    ['is_empty_emotions_' + ref_q]: data['is_empty']
                }

                // save responses
                save_fn(auth_instance, currentUser_instance, tmp_obj, 'questions', 'emotions').catch(error => {
                    console.log('Issue saving data')
                    console.log(error)
                })

                save_fn_user(auth_instance, currentUser_instance, {
                    empty_count: currentUser_instance.empty_count,
                    timeout_count: currentUser_instance.timeout_count
                }).catch(() => {
                })

                if (data['timeout'] || data['is_empty']) {
                    currentUser_instance.warning_count += 1
                    save_fn_user(auth_instance, currentUser_instance, {warning_count: currentUser_instance.warning_count}).catch(() => {
                    })
                    if (currentUser_instance.warning_count > max_timeout && no_skip) {
                        save_fn_user(auth_instance, currentUser_instance, {
                            completed: "Yes",
                            returned: "Yes",
                            code: 'WARNED'
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

