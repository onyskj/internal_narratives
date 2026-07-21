/*
-------------------------------------------------
------------> Firebase setup <---------------
-------------------------------------------------
*/
// Import libraries
// import {initializeApp} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";
import {initializeApp} from "https://www.gstatic.com/firebasejs/11.5.0/firebase-app.js";

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
// } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js";
} from "https://www.gstatic.com/firebasejs/11.5.0/firebase-firestore.js";
import {
    getAuth, signInAnonymously, onAuthStateChanged
// } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js"
} from "https://www.gstatic.com/firebasejs/11.5.0/firebase-auth.js"

let currentUser;

const jsPsych = my_jsPsych_init();
// jsPsych.pluginAPI.audioContext().resume();

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

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Load DB with enablde persistence - NEW - https://firebase.google.com/docs/firestore/manage-data/enable-offline
const db = initializeFirestore(app, {
    localCache: persistentLocalCache(/*settings*/{tabManager: persistentSingleTabManager()})
});

function waitForUserAuth(authInstance, timeoutMs = 10000) { // Pass auth instance
    return new Promise((resolve, reject) => {
        let unsubscribe = () => {
        };
        let timeoutId = null;

        if (timeoutMs > 0) {
            timeoutId = setTimeout(() => {
                console.warn(`waitForUserAuth timed out after ${timeoutMs}ms.`);
                unsubscribe();
                reject(new Error(`Timeout waiting for user authentication (${timeoutMs}ms).`));
            }, timeoutMs);
        }

        try {
            unsubscribe = onAuthStateChanged(authInstance, // Use passed instance
                (user) => {
                    if (timeoutId) clearTimeout(timeoutId);
                    unsubscribe();
                    if (user) {
                        // console.log("waitForUserAuth: User confirmed with UID:", user.uid);
                        resolve(user.uid);
                    } else {
                        console.error("waitForUserAuth: No authenticated user found on initial check.");
                        reject(new Error("User authentication failed (no user)."));
                    }
                },
                (error) => { // Error callback for the listener
                    if (timeoutId) clearTimeout(timeoutId);
                    unsubscribe();
                    console.error("waitForUserAuth: Error within onAuthStateChanged listener:", error);
                    reject(new Error(`Authentication listener error: ${error.message}`));
                }
            );
        } catch (initialError) {
            if (timeoutId) clearTimeout(timeoutId);
            console.error("waitForUserAuth: Failed to set up onAuthStateChanged listener:", initialError);
            reject(new Error(`Failed to setup auth listener: ${initialError.message}`));
        }
    });
}


async function get_code(currentUser_instance, code_name) {
    // 1. Check if online operation is permitted
    if (!do_online) {
        // console.log(`Offline mode: Cannot retrieve code "${code_name}".`);
        // Return null explicitly when offline
        return null;
    }

    // 2. Get the currently authenticated user
    // const user = auth_instance.currentUser;

    // 3. Validate that *a* user is authenticated (needed to interact with Firestore generally,
    //    and potentially required by security rules for the /codes collection)
    // if (!user) {
    //     console.error(`Get code "${code_name}" failed: No user is currently signed in.`);
    //     throw new Error('User is not signed in.'); // Reject promise
    // }

    // REMOVED: Check against currentUser_instance.uid - not needed for fetching a general code.

    // 4. Perform the Firestore read using try/catch
    try {
        // Construct the document reference path
        const codeDocRef = doc(db, 'codes', code_name);

        // Log the attempt (optional)
        // console.log(`Attempting to retrieve code "${code_name}"...`);

        // Perform the read asynchronously
        const docSnap = await getDoc(codeDocRef);

        if (docSnap.exists()) {
            // Document exists, try to get the 'code' field
            const data = docSnap.data();
            // Safely check if the 'code' field exists
            if (data && Object.prototype.hasOwnProperty.call(data, 'code')) {
                // console.log(`Code "${code_name}" retrieved successfully.`);
                // Return the code value (resolves the promise)
                return data.code;
            } else {
                // Document exists, but 'code' field is missing
                console.error(`Document "codes/${code_name}" exists but is missing the 'code' field.`);
                // Resolve with null, as the specific code wasn't found
                return null;
            }
        } else {
            // Document does not exist
            console.error(`Code document "codes/${code_name}" not found.`);
            // Resolve with null, as the code document wasn't found
            return null;
        }

    } catch (error) {
        // Handle potential errors during the Firestore getDoc operation
        console.error(`Firestore read error for "codes/${code_name}":`, error);
        // Re-throw the error to ensure the promise is rejected
        throw new Error(`Failed to retrieve code "${code_name}": ${error.message}`);
    }


}

// ===>>> CHECK CONSENT FUNCTION <<<=== //
async function retrieve_user_values(currentUser_instance, auth_instance, variables) {
    // 1. Get the currently authenticated user
    const user = auth_instance.currentUser;

    // 2. Validate the authenticated user state
    if (!user) {
        console.error('Retrieve failed: No user is currently signed in.');
        throw new Error('User is not signed in.'); // Rejects the promise
    }

    // 3. Validate the provided currentUser_instance and UID match
    if (!currentUser_instance || !currentUser_instance.uid) {
        console.error('Retrieve failed: Invalid local user instance provided.');
        throw new Error('Invalid local user instance provided for retrieval.');
    }

    if (user.uid !== currentUser_instance.uid) {
        console.error(`Retrieve failed: User ID mismatch. Authenticated: ${user.uid}, Expected: ${currentUser_instance.uid}`);
        throw new Error('User ID mismatch during retrieval.'); // Rejects the promise
    }

    // 4. Ensure 'variables' is an array
    const fieldsToRetrieve = Array.isArray(variables) ? variables : [variables];
    const returnObject = {}; // Initialize the object to return

    // 5. Perform the Firestore read using try/catch
    try {
        // Construct the document reference (consider using a helper)
        const userDocRef = doc(db, 'tasks', firestore_task, 'subjects', user.uid);
        // const userDocRef = getUserDocRef(user.uid); // If using a helper

        // console.log(`Attempting to retrieve fields [${fieldsToRetrieve.join(', ')}] for UID: ${user.uid}`);
        const docSnap = await getDoc(userDocRef); // Use await to get the document snapshot

        if (docSnap.exists()) {
            // Document exists, get the data
            const data = docSnap.data();
            // console.log(`Document found for UID: ${user.uid}. Processing fields.`);
            for (const field of fieldsToRetrieve) {
                // Use hasOwnProperty for safer check than 'in'
                if (Object.prototype.hasOwnProperty.call(data, field)) {
                    returnObject[field] = data[field];
                } else {
                    // console.log(`Field "${field}" not found in document.`);
                    returnObject[field] = null; // Assign null if the field doesn't exist
                }
            }
        } else {
            // Document does not exist
            // console.log(`Document not found for UID: ${user.uid}. Returning null for all requested fields.`);
            for (const field of fieldsToRetrieve) {
                returnObject[field] = null; // Assign null for all requested fields
            }
        }

        // 6. Return the result object (implicitly resolves the promise)
        return returnObject;

    } catch (error) {
        // Handle potential errors during the Firestore getDoc operation
        console.error(`Firestore read error for UID ${user.uid}:`, error);
        // Re-throw the error to ensure the promise is rejected
        throw new Error(`Failed to retrieve user values: ${error.message}`);
    }

}

// ===>>> CREATE DATABASE ENTRY FOR THE USER <<<=== //

