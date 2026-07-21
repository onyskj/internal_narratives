/*
-------------------------------------------------
------------> SDS questions <---------------
-------------------------------------------------
*/
let sds_preamble = `<div id="qs_preamble"><h3><u>For each item below, please select a response which best describes <br> how often you felt or behaved this way during the past several days.</u></h3>
<!--            <h4>Indicate your answer to each question and then submit by clicking the button at the bottom of the page.</h4>-->
        <p id='qs_preamble_disclosure'>(Please, scroll down to see all the questions.)</p>
        <p id="qsn_time">You have <span id="qsn_time_left"></span> seconds left</p>
                                ` + avoid_answer_qsn + `
        </div>`

let sds_map = {
    'A little of the time': 1,
    'Some of the time': 2,
    'Good part of the time': 3,
    'Most of the time': 4,
    // "I'd rather not say": 0
};

let sds_catch_q = "This is an attention check. Please select the 'Nearly every day' response."

let sds_q1 = "I feel down-hearted and blue.";
let sds_q2 = "Morning is when I feel the best.";
let sds_q3 = "I have crying spells or feel like it.";
let sds_q4 = "I have trouble sleeping at night.";
let sds_q5 = "I eat as much as I used to.";
let sds_q6 = "I still enjoy sex.";
let sds_q7 = "I notice that I am losing weight.";
let sds_q8 = "I have trouble with constipation.";
let sds_q9 = "My heart beats faster than usual.";
let sds_q10 = "I get tired for no reason.";
let sds_q11 = "My mind is as clear as it used to be.";
let sds_q12 = "I find it easy to do the things I used to.";
let sds_q13 = "I am restless and can't keep still.";
let sds_q14 = "I feel hopeful about the future.";
let sds_q15 = "I am more irritable than usual.";
let sds_q16 = "I find it easy to make decisions.";
let sds_q17 = "I feel that I am useful and needed.";
let sds_q18 = "My life is pretty full.";
let sds_q19 = "I feel that others would be better off if I were dead.";
let sds_q20 = "I still enjoy the things I used to do.";

let sds_qs = [sds_q1, sds_q2, sds_q3, sds_q4, sds_q5, sds_q6, sds_q7, sds_q8, sds_q9, sds_q10, sds_q11, sds_q12, sds_q13, sds_q14, sds_q15, sds_q16, sds_q17, sds_q18, sds_q19, sds_q20]
let sds_question_array = []

q = 0
for (let sds_q of sds_qs) {
    q += 1
    let q_string = q.toString() + ". "
    // if (q > 5) {
    //     q_string = (q + 1).toString() + ". "
    // }
    let tmp_json = {
        prompt: q_string + sds_qs[q - 1],
        name: 'sds_q' + q.toString(),
        options: ['A little of the time', 'Some of the time', 'Good part of the time', 'Most of the time'],
        // options: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day', "I'd rather not say"],
        required: false
    }
    sds_question_array.push(tmp_json)
}

