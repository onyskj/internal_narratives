/*
-------------------------------------------------
------------> Firebase setup <---------------
-------------------------------------------------
*/
// Import libraries
import {initializeApp} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";

import {
    // enableIndexedDbPersistence,
    // getFirestore,
    initializeFirestore,
    persistentLocalCache,
    persistentSingleTabManager,
    collection,
    doc,
    setDoc,
    updateDoc,
    getDoc
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js";
import {
    getAuth, signInAnonymously, onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js"
// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Load DB with enablde persistence - NEW - https://firebase.google.com/docs/firestore/manage-data/enable-offline
const db = initializeFirestore(app, {
    localCache: persistentLocalCache(/*settings*/{tabManager: persistentSingleTabManager()})
});

// Establish authentication
const auth = getAuth(app)
signInAnonymously(auth).catch(function (err) {
    let errorCode = err.code;
    let errorMessage = err.message;
    console.log(errorCode);
    console.log(errorMessage);
})

// Setup requisite objects
const currentUser = new User(uid)
const jsPsych = my_jsPsych_init();
let timeline = []

// Centralized error handling function
function handleFirestoreError(error, message = load_error) {
    console.error("Firestore error:", error);
    document.getElementById('jspsych-experiment').innerHTML = `
        <p>${message}</p>
        <button onclick="window.location.reload()">Refresh Page</button>
    `;
}

window.onerror = function (message, source, lineno, colno, error) {
    console.error("Global onerror caught:", {message, source, lineno, colno, error});
    handleFirestoreError(error);
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.textContent = `Status: Caught a synchronous error! Check the console. Message: ${message}`;
        statusElement.style.color = 'red';
    }
    // Return true to prevent default browser error logging
    return true;
};

window.addEventListener('unhandledrejection', function (event) {
    console.error("Global unhandledrejection caught:", event.reason);
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.textContent = `Status: Caught an unhandled async error! Check the console. Reason: ${event.reason}`;
        statusElement.style.color = 'orange';
    }
    // Prevent default browser logging of the rejection
    event.preventDefault();
})


// Sign in and Ensure UID is established
function waitForUserAuth(timeout) {
    let start = performance.now()
    return new Promise((resolve, reject) => {
        const unsubscribe = onAuthStateChanged(auth, user => {
            if (user) {
                currentUser.uid = user.uid;
                resolve(user.uid);
                unsubscribe(); // Clean up the subscription when done
            } else if (timeout && (performance.now() - start) >= timeout) {
                reject(new Error("Timeout while waiting for user authentication"));
            }
        });

        function waitForUid(resolve, reject) {
            if (currentUser.uid) {
                resolve(currentUser.uid);
            } else if (timeout && (performance.now() - start) >= timeout) {
                reject(new Error("Timeout while getting firebase UID"));
            } else {
                setTimeout(waitForUid.bind(this, resolve, reject), 30);
            }
        }

        waitForUid(resolve, reject);
    });
}

function get_code(currentUser_instance, code_name) {
    return new Promise((resolve, reject) => {
        let code = null
        if (do_online) {
            const unsubscribe = onAuthStateChanged(auth, async function (user) {
                try {
                    if (user) {
                        if (user.uid === currentUser_instance.uid) {
                            // const codeDoc = collection(db, 'codes')
                            const codeDoc = doc(collection(db, 'codes'), code_name);
                            const snap = await getDoc(codeDoc)
                            if (snap.exists()) {
                                code = snap.data()['code']
                                // console.log(code)
                            } else {
                                console.error('code not in data')
                            }
                            resolve(code);
                        } else {
                            console.log('\tuser ids dont match')
                            reject(new Error('User IDs do not match')); // Reject the promise with an error
                        }
                    } else {
                        console.log('\tuser signed out');
                        reject(new Error('User signed out')); // Reject the promise with an error
                    }
                } catch (error) {
                    console.error('\tError handling user document:', error);
                    reject(error)
                } finally {
                    unsubscribe()
                }
            })
        } else {
            // do nothing
            console.log('offline, no code')
            resolve()
        }
    })
}