async function create_user_db(currentUser_instance) {
    if (!currentUser_instance || !currentUser_instance.uid) {
        console.error("create_user_db called with invalid currentUser_instance:", currentUser_instance);
        throw new Error("Invalid user data provided for DB creation.");
    }

    const userDocRef = doc(collection(doc(collection(db, 'tasks'), firestore_task), 'subjects'), currentUser_instance.uid);

    try {
        const snap = await getDoc(userDocRef);

        if (!snap.exists()) {
            // console.log(`Creating Firestore document for user: ${currentUser_instance.uid}`);
            await setDoc(userDocRef, {
                uid: currentUser_instance.uid,
                PID: currentUser_instance.PID,
                ST_ID: currentUser_instance.ST_ID,
                SE_ID: currentUser_instance.SE_ID,
                date: new Date().toLocaleDateString('en-GB'),
                time: new Date().toLocaleTimeString('en-GB'),
                condition: currentUser.cName,
                group: currentUser.gName,
                completed: 'No',
                returned: 'No',
                consented: 'Yes', // Set when creating doc after consent
                code: '',
                // feedback: '',
                recent_task: 'consent', // Or 'load' if called earlier? Check logic.
                warning_count: 0,
                warning_count_pr: 0,
                attention_check1: 0,
                attention_check2: 0,
                attention_check: 0,
                attention_checks_bool: null,
                task_version: firestore_task
            });

            // Create empty placeholder docs for sub-collections
            // console.log(`Creating sub-collection documents for user: ${currentUser_instance.uid}`);
            await setDoc(doc(collection(userDocRef, 'practice'), 'type1'), {init: true});
            // await setDoc(doc(collection(userDocRef, 'practice'), 'type2'), {init: true});
            await setDoc(doc(collection(userDocRef, 'practice'), 'vas'), {init: true});
            await setDoc(doc(collection(userDocRef, 'baseline'), 'phq9'), {init: true});
            await setDoc(doc(collection(userDocRef, 'baseline'), 'vas_mood'), {init: true});
            await setDoc(doc(collection(userDocRef, 'baseline'), 'open_q_mood'), {init: true});
            await setDoc(doc(collection(userDocRef, 'baseline'), 'open_q_energy'), {init: true});
            await setDoc(doc(collection(userDocRef, 'baseline'), 'recall'), {init: true});
            await setDoc(doc(collection(userDocRef, 'intervention'), 'recreate'), {init: true});
            await setDoc(doc(collection(userDocRef, 'intervention'), 'act'), {init: true});
            await setDoc(doc(collection(userDocRef, 'fu'), 'recall'), {init: true});
            await setDoc(doc(collection(userDocRef, 'fu'), 'phq9'), {init: true});
            await setDoc(doc(collection(userDocRef, 'fu'), 'vas_mood'), {init: true});
            await setDoc(doc(collection(userDocRef, 'fu'), 'open_q_pospert'), {init: true});
            await setDoc(doc(collection(userDocRef, 'feedback'), 'closed_q'), {init: true});
            // await setDoc(doc(collection(userDocRef, 'feedback'), 'open_q'), {init: true});
            // console.log(`User document and sub-collections created successfully for ${currentUser_instance.uid}.`);
        } else {
        }
        // No need to explicitly resolve, async function completion handles it.
    } catch (error) {
        console.error(`Error during Firestore user document check/creation for ${currentUser_instance.uid}:`, error);
        throw error; // Re-throw the error to be caught by the caller (e.g., handleConsent)
    }


}

// ===>>> CHECK IDS FOR THE USER <<<=== //
async function check_user_db(currentUser_instance, auth_instance) {

    if (!currentUser_instance) {
        throw new Error("check_user_db called with invalid currentUser_instance.");
    }
    try {
        // console.log(`Checking Prolific IDs for user: ${currentUser_instance.uid}`);
        // Assumes retrieve_user_values handles the case where the doc might not exist yet
        const user_values = await retrieve_user_values(currentUser_instance, auth_instance, ['PID', 'SE_ID', 'ST_ID']);

        // Get IDs from URL parameters (ensure this method exists and works)
        // This might need adjustment if jsPsych is not global or needed differently
        currentUser_instance.get_ids(jsPsych);

        // console.log("Comparing DB values:", user_values, "with URL params:", {
        //     PID: currentUser_instance.PID,
        //     ST_ID: currentUser_instance.ST_ID,
        //     SE_ID: currentUser_instance.SE_ID
        // });

        // Important: Check if user_values were actually found. If retrieve_user_values returns {} for non-existent doc, this check fails safely.
        if (user_values && user_values.PID === currentUser_instance.PID && user_values.ST_ID === currentUser_instance.ST_ID && user_values.SE_ID === currentUser_instance.SE_ID) {
            // if (user_values && ((user_values.PID === currentUser_instance.PID && user_values.ST_ID === currentUser_instance.ST_ID && user_values.SE_ID === currentUser_instance.SE_ID)) || allow_user_mismatch ) {
            // console.log(`Prolific IDs match for user: ${currentUser_instance.uid}`);
            // Resolve (implicitly by completing)
            return;
        } else {
            console.error(`Prolific ID mismatch for user: ${currentUser_instance.uid}. DB: ${JSON.stringify(user_values)}, URL: ${JSON.stringify({
                PID: currentUser_instance.PID,
                ST_ID: currentUser_instance.ST_ID,
                SE_ID: currentUser_instance.SE_ID
            })}`);
            throw new Error(prolific_ids_error); // Throw specific error for mismatch
        }
    } catch (error) {
        // If it's already the specific mismatch error, re-throw it.
        if (error.message === prolific_ids_error) {
            throw error;
        }
        // Otherwise, wrap or log a more general retrieval error
        console.error(`Error during Prolific ID check for user ${currentUser_instance.uid}:`, error);
        throw new Error(`Failed to verify user IDs: ${error.message}`); // Re-throw
    }

    // return new Promise((resolve, reject) => {
    //     return retrieve_user_values(currentUser_instance,auth_instance, ['PID', 'SE_ID', 'ST_ID']).then(user_values => {
    //         currentUser_instance.get_ids(jsPsych) // read URL params
    //         // compare IDs with database
    //         if (user_values.PID === currentUser_instance.PID && user_values.ST_ID === currentUser_instance.ST_ID && user_values.SE_ID === currentUser_instance.SE_ID) {
    //             // prolific IDs match
    //             resolve()
    //         } else {
    //             //Prolific ids dont match
    //             reject(new Error(prolific_ids_error));
    //         }
    //     }).catch((error) => {
    //         reject(error)
    //     })
    // })
}

// ===>>> CONSENT AND COMPLETION CHECK FUNCTIONS <<<=== //
async function check_consent(currentUser_instance) {
    return new Promise((resolve, reject) => {
        const confirmButton = document.getElementById('confirmButton');
        const consentElement = document.getElementById('jspsych-experiment');

        if (!confirmButton || !consentElement) {
            console.error('Consent button or container element not found in the DOM.');
            return reject(new Error('Consent UI elements missing.'));
        }

        // Ensure previous listeners are removed if this can be called multiple times
        confirmButton.replaceWith(confirmButton.cloneNode(true));
        const newConfirmButton = document.getElementById('confirmButton'); // Get the new button

        newConfirmButton.onclick = async () => { // Make the handler async
            try {
                let consentGiven;
                if (quick_consent) {
                    consentGiven = document.getElementById('consent_checkbox1')?.checked;
                } else {
                    consentGiven = document.getElementById('consent_checkbox1')?.checked &&
                        document.getElementById('consent_checkbox2')?.checked &&
                        document.getElementById('consent_checkbox3')?.checked &&
                        document.getElementById('consent_checkbox4')?.checked &&
                        document.getElementById('consent_checkbox5')?.checked &&
                        document.getElementById('consent_checkbox6')?.checked &&
                        document.getElementById('consent_checkbox7')?.checked;
                }

                currentUser_instance.consent = consentGiven; // Update instance property

                if (consentGiven) {
                    // console.log('Consent given via UI.');
                    currentUser_instance.get_ids(jsPsych); // Assign URL ids

                    // --- Call the async DB creation function ---
                    await create_user_db(currentUser_instance);
                    // console.log('User DB check/creation successful after consent.');

                    consentElement.innerHTML = ""; // Clear consent form
                    resolve(); // Consent given and user potentially created/verified in DB

                } else {
                    console.warn('Consent not given via UI.');
                    // Use confirm() for simple blocking dialog
                    if (confirm('Unfortunately, you will be unable to participate in this research study if you do not consent to the above. Thank you for your time.')) {
                        // User clicked OK on the confirm dialog, but consent still not given
                        reject(new Error(no_consent_error));
                    } else {
                        // User clicked Cancel - Allow them to re-check boxes.
                        // console.log('User chose to re-check consent boxes.');
                        // Do not reject. Allow the user to try again by not resolving or rejecting the promise
                    }
                }
            } catch (error) {
                // Catch errors from create_user_db or other issues within onclick
                console.error('Error during consent confirmation click:', error);
                // Display a generic error to the user within the consent area?
                consentElement.innerHTML = `<p style="color: red;">An error occurred while processing your consent. Please try again or contact support.</p> ${consent_content}`; // Restore form

                // Ensure button listener might need re-attaching if UI is rebuilt
                // Do not reject. Allow the user to try again by not resolving or rejecting the promise
            }
        }; // end of onclick
    }); // end of new Promise
}


