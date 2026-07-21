function type_trials(jsPsych_instance, user_instance, save_fn_doc, save_fn_user, auth_instance, preamble_el, prompt_el, type_name, total_time_type, min_words, timepoint_colName, timepoint_docName = 'open_q') {
    user_instance.word_limit_ok = false
    // user_instance.act_word_limit_ok = false
    let tmp_type_name = type_name
    let type_task = {
        type: jsPsychSurveyTextFast,
        preamble: preamble_el,
        do_countdown: true,
        alert_content: function () {
            if (type_name.includes('type_practice')) {
                return 'instr'
            } else {
                return 'oq'
            }
        },
        questions: [{
            prompt: prompt_el,
            placeholder: 'Type your next word'
        }],
        // css_classes: ['type_text', type_name],
        css_classes: ['type_text'],
        do_wordcount: true,
        on_load: function () {

            if (prompt_el == '') {
                let type_cont_el = document.getElementById("type_cont")
                type_cont_el.style.marginTop = "-250px";
                // jspsych_el.style.marginTop = "none";
            }
            // if (prompt_el == '') {
            //     let jspsych_el = document.getElementById("jspsych-content")
            //     console.log(jspsych_el)
            //     jspsych_el.style.marginTop = "100px";
            // }
            tmp_type_name = type_name + '_' + user_instance.count_type
            user_instance.do_submit = false // track whether user submitted
            let time_start_trial = jsPsych_instance.getTotalTime() // get current time since start
            let data_first = null

            data_first = jsPsych_instance.data.get().filter({type: tmp_type_name}).first(1)
            let time_first = data_first.select('time_elapsed').values[0]
            if (time_first == null) {
                // if first trial
                user_instance.type_started = time_start_trial // time trial started
                user_instance.time_left = (total_time_type * 1000) // time left defined from argument
            }


            // Countdown
            timer_fn(total_time_type, 99, 1, user_instance.time_left, 10)

            // Text area
            let my_txt_area = document.querySelector(".type_text #input-0")
            document.addEventListener('keypress', function () {
                // Enforce focus on textarea
                my_txt_area.focus()
            })
            document.addEventListener('click', function () {
                my_txt_area.focus()
            })
            my_txt_area.addEventListener('paste', e => e.preventDefault());
            my_txt_area.addEventListener('keypress', prevent_return)

            // Responses and word counts
            let data_all = jsPsych_instance.data.get().filter({type: tmp_type_name, empty: false})
            let all_responses = data_all.select('response').values

            // Submit button
            let submit_bttn = document.querySelector(`.type_text input[type="submit"]`)
            submit_bttn.disabled = true
            if (all_responses.length >= min_words) {
                submit_bttn.disabled = false
            }

            counter_fn(all_responses.length, min_words, 46, 63)

            submit_bttn.onclick = function () {
                // if user submit - track submission state and finish prsd aactice state
                user_instance.do_submit = true
                // user_instance.practice_type = false
                if (type_name.includes('recreate') || type_name === 'act' || type_name.includes('type_practice')) {
                    // if (type_name.includes('type_practice')) {
                    submit_bttn.style.visibility = 'hidden'
                }

                jsPsych_instance.finishTrial()
            }


        },
        on_finish: function (data) {
            // get and calc times
            let [time_left, time_diff, time_started, time_now] = get_time_left(jsPsych_instance, user_instance, type_name, total_time_type * 1000)
            user_instance.time_left = time_left


            if (user_instance.do_submit) {
                // if user submitted - abort the timeline - no more typing
                tmp_type_name = type_name + '_' + user_instance.count_type
                save_fn_user(auth_instance, user_instance, {
                    // recent_task: 'type_' + tmp_type_name
                    recent_task: tmp_type_name
                }).catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                    // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                })

                if (type_name.includes('type_practice')) {
                    // Practice trial

                    // get this timeline data
                    let data_all = jsPsych_instance.data.get().filter({type: tmp_type_name, empty: false})
                    let all_responses = data_all.select('response').values
                    let practice_array = practice_texts[type_name]
                    let last_n_words = all_responses.slice(-practice_array.length).map(value => value.Q0.toLowerCase())

                    let all_responses_save = data_all.select('response').values.map(element => element['Q0'])
                    let all_rts_save = data_all.select('rt').values//.map(element => element['Q0'])

                    // Save practice type when submitted - CORRECT or INCORRECT


                    if (last_n_words.toString() === practice_array.toString()) {
                        // Save practice type when submitted - CORRECT ONLY
                        save_fn_doc(auth_instance, user_instance, {
                            ['responses_' + type_name + '_ok']: all_responses_save,
                            ['rts_' + type_name + '_ok']: all_rts_save,
                            ['timeout_' + type_name + '_ok']: false,
                            ['submitted_' + type_name + '_ok']: true,
                            ['correct_' + type_name + '_ok']: true,
                        }, timepoint_colName, timepoint_docName).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                            // document.body.innerHTML = generic_error;
                        })
                        // Correct practice response
                        // user_instance.count_pr = 0
                    } else {
                        // Save practice type when submitted - INCORRECT ONLY
                        save_fn_doc(auth_instance, user_instance, {
                            ['responses_' + tmp_type_name]: all_responses_save,
                            ['rts_' + tmp_type_name]: all_rts_save,
                            ['timeout_' + tmp_type_name]: false,
                            ['submitted_' + tmp_type_name]: true,
                            ['correct_' + tmp_type_name]: false,
                            ['word_limit_ok_' + tmp_type_name]: true,
                        }, timepoint_colName, timepoint_docName).catch(() => {
                            // console.log('error')
                            throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                            // document.body.innerHTML = generic_error;
                        })
                        user_instance.do_submit = false
                        user_instance.count_type += 1


                        if (user_instance.count_type > max_timeout) {
                            // kick out
                            save_fn_user(auth_instance, user_instance, {
                                completed: "Yes",
                                returned: "Yes",
                                code: warned_code_pr,
                                warning_count_pr: user_instance.count_type
                            }).catch(() => {
                                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                            })
                            jsPsych_instance.abortExperiment(return_text_practice)
                        } else {
                            // warn
                            showAlertType(jsPsych_instance, user_instance)
                        }
                    }
                }

                if (!tmp_type_name.includes('_practice')) {
                    // Live version
                    let data_all = jsPsych_instance.data.get().filter({type: tmp_type_name, empty: false})
                    let all_responses_save = data_all.select('response').values.map(element => element['Q0'])
                    let all_rts_save = data_all.select('rt').values//.map(element => element['Q0'])
                    // console.log('saving to ', timepoint, tmp_doc_name, all_responses, all_rts, data_all)
                    save_fn_doc(auth_instance, user_instance, {
                        ['responses_' + tmp_type_name]: all_responses_save,
                        ['rts_' + tmp_type_name]: all_rts_save,
                        ['timeout_' + tmp_type_name]: false,
                        ['submitted_' + tmp_type_name]: true,
                        ['word_limit_ok_' + tmp_type_name]: true,
                    }, timepoint_colName, timepoint_docName).catch(() => {
                        // console.log('error')
                        throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        // document.body.innerHTML = generic_error;
                    })
                    user_instance.do_submit = false
                    user_instance.count_type += 1
                }
                // console.log('trial type name   pre abort', tmp_type_name)
                jsPsych_instance.abortCurrentTimeline()
            }
        },
        data: {
            type: function () {
                return type_name + '_' + user_instance.count_type
            }

        },
        button_label: "",
        // button_label: "Click here once you are happy with your response",
        trial_duration: function () {
            if (user_instance.time_left === null) {
                return total_time_type * 1000 + (dur_buffer * 1000)
            } else {
                return user_instance.time_left + (dur_buffer * 1000)
            }
        }

    }

    return {
        timeline: [type_task],
        on_timeline_finish: function (data) {
            // // get this timeline data
            if (prompt_el == '') {
                let jspsych_el = document.getElementById("jspsych-content")
                // console.log(jspsych_el)
                // jspsych_el.style.marginTop = "100px";
                jspsych_el.style.marginTop = "none";
            }
            if (type_name.includes('type_practice')) {
                // reset time
                user_instance.time_left = (practice_time * 1000)
            } else {
                user_instance.time_left = (total_time_type * 1000)
            }
        },
        loop_function: function () {
            let [time_left, time_diff, time_started, time_now] = get_time_left(jsPsych_instance, user_instance, type_name, total_time_type * 1000)
            let outcome = false
            tmp_type_name = type_name + '_' + user_instance.count_type
            if (time_left <= 0) {
                if (!type_name.includes('_practice')) {
                    user_instance.count_type += 1
                    // Live version
                    save_fn_user(auth_instance, user_instance, {
                        recent_task: 'type_' + tmp_type_name
                    }).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    })


                    // Check word limit for entry
                    let data_all = jsPsych_instance.data.get().filter({type: tmp_type_name, empty: false})
                    let all_responses_save = data_all.select('response').values.map(element => element['Q0'])
                    let all_rts_save = data_all.select('rt').values//.map(element => element['Q0'])

                    let all_responses = data_all.select('response').values
                    let all_responses_length = all_responses.length
                    if (all_responses_length >= min_words) {
                        user_instance.word_limit_ok = true
                    } else {
                        user_instance.word_limit_ok = false
                    }

                    // save responses anyway
                    save_fn_doc(auth_instance, user_instance, {
                        ['responses_' + tmp_type_name]: all_responses_save,
                        ['rts_' + tmp_type_name]: all_rts_save,
                        ['timeout_' + tmp_type_name]: true,
                        ['submitted_' + tmp_type_name]: false,
                        ['word_limit_ok_' + tmp_type_name]: user_instance.word_limit_ok
                    }, timepoint_colName, timepoint_docName).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                    })

                    if (!(user_instance.word_limit_ok || type_name === 'act')) {
                        // user_instance.empty_count += 1 // increase not-complete responses
                        user_instance.warning_count += 1 // increase total warning count
                    }


                    if (user_instance.warning_count > max_timeout && type_name !== 'act') {
                        // Reached timeout/missed response limit - kick out
                        // console.log("Bye!")
                        save_fn_user(auth_instance, user_instance, {
                            completed: "Yes",
                            returned: "Yes",
                            code: warned_code,
                            warning_count: user_instance.warning_count
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                        jsPsych_instance.abortExperiment(return_timeout_text)
                    } else {
                        if (user_instance.word_limit_ok || type_name === 'act') {
                            // console.log('enough words single')
                        } else {
                            // console.log('not enough words sngle')
                            showAlert(jsPsych_instance, user_instance)
                        }
                    }


                }


                if (type_name.includes('type_practice')) {
                    // Practice trial
                    // tmp_type_name = type_name + '_' + user_instance.count_type

                    save_fn_user(auth_instance, user_instance, {
                        recent_task: 'type_' + tmp_type_name
                    }).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    })

                    // get this timeline data
                    let data_all = jsPsych_instance.data.get().filter({type: tmp_type_name, empty: false})

                    let all_responses_save = data_all.select('response').values.map(element => element['Q0'])
                    let all_rts_save = data_all.select('rt').values//.map(element => element['Q0'])

                    let all_responses = data_all.select('response').values
                    let practice_array = practice_texts[type_name]
                    let last_n_words = all_responses.slice(-practice_array.length).map(value => value.Q0.toLowerCase())


                    // save regardless if correct or not
                    if (last_n_words.toString() === practice_array.toString()) {
                        // Correct practice response
                        save_fn_doc(auth_instance, user_instance, {
                            ['responses_' + type_name + '_ok']: all_responses_save,
                            ['rts_' + type_name + '_ok']: all_rts_save,
                            ['timeout_' + type_name + '_ok']: true,
                            ['submitted_' + type_name + '_ok']: false,
                            ['correct_' + type_name + '_ok']: true,
                        }, timepoint_colName, timepoint_docName).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                            // document.body.innerHTML = generic_error;
                        })
                        // console.log(practice_array, last_n_words)
                        // console.log('Match after submit but time run out!')
                        user_instance.do_submit = true
                    } else {
                        save_fn_doc(auth_instance, user_instance, {
                            ['responses_' + tmp_type_name]: all_responses_save,
                            ['rts_' + tmp_type_name]: all_rts_save,
                            ['timeout_' + tmp_type_name]: true,
                            ['submitted_' + tmp_type_name]: false,
                            ['correct_ok_' + tmp_type_name]: false,
                        }, timepoint_colName, timepoint_docName).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                        })
                        user_instance.do_submit = false
                        user_instance.count_type += 1
                        // console.log('added practice timeout count in the condition')

                        save_fn_user(auth_instance, user_instance, {
                            warning_count_pr: user_instance.count_type
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                        if (user_instance.count_type > max_timeout) {
                            // kick out
                            save_fn_user(auth_instance, user_instance, {
                                completed: "Yes",
                                returned: "Yes",
                                code: warned_code_pr,
                                warning_count_pr: user_instance.count_type
                            }).catch(() => {
                                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                            })
                            jsPsych_instance.abortExperiment(return_text_practice)
                        } else {
                            // warn
                            showAlertType(jsPsych_instance, user_instance)
                        }
                    }
                }


                // abort the timeline as time run out
                jsPsych_instance.abortCurrentTimeline()
            } else {
                outcome = true
            }
            return outcome

        }
    }

}

function get_time_left(jsPsych_instance, user_instance, type_name, total_time_type) {
    let time_now = jsPsych_instance.getTotalTime()
    // let data_first = jsPsych_instance.data.get().filter({type: type_name}).first(1)
    // let time_started = data_first.select('start_time').values[0]
    let time_started = user_instance.type_started
    // console.log(data_first)
    let time_diff = time_now - time_started
    // let time_left = total_time_type - time_diff ? Math.ceil((total_time_type - time_diff) / 1000) : Math.ceil(total_time_type / 1000)
    let time_left = Math.max(total_time_type - time_diff ? total_time_type - time_diff : total_time_type, 0)// Math.ceil((total_time_type - time_diff) / 1000) : Math.ceil(total_time_type / 1000)
    return [time_left, time_diff, time_started, time_now]
}

