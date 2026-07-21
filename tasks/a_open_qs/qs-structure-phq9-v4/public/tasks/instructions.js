// ------------> Trigger texts <---------------

let trigger_text = `<div class="instr_stim trigger">
<p>If you become upset at any point when answering these questions, or are concerned about your mental health for any other reason, we recommend the below resources for further information.</p>
<p>You may also wish to discuss any concerns with your family doctor.</p>
    <ul style="list-style: none;">
        <li><a href="https://www.mind.org.uk/" target="_blank">Mind UK</a></li>
        <li><a href="https://www.samaritans.org/" target="_blank">Samaritans UK</a></li>
        <li><a href="https://www.nhs.uk/mental-health/" target="_blank">NHS Choices mental health page</a></li>
    </ul>
        <p class="next_page"></p>
        <p><b>This is the final instruction page. To proceed click "Start the experiment"</b></p>
    </div>
`

let trigger_text_end = `<div class="instr_stim trigger">
<p>If you became upset at any point when answering these questions, or are concerned about your mental health for any other reason, we recommend the below resources for further information.</p>
<p>You may also wish to discuss any concerns with your family doctor.</p>
    <ul style="list-style: none;">
        <li><a href="https://www.mind.org.uk/" target="_blank">Mind UK</a></li>
        <li><a href="https://www.samaritans.org/" target="_blank">Samaritans UK</a></li>
        <li><a href="https://www.nhs.uk/mental-health/" target="_blank">NHS Choices mental health page</a></li>
    </ul>
    </br>
    <p class="next_page">Press <b>n</b> to continue to the next page.</p>
    </div>
`

// ------------> Instruction texts <---------------

// Page - Welcome
let welcome_text = `
    <div class="instr_stim">
    <h2><b>Welcome to the experiment!</b></h2>
    <p>Thank you for consenting and taking time to help science.</p>
    <h4>Before we begin, please carefully go through the following instruction screens.</h4>
    <br>
    <p class="next_page">Press <b>n</b> to proceed.</p>
    </div>
`

// Page 2
let instr_page2_main = `
    <h4>In this experiment, you will have to answer questions by writing text.</h4>
    <p>The questions will be about yourself, your feelings, background, attitudes and behaviour in your everyday life.</p>
    <p>You will have <b>`+oq_timelimit_text+`</b> to write a response of at <b>least `+min_words.toString()+` words</b> for each question.</p>
`

let instr_page2 = `
    <div class="instr_stim">` +
    instr_page2_main
    + `<br>
        <p class="next_page"></p>
    </div>
`
// Page 3
let instr_page3_main = `
    <h4>In addition to open-ended questions, we will sometimes ask you multiple-choice questions.</h4>
    <p>Please read instructions at the top of each screen and then select one answer to each question.</p>
    <p>These will be <b>time-limited</b>, with a countdown provided towards the end of time.</p>
    `

let instr_page3 = `
    <div class="instr_stim">` +
    instr_page3_main
    + `<br>
        <p class="next_page"></p>
    </div>
`
// Page 4
let instr_page4_main = `
    <h4>We will also ask you about emotions that you are feeling.</h4>
    <p>You can select or unselect multiple.</p>
    <p>Please indicate this by clicking on appropriate buttons.</p>
    <p>You will have <b>30 seconds</b> to respond.</p>
    `
let instr_page4 = `
    <div class="instr_stim">` +
    instr_page4_main
    + `<br>
        <p class="next_page"></p>
    </div>
`

// Page 5
let instr_page5_main = `
    <div id='instr_req_warning'>
    <b>All the questions are required</b>. However, remember, you are <b>free to withdraw at any point</b>.<br>
    If you are <u>not comfortable answering a question, please indicate this by clicking a relevant checkbox.</u><br>
    You will then be asked to <b>return your submission.</b>
    </div>
    <br>
    &#8213;
    <p>You may notice that some questions look similar and appear to repeat themselves. <br>This is intentional, <b>please respond to all questions carefully and thoroughly.</b></p>
    &#8213;
    <p>As all the questions require a response within a time-limit, you will have to manage your time well.</p>
    <p>If you <b>exceed a time-limit</b> for a given question or do <b>not provide a full set of responses</b> more than <b>` + max_timeout + ` times</b> in total, <br>the experiment will stop and you will be asked to return your submission.</p>
    <p>To avoid this, be sure to <b>click the submit button before time runs out</b>!</p>
    `

let instr_page5 = `
    <div class="instr_stim">` +
    instr_page5_main
    + `<br>
        <p class="next_page"></p>
    </div>
`

// All pages
let instr_pages = [instr_page2, instr_page3, instr_page4, instr_page5, trigger_text]

// ------------> Study start texts <---------------
let begin_study_text = `
<div class="instr_stim">
    <h3>You have finished the instructions phase.</h3>
    <p>You can now proceed to the actual study</p>
    <br>
    <p class="next_page">Press <b>n</b> to proceed.</p>
    </div>
`

let begin_study_wait_text = `
    <div class="instr_stim">
    <h3>The experiment will start shortly.</h3>
    <h4>Please wait.</h4>
    </div>
`

// ------------> Study end texts and errors/cases <---------------
let thanks_study_text = `
    <div id="thanks_msg">Thanks!<br><br>Please wait while we save your data.
`

