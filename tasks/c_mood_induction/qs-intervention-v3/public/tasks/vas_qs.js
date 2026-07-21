// VAS Practice stuff
let vas_practice_instr = `
<div class="pre_trial_instr">
<h3>You will now practice responding to questions on a colour scale.</h3>
    <div id="story_instr_box"><p style="color:black">You can indicate your response by clicking anywhere on the scale.</p>
    </div>
    <br>
    <p class="next_page"></p>
</div>
`

let vas_pr_instr_duration = 15
let vas_pr_total_trial_duration = 15 // 15 vas practice duration


let vas_practice_preamble = `<div><h3><u>Please click anywhere you want (even between grey bars) on the colour scale.</u></h3>
                                </div>`
let vas_pr_label_list = ["A bit", "Somewhat", "Quite a lot", "Very much"]
let vas_practice_qs = [`Click as many times as you want and then submit your final response.`]

let vas_qs_trial = function (jsPsych_instance, user_instance,
                             save_fn_doc, save_fn_user, auth_instance, total_trial_duration, preamble_text = phq9_preamble_single, label_list = phq9_label_list, is_practice = false) {
    // if ('')
    // console.log(label_list)
    let is_vas_exp = label_list.length > 4
    let swr = 0.6
    if (is_vas_exp) {
        // swr = ((label_list.length / 4)*0.6)/1
        swr = .8
    } else {
        // let swr = 0.6
    }
    return {
        type: jsPsychHtmlVasResponse,
        preamble: preamble_text,
        stimulus: jsPsych_instance.timelineVariable('stimulus'),
        labels: jsPsych_instance.timelineVariable('label_list'),
        // labels: label_list,
        trial_duration: (total_trial_duration) * 1000 + (dur_buffer * 1000),
        // button_label: "Click here once you are happy with your response",
        // button_label: "Submit your response",
        button_label: "",
        do_countdown: true,
        scale_cursor: 'crosshair',
        marker_colour: '#333333',
        tick_colour: '#808080',
        scale_width: (window.innerWidth || document.documentElement.clientWidth ||
            document.body.clientWidth) * swr,
        label_size: 1.6,
        scale_height: 225,
        marker_width: 7,
        tick_width: 15,
        axis_height: 50,
        alert_content: function () {
            if (is_practice) {
                return 'pr'
            } else {
                return 'oq'
            }
        },
        resp_fcn: function (ppn, rt) {
            // console.log(ppn, rt)
            // user_instance.store_vas_loc.push(ppn)
            // user_instance.store_vas_rt.push(rt)
            // console.log(user_instance.store_vas_loc, user_instance.store_vas_rt)
        },
        on_load: function () {
            // user_instance.store_vas_loc = []
            // user_instance.store_vas_rt = []
            // let is_attn_check = jsPsych_instance.evaluateTimelineVariable('is_attn') // is attention check?
            // let is_live = !is_attn_check && !is_practice // check if live experiment and not att/practice

            user_instance.vas_pr_inrange = false // initialise if in range
            // user_instance.vas_pr_inrange = true // initialise if in range
            let stim_box = document.getElementById('jspsych-html-vas-response-stimulus')
            if (jsPsych_instance.evaluateTimelineVariable('index') % 2 === 0) {
                stim_box.style.background = 'rgb(211, 211, 211, 0.5)'
                stim_box.style.borderColor = '#319DD3'
            } else {
                stim_box.style.background = 'rgb(140,140,140,0.5)'
                stim_box.style.borderColor = '#425BD6'
            }
            // Countdown timer
            // timer_fn(total_trial_duration, 92.5, 50.5)
            timer_fn(total_trial_duration, 99, 1)

            // let button_el = document.getElementById("jspsych-html-vas-response-next")
            // handle na_check
            // na_return_check(jsPsych_instance, user_instance, button_el)


        },
        on_finish: function (data) {
            let rsp = data['response'] // final response
            let rsp_rt = data['rt'] // final response
            let q_index = jsPsych_instance.evaluateTimelineVariable('index').toString()
            let phq9_timepoint = data['type']
            let tmp_type_name = data['meta_type'] + '_' + phq9_timepoint + '_' + q_index
            let is_attn_check = jsPsych_instance.evaluateTimelineVariable('is_attn') // is attention check?
            let is_live = !is_attn_check && !is_practice // check if live experiment and not att/practice
            if (is_attn_check) {
                // if trial is attention check
                let catch_range = phq9_catch_ranges[phq9_timepoint]
                // console.log(catch_range)
                if (rsp !== null && rsp >= catch_range[0] && rsp <= catch_range[1]) {
                    // passed attention check
                    // console.log('attention check passed')
                    save_fn_doc(auth_instance, user_instance, {
                        ['is_empty_' + tmp_type_name + '_attnt']: rsp === null,
                        ['attnt_ok_' + tmp_type_name + '_attnt']: true,
                        // ['locs_all_' + tmp_type_name]: user_instance.store_vas_loc,
                        // ['rts_all_' + tmp_type_name]: user_instance.store_vas_rt,
                        ['response_' + tmp_type_name + '_attnt']: rsp,
                        ['rt_' + tmp_type_name + '_attnt']: rsp_rt,
                    }, phq9_timepoint, data['meta_type']).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        // document.body.innerHTML = generic_error;
                    })

                } else {
                    save_fn_doc(auth_instance, user_instance, {
                        ['is_empty_' + tmp_type_name + '_attnt']: rsp === null,
                        ['attnt_ok_' + tmp_type_name + '_attnt']: false,
                        // ['locs_all_' + tmp_type_name]: user_instance.store_vas_loc,
                        // ['rts_all_' + tmp_type_name]: user_instance.store_vas_rt,
                        ['response_' + tmp_type_name + '_attnt']: rsp,
                        ['rt_' + tmp_type_name + '_attnt']: rsp_rt,
                    }, phq9_timepoint, data['meta_type']).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        // document.body.innerHTML = generic_error;
                    })
                    // failed attention check
                    this.attention_check += 1
                    user_instance.attention_check += 1
                    if (data['type'] === 'baseline') {
                        this.attention_check1 = 1
                        user_instance.attention_check1 = 1
                        // console.log('attention check failed baseline')
                        save_fn_user(auth_instance, user_instance, {
                            ['attention_check1']: 1,
                            'attention_check': user_instance.attention_check
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                    }
                    if (data['type'] === 'fu') {
                        this.attention_check2 = 1
                        user_instance.attention_check2 = 1
                        save_fn_user(auth_instance, user_instance, {
                            ['attention_check2']: 1,
                            'attention_check': user_instance.attention_check
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                        // console.log('attention check failed fu')
                    }
                }
                save_fn_user(auth_instance, user_instance, {
                    recent_task: tmp_type_name + '_attnt',
                }).catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                    // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                })
            }

            if (!is_practice) {
                // Live task
                if (rsp === null) {

                    // No response provided
                    // user_instance.empty_count += 1 // increase not-complete responses
                    user_instance.warning_count += 1 // increase total warning count
                    if (user_instance.warning_count > max_timeout) {
                        // Reached timeout/missed response limit - kick out
                        // console.log("Bye!")
                        save_fn_user(auth_instance, user_instance, {
                            completed: "Yes",
                            returned: "Yes",
                            code: warned_code,
                            warning_count: user_instance.warning_count
                        }).catch(() => {
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                        })
                        jsPsych_instance.abortExperiment(return_timeout_text)
                    } else {
                        //
                        showAlert(jsPsych_instance, user_instance)
                    }
                }
                if (is_live) {
                    save_fn_doc(auth_instance, user_instance, {
                        ['is_empty_' + tmp_type_name]: rsp === null,
                        // ['locs_all_' + tmp_type_name]: user_instance.store_vas_loc,
                        // ['rts_all_' + tmp_type_name]: user_instance.store_vas_rt,
                        ['response_' + tmp_type_name]: rsp,
                        ['zclicks_' + tmp_type_name]: data['clicks'],
                        ['rt_' + tmp_type_name]: rsp_rt,
                    }, phq9_timepoint, data['meta_type']).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        // document.body.innerHTML = generic_error;
                    })
                    // Live and not attention check
                    // save_fn_doc(auth_instance, user_instance, {
                    //     ['is_empty_' + tmp_type_name]: true,
                    //     ['locs_all_' + tmp_type_name]: user_instance.store_vas_loc,
                    //     ['rts_all_' + tmp_type_name]: user_instance.store_vas_loc,
                    //     ['response_' + tmp_type_name]: rsp,
                    //     ['rt_' + tmp_type_name]: null,
                    //
                    // })

                    save_fn_user(auth_instance, user_instance, {
                        recent_task: tmp_type_name,
                    }).catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    })
                }

            }

            if (is_practice) {
                let tmp_type_name = data['meta_type'] + '_' + phq9_timepoint + '_' + q_index + '_' + user_instance.count_type
                save_fn_doc(auth_instance, user_instance, {
                    ['is_empty_' + tmp_type_name]: rsp === null,
                    // ['locs_all_' + tmp_type_name]: user_instance.store_vas_loc,
                    // ['rts_all_' + tmp_type_name]: user_instance.store_vas_rt,
                    ['response_' + tmp_type_name]: rsp,
                    ['rt_' + tmp_type_name]: rsp_rt,
                }, 'practice', 'vas').catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                    // console.log('error')
                    // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    // document.body.innerHTML = generic_error;
                })
                if (rsp === null) {
                    user_instance.count_type += 1
                    if (user_instance.count_type > max_timeout) {
                        save_fn_user(auth_instance, user_instance, {
                            completed: "Yes",
                            returned: "Yes",
                            code: warned_code_pr,
                            warning_count_pr: user_instance.count_type
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                            // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                        // kick out if reached a limit
                        jsPsych_instance.abortExperiment(return_text_practice)
                    } else {
                        // alert if timed out or wrong response
                        showAlertType(jsPsych_instance, user_instance)
                    }
                } else {
                    save_fn_doc(auth_instance, user_instance, {
                        ['is_empty_' + tmp_type_name + '_ok']: rsp === null,
                        // ['locs_all_' + tmp_type_name]: user_instance.store_vas_loc,
                        // ['rts_all_' + tmp_type_name]: user_instance.store_vas_rt,
                        ['response_' + tmp_type_name + '_ok']: rsp,
                        ['rt_' + tmp_type_name + '_ok']: rsp_rt,
                    }, 'practice', 'vas').catch(() => {
                        throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                        // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        // document.body.innerHTML = generic_error;
                    })
                    user_instance.vas_pr_inrange = true // initialise if in range

                }
                save_fn_user(auth_instance, user_instance, {
                    recent_task: tmp_type_name,
                }).catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                    // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                })
                // // practice trial
                // if (user_instance.count_type > max_timeout) {
                //     // kick out if reached a limit
                //     jsPsych_instance.abortExperiment(return_text_practice)
                // } else {
                //     // alert if timed out or wrong response
                //     showAlertType(jsPsych_instance, user_instance)
                // }
                // let rsp_range = vas_ans_range[jsPsych_instance.evaluateTimelineVariable('index')] // get acceptable range for the response
                // if (rsp !== null && rsp >= rsp_range[0] && rsp <= rsp_range[1]) {
                //     // is in required range - will break the loop function
                //     user_instance.vas_pr_inrange = true
                // } else {
                //     // not in range, increase counter and alert or kick out
                //     user_instance.vas_pr_inrange = false
                //     user_instance.count_type += 1
                //     if (user_instance.count_type > max_timeout) {
                //         // kick out if reached a limit
                //         jsPsych_instance.abortExperiment(return_text_practice)
                //     } else {
                //         // alert if timed out or wrong response
                //         showAlertType(jsPsych_instance, user_instance)
                //     }
                // }

            }
            // if (user_instance.last_checked && user_instance.do_return) {
            //     // if rather not say, then ask to return submission
            //     if (no_skip) {
            //         // save_fn_user(auth_instance, user_instance, {
            //         //     completed: "Yes", returned: "Yes", code: 'RETURNED'
            //         // }).catch(() => {
            //         //     document.getElementById('jspsych-experiment').innerHTML = generic_error;
            //         // })
            //         jsPsych_instance.abortExperiment(return_text)
            //     }
            // }
        },
        required: true,
    }
}

