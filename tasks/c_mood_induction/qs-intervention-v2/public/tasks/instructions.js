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
    <p class="next_page"></p>
<!--    <p class="next_page">Press <b>n</b> to continue to the next page.</p>-->
    </div>

`

let trigger_text_fs = `<div class="instr_stim trigger tr_fs">
<p>If you became upset at any point when answering these questions, or are concerned about your mental health for any other reason, we recommend the below resources for further information.</p>
<p>You may also wish to discuss any concerns with your family doctor.</p>
<p><u>If you no longer wish to participate, please exit and return your submission.</u></p>
    <ul style="list-style: none;">
        <li><a href="https://www.mind.org.uk/" target="_blank">Mind UK</a></li>
        <li><a href="https://www.samaritans.org/" target="_blank">Samaritans UK</a></li>
        <li><a href="https://www.nhs.uk/mental-health/" target="_blank">NHS Choices mental health page</a></li>
    </ul>
    </div>
`

// ------------> Instruction texts <---------------

// Page - Welcome
// let welcome_text = `
//     <div class="instr_stim">
//     <h2><b>Welcome to the experiment!</b></h2>
//     <p>Thank you for consenting and taking time to help science.</p>
//     <h4>Before we begin, please carefully go through the following instruction screens.</h4>
//     <br>
//     <p class="next_page">Press <b>n</b> to proceed.</p>
//     </div>
// `

let welcome_text = `
    <div class="instr_stim">
    <h2><b>Welcome to the experiment!</b></h2>
<!--    <p>Thank you for consenting and taking time to help science.</p>-->
<!--    <p>Thank you for consenting and taking time to help science.</p>-->
<!--    <h4>Before we begin, please carefully go through the following instruction screens.</h4>-->
<!--    <br>-->
    <p class="next_page">The experiment will switch to full-screen mode when you continue.</p>
<!--    <p class="next_page">The experiment will switch to full-screen mode.</p>-->
<!--    <p style="color:red; font-weight: bold">Please remain in full-screen for the duration of the experiment.</pstyle>-->
<!--    <p style="color:red; font-weight: bold">Please remain in full-screen for the duration of the experiment.</pstyle>-->
<!--    <br>-->
<!--    <p class="next_page">Press <b>n</b> to proceed.</p>-->
    </div>
`

// Page 2
let instr_page2_main = `
    <h4></h4>
<!--    <h4>In this experiment, you will have to answer questions by writing text.</h4>-->
<!--    <h4>In this experiment, you will have to answer open-ended questions.</h4>-->
    <h3>In this experiment, you will listen to diary entries of someone who is either well or unwell.</h3>
    <p>Your goal will be to imagine being that person and then complete a set of tasks.</p>
    &#8213;
    <h3>We will also ask you to answer questions about yourself.</h3>
    <p>The questions will be about yourself, your feelings, background, attitudes and behaviour in your everyday life.</p>
<!--    <p>We will also ask you similar questions about someone else (not from your life).</p>-->
    &#8213;
    <h3>Sometimes, you will be asked to do a short memory task.</h3>
`

let instr_page2 = `
    <div class="instr_stim">` +
    instr_page2_main
    + `<br>
        <p class="next_page"></p>
    </div>
`
// Page 33
let instr_page3_main = `
        <h3>Throughout the experiment, there will be three types of tasks:</h3><br>
        <p>1. You will <b>TYPE</b> to answer open-ended questions, one word at a time.</p>
        <p>2. You will <b>RESPOND</b> to questions by clicking on a colour scale.</p>
        <p>3. You will <b>READ</b> diary entries, one at a time.</p>
<!--    <h4>Additionally, we will ask you questions about yourself, where you have to provide a response on a scale.</h4>-->
<!--    <p>First, read the instructions and the question at the top of each screen.</p> -->
<!--    <p>You will then indicate your response by clicking anywhere on the labelled color scale.</p>-->
<!--    <p>These will be <b>time-limited</b>, with a countdown provided towards the end of time.</p>-->
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
<!--    <h4>Lastly, you will have to carefully and diligently read a set of short texts.</h4>-->
<!--    <p>You will read one snippet at a time.</p>-->
<!--    <p>You can navigate between the texts as many times as you want by pressing the <b><u><i>left/right arrow key</i></u></b> on the keyboard.</p>-->
<!--    <p>You can select or unselect multiple.</p>-->
<!--    <p>Please indicate this by clicking on appropriate buttons.</p>-->
<!--    <p>You will have <b>30 seconds</b> to respond.</p>-->
<!--<p>At s point, you will be asked to</p>-->
    `
