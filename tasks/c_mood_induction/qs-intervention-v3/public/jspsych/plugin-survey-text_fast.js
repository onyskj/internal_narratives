var jsPsychSurveyTextFast = (function (jspsych) {
    'use strict';

    var _package = {
        name: "@jspsych/plugin-survey-text",
        version: "2.0.0",
        description: "a jspsych plugin for free response survey questions",
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
            directory: "packages/plugin-survey-text"
        },
        author: "Josh de Leeuw",
        license: "MIT",
        bugs: {
            url: "https://github.com/jspsych/jsPsych/issues"
        },
        homepage: "https://www.jspsych.org/latest/plugins/survey-text",
        peerDependencies: {
            jspsych: ">=7.1.0"
        },
        devDependencies: {
            "@jspsych/config": "^3.0.0",
            "@jspsych/test-utils": "^1.2.0"
        }
    };

    const info = {
        name: "survey-text",
        version: _package.version,
        parameters: {
            questions: {
                type: jspsych.ParameterType.COMPLEX,
                array: true,
                pretty_name: "Questions",
                default: undefined,
                nested: {
                    /** Question prompt. */
                    prompt: {
                        type: jspsych.ParameterType.HTML_STRING,
                        pretty_name: "Prompt",
                        default: undefined,
                    },
                    /** Placeholder text in the response text box. */
                    placeholder: {
                        type: jspsych.ParameterType.STRING,
                        pretty_name: "Placeholder",
                        default: "",
                    },
                    /** The number of rows for the response text box. */
                    rows: {
                        type: jspsych.ParameterType.INT,
                        pretty_name: "Rows",
                        default: 1,
                    },
                    /** The number of columns for the response text box. */
                    columns: {
                        type: jspsych.ParameterType.INT,
                        pretty_name: "Columns",
                        default: 40,
                    },
                    /** Whether or not a response to this question must be given in order to continue. */
                    required: {
                        type: jspsych.ParameterType.BOOL,
                        pretty_name: "Required",
                        default: false,
                    },
                    /** Name of the question in the trial data. If no name is given, the questions are named Q0, Q1, etc. */
                    name: {
                        type: jspsych.ParameterType.STRING,
                        pretty_name: "Question Name",
                        default: "",
                    },
                },
            },
            /** If true, the order of the questions in the 'questions' array will be randomized. */
            randomize_question_order: {
                type: jspsych.ParameterType.BOOL,
                pretty_name: "Randomize Question Order",
                default: false,
            },
            /** HTML-formatted string to display at top of the page above all of the questions. */
            preamble: {
                type: jspsych.ParameterType.HTML_STRING,
                pretty_name: "Preamble",
                default: null,
            },
            /** Label of the button to submit responses. */
            button_label: {
                type: jspsych.ParameterType.STRING,
                pretty_name: "Button label",
                default: "Continue",
            },
            do_countdown: {
                type: jspsych.ParameterType.BOOL,
                pretty_name: "Countdown on",
                default: false,
            },
            do_wordcount: {
                type: jspsych.ParameterType.BOOL,
                pretty_name: "Wordcount on",
                default: false,
            },
            alert_content: {
                type: jspsych.ParameterType.STRING,
                pretty_name: "Alert content",
                default: 'oq'
            },
            /** Setting this to true will enable browser auto-complete or auto-fill for the form. */
            autocomplete: {
                type: jspsych.ParameterType.BOOL,
                pretty_name: "Allow autocomplete",
                default: false,
            },
            /** How long to show trial */
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

    /**
     * **survey-text**
     *
     * jsPsych plugin for free text response survey questions
     *
     * @author Josh de Leeuw
     * @see {@link https://www.jspsych.org/plugins/jspsych-survey-text/ survey-text plugin documentation on jspsych.org}
     */
    class SurveyTextPlugin {
        constructor(jsPsych) {
            this.jsPsych = jsPsych;
        }

        trial(display_element, trial) {
            for (var i = 0; i < trial.questions.length; i++) {
                if (typeof trial.questions[i].rows == "undefined") {
                    trial.questions[i].rows = 1;
                }
            }
            for (var i = 0; i < trial.questions.length; i++) {
                if (typeof trial.questions[i].columns == "undefined") {
                    trial.questions[i].columns = 40;
                }
            }
            for (var i = 0; i < trial.questions.length; i++) {
                if (typeof trial.questions[i].value == "undefined") {
                    trial.questions[i].value = "";
                }
            }
            var html = "";

            html += `<div id="dim-overlay"></div>`

            // html+= `<button type="button" id="play_audio"></button>`

            // show preamble text
            if (trial.preamble !== null) {
                html +=
                    `<div id='type_cont'>`+
                    '<div id="jspsych-survey-text-preamble" class="jspsych-survey-text-preamble">' +
                    trial.preamble +
                    "</div>";
            }
            // start form
            if (trial.autocomplete) {
                html += '<form id="jspsych-survey-text-form">';
            } else {
                html += '<form id="jspsych-survey-text-form" autocomplete="off">';
            }
            // generate question order
            var question_order = [];
            for (var i = 0; i < trial.questions.length; i++) {
                question_order.push(i);
            }
            if (trial.randomize_question_order) {
                question_order = this.jsPsych.randomization.shuffle(question_order);
            }
            // add questions
            for (var i = 0; i < trial.questions.length; i++) {
                var question = trial.questions[question_order[i]];
                var question_index = question_order[i];
                html +=
                    '<div id="jspsych-survey-text-' +
                    question_index +
                    // '" class="jspsych-survey-text-question" style="margin: 2em 0em;">' + counter_code+counter_code2;
                    '" class="jspsych-survey-text-question" style="margin: 2em 0em;">';
                html += '<p class="jspsych-survey-text">' + question.prompt + "</p>";
                var autofocus = i == 0 ? "autofocus" : "";
                var req = question.required ? "required" : "";
                if (question.rows == 1) {
                    html +=
                        '<input type="text" id="input-' +
                        question_index +
                        '"  name="#jspsych-survey-text-response-' +
                        question_index +
                        '" data-name="' +
                        question.name +
                        '" size="' +
                        question.columns +
                        '" ' +
                        autofocus +
                        " " +
                        req +
                        ' placeholder="' +
                        question.placeholder +
                        '"></input>';
                } else {
                    html +=
                        '<textarea id="input-' +
                        question_index +
                        '" name="#jspsych-survey-text-response-' +
                        question_index +
                        '" data-name="' +
                        question.name +
                        '" cols="' +
                        question.columns +
                        '" rows="' +
                        question.rows +
                        '" ' +
                        autofocus +
                        " " +
                        req +
                        ' placeholder="' +
                        question.placeholder +
                        '"></textarea>';
                }
                html += "</div>";
            }
            if (trial.do_wordcount) {
                html += counter_code
            }
            // add submit button
            html +=
                '<input type="submit" id="jspsych-survey-text-next" class="jspsych-btn jspsych-survey-text " value="' +
                trial.button_label +
                '"></input>';
            html += "</form>";
            if (trial.do_countdown) {
                html += timer_code
            }

            html+='</div>'


            display_element.innerHTML = html;
            // Added alert by Jakub 09/10/24
            if (trial.alert_content == 'oq') {
                display_element.innerHTML += alert_content_oq
            } else {

                display_element.innerHTML += alert_content_instr
            }
            var startTime = performance.now();
            timerControl.trialStarted = startTime;
            // backup in case autofocus doesn't work
            display_element.querySelector("#input-" + question_order[0]).focus();

            display_element.querySelector("#jspsych-survey-text-form").addEventListener("keydown", (e) => {
                if (e.key === " " && document.activeElement.id === "input-0") {

                    // console.log('submitted!')
                    e.preventDefault();
                    // measure response time
                    var endTime = performance.now();
                    var response_time = Math.round(endTime - startTime);
                    // create object to hold responses
                    var question_data = {};
                    for (var index = 0; index < trial.questions.length; index++) {
                        var id = "Q" + index;
                        var q_element = document
                            .querySelector("#jspsych-survey-text-" + index)
                            .querySelector("textarea, input");
                        var val = q_element.value;
                        var name = q_element.attributes["data-name"].value;
                        if (name == "") {
                            name = id;
                        }
                        var obje = {};
                        // console.log('plugin val', val)
                        obje[name] = val;
                        Object.assign(question_data, obje);
                    }
                    // save data
                    var trialdata = {
                        rt: response_time,
                        response: question_data,
                        empty: false
                    };
                    let tmp_resp = question_data['Q0'].replace(/\s+/g, '').replace(/[^a-zA-Z]/g, '')
                    if (!tmp_resp == '') {

                        display_element.innerHTML = "";
                        this.jsPsych.pluginAPI.clearAllTimeouts();
                        // next trial
                        this.jsPsych.finishTrial(trialdata);
                    } else {
                        // console.log('empty!')
                        // console.log(tmp_resp);
                        trialdata['empty'] = true
                        display_element.innerHTML = "";
                        this.jsPsych.pluginAPI.clearAllTimeouts();
                        // next trial
                        this.jsPsych.finishTrial(trialdata);

                    }

                }

                // }
                // display_element.querySelector("#jspsych-survey-text-form").addEventListener("submit", (e) => {
            });

            /// Added by Jakub 28/03
            // if (!tmp_resp == '') {
            //
            //     display_element.innerHTML = "";
            //     this.jsPsych.pluginAPI.clearAllTimeouts();
            //     // next trial
            //     this.jsPsych.finishTrial(trialdata);
            // } else {
            //     console.log('empty!')
            //     console.log(tmp_resp);
            //     trialdata['empty'] = true
            //     display_element.innerHTML = "";
            //     this.jsPsych.pluginAPI.clearAllTimeouts();
            //     // next trial
            //     this.jsPsych.finishTrial(trialdata);
            // }

            const end_mine = () => {
                /// ONLY WORKS WHEN ONE QUESTION!!!! (FOR FIRST QUESTION)
                var q_element = document
                    .querySelector("#jspsych-survey-text-" + 0)
                    .querySelector("textarea, input");
                var tmp_resp = q_element.value;
                tmp_resp = tmp_resp.replace(/\s+/g, '').replace(/[^a-zA-Z]/g, '')
                // console.log('plugin val trial', tmp_resp)

                if (!tmp_resp == '') {
                    display_element.innerHTML = "";
                    this.jsPsych.pluginAPI.clearAllTimeouts();
                    // next trial
                    this.jsPsych.finishTrial({
                        rt: null,
                        response: {Q0: tmp_resp},
                        empty: false
                    });
                } else {
                    // console.log('empty!')
                    // console.log(tmp_resp);
                    // trialdata['empty'] = true
                    display_element.innerHTML = "";
                    this.jsPsych.pluginAPI.clearAllTimeouts();
                    // next trial
                    this.jsPsych.finishTrial({
                        rt: null,
                        response: {Q0: tmp_resp},
                        empty: true,
                    });
                }
            };

            let remainingTime = trial.trial_duration - (performance.now() - timerControl.trialStarted);
            timerControl.trialRemaining = remainingTime

            window.resumeTrialTimer = () => {
                timerControl.trialTimeout = this.jsPsych.pluginAPI.setTimeout(() => {
                    end_mine();
                }, timerControl.trialRemaining);
            }

            if (trial.trial_duration !== null) {
                // this.jsPsych.pluginAPI.setTimeout(() => {
                //         end_mine();
                //     },
                //     // display_element.innerHTML = "";
                //     // this.jsPsych.pluginAPI.clearAllTimeouts();
                //     trial.trial_duration);
                timerControl.trialTimeout = this.jsPsych.pluginAPI.setTimeout(() => {
                    end_mine();
                }, timerControl.trialRemaining);
                // }, remainingTime);
            }

            ////
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
            let rt = 1000;
            for (const q of trial.questions) {
                const name = q.name ? q.name : `Q${trial.questions.indexOf(q)}`;
                const ans_words = q.rows == 1
                    ? this.jsPsych.randomization.sampleExponential(0.25)
                    : this.jsPsych.randomization.randomInt(1, 10) * q.rows;
                question_data[name] = this.jsPsych.randomization.randomWords({
                    exactly: ans_words,
                    join: " ",
                });
                rt += this.jsPsych.randomization.sampleExGaussian(2000, 400, 0.004, true);
            }
            const default_data = {
                response: question_data,
                rt: rt,
            }
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
            const answers = Object.entries(data.response).map((x) => {
                return x[1];
            });
            // console.log(answers)
            for (let i = 0; i < answers.length; i++) {
                this.jsPsych.pluginAPI.fillTextInput(display_element.querySelector(`#input-${i}`), answers[i], ((data.rt - 1000) / answers.length) * (i + 1));
            }
            this.jsPsych.pluginAPI.clickTarget(display_element.querySelector("#jspsych-survey-text-next"), data.rt);
        }
    }

    SurveyTextPlugin.info = info;

    return SurveyTextPlugin;

})(jsPsychModule);