async function handleConsent(user_instance, auth_instance) {
    if (!user_instance || !user_instance.uid) {
        throw new Error("handleConsent called with invalid user_instance.");
    }

    try {
        // console.log(`Handling consent for user: ${user_instance.uid}`);
        const user_values = await retrieve_user_values(user_instance, auth_instance, 'consented');
        const dbConsentStatus = user_values.consented; // Might be 'Yes', 'No', or undefined/null

        // console.log(`Retrieved consent status from DB: '${dbConsentStatus}'`);

        // Case 1: Consent status unknown or not set in DB (likely new user)
        if (dbConsentStatus !== 'Yes' && dbConsentStatus !== 'No') {
            // console.log("Consent status not found or invalid in DB. Displaying consent form.");
            const consentElement = document.getElementById('jspsych-experiment');
            if (consentElement) {
                consentElement.innerHTML = consent_content;
                // Wait for the UI interaction promise to resolve/reject
                await check_consent(user_instance);
                // console.log("Consent obtained via UI and user DB entry ensured.");
                // If check_consent_ui resolved, consent is 'Yes' implicitly now
                // No need to check IDs here, create_user_db was called by check_consent_ui
                return; // Consent handled successfully
            } else {
                console.error("Consent container element ('jspsych-experiment') not found.");
                throw new Error("UI Error: Consent form container missing.");
            }
        }
        // Case 2: Consent previously given ('Yes')
        else if (dbConsentStatus === 'Yes') {
            // console.log("Consent status is 'Yes' in DB. Verifying Prolific IDs.");
            // Verify Prolific IDs match the ones in the DB
            await check_user_db(user_instance, auth_instance); // Throws prolific_ids_error if mismatch
            // console.log("Prolific IDs verified successfully.");
            return; // Consent verified successfully
        }
        // Case 3: Consent previously denied ('No')
        else { // dbConsentStatus === 'No'
            console.warn(`User ${user_instance.uid} previously declined consent.`);
            throw new Error(no_consent_error); // Throw specific error for declined consent
        }

    } catch (error) {
        console.error(`Error during handleConsent for user ${user_instance.uid}:`, error.message);
        // Re-throw the error to be caught by the main try...catch
        // This includes no_consent_error, prolific_ids_error, and any Firestore errors
        throw error;
    }

}

async function handleCompletion(user_instance, auth_instance) {
    if (!user_instance || !user_instance.uid) {
        throw new Error("handleCompletion called with invalid user_instance.");
    }
    try {
        // console.log(`Checking completion status for user: ${user_instance.uid}`);
        const user_values = await retrieve_user_values(user_instance, auth_instance, 'completed');
        const completionStatus = user_values.completed; // Might be 'Yes', 'No', or undefined/null

        // console.log(`Retrieved completion status from DB: '${completionStatus}'`);

        // We expect 'No' or potentially undefined/null for an ongoing study.
        // If the document didn't exist, retrieve_user_values returns {}, so completionStatus is undefined.

        if ((completionStatus === 'Yes') && !allow_completed) {
            console.warn(`Study already marked as completed for user: ${user_instance.uid}.`);
            throw new Error(study_completed_error); // Throw specific error
        } else if (allow_completed || (completionStatus === 'No' || completionStatus === undefined || completionStatus === null)) {
            // Treat 'No', undefined, or null as not completed.
            // console.log(`Study not completed for user: ${user_instance.uid}. Proceeding.`);
            return; // Okay to proceed
        } else {
            // Unexpected value in 'completed' field
            console.error(`Unexpected completion status value ('${completionStatus}') for user: ${user_instance.uid}.`);
            throw new Error('Invalid completion status data in database.');
        }
    } catch (error) {
        // If it's already the specific completed error, re-throw it.
        if (error.message === study_completed_error) {
            throw error;
        }
        // Otherwise, log and re-throw a general error
        console.error(`Error during handleCompletion check for user ${user_instance.uid}:`, error);
        throw new Error(`Failed to check completion status: ${error.message}`); // Re-throw
    }
}


// Allows updating documents within subjects collections
async function updateUserDoc(auth_instance, currentUser_instance, object, which_col, which_doc) {
    // 1. Check if online operation is permitted
    if (!do_online) {
        // console.log(`Offline mode: Skipping Firestore update for ${which_col}/${which_doc}.`);
        return; // Resolve promise successfully with 'undefined'
    }
    // 2. Get the currently authenticated user
    const user = auth_instance.currentUser;

    // 3. Validate the authenticated user state
    if (!user) {
        console.error(`Update failed for ${which_col}/${which_doc}: No user is currently signed in.`);
        throw new Error('User is not signed in.'); // Reject promise
    }

    // 4. Validate the provided currentUser_instance and UID match
    if (!currentUser_instance || !currentUser_instance.uid) {
        console.error(`Update failed for ${which_col}/${which_doc}: Invalid local user instance provided.`);
        throw new Error('Invalid local user instance provided for update.');
    }

    if (user.uid !== currentUser_instance.uid) {
        console.error(`Update failed for ${which_col}/${which_doc}: User ID mismatch. Authenticated: ${user.uid}, Expected: ${currentUser_instance.uid}`);
        throw new Error('User ID mismatch.'); // Reject promise
    }

    // 5. Perform the Firestore update using try/catch
    try {
        // Construct the precise document reference path more clearly
        const userSubjectsCollection = collection(db, 'tasks', firestore_task, 'subjects');
        const userDoc = doc(userSubjectsCollection, user.uid);
        const targetSubcollection = collection(userDoc, which_col);
        const targetDocRef = doc(targetSubcollection, which_doc);

        // Log the attempt (optional)
        const docPath = `tasks/${firestore_task}/subjects/${user.uid}/${which_col}/${which_doc}`;
        // console.log(`Attempting to update document at path: ${docPath}`);

        // Perform the update asynchronously
        await updateDoc(targetDocRef, object);

        // Log success (optional)
        // console.log(`Successfully updated document at path: ${docPath}`);

        // If await completes without error, the promise resolves automatically.

    } catch (error) {
        // Handle potential errors during the Firestore operation
        const docPath = `tasks/${firestore_task}/subjects/${user.uid}/${which_col}/${which_doc}`;
        console.error(`Firestore update error for path ${docPath}:`, error);
        // Re-throw the error to ensure the promise is rejected
        throw new Error(`Failed to update sub-document ${which_col}/${which_doc}: ${error.message}`);
    }
}