// ===>>> CHECK CONSENT FUNCTION <<<=== //
function retrieve_user_values(currentUser_instance, variables) {
    // console.log('Retrieve consent')
    return new Promise((resolve, reject) => {
        const unsubscribe = onAuthStateChanged(auth, async function (user) {
            try {
                if (user) {
                    if (user.uid === currentUser_instance.uid) {
                        const subDoc = doc(collection(doc(collection(db, 'tasks'), firestore_task), 'subjects'), user.uid);
                        const snap = await getDoc(subDoc)
                        if (!Array.isArray(variables)) {
                            variables = [variables];
                        }
                        let return_object = {}
                        if (snap.exists()) {
                            for (let variable of variables) {
                                if (variable in snap.data()) {
                                    // console.log('var to retrieve: '+variable)
                                    // console.log('var value: '+snap.data()[variable])
                                    return_object[variable] = snap.data()[variable];
                                } else {
                                    console.log(variable + ' key not dataset')
                                    return_object[variable] = null
                                }
                            }
                            // console.log(snap.data())
                        }
                        resolve(return_object);
                    } else {
                        console.log('\tuser ids dont match')
                        reject(new Error('User IDs do not match')); // Reject the promise with an error
                    }
                } else {
                    console.log('\tuser signed out');
                    reject(new Error('User signed out')); // Reject the promise with an error
                }
            } catch (error) {
                console.error('\tError handling user document:', error);
                reject(error)
            } finally {
                unsubscribe()
            }

        })

    })
}

// ===>>> CREATE DATABASE ENTRY FOR THE USER <<<=== //
function create_user_db(currentUser_instance) {
    return new Promise((resolve, reject) => {
        const unsubscribe = onAuthStateChanged(auth, async function (user) {
            try {
                if (user) {
                    if (user.uid === currentUser_instance.uid) {
                        const subDoc = doc(collection(doc(collection(db, 'tasks'), firestore_task), 'subjects'), user.uid);
                        const snap = await getDoc(subDoc)
                        if (console_debug) {
                            console.log('sub exists: ', snap.exists())
                        }
                        if (!snap.exists()) {
                            await setDoc(subDoc, {
                                uid: currentUser_instance.uid,
                                PID: currentUser_instance.PID,
                                ST_ID: currentUser_instance.ST_ID,
                                SE_ID: currentUser_instance.SE_ID,
                                date: new Date().toLocaleDateString('en-GB'),
                                time: new Date().toLocaleTimeString('en-GB'),
                                completed: 'No',
                                returned: 'No',
                                consented: 'Yes',
                                feedback: '',
                                recent_task: 't_001',
                                warning_count: 0,
                                task_version: firestore_task
                            });
                            // Create empty docs to store data
                            await setDoc(doc(collection(subDoc, 'questions'), 'phq9_questions'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'gad7_questions'), {init: true})
                            // await setDoc(doc(collection(subDoc, 'questions'), 'ids30_questions'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'sds_questions'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'lvl1_closed_questions'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'lvl2_closed_questions'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'open_questions'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'open_questions_rts'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'open_questions_dump'), {init: true})
                            await setDoc(doc(collection(subDoc, 'questions'), 'emotions'), {init: true})
                        }
                        resolve()
                    } else {
                        console.log('user ids dont match')
                        reject(new Error('User IDs do not match or user signed out'));
                    }
                } else {
                    console.log('user signed out');
                    reject(new Error('User signed out'));
                }
            } catch (error) {
                console.error('Error creating user document:', error);
                reject(error)
            } finally {
                unsubscribe()
            }

        })
    })
}

