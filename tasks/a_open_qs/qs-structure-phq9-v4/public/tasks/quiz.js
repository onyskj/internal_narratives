/*
-------------------------------------------------
------------> Quiz texts <---------------
-------------------------------------------------
*/
let quiz_text = `
<div id='quiz_preamble'>
    <h2>This is a comprehension check. Check your understanding of the study.</h2>
    <h4>You can refer back to the instructions by scrolling through the text below.</h4>
    <div id='quiz_recap'>
        <div>` +
    instr_page2_main
    + `<br>
        </div>
        <div>
        ` +
    // instr_page3_main
    ``
    + `<br>
        </div>
    </div>
    <h4>Please answer the following questions. You need to get all the answers correct before you proceed with the experiment.</h4>
</div>    
`

// let qz_q1_options = ['One', 'Two', 'Three', 'Four']
let qz_q1_options = ['By providing a solution to simple maths problems', 'There is no option to respond', 'By recording myself', 'By writing text to a number of questions']
// let qz_q3_options = ['Multiple choice questions', 'Open-ended questions', 'Reading a story', 'A memory task']
let qz_q2_options = ['2 minutes', '1 minute', '30 seconds', '5 minutes']
let quiz = {
    questions: [{
        prompt: "How should you respond in the experiment?",
        name: "qz_q1",
        required: quiz_required,
        options: qz_q1_options
    },
    {
        prompt: "How long do you have to respond to each question in the experiment?",
        name: "qz_q2",
        required: quiz_required,
        options: qz_q2_options
    }],
    answers: {
        qz_q1: qz_q1_options[3],
        qz_q2: qz_q2_options[1],
        // qz_q3: qz_q3_options[0],
        // qz_q4: qz_q4_options[1]
    }
}

// let quiz_n_qs = quiz["questions"].length


let redo_quiz_text = `
    <div class="instr_stim">
    <h3>Oops! Not quite right.</h4>
    <p>You have a last chance. Please go through the instructions and try again.</p> 
    <br>
    <h4>If you fail the comprehension check this time, you will be asked to return your submission.</h4>
    
    <p class="next_page">Press <b>n</b> to proceed.</p>
    </div>
`

let failed_quiz_text = `
    <div class="instr_stim">
    <h3>Not quite right!</h3>
    <h4>Unfortunately, you have failed the comprehension check twice and won't be able to continue.</h4>
    <p>As per the <a href="https://researcher-help.prolific.com/en/article/fb63bb" target="_blank">latest policy</a>, you are asked to close the survey and then <u><b>return your submission</b></u> by clicking <b>"Stop Without Completing"</b> on Prolific.</p>
    <br>
    <a href="https://app.prolific.com/">Go to Prolific</a>
    </div>
`