// Allows updating subject document field with arbitrary json object
async function updateUser(auth_instance, currentUser_instance, object) {
    // 1. Check if online operation is permitted
    if (!do_online) {
        // console.log('Offline mode: Skipping Firestore update.');
        // In an async function, 'return' successfully resolves the promise (with 'undefined')
        return;
    }

    // 2. Get the currently authenticated user *now*
    const user = auth_instance.currentUser;

    // 3. Validate the authenticated user state
    if (!user) {
        console.error('Update failed: No user is currently signed in.');
        // Throwing an error automatically rejects the promise returned by the async function
        throw new Error('User is not signed in.');
    }
    // 4. Validate the provided currentUser_instance and UID match
    if (!currentUser_instance || !currentUser_instance.uid) {
        console.error('Update failed: Invalid local user instance provided.');
        throw new Error('Invalid local user instance provided for update.');
    }

    if (user.uid !== currentUser_instance.uid) {
        console.error(`Update failed: User ID mismatch. Authenticated: ${user.uid}, Expected: ${currentUser_instance.uid}`);
        throw new Error('User ID mismatch.');
    }
    try {
        // Construct the document reference
        // Consider using a helper function for this path if you use it often
        const userDocRef = doc(db, 'tasks', firestore_task, 'subjects', user.uid);

        // Log the attempt (optional)
        // console.log(`Attempting to update document for UID: ${user.uid}`);

        // Perform the update asynchronously
        await updateDoc(userDocRef, object);

        // Log success (optional)
        // console.log(`Successfully updated document for UID: ${user.uid}`);

        // If await updateDoc completes without error, the promise resolves automatically.
        // No explicit 'resolve()' needed.

    } catch (error) {
        // Handle potential errors during the Firestore operation
        console.error('Firestore update error:', error);
        // Re-throw the error (or a new one) to ensure the promise is rejected
        throw new Error(`Failed to update user data in Firestore: ${error.message}`);
    }


}

