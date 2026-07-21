/*
-------------------------------------------------
------------> GAD-7 questions <---------------
-------------------------------------------------
*/
let gad7_preamble = `<div id="qs_preamble"><h3><u>Over the last 2 weeks, how often have you been bothered by the following problems?</u></h3>
<!--            <h4>Indicate your answer to each question and then submit by clicking the button at the bottom of the page.</h4>-->
<!--        <p id='qs_preamble_disclosure'>(You can click on the question/statement to reset your answer.)</p>-->
        <p id='qs_preamble_disclosure'>(Please, scroll down to see all the questions.)</p>
        <p id="qsn_time">You have <span id="qsn_time_left"></span> seconds left</p>
                                ` + avoid_answer_qsn + `
        </div>`

let gad7_map = {
    'Not at all': 0,
    'Several days': 1,
    'More than half the days': 2,
    'Nearly every day': 3,
    // "I'd rather not say": 0
};


let gad7_q1 = "Feeling nervous, anxious or on edge";
let gad7_q2 = "Not being able to stop or control worrying";
let gad7_q3 = "Worrying too much about different things";
let gad7_q4 = "Trouble relaxing";
let gad7_q5 = "Being so restless that it is hard to sit still";
let gad7_q6 = "Becoming easily annoyed or irritated";
let gad7_q7 = "Feeling afraid as if something awful might happen";

let gad7_qs = [gad7_q1, gad7_q2, gad7_q3, gad7_q4, gad7_q5, gad7_q6, gad7_q7]
let gad7_question_array = []

q = 0
for (let gad7_q of gad7_qs) {
    q += 1
    let q_string = q.toString() + ". "
    let tmp_json = {
        prompt: q_string + gad7_qs[q - 1],
        name: 'gad7_q' + q.toString(),
        options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
        // options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day', "I'd rather not say"],
        required: false
    }
    gad7_question_array.push(tmp_json)
}