// ===>>> CHECK IDS FOR THE USER <<<=== //
function check_user_db(currentUser_instance) {
    return new Promise((resolve, reject) => {
        return retrieve_user_values(currentUser_instance, ['PID', 'SE_ID', 'ST_ID']).then(user_values => {
            currentUser_instance.get_ids(jsPsych) // read URL params
            // compare IDs with database
            if (user_values.PID === currentUser_instance.PID && user_values.ST_ID === currentUser_instance.ST_ID && user_values.SE_ID === currentUser_instance.SE_ID) {
                // prolific IDs match
                resolve()
            } else {
                //Prolific ids dont match
                reject(new Error(prolific_ids_error));
            }
        }).catch((error) => {
            reject(error)
        })
    })
}

// ===>>> CONSENT AND COMPLETION CHECK FUNCTIONS <<<=== //
function check_consent() {
    return new Promise((resolve, reject) => {
        const confirmButton = document.getElementById('confirmButton');
        // Ensure the button is clicked
        if (confirmButton) {
            confirmButton.onclick = function () {
                let consentGiven
                if (quick_consent) {
                    consentGiven = document.getElementById('consent_checkbox1').checked
                } else {

                    consentGiven = document.getElementById('consent_checkbox1').checked && document.getElementById('consent_checkbox2').checked && document.getElementById('consent_checkbox3').checked && document.getElementById('consent_checkbox4').checked && document.getElementById('consent_checkbox5').checked && document.getElementById('consent_checkbox6').checked && document.getElementById('consent_checkbox7').checked
                }
                currentUser.consent = consentGiven
                // Assuming consent form is handled here
                if (consentGiven) {
                    currentUser.get_ids(jsPsych) // assign URL ids
                    // create a user
                    create_user_db(currentUser).then(() => {
                        // console.log('Consent given! Proceeding with experiment');
                        document.getElementById('jspsych-experiment').innerHTML = "";
                        resolve();
                    }).catch((error) => {
                        console.error('Error creating user db')
                        reject(error)
                    })
                } else {
                    if (confirm('Unfortunately, you will be unable to participate in this research study if you do not consent to the above. Thank you for your time.')) {
                        console.error('Consent not given')
                        reject(new Error(no_consent_error));
                    }
                }
            };
        } else {
            console.error('Consent button not found')
            reject(new Error('Consent button not found'));
        }
    })
}

function handleConsent() {
    return retrieve_user_values(currentUser, 'consented').then(user_values => {
        if (!user_values.consented || (user_values.consented !== 'Yes' && user_values.consented !== 'No')) {
            // First time visiting, display consent form
            const consentElement = document.getElementById('jspsych-experiment');
            if (consentElement) {
                consentElement.innerHTML = consent_content;
                return check_consent(); // Return the promise outcome from check_consent
            } else {
                console.error("Consent element not found")
                return Promise.reject(new Error("Consent element not found"));
            }
        } else {
            if (user_values.consented === 'Yes') {
                // function to retrieve the id and compare with PID etc
                return check_user_db(currentUser).then(() => {
                    console.log('Prolific IDs match')
                    return Promise.resolve(); // Consent already given
                }).catch((error) => {
                    console.error('Prolific IDs dont match')
                    return Promise.reject(error)
                })
            } else if (user_values.consented === 'No') {
                console.error('Not consented')
                return Promise.reject(new Error('Not consented'));

            } else {
                console.error('Consent status error')
                return Promise.reject(new Error('Consent status error'));
            }
        }
    }).catch((error) => {
        // console.error('Error in retrieving data in handleConsent:', error)
        return Promise.reject(error)
    });
}

function handleCompletion() {
    return retrieve_user_values(currentUser, 'completed').then(user_values => {
        if (!user_values.completed || (user_values.completed !== 'Yes' && user_values.completed !== 'No')) {
            console.error('Completion status loading error')
            return Promise.reject(new Error('Completion status loading error'));
        } else {
            if (user_values.completed === 'Yes') {
                console.error('Study already completed')
                return Promise.reject(new Error(study_completed_error));
            } else if (user_values.completed === 'No') {
                // Run the study
                console.log('Run the study')
                return Promise.resolve();
            } else {
                console.error('Completion status other error')
                return Promise.reject(new Error('Completion status other error'));
            }
        }
    }).catch((error) => {
        // console.error('Error in retrieving data in handlecompletion:', error)
        return Promise.reject(error)
    })
}