// Run the study
function runStudy(user_instance, auth_instance) {
    // <===== Welcome

    // uppdate full screen behaviour
    jsPsych['options']['on_interaction_data_update'] = function (data) {
        let trial_type = jsPsych.getCurrentTrial().type.name
        // console.log(trial_type)
        if (data.event == 'fullscreenexit' && should_be_in_fullscreen) {
            // Pause experiment
            jsPsych.pauseExperiment();
            window.isPaused = true;
            user_instance.count_fs += 1
            // jsPsych.count_fs += 1
            // console.log('fs counter: ', jsPsych.count_fs)
            // console.log('fs counter: ', user_instance.count_fs)

            if (timerControl.alertActivated) {
                // pause the timeout timer - happens after other trials are killedj
                clearTimeout(timerControl.trialTimeoutAlert);
            } else { // pause other stuff
                // pause audio
                if (trial_type === 'AudioKeyboardResponsePlugin') {
                    var context = jsPsych.pluginAPI.audioContext();
                    context.suspend()
                }

                // pause keyboard listener
                if (trial_type === 'HtmlKeyboardResponsePlugin') {
                    jsPsych.pluginAPI.cancelAllKeyboardResponses(); // disables the current key listener

                }

                // pause trial timer in the plugin
                if (trial_type === 'HtmlKeyboardResponsePlugin' || trial_type === 'SurveyTextPlugin' || trial_type === "HtmlButtonResponsePlugin" || trial_type === "jsPsychHtmlVasResponsePlugin") {
                    clearTimeout(timerControl.trialTimeout);
                }

                // disable submit button in typing
                if (trial_type === 'SurveyTextPlugin') {
                    let form_el = document.getElementById("input-0")
                    if (form_el) {
                        form_el.disabled = true;
                    }
                }

                // pause countdown timer animated
                if (!(trial_type === 'InstructionsPlugin' || trial_type === 'AudioKeyboardResponsePlugin' || timerControl.noTimer)) {
                    // if (!(trial_type == 'InstructionsPlugin' || trial_type === 'AudioKeyboardResponsePlugin')) {
                    // if (trial_type !== 'InstructionsPlugin') {
                    pauseTimer()
                }

            }


            // create alert
            let fs_alert = `<div class ='fsAlert', id="fullScreenAlert" style="font-weight: bold; width:100%; height: 100%">
                        <p>Please remain in fullscreen mode during the task.</p>`

            if (user_instance.count_fs === max_fs) {
                fs_alert += `
                            <br>
                            <p>You exited full-screen mode for the second time. This is your last warning.</p>
                            <p>It's very important to complete the study in the full-screen mode.</p>
                            <p>Next time you will be asked to return your submission.</p>`
            }
            fs_alert += `
                    <br><p>When you click the button below, you will enter fullscreen mode.</p>
                    <button id="jspsych-fullscreen-btn" class="jspsych-btn">Continue</button>
                    ${trigger_text_fs}
                        </div>`


            // kickout if over the limit
            if (user_instance.count_fs > max_fs) {
                document.getElementById('jspsych-experiment').innerHTML = '';
                updateUser(auth_instance, user_instance, {
                    completed: "Yes", returned: "Yes", code: warned_code_fs
                }).catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                    // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                })
                jsPsych.abortExperiment(return_text_fs)
                // console.log('Kick out!')
                return
            }


            let current_Alertode = document.getElementById('customAlert') // save a custom alert if exists
            if (current_Alertode) {
                current_Alertode = current_Alertode.cloneNode(true)
            }

            // add full-screen alert
            document.getElementById('jspsych-experiment').innerHTML = fs_alert

            // show full screen alert box
            let fs_alertBox = document.getElementById("fullScreenAlert");
            fs_alertBox.style.display = "block";  // Show the alert box


            document.querySelector('#jspsych-fullscreen-btn').addEventListener('click', function () {
                if (timerControl.alertActivated) {
                    // case when there was a timeout alert displayed
                    window.isPaused = false;
                    document.getElementById('jspsych-experiment').innerHTML = ''
                    document.getElementById('jspsych-experiment').appendChild(current_Alertode)
                    window.resumeTrialTimerAlert()
                    // window.resumeTrialTimer()
                } else {
                    // case during trial
                    jsPsych.resumeExperiment()
                    window.isPaused = false;

                    // resume audio
                    if (trial_type === 'AudioKeyboardResponsePlugin') {
                        context.resume()
                    }

                    if (trial_type === 'HtmlKeyboardResponsePlugin' || trial_type === 'SurveyTextPlugin' || trial_type === "HtmlButtonResponsePlugin" || trial_type === "jsPsychHtmlVasResponsePlugin") {
                        // resume trial timer in the plugin
                        window.resumeTrialTimer()
                    }
                    if (trial_type === 'HtmlKeyboardResponsePlugin') {
                        // resume keyboard listener
                        window.resumeKeyListener();  //safely restarts listener
                    }
                    if (trial_type === 'SurveyTextPlugin') {
                        let form_el = document.getElementById("input-0")
                        if (form_el) {
                            form_el.disabled = false;
                        }

                    }

                    // resume countdown timer
                    if (!(trial_type === 'InstructionsPlugin' || trial_type === 'AudioKeyboardResponsePlugin' || timerControl.noTimer)) {
                        resumeTimer()
                    }
                    fs_alertBox.style.display = "none";
                }


                var element = document.documentElement;
                if (element.requestFullscreen) {
                    element.requestFullscreen();
                } else if (element.mozRequestFullScreen) {
                    element.mozRequestFullScreen();
                } else if (element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if (element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }

            })

        }
    }

    let preload_files = {
        type: jsPsychPreload,
        images: images,
        audio: all_audio,
        show_progress_bar: true,
        // continue_after_error: true,
        error_message: `
        <div id="loading_files">
                <p>Error loading files</p>
                <p>Try refreshing the page or contact the researcher</p>
                <button class='loading_button', onclick="window.location.reload()">Refresh Page</button></div>
            `,
        max_load_time: 1000 * 60 * 2,
        message: "Loading files. Please wait...",
        // show_detailed_errors:true,
        on_error: function () {
            document.getElementById('jspsych-experiment').innerHTML = `
                <p>Errr loading</p>
                <button onclick="window.location.reload()">Refresh Page</button>
            `;
            // handleFirestoreError('Eror loading')
            // console.error("Error loading files.");
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                condition: user_instance.cName,
                recent_task: 'preload',
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let pti_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: '',
        choices: "NO_KEYS",
        // trial_duration: jsPsych.randomization.sampleWithoutReplacement([400, 500, 600, 700, 800, 900], 1),
        trial_duration: function () {
            return jsPsych.randomization.sampleWithoutReplacement([400, 500, 600, 700, 800, 900], 1)
        },
        // trial_duration: function () {
        //     return Math.floor(Math.random() * type_gap_delta) + type_gap_low;  // 1 second gap
        // },
        on_load: function () {
            let dim_el = document.getElementById('dim-overlay-opt')
            dim_el.style.visibility = 'visible'
            timerControl.noTimer = true;
        },
        on_finish: function () {
            timerControl.noTimer = false;
        }
    }


    let welcome_trial = {
        type: jsPsychHtmlKeyboardResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        // post_trial_gap:
        choices: ['n'],
        stimulus: welcome_text,
        on_load: function () {
            timerControl.noTimer = true;
        },
        on_finish: function () {
            // Keep track which task is done
            updateUser(auth_instance, user_instance, {
                recent_task: 'welcome'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            timerControl.noTimer = false;
        },
    }
    // <==========================

    // <===== Full screen trial
    let fullscreen_trial = {
        type: jsPsychFullscreen,
        fullscreen_mode: true,
        message: welcome_text,
        button_label: 'Continue to the Experiment',
        on_start: function () {
            should_be_in_fullscreen = true; // once this trial starts, the participant should be in fullscreen
        },
        on_finish: function () {
            if (!document.fullscreenElement) {
                jsPsych.pauseExperiment();
                document.getElementById('jspsych-experiment').innerHTML = `
                <p>Full screen error</p>
                <p>${load_error}</p>
                <button onclick="window.location.reload()">Refresh Page</button>
            `;
                console.warn("Fullscreen request failed or was denied.");
            }
        }

    }
    // <==========================

    // <===== Instructions
    let instructions = {
        type: jsPsychInstructions,
        pages: instr_pages,
        show_clickable_nav: true,
        button_label_previous: 'Go to the previous page',
        button_label_next: 'Go to the next page',
        allow_keys: false,
        do_alert: true,
        // function (current_page) {
        // if (current_page === instr_pages.length - 1) {
        //     console.log('last')
        //     return true
        // } else {
        //     console.log('not last')
        //     return false
        // }
        // },
        on_page_change: function (current_page) {
            let next_button_element = document.querySelector('button#jspsych-instructions-next')
            if (current_page === instr_pages.length - 1) {
                next_button_element.innerHTML = '<b style="color:red"><u>Start the experiment!</u></b>'

                // na_return_check(jsPsych, user_instance, next_button_element)
            }
        },
        show_page_number: true,
        on_finish: function () {
            // Keep track which task is done
            updateUser(auth_instance, user_instance, {
                recent_task: 'instructions'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            if (user_instance.last_checked) {
                // if rather not say, then ask to return submission
                // if (no_skip) {
                //     // save_fn_user(auth_instance_instance, user_instance, {
                //     //     completed: "Yes", returned: "Yes", code: 'RETURNED'
                //     // }).catch(() => {
                //     //     document.getElementById('jspsych-experiment').innerHTML = generic_error;
                //     // })
                //     jsPsych.abortExperiment(return_text)
                // }
            }
        }
    }
    // <==========================

    // <===== Practice
    let begin_practice_wait_trial = {
        type: jsPsychHtmlKeyboardResponse,
        trial_duration: 3000,
        // post_trial_gap: 500,
        choices: ['NO_KEYS'],
        stimulus: begin_practice_wait_text,
        on_load: function () {
            timerControl.noTimer = true;
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'begin_practice_wait'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            timerControl.noTimer = false;
        }
    }

    // Audio typing practice

    let type_practice_instr_trial = {
        // type: jsPsychHtmlKeyboardResponse,
        type: jsPsychHtmlButtonResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        // choices: ['n'],
        choices: ['Continue'],
        stimulus: type_practice_instr,
        do_countdown: true,
        on_load: function () {
            // timer_fn(phq9_pre_instr_duration, 77.5, 50)
            timer_fn(practice_instr_time, 99, 1)
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '70vh'
            // button_el.style.marginBottom = '20%'
            // console.log('time left', timerControl.trialRemaining)
            // let countdownTimer = timer_fn(diary_instr_time, 77.5, 50)
            // user_instance.timer_object = countdownTimer
        },
        trial_duration: (practice_instr_time + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'type_practice_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let audio_practice_trial = {
        type: jsPsychAudioKeyboardResponse,
        prompt: `<div><button type="button" id="play_audio"></abutton></div>`,
        stimulus: jsPsych.timelineVariable('stimulus'),
        choices: audio_full ? "NO_KEYS" : " ",
        response_ends_trial: !audio_full,// ? false : true,
        trial_ends_after_audio: audio_full,// ? true : false,
        // choices: "ALL_KEYS",
        // response_ends_trial: true,
        // choices: "NO_KEYS",
        // trial_ends_after_audio: true,
    }

    let type_practice_timeline_1 = {
        timeline: [audio_practice_trial, type_trials(
            jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_practice_preamble, '', 'type_practice_1', practice_time, practice_min_words, 'practice', 'type1'),
        ],
        timeline_variables: [
            {'stimulus': audio_attn[0]}
        ],
        on_timeline_start: function () {
            user_instance.count_type = 0
        },
        loop_function: function () {
            if (user_instance.do_submit) {
                // if user submitted reset practice fails counter and abort timeline
                return false
            } else {
                user_instance.time_left = (practice_time * 1000)
                // if failed and within acceptable number of fail, try again - unless word limit ok
                return true
                // if (user_instance.word_limit_ok) {
                //     return false
                // } else {
                //     return true
                // }

            }
        }
    }

    // let type_practice_timeline_2 = {
    //     timeline: [audio_practice_trial, type_trials(
    //         jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_practice_preamble, '', 'type_practice_2', practice_time, practice_min_words, 'practice', 'type2'),
    //     ],
    //     timeline_variables: [
    //         {'stimulus': audio_attn[1]}
    //     ],
    //     on_timeline_start: function () {
    //         // user_instance.count_type = 0
    //     },
    //     loop_function: function () {
    //         if (user_instance.do_submit) {
    //             // if user submitted reset practice fails counter and abort timeline
    //             // user_instance.count_pr = 0
    //             return false
    //
    //         } else {
    //             user_instance.time_left = (practice_time * 1000)
    //             return true
    //             // if failed and within acceptable number of fail, try again - unless word limit ok
    //             // if (user_instance.word_limit_ok) {
    //             //     return false
    //             // } else {
    //             //     return true
    //             // }
    //
    //         }
    //     }
    // }
    //
    // VAS practice
    let vas_practice_instr_trial = {
        // type: jsPsychHtmlKeyboardResponse,
        type: jsPsychHtmlButtonResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        // choices: ['n'],
        choices: ['Continue'],
        stimulus: vas_practice_instr,
        do_countdown: true,
        on_load: function () {
            // timer_fn(phq9_pre_instr_duration, 77.5, 50)
            timer_fn(vas_pr_instr_duration, 99, 1)
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '30vh'
            // let countdownTimer = timer_fn(diary_instr_time, 77.5, 50)
            // user_instance.timer_object = countdownTimer
        },
        trial_duration: (vas_pr_instr_duration + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'vas_practice_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let vas_practice1 = vas_practice_timeline(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, 0)

    // <==========================

    // <=========== Begin study
    let begin_study_wait_trial = {
        type: jsPsychHtmlKeyboardResponse,
        trial_duration: 3000,
        // post_trial_gap: 500,
        choices: ['NO_KEYS'],
        stimulus: begin_study_wait_text,
        on_load: function () {
            timerControl.noTimer = true;
            user_instance.count_pr = user_instance.count_type
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'begin_study_wait', warning_count_pr: user_instance.count_pr
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            timerControl.noTimer = false;
        }
    }

    // <==========================

    // <=========== Baseline questions
    // PHQ9 Baseline
    let phq9_baseline_instr = {
        // type: jsPsychHtmlKeyboardResponse,
        type: jsPsychHtmlButtonResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        // choices: ['n'],
        choices: ['Continue'],
        stimulus: phq9_baseline_pre_instr,
        do_countdown: true,
        on_load: function () {
            user_instance.count_type = 0
            timer_fn(phq9_pre_instr_duration, 99, 1)
            // timer_fn(phq9_pre_instr_duration, 77.5, 50)
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '0vh'
            // let countdownTimer = timer_fn(diary_instr_time, 77.5, 50)
            // user_instance.timer_object = countdownTimer
        },
        trial_duration: (phq9_pre_instr_duration + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'phq9_baseline_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let phq9_baseline = {
        timeline: [vas_qs_trial(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, phq9_total_trial_duration)],
        timeline_variables: phq9_qs_baseline.map((q, index) => ({
            stimulus: q,
            index: index,
            is_attn: q.includes('attention check'),
            label_list: phq9_label_list,
        })),
        data: {
            type: 'baseline',
            meta_type: 'phq9'
        }


    }

    // Open ended Baseline
    // let oq_baseline = type_trials(
    //     jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_preamble, oq_baseline_el, 'oq_baseline', oq_time, oq_min_words, 'baseline', 'open_q')
    // <==========================

    let oq_mood = type_trials(
        jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_preamble, oq_mood_el, 'oq_baseline', oq_time, oq_min_words, 'baseline', 'open_q_mood')

    let oq_energy = type_trials(
        jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_preamble, oq_energy_el, 'oq_baseline', oq_time, oq_min_words, 'baseline', 'open_q_energy')

    let recall_instr = {
        type: jsPsychHtmlButtonResponse,
        choices: ['Continue'],
        stimulus: recall_instr_text,
        do_countdown: true,
        on_load: function () {
            user_instance.count_type = 0
            timer_fn(recall_instr_duration, 99, 1)
        },
        trial_duration: (recall_instr_duration + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'recall_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }
    let recall_instr2 = {
        type: jsPsychHtmlButtonResponse,
        choices: ['Continue'],
        stimulus: recall_instr_text2,
        do_countdown: true,
        on_load: function () {
            user_instance.count_type = 0
            timer_fn(recall_instr2_duration, 99, 1)
        },
        trial_duration: (recall_instr2_duration + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'recall_instr2'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let recall_instr3 = {
        type: jsPsychHtmlButtonResponse,
        choices: ['Continue'],
        stimulus: recall_instr_text3,
        do_countdown: true,
        on_load: function () {
            user_instance.count_type = 0
            timer_fn(recall_instr3_duration, 99, 1)
        },
        trial_duration: (recall_instr3_duration + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'recall_instr3'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let word_list_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: jsPsych.timelineVariable('stimulus'),
        choices: "NO_KEYS",
        trial_duration: 1600,
        // post_trial_gap: jsPsych.randomization.sampleWithoutReplacement([400, 500, 600, 700, 800, 900], 1),
        on_load: function () {
            let dim_el = document.getElementById('dim-overlay-opt')
            dim_el.style.visibility = 'visible'
        },
        // on_load: function () {
        //     timerControl.noTimer = true;
        // },
        // on_finish: function () {
        //     let dim_el = document.getElementById('dim-overlay-opt')
        //     dim_el.style.visibility = 'hidden'
        // },
    }


    let word_list_timeline = {
        on_timeline_start: function () {
            user_instance.count_type = 0
            user_instance.count_w_list += 1
        },
        on_timeline_finish: function () {
            let word_data = jsPsych.data.get().filter({type: 'word_list_' + user_instance.count_w_list}).trials;
            let presented_order = word_data.map((trial, index) => {
                if (index % 2 == 0) {
                    return trial.stimulus.replace(`<div id="word_display">`, '').replace(`</div>`, '')
                } else {
                    return null
                }
            });
            presented_order = presented_order.filter(item => item !== null);

            updateUserDoc(auth_instance, user_instance, {
                ['word_list_' + user_instance.count_w_list]: presented_order,
            }, 'baseline', 'recall',).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
            })

            updateUser(auth_instance, user_instance, {
                recent_task: 'word_list_' + user_instance.count_w_list
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
            })
        },
        timeline: [word_list_trial, pti_trial],
        timeline_variables: word_listA.map((w) => ({
            stimulus: `<div id="word_display">${w}</div>`,
        })),
        randomize_order: true,
        data: {
            // type: 'word_list_0'
            type: function () {
                return 'word_list_' + user_instance.count_w_list
            }
        },
    }
    let word_recall1 = recall_trials(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, recall_preamble, "", 'recall1', recall_time, recall_min_words, 'baseline', 'recall')
    let word_recall2 = recall_trials(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, recall_preamble, "", 'recall2', recall_time, recall_min_words, 'baseline', 'recall')


    // <======= Intervention - typing
    // Recreate instructions
    let recreate_instr = {
        type: jsPsychHtmlButtonResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        choices: ['Continue'],
        stimulus: recreate_instr_text,
        do_countdown: true,
        on_load: function () {
            timer_fn(recreate_instr_time, 99, 1)
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '65vh'
            // timer_fn(diary_instr_time, 80, 50)
            // let countdownTimer = timer_fn(diary_instr_time, 77.5, 50)
            // user_instance.timer_object = countdownTimer
            user_instance.count_type = 0
        },
        trial_duration: (recreate_instr_time) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'diary_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    // Recreate audio elements
    let recreate_audio_trial = {
        type: jsPsychAudioKeyboardResponse,
        prompt: `<div><button type="button" id="play_audio"></abutton></div>`,
        stimulus: jsPsych.timelineVariable('stimulus'),
        // choices: "ALL_KEYS",
        // response_ends_trial: true,
        // choices: audio_full ? "NO_KEYS" : "ALL_KEYS",
        choices: audio_full ? "NO_KEYS" : " ",
        response_ends_trial: !audio_full,// ? false : true,
        trial_ends_after_audio: audio_full,// ? true : false,
        on_start: function (trial) {
            // user_instance.audio_file = jsPsych.timelineVariable('stimulus')
            // console.log(trial.stimulus, audio_words)
            // user_instance.audio_file_min_words = audio_words[trial.stimulus]
            // user_instance.audio_file_min_words = null
        },
        // on_load: function(){
        // }
        // choices: "NO_KEYS",
        // trial_ends_after_audio: true,
    }

    let audio_warn = {
        type: jsPsychHtmlKeyboardResponse,
        // post_trial_gap: 0,
        choices: ['n'],
        stimulus: `<div id="audio_ready">Get ready</div>`,
        trial_duration: (0.5) * 1000,
        on_load: function () {
            let dim_el = document.getElementById('dim-overlay-opt')
            dim_el.style.visibility = 'visible'
            timerControl.noTimer = true;
        },
        on_finish: function () {
            timerControl.noTimer = false;
        }
    }

    let audio_warn_again = {
        type: jsPsychHtmlKeyboardResponse,
        // post_trial_gap: 500,
        choices: ['n'],
        stimulus: `<div id="audio_ready">Listen again</div>`,
        trial_duration: (0.75) * 1000,
        on_load: function () {
            let dim_el = document.getElementById('dim-overlay-opt')
            dim_el.style.visibility = 'visible'
            timerControl.noTimer = true;
        },
        on_finish: function () {
            timerControl.noTimer = false;
        }
    }

    // Recreate trials and timeline
    let recreate_trials = type_trials(
        jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, recreate_preamble, '', 'recreate', recreate_time, recreate_min_words, 'intervention', 'recreate')

    let mood_baseline = {
        timeline: [vas_qs_trial(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, mood_total_trial_duration, mood_preamble_single, mood_label_list)],
        timeline_variables: mood_vas_question.map((q, index) => ({
            stimulus: q,
            index: index,
            is_attn: q.includes('attention check'),
            label_list: mood_label_list,
        })),
        data: {
            type: 'baseline',
            meta_type: 'vas_mood'
        }
    }


    let recreate_timeline = {
        timeline: [audio_warn, pti_trial, recreate_audio_trial, audio_warn_again, pti_trial, recreate_audio_trial, recreate_trials],
        timeline_variables: audio_condition.map((file) => ({
            stimulus: file
        })),
        // randomize_order: true,
        on_timeline_start: function () {
            // currentUser.dim_el.style.visibility = 'hidden'
            user_instance.count_type = 0
        },
        on_timeline_finish: function () {
            // user_instance.audio_file_min_words = null
        }
    }

    // <==========================

    // <======= Intervention - creating
    let act_instr = {
        type: jsPsychHtmlButtonResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        choices: ['Continue'],
        stimulus: act_instr_text,
        do_countdown: true,
        on_load: function () {
            user_instance.count_type = 0
            timer_fn(act_instr_time, 99, 1)
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '60vh'
            // timer_fn(diary_instr_time, 80, 50)
            // let countdownTimer = timer_fn(diary_instr_time, 77.5, 50)
            // user_instance.timer_object = countdownTimer
        },
        trial_duration: (act_instr_time + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'diary_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    // let act_trials = type_trials(
    //     jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, act_preamble, '', 'act', act_time, act_min_words, 'intervention', 'act')
    //
    // let act_timeline = {
    //     // timeline: [act_trials, act_trials, act_trials],
    //     timeline: [act_trials, pti_trial],
    //     on_timeline_start: function () {
    //         user_instance.time_left = (act_time * 1000)
    //     }
    //     ,
    //     loop_function: function () {
    //         if (user_instance.time_left <= 0) {
    //             return false
    //         } else {
    //             return true
    //         }
    //     }
    // }

    let act_timeline_new = type_trials(
        jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, act_preamble, '', 'act', act_time, act_min_words_total, 'intervention', 'act')

    let mood_fu = {
        timeline: [vas_qs_trial(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, mood_total_trial_duration, mood_preamble_single, mood_label_list)],
        timeline_variables: mood_vas_question.map((q, index) => ({
            stimulus: q,
            index: index,
            is_attn: q.includes('attention check'),
            label_list: mood_label_list,
        })),
        data: {
            type: 'fu',
            meta_type: 'vas_mood'
        }
    }
    // <RECALL AFTER INTERVENTION==========================
    let word_recall3 = recall_trials(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, recall_preamble, "", 'recall3', recall_time, recall_min_words, 'fu', 'recall')
    // <==========================

    // <=========== Follow-up questions
    // PHQ9 FU
    let phq9_fu_instr = {
        // type: jsPsychHtmlKeyboardResponse,
        type: jsPsychHtmlButtonResponse,
        // trial_duration: debug_mode,
        // post_trial_gap: 500,
        // choices: ['n'],
        choices: ['Continue'],
        stimulus: phq9_fu_pre_instr,
        do_countdown: true,
        on_load: function () {
            user_instance.count_type = 0
            timer_fn(phq9_pre_instr_duration, 99, 1)
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '20vh'
            // button_el.style.marginTop = '0vh'
            // let countdownTimer = timer_fn(diary_instr_time, 77.5, 50)
            // user_instance.timer_object = countdownTimer
        },
        trial_duration: (phq9_pre_instr_duration + 0) * 1000 + (dur_buffer * 1000),
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'phq9_fu_instr'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let phq9_fu = {
        timeline: [vas_qs_trial(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, phq9_total_trial_duration)],
        timeline_variables: phq9_qs_fu.map((q, index) => ({
            stimulus: q,
            index: index,
            is_attn: q.includes('attention check'),
            label_list: phq9_label_list,
        })),
        data: {
            type: 'fu',
            meta_type: 'phq9'
        }

    }

    // Open-ended FU
    // let oq_fu = type_trials(
    //     jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_preamble, oq_fu_el, 'oq_fu', oq_time, oq_min_words, 'fu', 'open_q')
    // ===============

    let oq_pospert = type_trials(
        jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, oq_preamble, oq_pospert_el, 'oq_pospert', pospert_time, pospert_min_words, 'fu', 'open_q_pospert')

    // <========== Experience questions
    let study_experience_vas = {
        timeline: [vas_qs_trial(jsPsych, user_instance, updateUserDoc, updateUser, auth_instance, experience_qs_duration, experience_qs_preamble, vas_exp_label_list)],
        timeline_variables: experience_qs.map((q, index) => ({
            stimulus: q,
            index: index,
            is_attn: q.includes('attention check'),
            label_list: vas_exp_label_list[index],
        })),
        data: {
            type: 'feedback',
            meta_type: 'closed_q'
        }


    }
    // ===============


    // <========== END trials
    // Thanks study trial
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
            timerControl.noTimer = true;
            let data_json = jsPsych.data.get().json()
            let data_csv = jsPsych.data.get().csv()
            // let data_json = 'Saved - but change to actual data'
            // let data_csv = 'Saved - but change to actual data'

            // Attention checks
            // user_instance.attention_check = user_instance.attention_check1 + user_instance.attention_check2


            // Save data and other info
            // console.log('Uploading data')
            updateUser(auth_instance, user_instance, {
                // Upload data to Firebase
                // attention_checks_total: user_instance.attention_check,
                attention_checks_bool: user_instance.attention_check > attention_threshold,
                // qsn_empty: qsn_isEmpty,
                // phq9_empty: phq9_isEmpty,
                z_dump_json: data_json,
                z_dump_csv: data_csv,
                completed: "Yes",
                warning_count: user_instance.warning_count,
            }).then(() => {
                // Finish this trial
                // console.log('Data uploaded')
                // console.log('Finishing the trial')
                jsPsych.finishTrial({
                    // attention_checks_total: user_instance.attention_check,
                    attention_checks_bool: user_instance.attention_check > attention_threshold,
                    // qsn_empty: qsn_isEmpty,
                })
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
            })
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'thanks_study'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            timerControl.noTimer = true;
        }
    }

    // End trials
    let end_study_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: end_study_text,
        trial_duration: end_study_duration,
        choices: ['NO_KEYS'],
        on_load: function () {
            timerControl.noTimer = true;
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'end_study'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            timerControl.noTimer = false;
        }
    }

    let trigger_end_trial = {
        // type: jsPsychHtmlKeyboardResponse,
        type: jsPsychHtmlButtonResponse,
        stimulus: trigger_text_end,
        trial_duration: trigger_end_duration * 1000,
        do_countdown: false,
        // choices: ['n'],
        choices: ['Continue'],
        data: {
            type: 'trigger'
        },
        on_load: function () {
            timerControl.noTimer = true;
            // let button_el = document.getElementById('jspsych-btn_mine_0')
            // button_el.style.marginTop = '70vh'
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'trigger_end'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
            timerControl.noTimer = false;
        }
    }

    let feedback_trial = {
        type: jsPsychSurveyText,
        questions: [{
            prompt: 'If you wish, please provide us with any feedback about the study.',
            rows: 8,
            columns: 100,
            name: 'Q0',
        }],
        button_label: 'Click here to finish and be redirected back to Prolific.',
        data: {
            type: 'feedback'
        },
        css_classes: ['feedback_trial'],
        trial_duration: (feedback_duration + 0) * 1000 + (dur_buffer * 1000),
        do_countdown: true,
        on_load: function () {
            timer_fn(feedback_duration, 99, 1)
        },
        on_finish: function (data) {
            let feedback_content = data['response']['Q0']
            if (feedback_content) {
                updateUserDoc(auth_instance, user_instance, {
                    ['response']: feedback_content
                }, 'feedback', 'open_q').catch(() => {
                    // console.log('error')
                    throw new Error(`Error when saving data: ${saving_error_doc}`); // Throw specific error
                    // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    // document.body.innerHTML = generic_error;
                })
                updateUser(auth_instance, user_instance, {feedback: feedback_content}).catch(() => {
                    throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                })
            }
            updateUser(auth_instance, user_instance, {
                recent_task: 'feedback'
            }).catch(() => {
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
            })
        }
    }

    let redirect_prolific_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: redirect_prolific_text,
        // trial_duration: 1000,
        choices: ['NO_KEYS'],
        on_load: function (data) {
            timerControl.noTimer = true;
            // console.log(user_instance)
            if (user_instance.attention_check <= attention_threshold) {
                // Completed the task successfully
                get_code(user_instance, 'completed').then(code => {
                    // console.log('Exiting with completed code: ', code)
                    // console.log('Exiting with completed code: ', code)
                    if (do_online) {
                        updateUser(auth_instance, user_instance, {code: code}).then(() => {
                            window.location.href = base_url + code
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                        })
                    }
                }).catch(() => {
                    throw new Error(`Error when getting code: ${code_retrieve_error}`); // Throw specific error
                })
            } else {
                // Failed the attention check threshold
                get_code(user_instance, 'failed_attention').then(code => {
                    if (do_online) {
                        updateUser(auth_instance, user_instance, {code: code}).then(() => {
                            window.location.href = base_url + code
                        }).catch(() => {
                            throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
                        })
                    }
                }).catch(() => {
                    throw new Error(`Error when getting code: ${code_retrieve_error}`); // Throw specific error
                })

            }

            jsPsych.finishTrial()
        },
        on_finish: function () {
            updateUser(auth_instance, user_instance, {
                recent_task: 'final_redirect'
            }).catch(() => {
                // document.getElementById('jspsych-experiment').innerHTML = generic_error;
                throw new Error(`Error when saving data: ${saving_error_user}`); // Throw specific error
            })
            timerControl.noTimer = false;
        }


    }
    // ===============


    let timeline = []

    function fill_timeline(timeline) {
        // Full screen trial
        timeline.push(preload_files)
        // timeline.push(fullscreen_trial)// <--------
        //
        // // // Instructions timeline
        // timeline.push(instructions) // <--------
        //
        // // // Begin practice phase
        // timeline.push(begin_practice_wait_trial) // <---------
        //
        //
        // // =========== Practice phase =============
        // // Type practice
        // timeline.push(type_practice_instr_trial) ///**/ <-----
        // timeline.push(pti_trial)// <---------
        // timeline.push(type_practice_timeline_1) // <-----
        //
        // // VAS practice
        // timeline.push(vas_practice_instr_trial) // <---------
        // timeline.push(pti_trial)// <---------
        // timeline.push(vas_practice1)  // <-------
        // timeline.push(pti_trial)// <---------
        //
        // // Begin study
        // timeline.push(begin_study_wait_trial) // <--------
        //
        // // ======= Main study =========
        // // Baseline PHQ9
        // timeline.push(phq9_baseline_instr)// <--------
        // timeline.push(pti_trial)// <---------
        // timeline.push(phq9_baseline)// <--------
        // timeline.push(pti_trial)// <---------
        //
        // //// Baseline open-ended question
        // timeline.push(oq_mood)// <--------
        // timeline.push(pti_trial)// <---------
        // timeline.push(oq_energy)// <--------
        //
        // // Word recall baseline
        // timeline.push(recall_instr)
        // timeline.push(pti_trial)// <---------
        // timeline.push(word_list_timeline)
        // timeline.push(pti_trial)// <---------
        // timeline.push(word_recall1)
        // timeline.push(pti_trial)// <---------
        // timeline.push(recall_instr2)
        // timeline.push(pti_trial)// <---------
        // timeline.push(word_list_timeline)
        // timeline.push(pti_trial)// <---------
        // timeline.push(word_recall2)

        // Baseline mood
        // timeline.push(mood_baseline)

        // Recreate audio and check
        // timeline.push(recreate_instr)// <--------
        // timeline.push(pti_trial)// <---------
        // timeline.push(recreate_timeline)// <--------

        // Create new entries <--------
        // timeline.push(act_instr) // <----
        // timeline.push(pti_trial)// <---------
        // timeline.push(act_timeline_new)// <-----

        // FU mood
        timeline.push(mood_fu)

        // Word recall FU
        timeline.push(recall_instr3)
        timeline.push(pti_trial)// <---------
        timeline.push(word_recall3)
        //
        // Follow-up PHQ9
        timeline.push(pti_trial)// <---------
        timeline.push(phq9_fu_instr)// <-------
        timeline.push(pti_trial)// <---------
        timeline.push(phq9_fu)// <-------
        timeline.push(pti_trial)// <---------


        // // Follow-up open-ended question
        timeline.push(oq_pospert)// <-------
        timeline.push(pti_trial)// <---------

        // Experience vas
        timeline.push(study_experience_vas) // <-------

        // End of study
        timeline.push(thanks_study_trial); // <--------
        timeline.push(end_study_trial); // <--------
        timeline.push(trigger_end_trial) // <--------
        timeline.push(redirect_prolific_trial) // <--------

        return timeline;
    }

    timeline = fill_timeline(timeline)

    if (run_sim) {
        jsPsych.simulate(timeline)
    } else {
        jsPsych.run(timeline);
    }
}

// Main promises - establish UID and consent then run study
document.addEventListener('DOMContentLoaded', async function () {
        // Add random delay when loading website
        // const minDelay = 100; // 1 second in milliseconds
        // const maxDelay = 300; // 3 seconds in milliseconds
        const randomDelay = Math.floor(Math.random() * (load_exp_maxDelay - load_exp_minDelay + 1)) + load_exp_minDelay;

        console.log(`Delaying website load by ${randomDelay / 1000} seconds.`);
        document.body.innerHTML += website_loading

        // --- Wait for the delay ---
        // Create a promise that resolves after the delay
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
            return
        }
        if (do_online) {
            try {
                // --- Online Flow ---

                // Establish authentication
                const auth = getAuth(app)

                // console.log("Starting online initialization flow...");

                // 1. Initiate Anonymous Sign In
                // console.log("Attempting anonymous sign-in...");
                await signInAnonymously(auth); // Use await, errors caught by try...catch
                // console.log("signInAnonymously call completed.");

                // 2. Wait for Auth State Confirmation & Get UID
                // console.log("Waiting for user UID confirmation...");
                const userId = await waitForUserAuth(auth, 15000); // Pass auth, wait up to 15s
                // console.log('User authenticated with UID:', userId);

                // 3. Instantiate currentUser *NOW* with the confirmed UID
                currentUser = new User(userId);
                // console.log("currentUser object created:", currentUser);

                // 4. Proceed with subsequent async steps...
                // console.log("Handling consent...");
                await handleConsent(currentUser, auth); // Assumes this uses currentUser

                // console.log("Updating user status...");
                await updateUser(auth, currentUser, {recent_task: 'consent'}); // Pass auth, currentUser

                // console.log("Checking completion status...");
                await handleCompletion(currentUser, auth); // Assumes this uses currentUser

                // console.log("Running study...");
                runStudy(currentUser, auth); // Run the study if all checks passed


            } catch (error) {
                // --- Centralized Error Handling for Online Flow ---
                console.error("Error during online initialization flow:", error);

                if (error.message === no_consent_error) {
                    // console.log("Consent not given or withdrawn. Attempting redirect...");
                    try {
                        // Pass currentUser only if getCodeAsync needs it (but it likely shouldn't)
                        const code = await get_code(currentUser, 'no_consent');
                        if (code) {
                            // console.log('Exiting with no_consent code:', code);
                            window.location.href = base_url + code;
                        } else {
                            console.error("'no_consent' code not found in Firestore.");
                            document.getElementById('jspsych-experiment').innerHTML = generic_error;
                        }
                    } catch (codeError) {
                        console.error("Error retrieving 'no_consent' code:", codeError);
                        document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    }
                } else if (error.message === study_completed_error) {
                    // console.log("Study already completed by this user.");
                    document.getElementById('jspsych-experiment').innerHTML = completed_text;
                } else if (error.message === prolific_ids_error) {
                    console.error("Prolific ID mismatch detected.");
                    document.getElementById('jspsych-experiment').innerHTML = generic_error; // Or specific message
                } else {
                    // General error handler
                    handleFirestoreError(error);
                    // if (!document.getElementById('jspsych-experiment').innerHTML.includes('Error') && !document.getElementById('jspsych-experiment').innerHTML.includes('completed')) {
                    //     document.getElementById('jspsych-experiment').innerHTML = generic_error;
                    // }
                }
            }
        } else {
            // offline version - just run the study
            // console.log("Running offline version...");
            currentUser = new User(null);
            let auth = null
            // console.log("currentUser object created:", currentUser);
            runStudy(currentUser, auth); // Run the study if all checks passed
        }


    }
);

