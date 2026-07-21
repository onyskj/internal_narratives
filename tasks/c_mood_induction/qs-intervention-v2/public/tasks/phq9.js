// PHQ-9 stuff
let phq9_q_time = 18//18
let phq9_preamble_duration = 2 //2
let phq9_total_trial_duration = phq9_q_time + phq9_preamble_duration
let phq9_pre_instr_duration = 10

let phq9_preamble_single = `
    <div><h3><u>Over the last 2 weeks, how often have you been bothered by the following problem?</u></h3>
    </div>
`

let phq9_baseline_pre_instr = `
    <div class="pre_trial_instr">
    <h3>First, please answer a number of questions about yourself.</h3>
        <p class="next_page"></p>
    </div>
`

let phq9_fu_pre_instr = `
    <div class="pre_trial_instr">
    <h3>Again, please answer a number of questions <span style="color:red">about yourself.</span></h3>
        <p class="next_page"></p>
    </div>
`


let phq9_label_list = ["Not at all", "Several days", "More than half the days", "Nearly every day"]

let phq9_q1 = "Little interest or pleasure in doing things.";
let phq9_q2 = "Feeling down, depressed, or hopeless.";
let phq9_q3 = "Trouble falling or staying asleep, or sleeping too much.";
let phq9_q4 = "Feeling tired or having little energy.";
let phq9_q5 = "Poor appetite or overeating.";
let phq9_q6 = "Feeling bad about yourself - or that you are a failure or have let yourself or your family down.";
let phq9_q7 = "Trouble concentrating on things, such as reading the newspaper or watching television.";
let phq9_q8 = "Moving or speaking so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual.";
let phq9_q9 = "Thoughts that you would be better off dead or of hurting yourself in some way.";

let phq9_catch1 = `This is an attention check. Click in the middle between "Not at all" and "Several days".`
let phq9_catch2 = `This is an attention check. Click on "More than half the days".`
let phq9_catch_ranges = {'baseline': [0.105, 0.225], 'fu': [0.6, 0.72]}

let phq9_qs_baseline = [phq9_q1, phq9_q2, phq9_q3, phq9_q4, phq9_catch1, phq9_q5, phq9_q6, phq9_q7, phq9_q8, phq9_q9]
let phq9_qs_fu = [phq9_q1, phq9_q2, phq9_q3, phq9_q4, phq9_q5, phq9_q6, phq9_q7, phq9_catch2, phq9_q8, phq9_q9]


