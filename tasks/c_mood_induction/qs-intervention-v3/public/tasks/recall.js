// Word lists
let word_listA = ["VIGOROUS", "ENERGETIC", "LIVELY", "EXHAUSTED", "TIRED", "DRAINED", "JOYFUL", "DELIGHTED", "HAPPY", "UNHAPPY", "HOPELESS", "MISERABLE", "GENUINE", "WHOLESOME", "ETHICAL", "CORRUPT", "SLOPPY", "UNSAFE"]
// let word_listA = ["VIGOROUS", "EXHAUSTED"]
// let word_listA = ["VIGOROUS", "EXHAUSTED","HAPPY"]
let recall_time = 45// 45
let recall_preamble_text = "RECALL THE WORD LIST"
let recall_preamble = `<div id="type_audio_preamble">
        <h4>${recall_preamble_text}</h4></div>`

let recall_min_words = 0
// let recall_max_words = 12

let recall_instr_duration = 30
let recall_instr2_duration = 8
let recall_instr3_duration = 15


let recall_instr_text = `
    <div class="pre_trial_instr">
    <h3>Next, you will do a memory task.</h3>
    <h4>You will see a list of words, one by one. Try to memorise them as they appear.</h4>
        &#8213;
         <br>
         <br>
        <div id="story_instr_box">
        <p>You will then have to type as many words as you remember until the time runs out!</p>
         </div>
         <br>
    <p class="next_page"></p>
    </div>
`

let recall_instr_text2 = `
    <div class="pre_trial_instr">
    <h3>Again, look at the same words and then recall!</h3>
    <br>
    <p class="next_page"></p>
    </div>
`

let recall_instr_text3 = `
    <div class="pre_trial_instr">
    <h3>Recall the list of words you memorised before.</h3>
        &#8213;
         <br>
         <br>
        <div id="story_instr_box">
        <p>Type as many words as you remember until the time runs out!</p>
         </div>
         <br>
    <p class="next_page"></p>
    </div>
`

function recall_trials(jsPsych_instance, user_instance, save_fn_doc, save_fn_user, auth_instance, preamble_el, prompt_el, type_name, total_time_type, min_words, timepoint_colName, timepoint_docName = 'open_q') {
    let recall_trial = {
        type: jsPsychSurveyTextFast,
        preamble: preamble_el,
        do_countdown: true,
        // do_wordcount: true,
        questions: [{
            prompt: prompt_el,
            placeholder: 'Type a word from the list'
        }],
        css_classes: ['type_text', 'recall'],
        on_load: function () {
            if (prompt_el == '') {
                let type_cont_el = document.getElementById("type_cont")
                type_cont_el.style.marginTop = "-250px";
                // jspsych_el.style.marginTop = "none";
            }
            // let tmp_type_name = 'recall' + '_' + user_instance.count_type

            let time_start_trial = jsPsych_instance.getTotalTime() // get current time since start
            let data_first = null

            data_first = jsPsych_instance.data.get().filter({type: type_name}).first(1)
            let time_first = data_first.select('time_elapsed').values[0]
            if (time_first == null) {
                // if first trial
                user_instance.type_started = time_start_trial // time trial started
                user_instance.time_left = (total_time_type * 1000) // time left defined from argument
            }
            // console.log(user_instance.time_left)


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

            let submit_bttn = document.querySelector(`.type_text input[type="submit"]`)
            submit_bttn.style.visibility = 'hidden'

            // Responses and word counts
            let data_all = jsPsych_instance.data.get().filter({type: type_name, empty: false})
            let all_responses = data_all.select('response').values.map(element => element['Q0'])

            // counter_fn(all_responses.length, min_words, 46, 63)
        },
        on_finish: function () {
            // get and calc times
            let [time_left, time_diff, time_started, time_now] = get_time_left(jsPsych_instance, user_instance, type_name, total_time_type * 1000)
            user_instance.time_left = time_left

            // let tmp_type_name = 'recall' + '_' + user_instance.count_type
            let data_all = jsPsych_instance.data.get().filter({type: type_name, empty: false})
            let all_responses = data_all.select('response').values.map(element => element['Q0'])
            let all_rts_save = data_all.select('rt').values//.map(element => element['Q0'])
            if (all_responses.length <= 0 && time_left <= 0) {
                user_instance.warning_count += 1 // increase total warning count


                // Save null responses on timeout if not a single word
                save_fn_doc(auth_instance, user_instance, {
                    ['responses_' + type_name]: null,
                    ['rts_' + type_name]: null,
                    ['timeout_' + type_name]: true,
                }, timepoint_colName, timepoint_docName).catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                })

                if (user_instance.warning_count > max_timeout) {
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
                    showAlert(jsPsych_instance, user_instance)
                }
            }

            // If more than x words then terminate
            // if (all_responses.length >= recall_max_words) {
            //     save_fn_doc(auth_instance, user_instance, {
            //         ['responses_' + type_name]: all_responses,
            //         ['rts_' + type_name]: all_rts_save,
            //         ['timeout_' + type_name]: false,
            //     }, timepoint_colName, timepoint_docName).catch(() => {
            //         throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
            //         // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            //         // document.body.innerHTML = generic_error;
            //     })
            //     save_fn_user(auth_instance, user_instance, {
            //         recent_task: type_name
            //     }).catch(() => {
            //         throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
            //         // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            //     })
            //     jsPsych_instance.abortCurrentTimeline()
            // }

        },
        button_label: "",
        data: {
            type: function () {
                // return 'recall' + '_' + user_instance.count_type
                return type_name
            }
        },
        trial_duration: function () {
            if (user_instance.time_left === null) {
                return total_time_type * 1000 + (dur_buffer * 1000)
            } else {
                return user_instance.time_left + (dur_buffer * 1000)
            }
        }
    }

    return {
        timeline: [recall_trial],
        on_timeline_finish: function () {
            let data_all = jsPsych_instance.data.get().filter({type: type_name, empty: false})
            let all_responses = data_all.select('response').values.map(element => element['Q0'])
            let all_rts_save = data_all.select('rt').values//.map(element => element['Q0'])
            save_fn_doc(auth_instance, user_instance, {
                ['responses_' + type_name]: all_responses,
                ['rts_' + type_name]: all_rts_save,
                ['timeout_' + type_name]: false,
            }, timepoint_colName, timepoint_docName).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                // document.body.innerHTML = generic_error;
            })


            save_fn_user(auth_instance, user_instance, {
                recent_task: type_name
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })

        },
        loop_function: function () {
            let [time_left, time_diff, time_started, time_now] = get_time_left(jsPsych_instance, user_instance, type_name, total_time_type * 1000)
            let outcome = false
            // let tmp_type_name = type_name + '_' + user_instance.count_type
            if (time_left <= 0) {
            } else {
                outcome = true
            }
            return outcome
        }

    }

}


