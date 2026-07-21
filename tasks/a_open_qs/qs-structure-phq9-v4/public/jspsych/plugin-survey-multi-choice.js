var jsPsychSurveyMultiChoice = (function (jspsych) {
    'use strict';

    var _package = {
        name: "@jspsych/plugin-survey-multi-choice",
        version: "2.0.0",
        description: "a jspsych plugin for multiple choice survey questions",
        type: "module",
        main: "dist/index.cjs",
        exports: {
            import: "./dist/index.js",
            require: "./dist/index.cjs"
        },
        typings: "dist/index.d.ts",
        unpkg: "dist/index.browser.min.js",
        files: [
            "src",
            "dist"
        ],
        source: "src/index.ts",
        scripts: {
            test: "jest",
            "test:watch": "npm test -- --watch",
            tsc: "tsc",
            build: "rollup --config",
            "build:watch": "npm run build -- --watch"
        },
        repository: {
            type: "git",
            url: "git+https://github.com/jspsych/jsPsych.git",
            directory: "packages/plugin-survey-multi-choice"
        },
        author: "Shane Martin",
        license: "MIT",
        bugs: {
            url: "https://github.com/jspsych/jsPsych/issues"
        },
        homepage: "https://www.jspsych.org/latest/plugins/survey-multi-choice",
        peerDependencies: {
            jspsych: ">=7.1.0"
        },
        devDependencies: {
            "@jspsych/config": "^3.0.0",
            "@jspsych/test-utils": "^1.2.0"
        }
    };

    const info = {
        name: "survey-multi-choice",
        version: _package.version,
        parameters: {
            questions: {
                type: jspsych.ParameterType.COMPLEX,
                array: true,
                nested: {
                    prompt: {
                        type: jspsych.ParameterType.HTML_STRING,
                        default: void 0
                    },
                    options: {
                        type: jspsych.ParameterType.STRING,
                        array: true,
                        default: void 0
                    },
                    required: {
                        type: jspsych.ParameterType.BOOL,
                        default: false
                    },
                    horizontal: {
                        type: jspsych.ParameterType.BOOL,
                        default: false
                    },
                    name: {
                        type: jspsych.ParameterType.STRING,
                        default: ""
                    }
                }
            },
            confirm_if_empty: {
                type: jspsych.ParameterType.BOOL,
                pretty_name: "Confirm if empty",
                default: false,
            },

            randomize_question_order: {
                type: jspsych.ParameterType.BOOL,
                default: false
            },
            preamble: {
                type: jspsych.ParameterType.HTML_STRING,
                default: null
            },
            button_label: {
                type: jspsych.ParameterType.STRING,
                default: "Continue"
            },
            autocomplete: {
                type: jspsych.ParameterType.BOOL,
                default: false
            },
            /**
             * How long to show trial before it ends.
             */
            trial_duration: {
                type: jspsych.ParameterType.INT,
                pretty_name: "Trial duration",
                default: null,
            },

        },
        data: {
            response: {
                type: jspsych.ParameterType.COMPLEX,
                nested: {
                    identifier: {
                        type: jspsych.ParameterType.STRING
                    },
                    response: {
                        type: jspsych.ParameterType.STRING | jspsych.ParameterType.INT | jspsych.ParameterType.FLOAT | jspsych.ParameterType.BOOL | jspsych.ParameterType.OBJECT
                    }
                }
            },
            rt: {
                type: jspsych.ParameterType.INT
            },
            question_order: {
                type: jspsych.ParameterType.INT,
                array: true
            }
        }
    };

    class SurveyMultiChoicePlugin {
        constructor(jsPsych) {
            this.jsPsych = jsPsych;
        }

        static info = info;

        trial(display_element, trial) {
            var plugin_id_name = "jspsych-survey-multi-choice";
            var html = "";
            html += '<style id="jspsych-survey-multi-choice-css">';
            html += ".jspsych-survey-multi-choice-question { margin-top: 2em; margin-bottom: 2em; text-align: left; }.jspsych-survey-multi-choice-text span.required {color: darkred;}.jspsych-survey-multi-choice-horizontal .jspsych-survey-multi-choice-text {  text-align: center;}.jspsych-survey-multi-choice-option { line-height: 2; }.jspsych-survey-multi-choice-horizontal .jspsych-survey-multi-choice-option {  display: inline-block;  margin-left: 1em;  margin-right: 1em;  vertical-align: top;}label.jspsych-survey-multi-choice-text input[type='radio'] {margin-right: 1em;}";
            html += "</style>";
            if (trial.preamble !== null) {
                html += '<div id="jspsych-survey-multi-choice-preamble" class="jspsych-survey-multi-choice-preamble">' + trial.preamble + "</div>";
            }
            if (trial.autocomplete) {
                html += '<form id="jspsych-survey-multi-choice-form">';
            } else {
                html += '<form id="jspsych-survey-multi-choice-form" autocomplete="off">';
            }
            var question_order = [];
            for (var i = 0; i < trial.questions.length; i++) {
                question_order.push(i);
            }
            if (trial.randomize_question_order) {
                question_order = this.jsPsych.randomization.shuffle(question_order);
            }
            for (var i = 0; i < trial.questions.length; i++) {
                var question = trial.questions[question_order[i]];
                var question_id = question_order[i];
                var question_classes = ["jspsych-survey-multi-choice-question"];
                if (question.horizontal) {
                    question_classes.push("jspsych-survey-multi-choice-horizontal");
                }
                html += '<div id="jspsych-survey-multi-choice-' + question_id + '" class="' + question_classes.join(" ") + '"  data-name="' + question.name + '">';
                html += '<p class="jspsych-survey-multi-choice-text survey-multi-choice">' + question.prompt;
                if (question.required) {
                    html += "<span class='required'>*</span>";
                }
                html += "</p>";
                for (var j = 0; j < question.options.length; j++) {
                    var option_id_name = "jspsych-survey-multi-choice-option-" + question_id + "-" + j;
                    var input_name = "jspsych-survey-multi-choice-response-" + question_id;
                    var input_id = "jspsych-survey-multi-choice-response-" + question_id + "-" + j;
                    var required_attr = question.required ? "required" : "";
                    html += '<div id="' + option_id_name + '" class="jspsych-survey-multi-choice-option">';
                    html += '<label class="jspsych-survey-multi-choice-text" for="' + input_id + '">';
                    html += '<input type="radio" name="' + input_name + '" id="' + input_id + '" value="' + question.options[j] + '" ' + required_attr + "></input>";
                    html += question.options[j] + "</label>";
                    html += "</div>";
                }
                html += "</div>";
            }
            html += '<input type="submit" id="' + plugin_id_name + '-next" class="' + plugin_id_name + ' jspsych-btn"' + (trial.button_label ? ' value="' + trial.button_label + '"' : "") + "></input>";
            html += "</form>";
            display_element.innerHTML = html;

            // Added alert by Jakub 09/10/24
            display_element.innerHTML += alert_content

            document.querySelector("form").addEventListener("submit", (event) => {
                event.preventDefault();
                var endTime = performance.now();
                var response_time = Math.round(endTime - startTime);
                var question_data = {};
                for (var i2 = 0; i2 < trial.questions.length; i2++) {
                    var match = display_element.querySelector("#jspsych-survey-multi-choice-" + i2);
                    var id = "Q" + i2;
                    var val;
                    if (match.querySelector("input[type=radio]:checked") !== null) {
                        val = match.querySelector("input[type=radio]:checked").value;
                    } else {
                        val = "";
                    }
                    var obje = {};
                    var name = id;
                    if (match.attributes["data-name"].value !== "") {
                        name = match.attributes["data-name"].value;
                    }
                    obje[name] = val;
                    Object.assign(question_data, obje);
                }
                var trial_data = {
                    rt: response_time,
                    response: question_data,
                    timeout: false, // Added by Jakub
                    any_empty: false, // Added by Jakub
                    empty_return: false, // Added by Jakub
                    question_order
                };

                // Added by Jakub
                if (trial.confirm_if_empty) {
                    let tmp_store_empty = []
                    for (let i = 0; i < trial.questions.length; i++) {
                        var question = trial.questions[question_order[i]];
                        var selected_option = trial_data["response"][question.name]
                        var q_no = i + 1//question['prompt'][0]
                        if (selected_option === "") {
                            tmp_store_empty.push(i + 1)
                        }
                    }
                    if (tmp_store_empty.length > 0) {
                        let missing_qs_el = document.getElementById('qsn_missing_qs')
                        let alert_el = document.getElementById('formAlert')
                        let submit_button = document.getElementById('jspsych-survey-multi-choice-next')
                        let alert_q_list_el = document.getElementById('oq_list')
                        let na_check = document.getElementById("qs_preamble_na_check")
                        submit_button.style.visibility = 'hidden'
                        alert_el.style.visibility = 'visible'
                        missing_qs_el.innerText = tmp_store_empty.join(", ")                            // let form_el = document.getElementsByClassName("jspsych-content-wrapper")[0]
                        alert_q_list_el.style.visibility = 'visible'
                        na_check.disabled = true; // disable checkbox

                        document.getElementById('close_alert').addEventListener('click', function (event) {
                            event.preventDefault()
                            alert_el.style.visibility = 'hidden'
                            alert_q_list_el.style.visibility = 'hidden'
                            submit_button.style.visibility = 'visible'
                            na_check.disabled = false; // disable checkbox
                        });
                        document.getElementById('return_alert').addEventListener('click', (event)=> {
                            event.preventDefault()
                            alert_el.style.visibility = 'hidden'
                            submit_button.style.visibility = 'hidden'
                            trial_data["any_empty"] = true
                            trial_data["empty_return"] = true
                            display_element.innerHTML = "";
                            this.jsPsych.pluginAPI.clearAllTimeouts();
                            this.jsPsych.finishTrial(trial_data);
                        });
                        // if (confirm('You left out the following question(s): ' + tmp_store_empty.join(", ") + '\n\nIt is very important to us to have a full set of answers. \n\nIf you are not comfortable answering these questions, please proceed with a return of your submission to Prolific.')) {
                        //     trial_data["any_empty"] = true
                        //     trial_data["empty_return"] = true
                        //     display_element.innerHTML = "";
                        //     this.jsPsych.pluginAPI.clearAllTimeouts();
                        //     this.jsPsych.finishTrial(trial_data);
                        // }
                    } else {
                        display_element.innerHTML = "";
                        this.jsPsych.pluginAPI.clearAllTimeouts();
                        this.jsPsych.finishTrial(trial_data);
                    }
                } else {
                    display_element.innerHTML = "";
                    this.jsPsych.pluginAPI.clearAllTimeouts();
                    this.jsPsych.finishTrial(trial_data);
                }
            });
            var startTime = performance.now();
            /***
             * Added by Jakub Onysk 03/10/2024
             */
            if (trial.trial_duration !== null) {
                this.jsPsych.pluginAPI.setTimeout(() => {
                    var question_data = {};
                    let tmp_store_empty = []
                    for (var i2 = 0; i2 < trial.questions.length; i2++) {
                        var match = display_element.querySelector("#jspsych-survey-multi-choice-" + i2);
                        var id = "Q" + i2;
                        var val;
                        if (match.querySelector("input[type=radio]:checked") !== null) {
                            val = match.querySelector("input[type=radio]:checked").value;
                        } else {
                            val = "";
                            tmp_store_empty.push(i2 + 1);
                        }
                        var obje = {};
                        var name = id;
                        if (match.attributes["data-name"].value !== "") {
                            name = match.attributes["data-name"].value;
                        }
                        obje[name] = val;
                        Object.assign(question_data, obje);
                    }
                    let any_empty = false
                    if (tmp_store_empty.length > 0) {
                        any_empty = true
                    }

                    display_element.innerHTML = "";
                    this.jsPsych.pluginAPI.clearAllTimeouts();
                    this.jsPsych.finishTrial({
                        rt: null,
                        response: question_data,
                        timeout: true,
                        any_empty: any_empty,
                        empty_return: false, // Added by Jakub
                        question_order
                    });
                }, trial.trial_duration);
            }


        }

        simulate(trial, simulation_mode, simulation_options, load_callback) {
            if (simulation_mode == "data-only") {
                load_callback();
                this.simulate_data_only(trial, simulation_options);
            }
            if (simulation_mode == "visual") {
                this.simulate_visual(trial, simulation_options, load_callback);
            }
        }

        create_simulation_data(trial, simulation_options) {
            const question_data = {};
            let rt = 1e3;
            for (const q of trial.questions) {
                const name = q.name ? q.name : `Q${trial.questions.indexOf(q)}`;
                question_data[name] = this.jsPsych.randomization.sampleWithoutReplacement(q.options, 1)[0];
                rt += this.jsPsych.randomization.sampleExGaussian(1500, 400, 1 / 200, true);
            }
            const default_data = {
                response: question_data,
                rt,
                question_order: trial.randomize_question_order ? this.jsPsych.randomization.shuffle([...Array(trial.questions.length).keys()]) : [...Array(trial.questions.length).keys()]
            };
            const data = this.jsPsych.pluginAPI.mergeSimulationData(default_data, simulation_options);
            this.jsPsych.pluginAPI.ensureSimulationDataConsistency(trial, data);
            return data;
        }

        simulate_data_only(trial, simulation_options) {
            const data = this.create_simulation_data(trial, simulation_options);
            this.jsPsych.finishTrial(data);
        }

        simulate_visual(trial, simulation_options, load_callback) {
            const data = this.create_simulation_data(trial, simulation_options);
            const display_element = this.jsPsych.getDisplayElement();
            this.trial(display_element, trial);
            load_callback();
            const answers = Object.entries(data.response);
            for (let i = 0; i < answers.length; i++) {
                this.jsPsych.pluginAPI.clickTarget(
                    display_element.querySelector(
                        `#jspsych-survey-multi-choice-response-${i}-${trial.questions[i].options.indexOf(
                            answers[i][1]
                        )}`
                    ),
                    (data.rt - 1e3) / answers.length * (i + 1)
                );
            }
            this.jsPsych.pluginAPI.clickTarget(
                display_element.querySelector("#jspsych-survey-multi-choice-next"),
                data.rt
            );
        }
    }

    return SurveyMultiChoicePlugin;

})(jsPsychModule);