let instr_page4 = `
    <div class="instr_stim">` +
    instr_page4_main
    + `<br>
        <p class="next_page"></p>
    </div>
`

let example_timer = `<div class="timer animatable timer_example">
        <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">                        
            <circle cx="50%" cy="50%" r="40"/>
            <circle cx="50%" cy="50%" r="40" pathLength="1" stroke="#D32F2F" stroke-width="0.5vh" />
            <text x="50%" y="60%" text-anchor="middle">
                <tspan id="timeLeft">87</tspan>
            </text>
        </svg>
</div>`

let example_counter = `
<div id="word_counter_ex" class="counter_example">
<span id="n_words">6</span><span>/</span><span id="min_words">40</span>
</div>
`


let instr_page5a_main = `<adiv>
<h4>You will have to complete tasks within a specified time-limit as indicated by the countdown timer below.</h4>
${example_timer}
<br><br><br><br>&#8213;
<h4>Sometimes, you will have to type a minimum number of words.</h4>
<p>Your progress will be indicated on a bar as below.</p>
${example_counter}
<br>
<p>However, you are <u><i>encouraged to type as many words as you can.</i></u></p>
<!--&#8213;<br>-->
<!--<h4>You will submit your responses by clicking:</h4>-->
<!--<button id="instr_button"></button>-->
<!--<br>-->
</div>
`


let instr_page5a = `
    <div class="instr_stim">` +
    instr_page5a_main
    + `<br>
        <p class="next_page"></p>
    </div>
`

// Page 5
let instr_page5_main = `
    <div id='instr_req_warning'>
    <b>All the questions are required</b>. However, you are <b>free to withdraw at any point</b>.<br>
<!--    If you are <u>not comfortable answering a question, please indicate this by clicking a relevant checkbox.</u><br>-->
    If you are <u>not comfortable answering a question, please exit the study and return your submission.</u><br>
<!--    You will then be asked to <b>return your submission.</b>-->
    </div>
    <br>
    &#8213;
    <p>You may notice that some questions look similar and appear to repeat themselves. <br>This is intentional, <b>please respond to all questions carefully and thoroughly.</b></p>
<!--    // &#8213;-->
<!--    // <p>As all the questions require a response within a time-limit, you will have to manage your time well.</p>-->
<!--    // <p>If you <b>exceed a time-limit</b> for a given question or do <b>not provide a full set of responses</b> more than <b>` + max_timeout + ` times</b> in total, <br>the experiment will stop and you will be asked to return your submission.</p>-->
<!--    // <p>To avoid this, be sure to <b>click the submit button before time runs out</b>!</p>-->
    `

let instr_page5 = `
    <div class="instr_stim">` +
    instr_page5_main
    + `<br>
        <p class="next_page"></p>
    </div>
`

// All pages
// let instr_pages = [instr_page2, instr_page3, instr_page4, instr_page5a, instr_page5, trigger_text]
// let instr_pages = [instr_page2, instr_page3,  instr_page5a, instr_page5, trigger_text]
let instr_pages = [instr_page2, instr_page5a, instr_page5, trigger_text]
// let instr_pages = [ trigger_text]
// let instr_pages = [instr_page5a, instr_page5, trigger_text]
// let instr_pages = [instr_page2, instr_page3,  instr_page5, trigger_text]

// ------------> Practice phase start texts <---------------
let begin_practice_text = `
<div class="instr_stim">
    <h3>You have finished the instructions phase.</h3>
<!--    <p>You can now proceed to the actual study</p>-->
    <p>You can now proceed to the practice phase.</p>
    <br>
    <p class="next_page">Press <b>n</b> to proceed.</p>
    </div>
`

let begin_practice_wait_text = `
    <div class="instr_stim">
<!--    <h3>The experiment will start shortly.</h3>-->
    <h3>The practice phase will start shortly.</h3>
    <h4>Please wait.</h4>
    </div>
`