// Allows updating documents within subjects collections
function updateUserDoc(auth_instance, currentUser_instance, object, which_col, which_doc) {
    return new Promise((resolve, reject) => {
        if (do_online) {
            const unsubscribe = onAuthStateChanged(auth_instance, async function (user) {
                try {
                    if (user) {
                        if (user.uid === currentUser_instance.uid) {
                            const subDoc = doc(collection(doc(collection(doc(collection(db, 'tasks'), firestore_task), 'subjects'), user.uid), which_col), which_doc);
                            await updateDoc(subDoc, object);
                            resolve()
                        } else {
                            console.log('user ids dont match')
                            reject(new Error('User IDs do not match or user signed out'));
                        }
                    } else {
                        console.log('user signed out');
                        reject(new Error('User signed out'));
                        // return false
                    }
                } catch (error) {
                    console.error('Error saving data:', error);
                    reject(error)
                } finally {
                    unsubscribe()
                }
            });
        } else {
            // do nothing
            // console.log('offline')
            resolve()
            // return true
        }
    })
}

// Allows updating subject document field with arbitrary json object
function updateUser(auth_instance, currentUser_instance, object) {
    return new Promise((resolve, reject) => {
        if (do_online) {
            const unsubscribe = onAuthStateChanged(auth_instance, async function (user) {
                try {
                    if (user) {
                        if (user.uid === currentUser_instance.uid) {
                            const subDoc = doc(collection(doc(collection(db, 'tasks'), firestore_task), 'subjects'), user.uid);
                            await updateDoc(subDoc, object);
                            resolve()
                        } else {
                            console.log('user ids dont match')
                            reject(new Error('User IDs do not match or user signed out'));
                        }
                    } else {
                        console.log('user signed out');
                        reject(new Error('User signed out'));
                        // return false
                    }
                } catch (error) {
                    console.error('Error saving data:', error);
                    reject(error)
                } finally {
                    unsubscribe()
                }
            });
        } else {
            // do nothing
            console.log('offline')
            resolve()
            // return true
        }
    })
}

//
//------------> Study trials <---------------
//

let welcome_trial = {
    type: jsPsychHtmlKeyboardResponse,
    // trial_duration: debug_mode,
    post_trial_gap: 500,
    choices: ['n'],
    stimulus: welcome_text,
}


let instructions = {
    type: jsPsychInstructions,
    pages: instr_pages,
    show_clickable_nav: true,
    button_label_previous: 'Go to the previous page',
    button_label_next: 'Go to the next page',
    allow_keys: false,
    on_page_change: function (current_page) {
        let next_button_element = document.querySelector('button#jspsych-instructions-next')
        if (current_page === instr_pages.length - 1) {
            next_button_element.innerHTML = '<b style="color:red"><u>Start the experiment!</u></b>'
        }
    },
    show_page_number: true
}


let begin_study_trial = {
    type: jsPsychHtmlKeyboardResponse,
    // trial_duration: debug_mode,
    post_trial_gap: 500,
    choices: ['n'],
    stimulus: begin_study_text,
}

let begin_study_wait_trial = {
    type: jsPsychHtmlKeyboardResponse,
    trial_duration: 3000,
    post_trial_gap: 500,
    choices: ['NO_KEYS'],
    stimulus: begin_study_wait_text
}

let q_count = 0

// Level 1 - open questions
let lvl1_open_timeline_array = []
let q_max = lvl1_question_array.length
for (let i = 0; i < q_max; i++) {
    q_count += 1
    lvl1_open_timeline_array.push(question_trial(lvl1_question_array, i, q_count, updateUserDoc, updateUser, auth, currentUser, jsPsych))
}
let lvl1_open_timeline = {
    timeline: lvl1_open_timeline_array
}