let end_study_text = `
    <div id="thanks_msg">Thanks!<br><br>
    <br><br>
    Please wait a few seconds. You will be redirected shortly.</div>
`

let redirect_prolific_text = `
    <div id="thanks_msg">Thanks!<br><br>You will be redirected to Prolific shortly.</div>
`

let completed_text = `
    <div class="completed_text">
    <h3>You have already completed the study, so won't be able to take part again.</h3>
    <a href="https://app.prolific.com/">Go back to Prolific</a>
    <p>If you became upset at any point when answering these questions, or are concerned about your mental health for any other reason, we recommend the below resources for further information.</p>
    <p>You may also wish to discuss any concerns with your family doctor.</p>
        <ul style="list-style: none;">
            <li><a href="https://www.mind.org.uk/" target="_blank">Mind UK</a></li>
            <li><a href="https://www.samaritans.org/" target="_blank">Samaritans UK</a></li>
            <li><a href="https://www.nhs.uk/mental-health/" target="_blank">NHS Choices mental health page</a></li>
        </ul>
    </br>
</div>
`

let return_text = `
    <div class="return_text">
    <p>Thank you for your interest in this study.</p>
    <p>However, it is very important to us to have a full set of answers.</p>
    <p>As a result, you won't be able to continue with the experiment.</p>
    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.</p>
    <a href="https://app.prolific.com/">Go to Prolific</a>
    <br><br>
    &#8213;
    <br>
    <p>If you became upset at any point when answering these questions, or are concerned about your mental health for any other reason, we recommend the below resources for further information.</p>
    <p>You may also wish to discuss any concerns with your family doctor.</p>
        <ul style="list-style: none;">
            <li><a href="https://www.mind.org.uk/" target="_blank">Mind UK</a></li>
            <li><a href="https://www.samaritans.org/" target="_blank">Samaritans UK</a></li>
            <li><a href="https://www.nhs.uk/mental-health/" target="_blank">NHS Choices mental health page</a></li>
        </ul>
    </br>
    </div>
`

let return_timeout_text = `
    <div class="return_text">
    <p>Thank you for your interest in this study.</p>
    <p>However, it is very important to us to have a full set of answers obtained within a time-limit.</p>
    <p>As a result, you won't be able to continue with the experiment.</p>
    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.</p>
    <a href="https://app.prolific.com/">Go to Prolific</a>
    <br><br>
    &#8213;
    <br>
    <p>If you became upset at any point when answering these questions, or are concerned about your mental health for any other reason, we recommend the below resources for further information.</p>
    <p>You may also wish to discuss any concerns with your family doctor.</p>
        <ul style="list-style: none;">
            <li><a href="https://www.mind.org.uk/" target="_blank">Mind UK</a></li>
            <li><a href="https://www.samaritans.org/" target="_blank">Samaritans UK</a></li>
            <li><a href="https://www.nhs.uk/mental-health/" target="_blank">NHS Choices mental health page</a></li>
        </ul>
    </br>
    </div>
`

let mobile_text = `
    <div class="instr_stim">
    <p>Thank you for your interest in this study.</p>
    <p>However, it is critical that you complete this task on a laptop or desktop computer, and our data indicates that you are using a mobile device.</p>
    <p>As a result, you won't be able to continue with the experiment.</p>
    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.'</p>
    <a href="https://app.prolific.com/">Go to Prolific</a>
    </div>
`

let generic_error = `
    <div class="instr_stim">
    <h3>Oops. Something went wrong. Please go back to Prolific and try again.</h3>
    <a href="https://app.prolific.com/">Go to Prolific</a>
    <h4>Alternatively contact the researcher</h4>
    </div>
`

let alert_content  = `
            <div id='formAlert'>
            <div id="oq_list"><p>You left out the following question(s): <span id="qsn_missing_qs"></span></p></div>
                ` + `<br><br>It is very important to us to have a full set of answers. <br><br>If you are not comfortable answering these questions, please proceed with a return of your submission to Prolific.
                    <div class="button_div">
                            <button class='alert_button' id="close_alert" >Continue with Experiment</button>
                            <button class='alert_button' id="return_alert">Return submission to Prolific</button>
                    </div>
            </div>
`
let alert_content_oq  = `
            <div id='formAlert'>
                <p>It is very important to us to have a full set of answers. <br><br>If you are not comfortable answering this question, please return your submission to Prolific.
                    <div class="button_div">
                            <button class='alert_button' id="close_alert" >Continue with Experiment</button>
                            <button class='alert_button' id="return_alert">Return submission to Prolific</button>
                    </div>
            </div>
`

let website_loading  = `
    <div id="loading_web" class="instr_stim">
    <h3>The study will load shortly.</h3>
    <h4>Please wait...</h4>
<!--    <h3>Please refresh the page.</h3>-->
<!--&lt;!&ndash;    <a href="https://app.prolific.com/">Go to Prolific</a>&ndash;&gt;-->
<!--    <h4>Alternatively contact the researcher</h4>-->
    </div>
`
let load_error = `
    <div class="instr_stim">
    <h3>Oops. Something went wrong</h3>
    <h3>Please refresh the page.</h3>
<!--    <a href="https://app.prolific.com/">Go to Prolific</a>-->
    <h4>Alternatively contact the researcher</h4>
    </div>
`