// ------------> Study start texts <---------------
let begin_study_text = `
<div class="instr_stim">
<!--    <h3>You have finished the instructions phase.</h3>-->
    <h3>You have finished the practice phase.</h3>
    <p>You can now proceed to the actual study</p>
<!--    <p>You can now proceed to the practice phase.</p>-->
    <br>
    <p class="next_page">Press <b>n</b> to proceed.</p>
    </div>
`

let begin_study_wait_text = `
    <div class="instr_stim">
    <h3>You have finished the practice phase.</h3>
    <h4>The experiment will start shortly.</h4>
    <br>
<!--    <h3>The practice phase will start shortly.</h3>-->
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
<!--    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.</p>-->
<!--    <a href="https://app.prolific.com/">Go to Prolific</a>-->
    <a href=${return_url}>Click here to return your submission</a>
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
<!--    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.</p>-->
<!--    <a href="https://app.prolific.com/">Go to Prolific</a>-->
    <a href=${return_url}>Click here to return your submission</a>
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

let return_text_practice = `
    <div class="return_text">
    <p>Thank you for your interest in this study.</p>
    <p>Unfortunately, you didn't manage to complete the instructions and practice phase successfully.</p>
    <p>As a result, you won't be able to continue with the experiment.</p>
    
<!--    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.</p>-->
<!--    <a href="https://app.prolific.com/">Go to Prolific</a>-->
    <a href=${return_url}>Click here to return your submission</a>

    
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

let return_text_fs = `
    <div class="return_text">
    <p>Thank you for your interest in this study.</p>
    <p>However, it is very important to us for the study to be completed in full-screen mode.</p>
    <p>As a result, you won't be able to continue with the experiment.</p>
<!--    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.</p>-->
<!--    <a href="https://app.prolific.com/">Go to Prolific</a>-->
    <a href=${return_url}>Click here to return your submission</a>
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
<!--    <p>Please return your submission on Prolific by clicking the 'stop without completing' button.'</p>-->
<!--    <a href="https://app.prolific.com/">Go to Prolific</a>-->
        <a href=${return_url}>Click here to return your submission</a>

    </div>
`

let generic_error = `
    <div class="instr_stim">
    <h3>Oops. Something went wrong. Please go back to Prolific and try again.</h3>
    <a href="https://app.prolific.com/">Go to Prolific</a>
    <h4>Alternatively contact the researcher</h4>
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
let website_loading  = `
    <div id="loading_web" class="instr_stim">
    <h3>The study will load shortly.</h3>
    <h4>Please wait...</h4>
<!--    <h3>Please refresh the page.</h3>-->
<!--&lt;!&ndash;    <a href="https://app.prolific.com/">Go to Prolific</a>&ndash;&gt;-->
<!--    <h4>Alternatively contact the researcher</h4>-->
    </div>
`


// ------- ALERT STUFF -------
let alert_content = `
            <div id='formAlert'>
            <div id="oq_list"><p>You left out the following question(s): <span id="qsn_missing_qs"></span></p></div>
                ` + `<br><br>It is very important to us to have a full set of answers. <br><br>If you are not comfortable answering these questions, please proceed with a return of your submission to Prolific.
                    <div class="button_div">
                            <button class='alert_button' id="close_alert" >Continue with Experiment</button>
                            <button class='alert_button' id="return_alert">Return submission to Prolific</button>
                    </div>
            </div>
`
let alert_content_oq = `
            <div id='formAlert'>
                <p>It is very important to us to have a full set of answers. <br><br>If you are not comfortable answering this question, please return your submission to Prolific.
                    <div class="button_div">
                            <button class='alert_button' id="close_alert" >Continue with Experiment</button>
                            <button class='alert_button' id="return_alert">Return submission to Prolific</button>
                    </div>
            </div>
`

let alert_content_instr = `
            <div id='formAlert'>
                <p>If you are not comfortable taking part in the study, please return your submission to Prolific.
                    <div class="button_div">
                            <button class='alert_button' id="close_alert" >Continue with Experiment</button>
                            <button class='alert_button' id="return_alert">Return submission to Prolific</button>
                    </div>
            </div>
`

let avoid_label = "If you'd rather not say, check this box and return your submission."
let avoid_answer_qsn = `<div id="qs_avoid_qsn">
        <label>
            <input type="checkbox" id="qs_preamble_na_check">
                <span>` + avoid_label + `</span> 
        </label>
    </div>
    `