// Level 1 - closed questions
let lvl1_closed_trial = qsn_trial(lvl1_closed_preamble, lvl1_closed_array, lvl1_closed_duration, 'lvl1_closed', null, null, auth, updateUserDoc, updateUser, currentUser, jsPsych)

// Level 2 - open questions
let lvl2_open_timeline_array = []
q_max = lvl2_question_array.length
for (let i = 0; i < q_max; i++) {
    q_count += 1
    lvl2_open_timeline_array.push(question_trial(lvl2_question_array, i, q_count, updateUserDoc, updateUser, auth, currentUser, jsPsych))
    if (lvl2_question_array[i].name === "lvl2_q1") {
        lvl2_open_timeline_array.push(emotion_trial(lvl2_question_array[i].name, updateUserDoc, updateUser, auth, currentUser, jsPsych))
    }
}
let lvl2_open_timeline = {
    timeline: lvl2_open_timeline_array
}

// Level 2 - closed questions
let lvl2_closed_trial = qsn_trial(lvl2_closed_preamble, lvl2_closed_array, lvl2_closed_duration, 'lvl2_closed', null, null, auth, updateUserDoc, updateUser, currentUser, jsPsych)

// Level 3 - open questions
let lvl3_open_timeline_array = []
q_max = lvl3_question_array.length
for (let i = 0; i < q_max; i++) {
    q_count += 1
    lvl3_open_timeline_array.push(question_trial(lvl3_question_array, i, q_count, updateUserDoc, updateUser, auth, currentUser, jsPsych))
    if (lvl3_question_array[i].name === "lvl3_q6") {
        lvl3_open_timeline_array.push(emotion_trial(lvl3_question_array[i].name, updateUserDoc, updateUser, auth, currentUser, jsPsych))
    }
}
let lvl3_open_timeline = {
    timeline: lvl3_open_timeline_array
}

// PHQ-9 trial
let phq9_trial = qsn_trial(phq9_preamble, phq9_question_array, phq9_duration, 'phq9', 'phq9_q_catch', phq9_catch_ans, auth, updateUserDoc, updateUser, currentUser, jsPsych)

// GAD-7 trial
let gad7_trial = qsn_trial(gad7_preamble, gad7_question_array, gad7_duration, 'gad7', null, null, auth, updateUserDoc, updateUser, currentUser, jsPsych)

// // IDS-30 trial
// let ids30_trial = qsn_trial(ids30_preamble, ids30_question_array, ids30_duration, 'ids30', null, null, auth, updateUserDoc, updateUser, currentUser, jsPsych)

// SDS trial
let sds_trial = qsn_trial(sds_preamble, sds_question_array, sds_duration, 'sds', null, null, auth, updateUserDoc, updateUser, currentUser, jsPsych)

// Repeated question from level 2
let rep_question_timeline_array = []
q_max = rep_question_array.length
for (let i = 0; i < q_max; i++) {
    q_count += 1
    rep_question_timeline_array.push(question_trial(rep_question_array, i, q_count, updateUserDoc, updateUser, auth, currentUser, jsPsych))
}
let rep_question_timeline = {
    timeline: rep_question_timeline_array,
}


