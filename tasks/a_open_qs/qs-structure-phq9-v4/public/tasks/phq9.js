/*
-------------------------------------------------
------------> PHQ-9 questions <---------------
-------------------------------------------------
*/
let phq9_preamble = `<div id="qs_preamble"><h3><u>Over the last 2 weeks, how often have you been bothered by any of the following problems?</u></h3>
<!--            <h4>Indicate your answer to each question and then submit by clicking the button at the bottom of the page.</h4>-->
        <p id='qs_preamble_disclosure'>(Please, scroll down to see all the questions.)</p>
        <p id="qsn_time">You have <span id="qsn_time_left"></span> seconds left</p>
                                ` + avoid_answer_qsn + `
        </div>`

let phq9_map = {
    'Not at all': 0,
    'Several days': 1,
    'More than half the days': 2,
    'Nearly every day': 3,
    // "I'd rather not say": 0
};

let phq9_catch_q = "This is an attention check. Please select the 'Nearly every day' response."
let phq9_catch_ans = 'Nearly every day'

let phq9_q1 = "Little interest or pleasure in doing things.";
let phq9_q2 = "Feeling down, depressed, or hopeless.";
let phq9_q3 = "Trouble falling or staying asleep, or sleeping too much.";
let phq9_q4 = "Feeling tired or having little energy.";
let phq9_q5 = "Poor appetite or overeating.";
let phq9_q6 = "Feeling bad about yourself - or that you are a failure or have let yourself or your family down.";
let phq9_q7 = "Trouble concentrating on things, such as reading the newspaper or watching television.";
let phq9_q8 = "Moving or speaking so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual.";
let phq9_q9 = "Thoughts that you would be better off dead or of hurting yourself in some way.";

let phq9_qs = [phq9_q1, phq9_q2, phq9_q3, phq9_q4, phq9_q5, phq9_q6, phq9_q7, phq9_q8, phq9_q9]
let phq9_question_array = []

q = 0
for (let phq9_q of phq9_qs) {
    q += 1
    let q_string = q.toString() + ". "
    if (q > 5) {
        q_string = (q + 1).toString() + ". "
    }
    let tmp_json = {
        prompt: q_string + phq9_qs[q - 1],
        name: 'phq9_q' + q.toString(),
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        // options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day', "I'd rather not say"],
        required: false
    }
    phq9_question_array.push(tmp_json)
    if (q === 5) {
        let catch_json = {
            prompt: (q + 1).toString() + ". " + phq9_catch_q,
            name: 'phq9_q_catch',
            options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
            // options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day', "I'd rather not say"],
            required: false
        }
        phq9_question_array.push(catch_json)
    }
}