// Mood stuff
let mood_q_time = 18//18
let mood_preamble_duration = 2 //2
let mood_total_trial_duration = mood_q_time + mood_preamble_duration
let mood_pre_instr_duration = 10
// let mood_preamble_single = `
//     <div><h3><u>Reflect about yourself and answer the following question.</u></h3>
//     </div>
// `

let mood_preamble_single = ``
let mood_vas_question = ['How happy are you at this moment?']
// let mood_label_list = ["Very happy", "Quite happy", "A bit happy", "Neutral", "A bit unhappy", "Quite unhappy", "Very unhappy"]
let mood_label_list = ['Very unhappy', 'Quite unhappy', 'A bit unhappy', 'Neutral', 'A bit happy', 'Quite happy', 'Very happy']



let vas_practice_timeline = function (jsPsych_instance, user_instance, save_fn_doc, save_fn_user, auth_instance, i) {
    return {
        timeline: [vas_qs_trial(jsPsych_instance, user_instance, save_fn_doc, save_fn_user, auth_instance, vas_pr_total_trial_duration, vas_practice_preamble, vas_pr_label_list, true)],
        timeline_variables: [{stimulus: vas_practice_qs[i], index: i, is_attn: false, label_list: vas_pr_label_list}],
        loop_function: function () {
            return !user_instance.vas_pr_inrange;
        },
        on_timeline_start: function () {
            // user_instance.count_type = 0
        },
        data: {
            type: 'practice',
            meta_type: 'vas'
        }
    }
}
let experience_qs_preamble = `
    <div><h3><u>Reflect about the study and answer the following question.</u></h3>
    </div>
`
let experience_qs_duration = 20 //20
// let experience_qs = [
//     "How much were you able to put yourself in the other person's shoes after listening to their diary?",
//     "How easy did you find creating new diary entries?",
//     "After the diary tasks, I responded to questions about myself in a way that felt natural to me.",
//     "How much were you affected by the diary entries and the tasks relating to them?",
//     "How much did the diary entries and related tasks change your responses about yourself?",
//     "To what extent did the entries remind you of similar situations from your own life?",
//     "My responses to questions about myself were shaped by what I thought the researcher wanted to hear."
// ]
let experience_qs = [
    "I was able to put myself in the other person's shoes after listening to their diary entries.",
    "Listening to and recreating diary entries affected my mood.",
    "The diary entries reminded me of similar situations from my own life.",
    "Creating my own diary entry based on similar life experiences affected my mood.",
    "My responses to questions about myself were shaped by what I thought the researcher wanted to hear.",
    "Creating my own diary entry based on similar life experiences DID NOT affect mood.",
]

// let vas_exp_label_list = ["Not at all", "Slightly", "Somewhat", "Moderately", "Quite a lot", "Very much"]
let vas_exp_label_list = [
    // ["Not at all", "Slightly", "Somewhat", "Moderately", "Mostly", "Completely"],
    // ["Very Difficult", "Difficult", "Somewhat Difficult", "Somewhat Easy", "Easy", "Very Easy"],
    ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
    ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
    ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
    ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
    ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
    ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
    // ["Not at all", "Slightly", "Somewhat", "Moderately", "Mostly", "Completely"],
    // ["Not at all", "Slightly", "Somewhat", "Moderately", "Mostly", "Completely"],
    // ["Not at all", "Slightly", "Somewhat", "Moderately", "Mostly", "Completely"],
    // ["Strongly disagree", "Disagree", "Somewhat disagree", "Somewhat agree", "Agree", "Strongly agree"],
]