// Thank study trial
let thanks_study_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: thanks_study_text,
    // trial_duration: 1000,
    choices: ['NO_KEYS'],
    data: {
        type: 'thanks'
    },
    // Save all data!
    on_load: function () {
        // Get data
        let data_json = jsPsych.data.get().json()
        let data_csv = jsPsych.data.get().csv()
        // let data_json = 'Saved - but change to actual data'
        // let data_csv = 'Saved - but change to actual data'

        // Attention checks
        currentUser.attention_check = currentUser.attention_check1 + currentUser.attention_check2

        // if (currentUser.attention_check >= attention_threshold) {
        //     console.log('Attention checks passed')
        // } else {
        //     console.log('Attention checks failed')
        // }

        // Check if closed responses are empty
        // let phq9_data = jsPsych.data.get().filter({type: 'phq9_qs'}).last()['trials'][0]['response']
        // let gad7_data = jsPsych.data.get().filter({type: 'gad7_qs'}).last()['trials'][0]['response']
        // let sds_data = jsPsych.data.get().filter({type: 'sds_qs'}).last()['trials'][0]['response']
        // let ids30_data = jsPsych.data.get().filter({type: 'ids30_qs'}).last()['trials'][0]['response']
        // let lvl1_closed_data = jsPsych.data.get().filter({type: 'lvl1_closed_qs'}).last()['trials'][0]['response']
        // let lvl2_closed_data = jsPsych.data.get().filter({type: 'lvl2_closed_qs'}).last()['trials'][0]['response']

        // let qsn_data_objects = [phq9_data, gad7_data, ids30_data, lvl1_closed_data, lvl2_closed_data]

        // let qsn_isEmpty = true
        // for (let qsn_data_object of qsn_data_objects) {
        //     for (let key in qsn_data_object) {
        //         qsn_isEmpty = qsn_isEmpty && qsn_data_object[key] === ""
        //     }
        // }
        // currentUser.empty_responses = qsn_isEmpty


        // Save data and other info
        console.log('Uploading data')
        updateUser(auth, currentUser, {
            // Upload data to Firebase
            attention_checks_total: currentUser.attention_check,
            attention_checks_bool: currentUser.attention_check >= attention_threshold,
            // qsn_empty: qsn_isEmpty,
            // phq9_empty: phq9_isEmpty,
            z_dump_json: data_json,
            z_dump_csv: data_csv,
            completed: "Yes"
        }).then(() => {
            // Finish this trial
            console.log('Data uploaded')
            console.log('Finishing the trial')
            jsPsych.finishTrial({
                attention_checks_total: currentUser.attention_check,
                attention_checks_bool: currentUser.attention_check >= attention_threshold,
                // qsn_empty: qsn_isEmpty,
            })
        }).catch(() => {
        })
    }
}

// End trials
let end_study_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: end_study_text,
    trial_duration: end_study_duration,
    choices: ['NO_KEYS'],
}

let trigger_end_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: trigger_text_end,
    choices: ['n'],
    data: {
        type: 'trigger'
    },
}

let feedback_trial = {
    type: jsPsychSurveyText,
    questions: [{
        prompt: 'If you wish, please provide us with any feedback about the study.',
        rows: 8,
        columns: 100,
        name:'Q0'
    }],
    button_label: 'Click here to finish and be redirected back to Prolific.',
    data: {
        type: 'feedback'
    },
    css_classes: ['feedback_trial'],
    trial_duration: (feedback_duration + 0) * 1000+ (dur_buffer * 1000),
    on_finish: function (data) {
        let feedback_content = data['response']['Q0']
        if (feedback_content) {
            updateUser(auth, currentUser, {feedback: feedback_content}).catch(() => {
            })
        }
    }
}

let redirect_prolific_trial = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: redirect_prolific_text,
    // trial_duration: 1000,
    choices: ['NO_KEYS'],
    on_load: function (data) {
        console.log(currentUser)
        if (!currentUser.empty_responses) {
            if (currentUser.attention_check) {
                // Completed the task successfully
                get_code(currentUser, 'completed').then(code => {
                    console.log('Exiting with completed code: ', code)
                    if (do_online) {
                        updateUser(auth, currentUser, {code: code}).then(() => {
                            window.location.href = base_url + code
                        }).catch(() => {
                        })
                    }
                }).catch(() => {
                })
            } else {
                // Failed the attention check threshold
                get_code(currentUser, 'failed_attention').then(code => {
                    console.log('Exiting with failed attention code: ', code)
                    if (do_online) {
                        updateUser(auth, currentUser, {code: code}).then(() => {
                            window.location.href = base_url + code
                        }).catch(() => {
                        })
                    }
                }).catch(() => {
                })
            }
        } else {
            // No Qs responses
            get_code(currentUser, 'no_responses').then(code => {
                console.log('Exiting with no responses code: ', code)
                if (do_online) {
                    updateUser(auth, currentUser, {code: code}).then(() => {
                        window.location.href = base_url + code
                    }).catch(() => {
                    })
                }
            }).catch(() => {
            })
        }
        jsPsych.finishTrial()
    }


}


// Run the study
function runStudy() {
    // Welcome trial
    timeline.push(welcome_trial) // <--------

    // Instructions timeline
    timeline.push(instructions) // <--------

    // Begin study
    // timeline.push(begin_study_trial) //
    // timeline.push(begin_study_wait_trial) //

    // Main study - Level 1 open-ended and closed questionnaires
    timeline.push(lvl1_open_timeline); // <--------
    timeline.push(lvl1_closed_trial); // <--------

    // Main study - Level 2 open-ended and closed questionnaires
    timeline.push(lvl2_open_timeline); // <--------
    timeline.push(lvl2_closed_trial); // <--------

    // Main study - Level 3 open-ended questionnaires
    timeline.push(lvl3_open_timeline); // <--------

    // Main study - PHQ-9 questionnaires
    timeline.push(phq9_trial) // <--------

    // Main study - GAD-7 questionnaires
    timeline.push(gad7_trial) // <--------

    // // Main study - IDS-30 questionnaires
    // timeline.push(ids30_trial) // <--------

    // Main study - SDS questionnaires
    timeline.push(sds_trial) // <--------

    // Repeated question
    timeline.push(rep_question_timeline); // <--------

    // End of study
    timeline.push(thanks_study_trial); // <--------
    timeline.push(end_study_trial); // <--------
    timeline.push(trigger_end_trial) // <--------
    timeline.push(feedback_trial) // <--------
    timeline.push(redirect_prolific_trial) // <--------

    if (run_sim) {
        jsPsych.simulate(timeline)
    } else {
        jsPsych.run(timeline);
    }
}

// Main promises - establish UID and consent then run study
document.addEventListener('DOMContentLoaded', async function () {

    const randomDelay = Math.floor(Math.random() * (load_exp_maxDelay - load_exp_minDelay + 1)) + load_exp_minDelay;

    console.log(`Delaying website load by ${randomDelay / 1000} seconds.`);
    document.body.innerHTML += website_loading

    await new Promise(resolve => setTimeout(resolve, randomDelay));
    // remove the loading element
    let load_el = document.getElementById("loading_web")
    if (load_el) {
        load_el.remove()
    }

    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        // Alert the user and do not display the consent form
        alert("Sorry, this experiment does not work on mobile devices");
        document.getElementById('jspsych-experiment').innerHTML = mobile_text

    } else {
        if (do_online) {
            waitForUserAuth().then(() => {
                // UID established
                console.log('User logged in')
                handleConsent().then(() => {
                    // Consent is given (either just now or in the past), now run the study
                    handleCompletion().then(() => {
                        // Study not completed yet
                        runStudy();
                    }).catch(error => {
                        console.error('Completion handling error:', error);
                        if (error.message === study_completed_error) {
                            // Handle when study already completed by the participant
                            document.getElementById('jspsych-experiment').innerHTML = completed_text;
                        } else {
                            document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        }
                    })
                }).catch(error => {
                    console.error('Consent handling error:', error);
                    // console.log(Error(no_consent_error))
                    if (error.message === no_consent_error) {
                        get_code(currentUser, 'no_consent').then(code => {
                            console.log('Exiting with no_consent code: ', code)
                            if (do_online) {
                                window.location.href = base_url + code
                            }
                        }).catch(() => {
                            document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        })
                    }
                    if (error.message === prolific_ids_error) {
                        // Prolific IDs don't match
                        document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    }
                    // Handle the error case, e.g., redirect to another page or display a message
                });
            }).catch(error => {
                console.error("Failed to initialize task config:", error);
            })
        } else {
            // offline version - just run the study
            runStudy();
        }
    }

});

